"""Real section routes retain the vault's existing authorization boundary."""

import tempfile
import unittest
from authentactor.server import create_app, PAGE_PATHS


class PageRouteTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = create_app(self.directory.name)
        self.client = self.app.test_client()
        self.headers = {"X-Requested-With": "Authentactor"}

    def setup_vault(self):
        response = self.client.post(
            "/api/setup",
            json={
                "email": "owner@routes.test",
                "password": "Private-test-password-938!",
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.headers["X-CSRF-Token"] = response.json["csrf"]

    def test_empty_vault_deep_links_go_to_setup(self):
        for path in PAGE_PATHS:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.location, "/setup?next=" + path.replace("/", "%2F")
            )
        self.assertEqual(self.client.get("/").location, "/setup")

    def test_each_section_is_reloadable_after_unlock(self):
        self.setup_vault()
        for path in PAGE_PATHS:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn(b"KagNode.", response.data)
            self.assertNotIn(b"Private-test-password-938!", response.data)
            response.close()
        self.assertEqual(self.client.get("/").location, "/overview")
        self.assertEqual(
            self.client.get("/unlock?next=/passwords").location, "/passwords"
        )

    def test_locked_pages_preserve_only_a_local_destination(self):
        self.setup_vault()
        self.client.post("/api/lock", json={}, headers=self.headers)
        self.assertEqual(
            self.client.get("/settings").location, "/unlock?next=%2Fsettings"
        )
        response = self.client.get("/setup?next=https://attacker.example")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response.headers)
        response.close()
        self.assertEqual(self.client.get("/api/items").status_code, 401)

    def test_demo_does_not_authorize_real_vault_apis(self):
        self.setup_vault()
        self.client.post("/api/lock", json={}, headers=self.headers)
        for path in PAGE_PATHS:
            response = self.client.get(path + "?demo=1")
            self.assertEqual(response.status_code, 200)
            response.close()
        for path in ("/api/items", "/api/codes", "/api/backup"):
            self.assertEqual(self.client.get(path + "?demo=1").status_code, 401)

    def test_auth_redirects_reject_external_and_unknown_destinations(self):
        self.setup_vault()
        for target in (
            "https://attacker.example",
            "//attacker.example",
            "/api/backup",
            "/unknown",
            "/settings?redirect=https://attacker.example",
        ):
            self.assertEqual(
                self.client.get("/unlock", query_string={"next": target}).location,
                "/overview",
            )

    def test_unknown_path_is_not_a_vault_page(self):
        self.assertEqual(self.client.get("/missing-page").status_code, 404)
        self.assertEqual(self.client.get("/demo").location, "/overview?demo=1")


if __name__ == "__main__":
    unittest.main()
