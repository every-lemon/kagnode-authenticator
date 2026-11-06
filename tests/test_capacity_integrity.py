import sqlite3
import tempfile
import time
import unittest
from authentactor.server import create_app


class CapacityIntegrityTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.app = create_app(directory.name)
        self.client = self.app.test_client()
        self.headers = {"X-Requested-With": "Authentactor"}
        response = self.client.post(
            "/api/setup",
            json={
                "email": "owner@integrity.test",
                "password": "Only isolated account testing!",
            },
            headers=self.headers,
        )
        self.csrf = response.json["csrf"]
        self.headers["X-CSRF-Token"] = self.csrf

    def test_full_session_capacity_does_not_save_a_new_account(self):
        extension = self.app.extensions["vault_testing"]
        sessions = extension["sessions"]
        state = next(iter(sessions.values()))
        for n in range(256 - len(sessions)):
            sessions["capacity-fixture-" + str(n)] = {
                **state,
                "active": time.time(),
                "created": time.time(),
            }
        with sqlite3.connect(extension["db_path"]) as conn:
            before = conn.execute(
                "SELECT id,email,salt,payload FROM accounts ORDER BY id"
            ).fetchall()
        response = self.app.test_client().post(
            "/api/setup",
            json={
                "email": "new@integrity.test",
                "password": "Only isolated new account!",
            },
            headers={"X-Requested-With": "Authentactor"},
        )
        self.assertEqual(response.status_code, 429)
        with sqlite3.connect(extension["db_path"]) as conn:
            self.assertEqual(
                conn.execute(
                    "SELECT id,email,salt,payload FROM accounts ORDER BY id"
                ).fetchall(),
                before,
            )

    def test_non_ascii_csrf_is_rejected_without_server_error(self):
        response = self.client.post(
            "/api/lock", json={}, headers={**self.headers, "X-CSRF-Token": "ß"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.client.get("/api/status").json["unlocked"])

    def test_malformed_backup_payload_types_do_not_mutate_the_vault(self):
        original = self.client.get("/api/backup").json
        for value in [None, 123, {}, []]:
            corrupted = {**original, "payload": value}
            response = self.client.post(
                "/api/restore",
                json={
                    "backup": corrupted,
                    "password": "Only isolated account testing!",
                },
                headers=self.headers,
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(self.client.get("/api/backup").json, original)
