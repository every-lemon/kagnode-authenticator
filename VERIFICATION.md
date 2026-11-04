# Verification — 0.3.0 source preview

Validation uses disposable vaults. No owner's database or credentials are part of this repository.

## Backend

The 33 unittest cases include the original vault regressions and new route/proxy tests:

- 18 RFC 6238 reference vectors across SHA1/SHA256/SHA512.
- Encryption at rest and restart persistence, item CRUD, input limits and generator constraints.
- Locked access, origin/CSRF checks, idle/session expiry and unlock throttling.
- Encrypted backup/merge restore and master-password rotation.
- Password reuse checks, URL validation and rejection of private-address icon requests.
- Backup-code-only items, counts without secret disclosure, validation and duplicate rejection, explicit/idempotent usage and undo, edit preservation, older vault/backup compatibility, and backup code persistence through password rotation and restart.
- All eight section routes, known local unlock destinations, external redirect refusal, and demo/API separation.
- Secure cookies behind the configured TLS proxy; rejection of untrusted forwarding headers and cross-origin writes.

Run `python -m unittest discover -s tests -v`.

## Browser

`tests/browser_smoke.py` creates a temporary loopback server and empty vault, and checks:

- All eight section pages in dark and light themes at 320, 390, 820 and 1440 pixels (64 layouts), with no page-level horizontal overflow.
- Direct links, setup/unlock return paths, reload, browser Back/Forward and active navigation.
- Eight-digit authenticator creation, keyboard choice controls and the saved automatic-lock setting.
- Encrypted backup download, duplicate-safe restore, password rotation and subsequent unlock.
- Sensitive item fields cleared on lock; mobile navigation and Escape behavior.
- A viewport-sized loader, centered logo and top progress strip; data skeletons and successful retry after simulated failures.
- Backup code paste, individual reveal/copy, explicit use and undo, usage preserved after editing, standalone items and exhausted code sets.
- Backup-code details in both themes at 320, 390 and 1440 pixels, including long codes; 20 total browser workflows.
- A small-screen item form and dropdown, with no JavaScript exceptions.

Reports and screenshots are generated in ignored `test-artifacts/`. GitHub Actions runs the same checks. These checks are reproducible functional evidence, not an independent security audit.

## Remaining qualification

The 0.3.0 compatibility Debian package has not been built or installation-qualified. No binary stable release or production deployment is represented. Browser automation covers Chromium; physical Safari/iOS/Android and assistive-technology testing remain separate checks. There is no multi-user, cloud-sync or hosted-account functionality.

The original 0.1.0 preview's broader manual checks are historical; this file reports the current reproducible checks only.
