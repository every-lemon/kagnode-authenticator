# Security

KagNode Authenticator 0.4.0 is a functional source preview. It has not had an independent security audit and should not yet be your sole store for irreplaceable credentials.

## Deployment boundary

This is a private server with independent email-based vaults. Registration is available to anyone permitted by your network/proxy access rules. Emails identify accounts but are not verified; there is no email-based password reset. Keep the proxy restricted to trusted users. Use HTTPS for remote access and protect the underlying host, backups, swap and process dumps. Server-side encryption protects the stored ciphertext, not an unlocked process on a compromised host. Keeping a password and its TOTP seed together also makes the vault a shared access point for both factors.

Proxy trust is off by default. Configure only the immediate proxy's exact IP and make that proxy overwrite forwarded host/scheme headers. Restrict direct access to the backend. The app does not trust arbitrary forwarding headers, create certificates or change your firewall.

There is no master-password recovery. A lost master password cannot be reset to decrypt the existing vault. Keep tested encrypted backups and the password that encrypted each backup. Changing the current password does not change earlier backup files.

Only the theme preference is stored in browser localStorage. Unlocked credentials are held in page memory for the relevant UI actions. Locking clears the app's sensitive fields and dialogs, but cannot erase copies already placed on a clipboard, screenshots or an untrusted browser extension.

## Reporting

Use the repository's **Security → Report a vulnerability** feature when it is enabled. Do not post passwords, authenticator seeds, vault databases, tokens or private infrastructure details in a public issue. If private reporting is unavailable, request a private contact without including exploit details or secrets.

Ordinary UI and reproducible non-sensitive bugs can be reported in Issues. Include the app version, browser, route, steps and expected result, using a disposable demo vault.

Backup codes are vault secrets, protected with the same encryption and session boundary as passwords. Lists expose only counts; detail reads expose codes to the unlocked owner. Marking a code used changes local vault state only and is not confirmation from the account service. No code, password or TOTP seed is added to browser storage.

Each session is bound to one immutable account ID and password version. Every
vault read/write, backup, restore and backup-code action uses that account ID;
request-body or query-string email values cannot select a different vault.
Password rotation and lock-setting changes affect only the current account.
Email/password failures use the same sign-in error for unknown emails and wrong
passwords; signup/sign-in requests are rate limited.

Legacy migration requires an explicit owner email and preserves the original
ciphertext. The old table is retained for compatibility, not as a second public
API. Back up the whole database and preserve the upgraded application. Use one
Waitress process because active encryption keys and sessions are process-local.
