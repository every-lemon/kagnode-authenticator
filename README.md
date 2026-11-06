<p align="center"><img src="assets/kagnode-wordmark.svg" width="540" alt="KagNode. Authenticator"></p>

# KagNode Authenticator

A self-hosted authenticator and password manager with separate encrypted vaults for email-based accounts. KagNode's black-and-white interface, blue accents, rounded controls and mobile navigation surround the existing encrypted vault, with individually managed recovery codes.

**0.4.1 is a source preview.** It is a working personal vault, not a hosted KagNode account service or an independently audited password manager. Existing vault files and encrypted backups remain compatible.

## Start locally

Requires Python 3.10 or later.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m authentactor \
  --host 127.0.0.1 --port 8091 --data-dir ./preview-data --preview
```

Open [the local app](http://127.0.0.1:8091/) to create an email account and vault password, or [the sample vault](http://127.0.0.1:8091/demo) to explore fictional entries. No default password is supplied. Keep this personal server private. Anyone allowed to reach the app can create a separate account; email addresses are identifiers and are not verified. Use test credentials on HTTP; set up HTTPS before accessing real secrets over a network.

When updating an existing installation, keep its existing `--data-dir` value. The Python module, `AUTHENTACTOR_HOST`, `AUTHENTACTOR_PORT`, `AUTHENTACTOR_DATA`, compatibility service name and default `/var/lib/authentactor` location are retained. This update does not relocate or reset a vault. Without explicit flags, the legacy command still binds `0.0.0.0:80`; the example above deliberately uses an unprivileged loopback port.

## Pages with their own URLs

| Path | Page |
| --- | --- |
| `/overview` | Vault overview and recent items |
| `/authenticators` | Time-based verification codes |
| `/passwords` | Saved logins |
| `/backup-codes` | Accounts with recovery codes and remaining counts |
| `/favorites` | Starred entries |
| `/generator` | Password generator |
| `/security` | Password length, variety and reuse checks |
| `/settings` | Automatic locking, master password and backups |
| `/setup` | Create an email account and its separate vault |
| `/unlock` | Sign in with an email and vault password |
| `/demo` | Fictional sample vault |

Each section is a real server route. Links work directly and after refresh; browser Back/Forward follows navigation. A locked deep link returns to the requested section after setup or unlock. Redirect destinations are limited to known local pages. The demo serves an empty shell with fictional browser data; it never authorizes the vault API.

## What works

- TOTP from a Base32 setup key or `otpauth://totp/` link, including SHA1/SHA256/SHA512, 6/8 digits and 30/60-second periods. Accurate server time is required.
- Backup-code-only items, or recovery codes alongside a password or authenticator. Paste one code per line, up to 100 per item. Reveal and copy codes individually; explicitly mark a code used after the service accepts it, or undo that mark. Copying and viewing never consume a code. Used codes remain visible with their usage date; copying one requires marking it available first.
- Password-only, authenticator-only or combined entries; favorites, search, sorting, grid/list views and quick search with Ctrl/Cmd+K.
- Password generation with length and character controls. Security checks are local heuristics, not a breach-database lookup.
- Optional website icons fetched directly by your server. Private/internal addresses, unsafe redirects and oversized responses are rejected. Letter icons work without a fetch.
- Automatic lock after 5/15/30/60 idle minutes and an eight-hour maximum session lifetime.
- Encrypted backup download and merge restore. Matching IDs are skipped; existing entries remain. Old backups need the password used when they were created.
- Master-password rotation, which re-encrypts the vault and invalidates other sessions.
- Dark/light themes, keyboard-operated select controls, mobile navigation, reduced-motion support, load skeletons and retry actions.

## Accounts and an existing vault

Each email has its own salt, encrypted vault, settings and sessions. Sign in with
email and password; sign out before switching accounts. Creating another account
does not import or expose existing vault data. Changing a password signs out only
that account’s other sessions. This is independent of the main KagNode website’s
account system.

When upgrading a 0.1–0.3 installation, stop the app and make a protected backup of
its existing SQLite database first. Keep the same data directory and start with:

```sh
.venv/bin/python -m authentactor \
  --host 127.0.0.1 --port 8091 --data-dir /path/to/existing-vault \
  --legacy-email owner@example.com
```

`AUTHENTACTOR_LEGACY_EMAIL` is the equivalent environment setting. The migration
adds account tables in the existing database and copies the original salt and
ciphertext unchanged. It does not need or reset the password, decrypt items,
replace the database, or remove the original `vault` table. It is transactional
and runs only once. An unassigned legacy vault refuses startup without an explicit
owner email; an already assigned vault refuses a different owner.

The original owner’s future changes are mirrored to its retained legacy row for
emergency compatibility. Other accounts never write that row. A downgrade to the
old single-owner app cannot serve the additional accounts, so keep the upgraded
source and full database backup together. If the legacy app writes different data
after a downgrade, the newer app refuses to choose between the divergent copies;
review the preserved database and backups before continuing.

This app does not send verification or password-reset emails, share vaults, or
provide administrator access to someone else’s vault. A lost password cannot be
reset by email. Run one Waitress process; do not run multiple server workers for
the same data directory.

## Backup codes

Open **Backup codes → Add item**, enter the account name, and paste the service’s recovery codes one per line. You can also edit an existing item to attach codes. Spaces, hyphens and case inside each code are retained. Identical codes in the same item are rejected. Codes can be up to 512 characters each.

Codes are encrypted inside the existing vault document, including their identifiers, used state and usage dates. Item lists return counts, not the codes themselves. Opening a detail view requires an unlocked vault. Locking clears revealed values and edit fields from the page. Nothing is sent to the account’s service; the used state is your own record.

Editing an item preserves the state of unchanged codes. New codes start available, and omitted lines are removed when the edit is saved. Replacing a code set does not revoke the old codes at its service. Encrypted backups include codes and their used state; encrypted backups from 0.1–0.3 remain readable; existing databases use the additive account migration above. Merge restore keeps existing item IDs unchanged.

## Storage and security

Each account’s entire vault document is encrypted with Fernet before it enters SQLite. A fresh 16-byte salt and scrypt (`N=32768`, `r=8`, `p=1`) derive the key from the master password. The database contains account emails, independent salts and ciphertexts. Passwords and derived keys are not deliberately written to disk; active session keys exist in the server process's memory. This is **server-side encryption**, so a compromised running host can access an unlocked vault.

The data directory is mode 0700 and the database mode 0600. Random session cookies are HttpOnly and SameSite=Strict, and are Secure when the app receives a trusted HTTPS request. Writes require JSON, same-origin checks and a CSRF token. No-store responses, CSP and frame protection apply to the app. Browser storage contains only the theme preference, never vault credentials.

There is no password recovery, email verification, shared-vault access, cloud sync, browser autofill, QR scanning or hardware-key support. Keep encrypted backups and their corresponding passwords. Per-account limits are 1,000 entries and an 8 MB decrypted vault; requests are limited to 16 MB. See [SECURITY.md](SECURITY.md) for deployment and reporting details.

## HTTPS reverse proxy

Set up a valid TLS certificate on your proxy and forward **all paths**, including `/api/` and `/static/`, to this app. Do not rewrite every request to `/` or to `index.html`.

For a proxy on the same machine, run the app with:

```sh
.venv/bin/python -m authentactor \
  --host 127.0.0.1 --port 8091 --data-dir /path/to/existing-vault \
  --trusted-proxy 127.0.0.1
```

Inside the HTTPS virtual host, an Nginx location can be:

```nginx
location / {
    proxy_pass http://127.0.0.1:8091;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    client_max_body_size 16m;
}
```

`--trusted-proxy` (or `AUTHENTACTOR_TRUSTED_PROXY`) accepts one exact IP address. Forwarded host/scheme headers are ignored by default and from other peers. If your proxy runs on another machine, use its exact address and restrict backend access to it. The proxy must replace these headers, not append client-supplied values. This option creates neither a certificate nor a public listener on your proxy.

## Development and checks

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/pip install -r requirements-test.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python tests/browser_smoke.py
```

The browser suite starts its own temporary loopback server and vault, then removes them. It does not connect to an owner's installation. The checks cover real setup/unlock, direct routes, history, item creation, custom selects, backups, failed loads, both themes and small screens. GitHub Actions runs the unit and browser checks. See [VERIFICATION.md](VERIFICATION.md) for scope and remaining limits.

The compatibility Debian recipe in `packaging/` remains available for development. It preserves the existing `authentactor` package/service/data paths. It has not been installation-qualified for 0.4.1 and is not offered as a stable binary release. Runtime databases, backups and credentials are never included in source or packages.

## Source and identity

Application source is **AGPL-3.0-only**; see [LICENSE](LICENSE) and [NOTICE](NOTICE). KagNode artwork is covered separately by [ARTWORK-LICENSE](ARTWORK-LICENSE). The artwork terms do not restrict the rights granted by the software license or require a fork to retain KagNode branding.


UI assets
---------
The interface uses the shared KagNode black/white/blue design. Browser assets are minified and content-fingerprinted at build time; source maps are not published. Readable source and required license notices stay in this repository. Branding and hashes discourage casual reuse; they do not prevent inspection or copying.

To rebuild, install esbuild 0.28.2 as a development tool, then run:

```sh
ESBUILD=/path/to/esbuild python3 scripts/build-web.py --package authentactor --product Authenticator
```

Generated assets and their private package manifest ship with the application. Node.js is not required on the server.
