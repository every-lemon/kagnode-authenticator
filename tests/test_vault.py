"""Security and persistence regressions for the first-edition vault."""

import base64
import json
import socket
import tempfile
import time
import unittest
from unittest.mock import patch

from authentactor.server import (
    create_app,
    derive_key,
    normalize_url,
    parse_totp,
    public_fetch,
    totp_code,
    VaultError,
)


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.app = create_app(self.tmp.name)
        self.client = self.app.test_client()
        self.headers = {"X-Requested-With": "Authentactor"}
        self.email = "owner@vault.test"
        self.password = "Test-vault-master!123"
        result = self.send("/setup", {"password": self.password})
        self.assertEqual(result.status_code, 200)
        self.headers["X-CSRF-Token"] = result.json["csrf"]

    def send(self, path, body=None, method="POST", client=None, headers=None):
        if path in ("/setup", "/unlock"):
            body = {**(body or {}), "email": self.email}
        return (client or self.client).open(
            "/api" + path,
            method=method,
            json=body or {},
            headers=headers or self.headers,
        )

    def add(self, **extra):
        data = {
            "name": "Test account",
            "username": "tester@example.test",
            "password": "Unique-Example!Long-937",
            "url": "https://example.com",
        }
        data.update(extra)
        result = self.send("/items", data)
        self.assertEqual(result.status_code, 201, result.json)
        return result.json["id"]

    def items(self):
        return self.client.get("/api/items").json["items"]

    def test_ciphertext_at_rest_and_restart(self):
        item_id = self.add(secret="JBSWY3DPEHPK3PXP")
        raw = self.app.extensions["vault_testing"]["db_path"].read_bytes()
        for clear in (
            b"Test account",
            b"Unique-Example!Long-937",
            b"JBSWY3DPEHPK3PXP",
            b"example.com",
            self.password.encode(),
        ):
            self.assertNotIn(clear, raw)
        restarted = create_app(self.tmp.name).test_client()
        self.assertEqual(restarted.get("/api/items").status_code, 401)
        unlock = self.send("/unlock", {"password": self.password}, client=restarted)
        self.assertEqual(unlock.status_code, 200)
        self.assertEqual(restarted.get("/api/items").json["items"][0]["id"], item_id)

    def test_crud_and_no_secret_in_summary(self):
        item_id = self.add(secret="JBSWY3DPEHPK3PXP")
        item = self.items()[0]
        self.assertTrue(item["has_password"] and item["has_totp"])
        self.assertNotIn("secret", item)
        self.assertNotIn("password", item)
        self.assertEqual(len(item["code"]), 6)
        self.assertEqual(
            self.send("/items/" + item_id, {"favorite": True}, "PUT").status_code, 200
        )
        self.assertTrue(self.items()[0]["favorite"])
        full = self.client.get("/api/items/" + item_id).json["item"]
        full["name"] = "Changed name"
        self.assertEqual(self.send("/items/" + item_id, full, "PUT").status_code, 200)
        self.assertEqual(self.items()[0]["name"], "Changed name")
        self.assertEqual(self.send("/items/" + item_id, {}, "DELETE").status_code, 200)
        self.assertEqual(self.items(), [])

    def test_csrf_and_cross_origin(self):
        self.assertEqual(
            self.client.post("/api/items", json={"name": "evil"}).status_code, 403
        )
        self.assertEqual(
            self.send(
                "/items", {}, headers={"X-Requested-With": "Authentactor"}
            ).status_code,
            403,
        )
        headers = {**self.headers, "Origin": "https://attacker.test"}
        self.assertEqual(self.send("/items", {}, headers=headers).status_code, 403)
        headers = {**self.headers, "Sec-Fetch-Site": "cross-site"}
        self.assertEqual(self.send("/items", {}, headers=headers).status_code, 403)
        res = self.client.get("/")
        self.assertIn("script-src 'self'", res.headers["Content-Security-Policy"])
        self.assertEqual(res.headers["Cache-Control"], "no-store")
        res.close()

    def test_lock_and_idle_expiration(self):
        self.add()
        self.assertEqual(self.send("/lock").status_code, 200)
        for path in ("/api/items", "/api/codes", "/api/backup"):
            self.assertEqual(self.client.get(path).status_code, 401)
        unlock = self.send("/unlock", {"password": self.password})
        self.headers["X-CSRF-Token"] = unlock.json["csrf"]
        sessions = self.app.extensions["vault_testing"]["sessions"]
        for session in sessions.values():
            session["active"] = time.time() - 3601
        self.assertEqual(self.client.get("/api/items").status_code, 401)
        self.assertEqual(len(sessions), 0)

    def test_unauthorized_detail_and_writes(self):
        item_id = self.add()
        other = self.app.test_client()
        self.assertEqual(other.get("/api/items/" + item_id).status_code, 401)
        for path, method in (
            ("/items", "POST"),
            ("/items/" + item_id, "DELETE"),
            ("/backup", "GET"),
            ("/restore", "POST"),
            ("/generate", "POST"),
            ("/icon", "POST"),
        ):
            self.assertEqual(self.send(path, {}, method, client=other).status_code, 401)

    def test_generator_category_and_length(self):
        for length in (8, 20, 64, 128):
            password = self.send("/generate", {"length": length}).json["password"]
            self.assertEqual(len(password), length)
            for chars in (
                "abcdefghijklmnopqrstuvwxyz",
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "0123456789",
                "!@#$%^&*()-_=+[]{}:,.?",
            ):
                self.assertTrue(any(c in chars for c in password))
        options = {
            "length": 40,
            "uppercase": False,
            "lowercase": False,
            "numbers": True,
            "symbols": False,
            "exclude_ambiguous": True,
        }
        password = self.send("/generate", options).json["password"]
        self.assertTrue(set(password) <= set("23456789"))
        self.assertEqual(
            self.send(
                "/generate",
                {
                    "uppercase": False,
                    "lowercase": False,
                    "numbers": False,
                    "symbols": False,
                },
            ).status_code,
            400,
        )
        self.assertEqual(self.send("/generate", {"length": 1000000}).status_code, 400)

    def test_backup_restore_and_duplicate_protection(self):
        first_id = self.add()
        backup = self.client.get("/api/backup").json
        self.assertNotIn("password", backup)
        self.assertNotIn("Unique-Example", json.dumps(backup))
        self.assertEqual(
            self.send("/restore", {"backup": backup, "password": "wrong"}).status_code,
            400,
        )
        result = self.send("/restore", {"backup": backup, "password": self.password})
        self.assertEqual((result.json["imported"], result.json["skipped"]), (0, 1))
        name = self.client.get("/api/items/" + first_id).json["item"]["name"]
        self.send("/items/" + first_id, {}, "DELETE")
        self.send("/trash/" + first_id + "/purge", {"confirm": name})
        self.add(name="Existing other item")
        result = self.send("/restore", {"backup": backup, "password": self.password})
        self.assertEqual((result.json["imported"], result.json["skipped"]), (1, 0))
        self.assertEqual(len(self.items()), 2)
        backup["kdf"]["n"] = 2**30
        self.assertEqual(
            self.send(
                "/restore", {"backup": backup, "password": self.password}
            ).status_code,
            400,
        )

    def test_master_rotation_and_other_session_revocation(self):
        self.add()
        other = self.app.test_client()
        self.send("/unlock", {"password": self.password}, client=other)
        new = "New-long-master-password!43"
        response = self.send(
            "/change-password", {"current": self.password, "password": new}
        )
        self.assertEqual(response.status_code, 200)
        self.headers["X-CSRF-Token"] = response.json["csrf"]
        self.assertEqual(other.get("/api/items").status_code, 401)
        self.assertEqual(len(self.items()), 1)
        self.send("/lock")
        self.assertEqual(
            self.send("/unlock", {"password": self.password}).status_code, 401
        )
        self.assertEqual(self.send("/unlock", {"password": new}).status_code, 200)

    def test_invalid_inputs_and_rate_limit(self):
        self.assertEqual(
            self.send("/items", {"name": "No credential"}).status_code, 400
        )
        self.assertEqual(
            self.send("/items", {"name": "Bad", "secret": "not-base32!"}).status_code,
            400,
        )
        self.assertEqual(
            self.send(
                "/items", {"name": "Bad", "password": "x", "url": "javascript:alert(1)"}
            ).status_code,
            400,
        )
        self.assertEqual(
            self.send(
                "/items",
                {
                    "name": "Bad",
                    "password": "x",
                    "icon": "data:image/svg+xml;base64,PHN2Zz4=",
                },
            ).status_code,
            400,
        )
        self.assertEqual(
            self.send("/settings", {"auto_lock": 0}, "PUT").status_code, 400
        )
        for _ in range(10):
            self.assertEqual(
                self.send("/unlock", {"password": "wrong"}).status_code, 401
            )
        self.assertEqual(
            self.send("/unlock", {"password": self.password}).status_code, 429
        )

    def test_reused_password_flags(self):
        self.add()
        self.add(name="Another account")
        self.assertTrue(all(i["reused"] for i in self.items()))


class ProtocolTests(unittest.TestCase):
    def test_rfc6238_vectors_all_algorithms(self):
        seeds = {
            "SHA1": b"12345678901234567890",
            "SHA256": b"12345678901234567890123456789012",
            "SHA512": b"1234567890123456789012345678901234567890123456789012345678901234",
        }
        vectors = [
            (59, ["94287082", "46119246", "90693936"]),
            (1111111109, ["07081804", "68084774", "25091201"]),
            (1111111111, ["14050471", "67062674", "99943326"]),
            (1234567890, ["89005924", "91819424", "93441116"]),
            (2000000000, ["69279037", "90698825", "38618901"]),
            (20000000000, ["65353130", "77737706", "47863826"]),
        ]
        for timestamp, expected in vectors:
            for (algorithm, seed), code in zip(seeds.items(), expected):
                item = {
                    "secret": base64.b32encode(seed).decode().rstrip("="),
                    "algorithm": algorithm,
                    "digits": 8,
                    "period": 30,
                }
                self.assertEqual(totp_code(item, timestamp), code)

    def test_setup_uri(self):
        otp, extra = parse_totp(
            "otpauth://totp/Example:me%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=Example&algorithm=SHA256&digits=8&period=60"
        )
        self.assertEqual(
            (otp["algorithm"], otp["digits"], otp["period"]), ("SHA256", 8, 60)
        )
        self.assertEqual(extra, {"name": "Example", "username": "me@example.com"})

    def test_ssrf_private_and_mixed_dns_are_blocked_before_connection(self):
        private = [
            "127.0.0.1",
            "169.254.169.254",
            "10.0.0.1",
            "192.168.0.7",
            "::1",
            "::ffff:127.0.0.1",
        ]
        for ip in private:
            with (
                patch(
                    "authentactor.server.socket.getaddrinfo",
                    return_value=[
                        (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))
                    ],
                ),
                patch("authentactor.server.socket.create_connection") as connection,
            ):
                with self.assertRaises(VaultError):
                    public_fetch("https://example.com/", time.monotonic() + 3)
                connection.assert_not_called()
        mixed = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))
            for ip in ["1.1.1.1", "127.0.0.1"]
        ]
        with patch("authentactor.server.socket.getaddrinfo", return_value=mixed):
            with self.assertRaises(VaultError):
                public_fetch("https://example.com/", time.monotonic() + 3)

    def test_url_restrictions(self):
        self.assertEqual(normalize_url("example.com"), "https://example.com")
        for url in [
            "file:///etc/passwd",
            "https://user:pass@example.com",
            "http://example.com:22",
            "https://example.com\r\nX:yes",
        ]:
            with self.assertRaises(VaultError):
                normalize_url(url)


if __name__ == "__main__":
    unittest.main()
