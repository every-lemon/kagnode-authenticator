<p align="center"><img src="assets/kagnode-wordmark.svg" width="440" alt="KagNode."></p>

# KagNode Authenticator

## Overview

Independent email-based accounts with encrypted authenticator vaults and backup codes.

## Release status

Product source: **0.5.0**. Packaging preview: **0.5.0-packaging.1**.

Packaging prereleases do not change the latest stable release or establish new hardware or service compatibility. See [verification](docs/VERIFICATION.md) and [changelog](CHANGELOG.md).

## Features

- Separate encrypted vaults for multiple email accounts.
- TOTP entries, passwords and backup-code storage.
- Dedicated account and vault routes, export and recovery controls.

## Requirements

Python 3.12 for the validated development environment; HTTPS for remote use. See the existing reverse-proxy and vault setup instructions.

## Installation and downloads

Download from [GitHub Releases](https://github.com/every-lemon/kagnode-authenticator/releases). Verify `SHA256SUMS` before extracting or installing a package.

| Payload | Formats | Support |
| --- | --- | --- |
| Complete source / artwork | `.tar.xz`, `.tar.gz`, `.zip` | Named top-level directory; manual setup |
| Source preview | `.deb` | Source only; does not provision a service |
| Source preview | `.rpm` | Rocky Linux 10 packaging preview; native services unverified |

The existing `authentactor` Debian package builder remains in packaging/build-deb.sh.

Source packages install under `/usr/share/kagnode/`; they do not replace an existing application, migrate data, start services or configure networking.  See [package details](docs/PACKAGING.md).

## Usage

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m authentactor
```

See [operations and existing setup instructions](docs/OPERATIONS.md) for the full workflow and its prerequisites.

## Configuration and storage

The legacy authentactor package/service spelling is retained for compatibility. Never delete or reinitialize an existing vault to upgrade the UI.

## Security

Use HTTPS and least-privilege accounts for hosted services. Keep secrets and user data out of Git. Preview packages are for inspection and controlled testing; native service and hardware claims remain limited to recorded verification. See [security guidance](docs/SECURITY.md).

## Development and testing

```sh
python -m unittest discover -s tests -v
python3 scripts/repository_check.py
python3 scripts/format_source.py --check
python3 scripts/release.py --output dist/packages
```

Install the formatting dependencies from `requirements-format.txt`. Package building additionally needs `dpkg-deb`, `rpmbuild`, XZ support and, for CLI binaries, Go. Read [the repository map](docs/STRUCTURE.md) before editing generated files.

## Documentation

- [Repository structure](docs/STRUCTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Packages and release process](docs/PACKAGING.md)
- [Verification and limits](docs/VERIFICATION.md)
- [Changelog](CHANGELOG.md)

## Licensing

See [LICENSE](LICENSE) and retained third-party notices. KagNode artwork retains its separate permission and brand policy; the application uses AGPL-3.0-only.
