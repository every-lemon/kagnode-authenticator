# KagNode Passwords

The former Authenticator application now includes passwords, TOTP, backup codes,
secure notes, folder labels, favorites, a generator, security checks and Trash.
It retains the `authentactor` Python package, cookie, system-service identities,
GitHub repository and `authentactor-encrypted-v1` backup format for compatibility.
No database reset or automatic account reassignment is part of this change.

## Two supported vault services

The existing web vault stores each account's encrypted payload on your server.
It decrypts that payload in server memory while the vault is unlocked. It is not
an end-to-end encrypted Bitwarden server. Keep it on a trusted private server.

The optional compatible engine is upstream [Vaultwarden](https://github.com/dani-garcia/vaultwarden).
Bitwarden apps and extensions use that engine's API and encryption protocol.
KagNode does not replace the protocol or claim affiliation with Bitwarden.
Upstream source and licenses remain available. The compatible engine uses its
upstream web vault; KagNode's local web vault retains the KagNode interface.

## Set up compatible clients

Run `sudo kagnode setup`, choose Passwords, then **Bitwarden apps & extensions**.
Docker with its Compose plugin must already be installed. Choose a separate HTTPS
origin for the compatible engine. The CLI can resolve the latest stable official
image and pin its immutable digest, or accept an explicitly chosen official digest.
The default root is `/srv/kagnode`; engine configuration and data live under
`passwords/bitwarden/`. The container only binds to loopback. Configure your HTTPS
reverse proxy, including WebSockets, before connecting a client.

New-account registration and organization invitations are disabled. The generated
administrator token is stored privately in `passwords/bitwarden/admin.env`; it is
not printed or sent to browsers. Use it privately at the compatible engine's
`/admin` page to invite your accounts. Follow upstream's hardening guidance and
replace the token with its supported Argon2 hash if desired. Do not expose the
administration page beyond your trusted network.

Set `KAGNODE_PASSWORDS_BITWARDEN_URL=https://your-compatible-vault.example` in the
existing Passwords service environment. Its **Apps & extensions** page then shows
the URL. In a Bitwarden client, select **Self-hosted**, enter that URL, and sign in
with an account created on the compatible engine. KagNode Account profile linking
does not grant access to either vault or replace either master password.

## Transfer existing items without resetting anything

1. Keep an encrypted KagNode backup first.
2. In **Apps & extensions**, choose **Export for Bitwarden** and re-enter your
   current master password. This explicit export is **not encrypted**.
3. Import the JSON as Bitwarden JSON in the compatible web vault.
4. Verify passwords, TOTP settings, notes and folders. Backup codes transfer as
   notes with their Used/Available status. Trash and custom icons are excluded.
5. Remove the plaintext export from your device and its Trash after verification.

The original vault remains intact. There is no automatic continuous synchronization,
shared session, automatic migration, browser-extension implementation or silent
re-encryption. Existing encrypted backups remain the recovery path for the local
vault. Back up the compatible engine separately using upstream's documented
SQLite and attachment backup procedure; do not treat a live filesystem copy as a
consistent database backup.

## Verification status

Local-vault isolation, legacy backup compatibility, Trash, explicit export and
administrator checks have automated tests. Compatible-engine setup is tested with
mocked process boundaries. Actual browser-extension/mobile login must be verified
against your configured HTTPS engine before claiming end-to-end compatibility on
your installation. Installing an engine does not migrate your live vault.
