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
