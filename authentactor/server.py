"""Separate encrypted vaults for email-based accounts. No master password or vault key is persisted."""
import base64
import hashlib
import hmac
import http.client
import ipaddress
import json
import os
import re
import secrets
import socket
import sqlite3
import ssl
import struct
import threading
import time
import uuid
from collections import Counter, defaultdict, deque
from functools import wraps
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit, urlunsplit, urlencode

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from flask import Flask, g, jsonify, make_response, redirect, request, send_from_directory
from werkzeug.exceptions import HTTPException
from .storage import email_address, initialize_database

VERSION = "0.5.0"
KDF = {"name": "scrypt", "n": 32768, "r": 8, "p": 1}
COOKIE = "authentactor_session"
PAGE_PATHS = ("/overview", "/authenticators", "/passwords", "/backup-codes", "/favorites", "/generator", "/security", "/settings")


class VaultError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status


def derive_key(password, salt):
    return base64.urlsafe_b64encode(Scrypt(salt=salt, length=32, n=KDF["n"], r=8, p=1).derive(password.encode()))


def normalize_url(value):
    value = str(value or "").strip()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    try:
        parts = urlsplit(value)
        if parts.scheme not in ("https", "http") or not parts.hostname or parts.username or parts.password:
            raise ValueError()
        if parts.port and parts.port not in (80, 443):
            raise ValueError()
        host = parts.hostname.encode("idna").decode("ascii")
        if len(value) > 2048 or any(c.isspace() for c in host) or any(c in value for c in "\r\n\x00"):
            raise ValueError()
        netloc = f"[{host}]" if ":" in host else host
        if parts.port:
            netloc += f":{parts.port}"
        return urlunsplit((parts.scheme, netloc, parts.path or "", "", ""))
    except (ValueError, UnicodeError):
        raise VaultError("Enter a valid http:// or https:// website URL (port 80 or 443).")


def parse_totp(secret, algorithm="SHA1", digits=6, period=30):
    secret = str(secret or "").strip()
    extras = {}
    if secret.lower().startswith("otpauth://"):
        try:
            uri = urlsplit(secret)
            if uri.netloc != "totp":
                raise VaultError("Only time-based (TOTP) setup links are supported.")
            q = parse_qs(uri.query)
            secret = q.get("secret", [""])[0]
            algorithm = q.get("algorithm", ["SHA1"])[0].upper()
            digits = q.get("digits", [6])[0]
            period = q.get("period", [30])[0]
            label = unquote(uri.path.lstrip("/"))
            extras = {"name": q.get("issuer", [label.split(":")[0]])[0], "username": label.split(":")[-1]}
        except ValueError:
            raise VaultError("That authenticator setup link is invalid.")
    try:
        digits, period = int(digits), int(period)
    except (ValueError, TypeError):
        raise VaultError("Invalid code length or refresh period.")
    algorithm = str(algorithm).upper()
    secret = re.sub(r"[\s=-]", "", secret).upper()
    if algorithm not in ("SHA1", "SHA256", "SHA512") or digits not in (6, 8) or period not in (30, 60):
        raise VaultError("Use SHA1/SHA256/SHA512, 6 or 8 digits, and a 30 or 60 second period.")
    if secret:
        try:
            raw = base64.b32decode(secret + "=" * ((-len(secret)) % 8), casefold=True)
            if not 10 <= len(raw) <= 128:
                raise ValueError()
        except (ValueError, base64.binascii.Error):
            raise VaultError("Enter a valid Base32 authenticator secret (at least 16 characters).")
    return {"secret": secret, "algorithm": algorithm, "digits": digits, "period": period}, extras


def totp_code(item, timestamp=None):
    now = time.time() if timestamp is None else timestamp
    secret = item["secret"]
    raw = base64.b32decode(secret + "=" * ((-len(secret)) % 8))
    counter = struct.pack(">Q", int(now // item.get("period", 30)))
    digest = hmac.new(raw, counter, getattr(hashlib, item.get("algorithm", "SHA1").lower())).digest()
    offset = digest[-1] & 15
    value = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff) % (10 ** item.get("digits", 6))
    return str(value).zfill(item.get("digits", 6))


def password_strength(password):
    if not password:
        return None
    groups = sum(bool(re.search(p, password)) for p in (r"[a-z]", r"[A-Z]", r"[0-9]", r"[^a-zA-Z0-9]"))
    if len(password) >= 16 and (groups >= 3 or len(password) >= 24):
        return "strong"
    return "fair" if len(password) >= 12 and groups >= 2 else "weak"


def clean_backup_codes(value, previous=()):
    """Keep code text exact and preserve usage when a multiline edit is unchanged."""
    if isinstance(value, str):
        if len(value) > 51300:
            raise VaultError("Save at most 100 backup codes, up to 512 characters each.")
        value = [line.strip() for line in value.splitlines() if line.strip()]
    if not isinstance(value, list) or len(value) > 100:
        raise VaultError("Use one backup code per line, up to 100 codes per item.")
    existing = {code["code"]: code for code in previous}
    result, seen, identifiers = [], set(), set()
    for entry in value:
        text = entry.get("code") if isinstance(entry, dict) else entry
        if not isinstance(text, str) or not text.strip() or len(text.strip()) > 512 or re.search(r"[\x00-\x1f\x7f]", text):
            raise VaultError("Each backup code must be a single line of 1–512 characters.")
        text = text.strip()
        if text in seen:
            raise VaultError("Remove duplicate backup codes before saving.")
        seen.add(text)
        metadata = entry if isinstance(entry, dict) else existing.get(text, {})
        try:
            identifier = str(uuid.UUID(metadata["id"])) if "id" in metadata else str(uuid.uuid4())
        except (ValueError, TypeError, AttributeError):
            raise VaultError("Invalid backup code identifier.")
        used = metadata.get("used", False)
        used_at = metadata.get("used_at")
        if type(used) is not bool or (used_at is not None and (type(used_at) is not int or not 0 <= used_at <= 2**53)):
            raise VaultError("Invalid backup code usage state.")
        if identifier in identifiers:
            raise VaultError("Backup code identifiers must be unique within an item.")
        identifiers.add(identifier)
        result.append({"id": identifier, "code": text, "used": used,
                       "used_at": (used_at if used_at is not None else int(time.time())) if used else None})
    return result


def clean_item(data, previous=None):
    if not isinstance(data, dict):
        raise VaultError("Invalid vault item.")
    previous = previous or {}
    name = str(data.get("name", "")).strip()
    if not name or len(name) > 100:
        raise VaultError("Give this item a name (up to 100 characters).")
    password = str(data.get("password", ""))
    username = str(data.get("username", "")).strip()
    notes = str(data.get("notes", ""))
    if len(password) > 1024 or len(username) > 256 or len(notes) > 8000:
        raise VaultError("An item field is too long.")
    otp, _ = parse_totp(data.get("secret", ""), data.get("algorithm", "SHA1"), data.get("digits", 6), data.get("period", 30))
    backup_codes = clean_backup_codes(data.get("backup_codes", previous.get("backup_codes", [])), previous.get("backup_codes", []))
    if not password and not otp["secret"] and not backup_codes:
        raise VaultError("Add a password, an authenticator secret, or backup codes.")
    icon = str(data.get("icon", ""))
    if icon:
        try:
            match = re.fullmatch(r"data:image/(png|jpeg|gif|webp|x-icon);base64,([A-Za-z0-9+/=]+)", icon)
            raw = base64.b64decode(match[2], validate=True) if match else b""
            if not raw or len(raw) > 120_000 or not image_type(raw):
                raise ValueError()
        except (ValueError, base64.binascii.Error):
            raise VaultError("The icon must be a small PNG, JPEG, GIF, WebP, or ICO image.")
    return {"id": previous.get("id", str(uuid.uuid4())), "name": name, "username": username,
            "url": normalize_url(data.get("url")), "password": password, **otp,
            "notes": notes, "icon": icon, "favorite": bool(data.get("favorite", False)), "backup_codes": backup_codes,
            "created_at": previous.get("created_at", int(time.time())), "updated_at": int(time.time())}


def image_type(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"\x00\x00\x01\x00"):
        return "x-icon"
    return None


class IconLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "link" and "icon" in attr.get("rel", "").lower() and attr.get("href"):
            self.links.append(attr["href"])


def public_fetch(url, deadline, max_bytes=262144):
    """Resolve once and pin the connection; revalidate every redirect to prevent SSRF."""
    for _ in range(4):
        url = normalize_url(url)
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
                raise VaultError("Icons can only be fetched from public websites.")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            conn = http.client.HTTPConnection(host, port, timeout=min(3, remaining))
            sock = socket.create_connection((addresses[0][4][0], port), timeout=min(3, remaining))
            if parsed.scheme == "https":
                sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
            conn.sock = sock
            try:
                conn.request("GET", parsed.path or "/", headers={"Host": parsed.netloc, "User-Agent": f"KagNode-Authenticator/{VERSION} favicon-fetcher", "Accept-Encoding": "identity"})
                response = conn.getresponse()
                if response.status in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.getheader("Location", ""))
                    continue
                if response.status != 200:
                    raise VaultError("This website did not return an icon.")
                chunks, total = [], 0
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError()
                    sock.settimeout(min(3, remaining))
                    chunk = response.read(min(16384, max_bytes + 1 - total))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total += len(chunk)
                    if total > max_bytes:
                        raise VaultError("The website icon is too large.")
                return b"".join(chunks), url
            finally:
                conn.close()
        except VaultError:
            raise
        except (OSError, http.client.HTTPException, ValueError):
            raise VaultError("Could not reach this website. You can still save it without an icon.")
    raise VaultError("The website redirected too many times.")


def fetch_icon(url):
    url = normalize_url(url)
    if not url:
        raise VaultError("Enter a website URL first.")
    deadline = time.monotonic() + 10
    candidates = []
    try:
        body, final = public_fetch(url, deadline)
        mime = image_type(body)
        if mime and len(body) <= 120000:
            return f"data:image/{mime};base64," + base64.b64encode(body).decode()
        parser = IconLinks()
        parser.feed(body.decode("utf-8", errors="ignore"))
        candidates = [urljoin(final, link) for link in parser.links[:2]]
    except VaultError as exc:
        if "public websites" in exc.message:
            raise
    candidates.append(urljoin(url, "/favicon.ico"))
    for candidate in candidates[:3]:
        if time.monotonic() >= deadline:
            break
        try:
            data, _ = public_fetch(candidate, deadline, 120000)
            mime = image_type(data)
            if mime:
                return f"data:image/{mime};base64," + base64.b64encode(data).decode()
        except VaultError:
            continue
    raise VaultError("No supported icon found. A letter icon will be used instead.")


def create_app(data_dir, preview=False, legacy_email=None):
    app = Flask(__name__, static_folder="static")
    from .web_assets import register_assets
    register_assets(app)
    app.url_map.strict_slashes = False
    app.config.update(MAX_CONTENT_LENGTH=16_000_000, JSON_SORT_KEYS=False)
    directory = Path(data_dir)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    db_path = directory / "vault.sqlite3"
    mutex = threading.RLock()
    sessions = {}
    failures = defaultdict(deque)
    icon_limits = defaultdict(deque)

    def connect():
        db = sqlite3.connect(db_path)
        db.execute("PRAGMA secure_delete=ON")
        return db

    initialize_database(db_path, legacy_email)
    os.chmod(db_path, 0o600)

    def any_accounts():
        with connect() as db:
            return bool(db.execute('SELECT 1 FROM accounts LIMIT 1').fetchone())

    def row(account_id):
        with connect() as db:
            return db.execute('SELECT salt,payload FROM accounts WHERE id=?', (account_id,)).fetchone()

    def read_vault(key, account_id):
        current = row(account_id)
        if not current:
            raise VaultError('Your account is unavailable.', 401)
        try:
            return json.loads(Fernet(key).decrypt(current[1]))
        except (InvalidToken, ValueError):
            raise VaultError('Incorrect email or password.', 401)

    def write_vault(vault, key, account_id, salt=None):
        clear = json.dumps(vault, ensure_ascii=False).encode()
        if len(clear) > 8_000_000:
            raise VaultError('Each account supports an 8 MB vault. Remove unused icons or items to make room.')
        payload = Fernet(key).encrypt(clear)
        state = getattr(g, 'vault_session', None)
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute('SELECT salt,secret_version FROM accounts WHERE id=?', (account_id,)).fetchone()
            if not current or not state or state['account_id'] != account_id or state['secret_version'] != current[1]:
                raise VaultError('Your vault is locked. Sign in again.', 401)
            new_salt = current[0] if salt is None else salt
            db.execute('UPDATE accounts SET salt=?,payload=?,secret_version=secret_version+? WHERE id=?', (new_salt, payload, int(salt is not None), account_id))
            # Preserve the original table, and mirror only its mapped owner's
            # legitimate changes so an emergency legacy rollback retains them.
            if db.execute('SELECT 1 FROM legacy_vault_owners WHERE account_id=?', (account_id,)).fetchone():
                db.execute('UPDATE vault SET salt=?,payload=? WHERE id=1', (new_salt, payload))

    def cleanup_sessions():
        now = time.time()
        for token, state in list(sessions.items()):
            if now - state["active"] >= state["timeout"] * 60 or now - state["created"] > 8 * 3600:
                sessions.pop(token, None)
                icon_limits.pop(token, None)
        for bucket, attempts in list(failures.items()):
            window = 900 if bucket.startswith('signup-') else 300
            while attempts and attempts[0] < now - window:
                attempts.popleft()
            if not attempts:
                failures.pop(bucket, None)

    def session_state():
        with mutex:
            cleanup_sessions()
            token = request.cookies.get(COOKIE, '')
            state = sessions.get(token)
            if state:
                with connect() as db:
                    current = db.execute('SELECT secret_version FROM accounts WHERE id=?', (state['account_id'],)).fetchone()
                if not current or current[0] != state['secret_version']:
                    sessions.pop(token, None)
                    return None
            return state

    def authenticated(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            state = session_state()
            if not state:
                raise VaultError('Your vault is locked. Sign in to continue.', 401)
            if request.method not in ('GET', 'HEAD') and not secrets.compare_digest(request.headers.get('X-CSRF-Token', '').encode(), state['csrf'].encode()):
                raise VaultError('Please reload the page and try again.', 403)
            g.vault_session = state
            return fn(*args, **kwargs)
        return inner

    def new_session(key, vault, account_id):
        cleanup_sessions()
        with connect() as db:
            email, version = db.execute('SELECT email,secret_version FROM accounts WHERE id=?', (account_id,)).fetchone()
        sessions.pop(request.cookies.get(COOKIE, ''), None)
        own = [(token, state) for token, state in sessions.items() if state['account_id'] == account_id]
        if len(own) >= 16:
            sessions.pop(min(own, key=lambda pair: pair[1]['active'])[0], None)
        if len(sessions) >= 256:
            raise VaultError('Too many active sessions. Try again after another session locks.', 429)
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        sessions[token] = {'key': key, 'account_id': account_id, 'email': email, 'secret_version': version,
                           'csrf': csrf, 'active': time.time(), 'created': time.time(), 'timeout': vault['settings']['auto_lock']}
        response = jsonify(ok=True, csrf=csrf, settings=vault['settings'], account={'email': email})
        response.set_cookie(COOKIE, token, httponly=True, secure=request.is_secure, samesite='Strict', path='/')
        return response

    @app.before_request
    def protect():
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            origin = request.headers.get("Origin")
            if request.headers.get("Sec-Fetch-Site") == "cross-site" or (origin and origin != request.host_url.rstrip("/")):
                raise VaultError("Cross-site requests are not allowed.", 403)
            if request.headers.get("X-Requested-With") != "Authentactor" or not request.is_json:
                raise VaultError("A same-origin JSON request is required.", 403)

    @app.after_request
    def headers(response):
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer", "Permissions-Policy": "camera=(), microphone=(), geolocation=()", "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"})
        return response

    @app.errorhandler(VaultError)
    def vault_error(error):
        return jsonify(error=error.message), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error="Request too large." if error.code == 413 else error.description), error.code

    @app.errorhandler(Exception)
    def unexpected(error):
        app.logger.error("Request failed: %s", type(error).__name__)
        return jsonify(error="The request could not be completed. Your saved vault has not been cleared."), 500

    def json_body():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise VaultError("Invalid JSON request.")
        return body

    @app.get("/")
    def index():
        if request.args.get("demo") == "1":
            return redirect("/overview?demo=1")
        return redirect("/overview" if session_state() else "/unlock" if any_accounts() else "/setup")

    @app.get("/unlock")
    @app.get("/setup")
    @app.get("/signup")
    def sign_in_page():
        target = request.args.get("next", "/overview")
        if target not in PAGE_PATHS:
            target = "/overview"
        if session_state():
            return redirect(target)
        expected = "/setup" if request.path in ("/setup", "/signup") or not any_accounts() else "/unlock"
        if request.path.rstrip("/") != expected:
            return redirect(expected + "?" + urlencode({"next": target}))
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/demo")
    def demo_page():
        return redirect("/overview?demo=1")

    def vault_page():
        # Demo routing serves only the empty shell. API authorization is always
        # enforced separately; adding ?demo=1 never unlocks a real vault.
        if request.args.get("demo") != "1" and not session_state():
            destination = "/unlock" if any_accounts() else "/setup"
            return redirect(destination + "?" + urlencode({"next": request.path.rstrip("/")}))
        return send_from_directory(app.static_folder, "index.html")

    for page_path in PAGE_PATHS:
        app.add_url_rule(page_path, endpoint="page_" + page_path[1:], view_func=vault_page, methods=["GET"])

    @app.get("/api/status")
    def status():
        state = session_state()
        return jsonify(initialized=any_accounts(), unlocked=bool(state), csrf=state["csrf"] if state else None,
                       settings={"auto_lock": state["timeout"]} if state else None, account={"email": state["email"]} if state else None, registration=True, preview=preview, version=VERSION)

    @app.post('/api/setup')
    def setup():
        body = json_body()
        try:
            email = email_address(body.get('email'))
        except ValueError as error:
            raise VaultError(str(error))
        password = body.get('password', '')
        if not isinstance(password, str) or not 12 <= len(password) <= 1024:
            raise VaultError('Use a password between 12 and 1024 characters.')
        with mutex:
            cleanup_sessions()
            if len(sessions) - int(request.cookies.get(COOKIE, '') in sessions) >= 256:
                raise VaultError('Too many active sessions. Try again after another session locks.', 429)
            now = time.time()
            for bucket, limit in (('signup-global', 20), ('signup-ip:'+request.remote_addr, 5)):
                q = failures[bucket]
                while q and q[0] < now - 900:
                    q.popleft()
                if len(q) >= limit:
                    raise VaultError('Too many account requests. Try again later.', 429)
                q.append(now)
            salt = secrets.token_bytes(16)
            key = derive_key(password, salt)
            vault = {'items': [], 'settings': {'auto_lock': 15}, 'created_at': int(now)}
            payload = Fernet(key).encrypt(json.dumps(vault).encode())
            identifier = str(uuid.uuid4())
            try:
                with connect() as db:
                    db.execute('INSERT INTO accounts(id,email,salt,payload,created) VALUES(?,?,?,?,?)', (identifier, email, salt, payload, int(now)))
            except sqlite3.IntegrityError:
                raise VaultError('Unable to create this account. Try signing in, or use another email.', 409)
            return new_session(key, vault, identifier)

    @app.post('/api/unlock')
    def unlock():
        body = json_body()
        password = body.get('password', '')
        try:
            email = email_address(body.get('email'))
        except ValueError:
            email = ''
        if not isinstance(password, str) or len(password) > 1024:
            raise VaultError('Incorrect email or password.', 401)
        with mutex:
            now = time.time()
            email_bucket = 'email:'+hashlib.sha256(email.encode()).hexdigest()
            for bucket, limit in (('global', 50), ('ip:'+request.remote_addr, 10), (email_bucket, 10)):
                q = failures[bucket]
                while q and q[0] < now - 300:
                    q.popleft()
                if len(q) >= limit:
                    raise VaultError('Too many sign-in attempts. Try again in five minutes.', 429)
            with connect() as db:
                account = db.execute('SELECT id,salt FROM accounts WHERE email=?', (email,)).fetchone()
            # Unknown emails still pay the same password-derivation cost.
            key = derive_key(password, account[1] if account else b'unknown-account!')
            try:
                if not account:
                    raise VaultError('Incorrect email or password.', 401)
                vault = read_vault(key, account[0])
            except VaultError:
                for bucket in ('global', 'ip:'+request.remote_addr, email_bucket):
                    failures[bucket].append(now)
                raise
            failures.pop(email_bucket, None)
            return new_session(key, vault, account[0])

    @app.post("/api/lock")
    @authenticated
    def lock():
        with mutex:
            sessions.pop(request.cookies.get(COOKIE), None)
        response = jsonify(ok=True)
        response.delete_cookie(COOKIE, path="/", samesite="Strict")
        return response

    @app.post("/api/activity")
    @authenticated
    def activity():
        with mutex:
            g.vault_session["active"] = time.time()
        return jsonify(ok=True)

    def summary(item, counts, now):
        public = {k: v for k, v in item.items() if k not in ("password", "secret", "backup_codes")}
        public.update(has_password=bool(item["password"]), has_totp=bool(item["secret"]),
                      strength=password_strength(item["password"]), reused=bool(item["password"] and counts[item["password"]] > 1))
        backup_codes = item.get("backup_codes", [])
        public.update(has_backup_codes=bool(backup_codes), backup_codes_total=len(backup_codes),
                      backup_codes_remaining=sum(not code["used"] for code in backup_codes))
        if item["secret"]:
            public.update(code=totp_code(item, now), expires_at=(int(now // item["period"]) + 1) * item["period"])
        return public

    @app.get("/api/items")
    @authenticated
    def list_items():
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            counts = Counter(i["password"] for i in vault["items"] if i["password"])
            now = time.time()
            return jsonify(items=[summary(i, counts, now) for i in vault["items"]], settings=vault["settings"], server_time=now)

    @app.get("/api/codes")
    @authenticated
    def codes():
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            now = time.time()
            return jsonify(server_time=now, codes=[{"id": i["id"], "code": totp_code(i, now), "expires_at": (int(now // i["period"]) + 1) * i["period"]} for i in vault["items"] if i["secret"]])

    @app.get("/api/items/<item_id>")
    @authenticated
    def item_detail(item_id):
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            item = next((i for i in vault["items"] if i["id"] == item_id), None)
            if not item:
                raise VaultError("Item not found.", 404)
            return jsonify(item=item)

    @app.post("/api/items")
    @authenticated
    def add_item():
        body = json_body()
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            if len(vault["items"]) >= 1000:
                raise VaultError("This version supports up to 1,000 items.")
            item = clean_item(body)
            vault["items"].append(item)
            write_vault(vault, g.vault_session["key"], g.vault_session["account_id"])
        return jsonify(ok=True, id=item["id"]), 201

    @app.route("/api/items/<item_id>", methods=["PUT", "DELETE"])
    @authenticated
    def update_item(item_id):
        body = json_body()
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            index = next((j for j, i in enumerate(vault["items"]) if i["id"] == item_id), None)
            if index is None:
                raise VaultError("Item not found.", 404)
            if request.method == "DELETE":
                vault["items"].pop(index)
            elif set(body) == {"favorite"}:
                vault["items"][index]["favorite"] = bool(body["favorite"])
            else:
                vault["items"][index] = clean_item(body, vault["items"][index])
            write_vault(vault, g.vault_session["key"], g.vault_session["account_id"])
        return jsonify(ok=True)

    @app.post("/api/items/<item_id>/backup-codes/<code_id>/usage")
    @authenticated
    def backup_code_usage(item_id, code_id):
        body = json_body()
        if set(body) != {"used"} or type(body["used"]) is not bool:
            raise VaultError("Choose whether this backup code has been used.")
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            item = next((i for i in vault["items"] if i["id"] == item_id), None)
            code = next((c for c in item.get("backup_codes", []) if c["id"] == code_id), None) if item else None
            if code is None:
                raise VaultError("Backup code not found.", 404)
            if code["used"] != body["used"]:
                code["used"] = body["used"]
                code["used_at"] = int(time.time()) if code["used"] else None
                item["updated_at"] = int(time.time())
                write_vault(vault, g.vault_session["key"], g.vault_session["account_id"])
            return jsonify(ok=True, used=code["used"], used_at=code["used_at"],
                           remaining=sum(not c["used"] for c in item["backup_codes"]))

    @app.post("/api/parse-totp")
    @authenticated
    def parse_setup():
        otp, extras = parse_totp(json_body().get("secret"))
        return jsonify(**otp, **extras)

    @app.post("/api/generate")
    @authenticated
    def generate():
        body = json_body()
        try:
            length = int(body.get("length", 20))
        except (ValueError, TypeError):
            raise VaultError("Choose a password length from 8 to 128.")
        if not 8 <= length <= 128:
            raise VaultError("Choose a password length from 8 to 128.")
        groups = [chars for flag, chars in (("uppercase", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), ("lowercase", "abcdefghijklmnopqrstuvwxyz"), ("numbers", "0123456789"), ("symbols", "!@#$%^&*()-_=+[]{}:,.?")) if body.get(flag, True)]
        if body.get("exclude_ambiguous", False):
            groups = ["".join(c for c in s if c not in "Il1O0o") for s in groups]
        if not groups:
            raise VaultError("Select at least one character type.")
        alphabet = "".join(groups)
        while True:
            password = "".join(secrets.choice(alphabet) for _ in range(length))
            if all(any(c in s for c in password) for s in groups):
                break
        return jsonify(password=password, strength=password_strength(password))

    @app.post("/api/icon")
    @authenticated
    def icon():
        token = request.cookies.get(COOKIE)
        with mutex:
            q = icon_limits[token]
            now = time.time()
            while q and q[0] < now - 60:
                q.popleft()
            if len(q) >= 12:
                raise VaultError("Please wait a minute before fetching more icons.", 429)
            q.append(now)
        return jsonify(icon=fetch_icon(json_body().get("url")))

    @app.put("/api/settings")
    @authenticated
    def settings():
        minutes = json_body().get("auto_lock")
        if minutes not in (5, 15, 30, 60):
            raise VaultError("Choose 5, 15, 30, or 60 minutes.")
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            vault["settings"]["auto_lock"] = minutes
            write_vault(vault, g.vault_session["key"], g.vault_session["account_id"])
            for state in sessions.values():
                if state["account_id"] == g.vault_session["account_id"]:
                    state["timeout"] = minutes
        return jsonify(ok=True)

    @app.get("/api/backup")
    @authenticated
    def backup():
        with mutex:
            salt, payload = row(g.vault_session["account_id"])
        response = jsonify(format="authentactor-encrypted-v1", version=1, kdf=KDF,
                           salt=base64.b64encode(salt).decode(), payload=payload.decode())
        response.headers["Content-Disposition"] = 'attachment; filename="kagnode-authenticator-encrypted-backup.json"'
        return response

    @app.post("/api/restore")
    @authenticated
    def restore():
        body = json_body()
        try:
            backup = body["backup"]
            password = body["password"]
            if not isinstance(password, str) or len(password) > 1024 or backup["format"] != "authentactor-encrypted-v1" or backup["kdf"] != KDF:
                raise ValueError()
            if not isinstance(backup.get("salt"), str) or not isinstance(backup.get("payload"), str):
                raise ValueError()
            salt = base64.b64decode(backup["salt"], validate=True)
            if len(salt) != 16:
                raise ValueError()
            imported = json.loads(Fernet(derive_key(password, salt)).decrypt(backup["payload"].encode()))
            if not isinstance(imported["items"], list) or len(imported["items"]) > 1000:
                raise ValueError()
            items = []
            for data in imported["items"]:
                item = clean_item(data)
                item["id"] = str(uuid.UUID(data["id"]))
                items.append(item)
        except (KeyError, TypeError, ValueError, InvalidToken):
            raise VaultError("Unable to read backup. Check its master password and file format.")
        with mutex:
            vault = read_vault(g.vault_session["key"], g.vault_session["account_id"])
            ids = {i["id"] for i in vault["items"]}
            added = []
            for item in items:
                if item["id"] not in ids:
                    ids.add(item["id"])
                    added.append(item)
            if len(vault["items"]) + len(added) > 1000:
                raise VaultError("The restored vault would exceed 1,000 items.")
            vault["items"].extend(added)
            write_vault(vault, g.vault_session["key"], g.vault_session["account_id"])
        return jsonify(ok=True, imported=len(added), skipped=len(items)-len(added))

    @app.post("/api/change-password")
    @authenticated
    def change_password():
        body = json_body()
        old, new = body.get("current", ""), body.get("password", "")
        if not isinstance(old, str) or not isinstance(new, str) or not 12 <= len(new) <= 1024 or len(old) > 1024:
            raise VaultError("Use a new master password of at least 12 characters.")
        with mutex:
            salt, _ = row(g.vault_session["account_id"])
            old_key = derive_key(old, salt)
            if not secrets.compare_digest(old_key, g.vault_session["key"]):
                raise VaultError("Current master password is incorrect.", 400)
            vault = read_vault(old_key, g.vault_session["account_id"])
            salt = secrets.token_bytes(16)
            key = derive_key(new, salt)
            account_id = g.vault_session['account_id']
            write_vault(vault, key, account_id, salt)
            for token, state in list(sessions.items()):
                if state['account_id'] == account_id:
                    sessions.pop(token, None)
            return new_session(key, vault, account_id)

    app.extensions["vault_testing"] = {"sessions": sessions, "read": read_vault, "db_path": db_path}
    return app
