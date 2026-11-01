"""A configured TLS proxy supplies the public origin; other clients cannot."""
import argparse
import tempfile
import unittest

from waitress.proxy_headers import proxy_headers_middleware

from authentactor.__main__ import proxy_address
from authentactor.server import create_app


class ProxyTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.app = create_app(directory.name)
        self.app.wsgi_app = proxy_headers_middleware(
            self.app.wsgi_app, trusted_proxy="127.0.0.1", trusted_proxy_count=1,
            trusted_proxy_headers={"x-forwarded-proto", "x-forwarded-host"}, clear_untrusted=True)
        self.client = self.app.test_client()
        self.headers = {"X-Requested-With": "Authentactor", "X-Forwarded-Proto": "https",
                        "X-Forwarded-Host": "vault.example.test", "Origin": "https://vault.example.test"}

    def test_trusted_tls_proxy_sets_secure_cookie_and_public_origin(self):
        response = self.client.post("/api/setup", json={"password": "Disposable proxy test password!"},
                                    headers=self.headers, environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
        self.assertEqual(response.status_code, 200)
        cookie = response.headers["Set-Cookie"]
        for flag in ("Secure", "HttpOnly", "SameSite=Strict"):
            self.assertIn(flag, cookie)

    def test_untrusted_forwarding_headers_do_not_change_origin(self):
        response = self.client.post("/api/setup", json={"password": "Disposable proxy test password!"},
                                    headers=self.headers, environ_overrides={"REMOTE_ADDR": "198.51.100.15"})
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(response.headers.get("Set-Cookie"))

    def test_trusted_proxy_cannot_bypass_cross_origin_protection(self):
        response = self.client.post("/api/setup", json={"password": "Disposable proxy test password!"},
                                    headers={**self.headers, "Origin": "https://elsewhere.example"},
                                    environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
        self.assertEqual(response.status_code, 403)

    def test_proxy_must_be_an_exact_address(self):
        self.assertEqual(proxy_address("127.0.0.1"), "127.0.0.1")
        self.assertEqual(proxy_address("::1"), "::1")
        for value in ("*", "proxy.example", "10.0.0.0/8", "127.0.0.1,198.51.100.15"):
            with self.assertRaises(argparse.ArgumentTypeError):
                proxy_address(value)
