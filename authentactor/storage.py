"""Additive migration of the original encrypted vault; ciphertext is copied intact."""

import re
import sqlite3
import time
import uuid


def email_address(value):
    if not isinstance(value, str):
        raise ValueError("Enter a valid email address.")
    value = value.strip().lower()
    if len(value) > 254 or value.count("@") != 1:
        raise ValueError("Enter a valid email address.")
    local, domain = value.split("@")
    if (
        not 1 <= len(local) <= 64
        or local.startswith(".")
        or local.endswith(".")
        or ".." in local
    ):
        raise ValueError("Enter a valid email address.")
    if not re.fullmatch(r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+", local) or not re.fullmatch(
        r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+",
        domain,
    ):
        raise ValueError("Enter a valid email address.")
    return value


def initialize_database(path, legacy_email=None):
    owner = email_address(legacy_email) if legacy_email else None
    with sqlite3.connect(path, timeout=20) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE COLLATE NOCASE, salt BLOB NOT NULL, payload BLOB NOT NULL, secret_version INTEGER NOT NULL DEFAULT 1, created INTEGER NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS legacy_vault_owners (legacy_id INTEGER PRIMARY KEY CHECK(legacy_id=1), account_id TEXT NOT NULL UNIQUE REFERENCES accounts(id), migrated INTEGER NOT NULL)"
        )
        exists = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='vault'"
        ).fetchone()
        legacy = (
            db.execute("SELECT salt,payload FROM vault WHERE id=1").fetchone()
            if exists
            else None
        )
        mapping = db.execute(
            "SELECT account_id FROM legacy_vault_owners WHERE legacy_id=1"
        ).fetchone()
        if mapping:
            account = db.execute(
                "SELECT email,salt,payload FROM accounts WHERE id=?", mapping
            ).fetchone()
            if not account or (owner and owner != account[0]):
                raise ValueError(
                    "Existing vault ownership differs from --legacy-email. No ownership was changed."
                )
            if not legacy or tuple(account[1:]) != tuple(legacy):
                raise ValueError(
                    "Legacy and account vault contents differ. Review the preserved database and backups before continuing; neither copy was overwritten."
                )
        elif legacy:
            if not owner:
                raise ValueError(
                    "Existing single-owner vault found. Restart with --legacy-email OWNER_EMAIL to assign it without resetting its password or data."
                )
            if db.execute("SELECT 1 FROM accounts WHERE email=?", (owner,)).fetchone():
                raise ValueError(
                    "That email already has an account. Refusing to overwrite either vault."
                )
            identifier = str(uuid.uuid4())
            db.execute(
                "INSERT INTO accounts(id,email,salt,payload,created) VALUES(?,?,?,?,?)",
                (identifier, owner, *legacy, int(time.time())),
            )
            db.execute(
                "INSERT INTO legacy_vault_owners VALUES(1,?,?)",
                (identifier, int(time.time())),
            )
            assert (
                db.execute(
                    "SELECT salt,payload FROM accounts WHERE id=?", (identifier,)
                ).fetchone()
                == legacy
            )
            assert (
                db.execute("SELECT salt,payload FROM vault WHERE id=1").fetchone()
                == legacy
            )
