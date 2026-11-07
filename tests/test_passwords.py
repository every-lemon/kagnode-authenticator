"""Passwords additions preserve the existing vault format and account isolation."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch
from authentactor.server import create_app


class PasswordsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = create_app(self.directory.name)
        self.client = self.app.test_client()
        self.password = "Disposable password for regression tests!2026"
        self.headers = {"X-Requested-With": "Authentactor"}
        response = self.client.post(
            "/api/setup",
            json={"email": "owner@example.test", "password": self.password},
            headers=self.headers,
        )
        self.headers["X-CSRF-Token"] = response.json["csrf"]

    def send(self, path, data=None, method="POST"):
        return self.client.open(
            "/api" + path, method=method, json=data or {}, headers=self.headers
        )

    def test_notes_folders_trash_restore_and_explicit_purge(self):
        response = self.send(
            "/items", {"name": "Note", "notes": "Private content", "folder": "Personal"}
        )
        self.assertEqual(response.status_code, 201)
        uid = response.json["id"]
        self.assertNotIn(
            b"Private content",
            (self.app.extensions["vault_testing"]["db_path"]).read_bytes(),
        )
        self.send("/items/" + uid, method="DELETE")
        self.assertEqual(self.client.get("/api/items").json["items"], [])
        self.assertEqual(self.client.get("/api/items/" + uid).status_code, 404)
        trash = self.client.get("/api/trash").json["items"]
        self.assertEqual(trash[0]["folder"], "Personal")
        self.assertNotIn("Private content", json.dumps(trash))
        self.assertEqual(
            self.send("/trash/" + uid + "/purge", {"confirm": "wrong"}).status_code, 400
        )
        self.assertEqual(self.send("/trash/" + uid + "/restore").status_code, 200)
        self.assertEqual(
            self.client.get("/api/items/" + uid).json["item"]["notes"],
            "Private content",
        )
        self.send("/items/" + uid, method="DELETE")
        self.assertEqual(
            self.send("/trash/" + uid + "/purge", {"confirm": "Note"}).status_code, 200
        )
        self.assertEqual(self.client.get("/api/trash").json["items"], [])

    def test_export_requires_password_confirmation_csrf_and_preserves_vault(self):
        self.send(
            "/items",
            {
                "name": "Login",
                "password": "secret",
                "folder": "Work",
                "secret": "JBSWY3DPEHPK3PXP",
                "backup_codes": "CODE-ONE",
            },
        )
        uid = self.send("/items", {"name": "Deleted", "notes": "must not export"}).json[
            "id"
        ]
        self.send("/items/" + uid, method="DELETE")
        before = self.client.get("/api/items").json["items"]
        self.assertEqual(
            self.send("/export/bitwarden", {"password": self.password}).status_code, 400
        )
        self.assertEqual(
            self.send(
                "/export/bitwarden",
                {"password": "bad", "confirm": "unencrypted-export"},
            ).status_code,
            403,
        )
        data = {"password": self.password, "confirm": "unencrypted-export"}
        self.assertEqual(
            self.client.post(
                "/api/export/bitwarden",
                json=data,
                headers={"X-Requested-With": "Authentactor"},
            ).status_code,
            403,
        )
        response = self.send("/export/bitwarden", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(len(response.json["items"]), 1)
        self.assertEqual(response.json["items"][0]["login"]["password"], "secret")
        self.assertIn("otpauth://", response.json["items"][0]["login"]["totp"])
        self.assertIn("[Available] CODE-ONE", response.json["items"][0]["notes"])
        self.assertEqual(response.json["folders"][0]["name"], "Work")
        self.assertEqual(self.client.get("/api/items").json["items"], before)

    def test_new_account_cannot_see_trash_or_request_admin_updates(self):
        uid = self.send("/items", {"name": "Owner note", "notes": "private"}).json["id"]
        self.send("/items/" + uid, method="DELETE")
        other = self.app.test_client()
        headers = {"X-Requested-With": "Authentactor"}
        result = other.post(
            "/api/setup",
            json={"email": "other@example.test", "password": self.password},
            headers=headers,
        )
        headers["X-CSRF-Token"] = result.json["csrf"]
        self.assertEqual(other.get("/api/trash").json["items"], [])
        self.assertEqual(
            other.post(
                "/api/trash/" + uid + "/restore", json={}, headers=headers
            ).status_code,
            404,
        )
        result = other.post(
            "/api/kagnode-account",
            json={"action": "updates.apply", "release_id": 42},
            headers=headers,
        )
        self.assertEqual(result.status_code, 403)

    def test_legacy_backup_retains_trash_and_secure_notes(self):
        uid = self.send(
            "/items", {"name": "Saved note", "notes": "preserved", "folder": "Family"}
        ).json["id"]
        self.send("/items/" + uid, method="DELETE")
        backup = self.client.get("/api/backup").json
        self.assertEqual(backup["format"], "authentactor-encrypted-v1")
        self.send("/trash/" + uid + "/purge", {"confirm": "Saved note"})
        self.assertEqual(
            self.send(
                "/restore", {"backup": backup, "password": self.password}
            ).status_code,
            200,
        )
        self.assertEqual(self.client.get("/api/items").json["items"], [])
        self.assertEqual(
            self.client.get("/api/trash").json["items"][0]["name"], "Saved note"
        )

    def test_clients_only_returns_configured_https_origin(self):
        for origin in [
            "http://example.test",
            "https://name:secret@example.test",
            "https://example.test/abc",
            "https://example.test?secret=a",
        ]:
            with patch.dict(os.environ, {"KAGNODE_PASSWORDS_BITWARDEN_URL": origin}):
                self.assertFalse(self.client.get("/api/clients").json["configured"])
        with patch.dict(
            os.environ,
            {"KAGNODE_PASSWORDS_BITWARDEN_URL": "https://vault.example.test"},
        ):
            self.assertEqual(
                self.client.get("/api/clients").json["server"],
                "https://vault.example.test",
            )
