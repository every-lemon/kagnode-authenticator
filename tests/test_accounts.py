"""Account isolation and a byte-preserving migration from the original vault."""

import base64
import hashlib
import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from authentactor.server import create_app, derive_key

PASSWORD = "Disposable account password!2048"
HEADERS = {"X-Requested-With": "Authentactor"}


class AccountTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name
        self.app = create_app(directory.name)
        self.a, self.b = self.app.test_client(), self.app.test_client()
        self.ah = self.signup(self.a, "one@accounts.test", PASSWORD)
        self.bh = self.signup(self.b, "two@accounts.test", PASSWORD + "B")

    def signup(self, client, email, password):
        response = client.post(
            "/api/setup", json={"email": email, "password": password}, headers=HEADERS
        )
        self.assertEqual(response.status_code, 200, response.json)
        return {**HEADERS, "X-CSRF-Token": response.json["csrf"]}

    def add(self, client, headers, label):
        response = client.post(
            "/api/items",
            json={
                "name": label,
                "password": "Secret item password!",
                "secret": "JBSWY3DPEHPK3PXP",
                "backup_codes": "RECOVERY-1234\nRECOVERY-5678",
            },
            headers=headers,
        )
        self.assertEqual(response.status_code, 201)
        return response.json["id"]

    def test_every_vault_endpoint_is_scoped_to_the_signed_in_account(self):
        identifier = self.add(self.a, self.ah, "Only account one")
        self.assertEqual(self.b.get("/api/items").json["items"], [])
        self.assertEqual(self.b.get("/api/codes").json["codes"], [])
        self.assertEqual(self.b.get("/api/items/" + identifier).status_code, 404)
        for method in ("PUT", "DELETE"):
            response = self.b.open(
                "/api/items/" + identifier,
                method=method,
                json={"name": "Overwrite", "password": "Bad"},
                headers=self.bh,
            )
            self.assertEqual(response.status_code, 404)
        code = self.a.get("/api/items/" + identifier).json["item"]["backup_codes"][0][
            "id"
        ]
        response = self.b.post(
            f"/api/items/{identifier}/backup-codes/{code}/usage",
            json={"used": True},
            headers=self.bh,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(self.a.get("/api/items").json["items"]), 1)
        self.assertFalse(
            self.a.get("/api/items/" + identifier).json["item"]["backup_codes"][0][
                "used"
            ]
        )

    def test_password_rotation_and_lock_preferences_affect_only_one_account(self):
        self.add(self.a, self.ah, "One")
        self.add(self.b, self.bh, "Two")
        a2 = self.app.test_client()
        response = a2.post(
            "/api/unlock",
            json={"email": "one@accounts.test", "password": PASSWORD},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        self.a.put("/api/settings", json={"auto_lock": 5}, headers=self.ah)
        self.assertEqual(self.a.get("/api/status").json["settings"]["auto_lock"], 5)
        self.assertEqual(self.b.get("/api/status").json["settings"]["auto_lock"], 15)
        response = self.a.post(
            "/api/change-password",
            json={"current": PASSWORD, "password": PASSWORD + "changed"},
            headers=self.ah,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(a2.get("/api/items").status_code, 401)
        self.assertEqual(self.b.get("/api/items").status_code, 200)
        self.assertEqual(self.b.get("/api/items").json["items"][0]["name"], "Two")

    def test_backup_exports_only_its_owner_and_explicit_restore_stays_in_the_target(
        self,
    ):
        self.add(self.a, self.ah, "One private vault")
        self.add(self.b, self.bh, "Two private vault")
        backup = self.b.get("/api/backup").json
        salt = base64.b64decode(backup["salt"])
        vault = json.loads(
            Fernet(derive_key(PASSWORD + "B", salt)).decrypt(backup["payload"].encode())
        )
        self.assertEqual([i["name"] for i in vault["items"]], ["Two private vault"])
        response = self.a.post(
            "/api/restore",
            json={"backup": backup, "password": PASSWORD + "B"},
            headers=self.ah,
        )
        self.assertEqual(response.json["imported"], 1)
        self.assertEqual(len(self.a.get("/api/items").json["items"]), 2)
        self.assertEqual(len(self.b.get("/api/items").json["items"]), 1)

    def test_emails_are_required_normalized_unique_and_not_bearer_credentials(self):
        client = self.app.test_client()
        response = client.post(
            "/api/setup",
            json={"email": " ONE@ACCOUNTS.TEST ", "password": PASSWORD},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 409)
        for email in [
            "",
            None,
            "not-an-email",
            "one@accounts.test\nX:evil",
            "a..b@example.test",
        ]:
            response = client.post(
                "/api/setup",
                json={"email": email, "password": PASSWORD},
                headers=HEADERS,
            )
            self.assertEqual(response.status_code, 400, email)
        response = client.post(
            "/api/unlock",
            json={"email": " ONE@ACCOUNTS.TEST ", "password": PASSWORD},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["account"]["email"], "one@accounts.test")
        self.assertEqual(
            client.get("/api/items?email=two@accounts.test").json["items"], []
        )
        client.post(
            "/api/lock",
            json={},
            headers={**HEADERS, "X-CSRF-Token": response.json["csrf"]},
        )
        response = client.post(
            "/api/unlock",
            json={"email": "two@accounts.test", "password": PASSWORD},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"], "Incorrect email or password.")
        self.assertEqual(
            client.get("/api/items?email=one@accounts.test").status_code, 401
        )

    def test_session_and_csrf_tokens_cannot_be_used_to_select_another_vault(self):
        self.add(self.a, self.ah, "One")
        response = self.b.put("/api/settings", json={"auto_lock": 5}, headers=self.ah)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.b.get("/api/status").json["settings"]["auto_lock"], 15)
        self.a.post("/api/lock", json={}, headers=self.ah)
        self.assertEqual(self.a.get("/api/status").json["account"], None)
        self.assertEqual(
            self.b.get("/api/status").json["account"]["email"], "two@accounts.test"
        )

    def test_unknown_emails_and_wrong_passwords_have_the_same_error(self):
        client = self.app.test_client()
        failures = []
        for email in ["one@accounts.test", "unknown@accounts.test"]:
            response = client.post(
                "/api/unlock",
                json={"email": email, "password": "Incorrect password"},
                headers=HEADERS,
            )
            failures.append((response.status_code, response.json))
        self.assertEqual(failures[0], failures[1])


class LegacyMigrationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.path = self.directory / "vault.sqlite3"
        self.salt = b"legacy-salt-1234"
        self.vault = {
            "items": [
                {
                    "id": "09388145-f133-4d08-82a8-973d3680f2c4",
                    "name": "Retained legacy item",
                    "password": "Original item password",
                    "username": "owner@example.test",
                    "url": "",
                    "secret": "JBSWY3DPEHPK3PXP",
                    "algorithm": "SHA1",
                    "digits": 6,
                    "period": 30,
                    "notes": "Original notes",
                    "icon": "",
                    "favorite": True,
                    "backup_codes": [
                        {
                            "id": "09388145-f133-4d08-82a8-973d3680f2c5",
                            "code": "USED-BACKUP-CODE",
                            "used": True,
                            "used_at": 1700000000,
                        }
                    ],
                    "created_at": 1700000000,
                    "updated_at": 1700000000,
                }
            ],
            "settings": {"auto_lock": 30},
            "created_at": 1700000000,
        }
        self.payload = Fernet(derive_key(PASSWORD, self.salt)).encrypt(
            json.dumps(self.vault).encode()
        )
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE vault(id INTEGER PRIMARY KEY CHECK(id=1),salt BLOB NOT NULL,payload BLOB NOT NULL)"
            )
            db.execute("INSERT INTO vault VALUES(1,?,?)", (self.salt, self.payload))

    def test_migration_copies_existing_ciphertext_and_original_table_without_reset(
        self,
    ):
        app = create_app(self.directory, legacy_email="caleb@example.test")
        with sqlite3.connect(self.path) as db:
            self.assertEqual(
                db.execute("SELECT salt,payload FROM vault").fetchone(),
                (self.salt, self.payload),
            )
            self.assertEqual(
                db.execute("SELECT salt,payload FROM accounts").fetchone(),
                (self.salt, self.payload),
            )
            self.assertEqual(
                db.execute("SELECT email FROM accounts").fetchone()[0],
                "caleb@example.test",
            )
        client = app.test_client()
        response = client.post(
            "/api/unlock",
            json={"email": "caleb@example.test", "password": PASSWORD},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        item = client.get("/api/items").json["items"][0]
        self.assertEqual(item["id"], self.vault["items"][0]["id"])
        self.assertEqual(item["backup_codes_remaining"], 0)
        self.assertEqual(
            client.get("/api/items/" + item["id"]).json["item"]["notes"],
            "Original notes",
        )
        create_app(self.directory, legacy_email="caleb@example.test")
        with sqlite3.connect(self.path) as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM accounts").fetchone()[0], 1
            )

    def test_missing_owner_or_changed_owner_refuses_without_overwriting_the_vault(self):
        with self.assertRaisesRegex(ValueError, "legacy-email"):
            create_app(self.directory)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(
                db.execute("SELECT salt,payload FROM vault").fetchone(),
                (self.salt, self.payload),
            )
            self.assertIsNone(
                db.execute(
                    "SELECT 1 FROM sqlite_master WHERE name='accounts'"
                ).fetchone()
            )
        create_app(self.directory, legacy_email="caleb@example.test")
        with self.assertRaisesRegex(ValueError, "ownership"):
            create_app(self.directory, legacy_email="different@example.test")
        with sqlite3.connect(self.path) as db:
            self.assertEqual(
                db.execute("SELECT email FROM accounts").fetchone()[0],
                "caleb@example.test",
            )

    def test_other_accounts_cannot_modify_legacy_data_and_owner_edits_keep_a_rollback_copy(
        self,
    ):
        app = create_app(self.directory, legacy_email="caleb@example.test")
        other = app.test_client()
        response = other.post(
            "/api/setup",
            json={"email": "someone@example.test", "password": PASSWORD + "other"},
            headers=HEADERS,
        )
        h = {**HEADERS, "X-CSRF-Token": response.json["csrf"]}
        other.post(
            "/api/items",
            json={"name": "Someone else", "password": "Another password"},
            headers=h,
        )
        with sqlite3.connect(self.path) as db:
            self.assertEqual(
                db.execute("SELECT payload FROM vault").fetchone()[0], self.payload
            )
        owner = app.test_client()
        response = owner.post(
            "/api/unlock",
            json={"email": "caleb@example.test", "password": PASSWORD},
            headers=HEADERS,
        )
        h = {**HEADERS, "X-CSRF-Token": response.json["csrf"]}
        owner.put("/api/settings", json={"auto_lock": 5}, headers=h)
        with sqlite3.connect(self.path) as db:
            legacy = db.execute("SELECT salt,payload FROM vault").fetchone()
            current = db.execute(
                "SELECT salt,payload FROM accounts WHERE email=?",
                ("caleb@example.test",),
            ).fetchone()
            self.assertEqual(legacy, current)
        self.assertEqual(
            json.loads(Fernet(derive_key(PASSWORD, legacy[0])).decrypt(legacy[1]))[
                "settings"
            ]["auto_lock"],
            5,
        )

    def test_changed_legacy_copy_after_a_downgrade_is_not_silently_overwritten(self):
        create_app(self.directory, legacy_email="caleb@example.test")
        changed = Fernet(derive_key(PASSWORD, self.salt)).encrypt(
            json.dumps({**self.vault, "created_at": 1700000010}).encode()
        )
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE vault SET payload=? WHERE id=1", (changed,))
        with self.assertRaisesRegex(ValueError, "contents differ"):
            create_app(self.directory, legacy_email="caleb@example.test")
        with sqlite3.connect(self.path) as db:
            self.assertEqual(
                db.execute("SELECT payload FROM vault").fetchone()[0], changed
            )
            self.assertEqual(
                db.execute("SELECT payload FROM accounts").fetchone()[0], self.payload
            )
