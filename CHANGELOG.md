# 0.6.0-beta.1 — KagNode Passwords preview

## 0.6.0-beta.1 packaging.2

- Renamed the GitHub repository to kagnode-passwords and updated source/download links.
- Preserved legacy package identities, account client IDs and existing vault storage paths.

- Rename the interface while retaining existing encrypted data, identities and backup format.
- Add secure notes, folder labels and recoverable Trash with explicit permanent removal.
- Add a password-confirmed Bitwarden JSON export and Apps & extensions setup page.
- Integrate optional local-administrator update controls through KagNode CLI.
- Support an independently configured Vaultwarden engine; actual extension/mobile
  sign-in needs an HTTPS installation check. Existing vaults are not migrated automatically.

# 0.5.0

- Shared KagNode product styling, mobile controls, and persistent product branding.
- Prebuilt, fingerprinted UI assets with minified aliases and no source maps.
- Existing account data, credentials, and API behavior are retained.

# 0.4.1

- Refuse signup at the session limit before saving an account.
- Reject malformed CSRF and encrypted-backup fields without server errors.
- Existing account passwords, vault ciphertext, and backup format remain compatible.

# Changes

## 0.4.0 — source preview

- Added email signup/sign-in with separate encrypted vaults, settings and sessions.
- Added an explicit-owner migration that retains the database, original ciphertext and password.
- Scoped item actions, codes, backups, restore, password changes and automatic locking to each account.
- Added account switching, clearer sign-in text and multi-account/migration tests.

## 0.3.0 — source preview

- Added encrypted backup codes, standalone or attached to existing items, and a dedicated `/backup-codes` route.
- Added per-code reveal/copy, explicit Mark used and Mark available controls, usage dates and remaining counts.
- Preserved code-use history on edits, encrypted backups, password rotation and restarts; retained older vault/backup compatibility.
- Added validation, authorization, encryption, persistence and browser workflow checks.

## 0.2.0 — source preview

- Added KagNode branding, dark/light themes, responsive navigation and custom choice controls.
- Added individual routes, authenticated deep links, history navigation and local unlock return paths.
- Added vault-loading skeletons, error recovery, a centered logo loader and the top progress strip.
- Added explicit single-proxy HTTPS origin support and route/proxy/browser regression checks.
- Retained vault encryption, saved-data location, session protections and encrypted backup compatibility.

## 0.1.0 — original local preview

- Authentactor single-owner vault, TOTP codes, password storage, generator, encrypted backup/restore and master-password rotation.

## Account profile integration preview

Added optional KagNode Account display-name/photo linking, local administrator disable controls and private credential storage. Existing local account authentication and data remain independent.
