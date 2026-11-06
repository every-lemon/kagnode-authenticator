#!/bin/sh
# Prepared for the next step. The preview task does not execute this script.
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
version=0.5.0
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT HUP INT TERM
root="$stage/authentactor"
mkdir -p "$root/DEBIAN" "$root/usr/share/authentactor" "$root/lib/systemd/system" "$root/etc/default" "$root/usr/bin" "$root/usr/share/doc/authentactor"
cp -R "$source_dir/authentactor" "$root/usr/share/authentactor/"
find "$root/usr/share/authentactor" -type d -name __pycache__ -exec rm -rf {} +
# The system's Flask and cryptography packages remain distro-managed. Bundle
# Waitress 3.0.2 because Ubuntu 24.04 ships an older server. Verify the wheel hash.
python3 -m pip download --no-deps --only-binary=:all: --require-hashes -r "$source_dir/packaging/server-requirements.txt" --dest "$stage/wheels"
python3 - "$stage/wheels/waitress-3.0.2-py3-none-any.whl" "$root/usr/share/authentactor" "$root/usr/share/doc/authentactor" <<'VENDOR'
import pathlib
import sys
import zipfile
destination = pathlib.Path(sys.argv[2])
licenses = pathlib.Path(sys.argv[3])
with zipfile.ZipFile(sys.argv[1]) as archive:
    for name in archive.namelist():
        if name.startswith('waitress/') and not name.endswith('/'):
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
        if name.endswith('/LICENSE.txt'):
            licenses.mkdir(parents=True, exist_ok=True)
            (licenses / 'waitress-LICENSE.txt').write_bytes(archive.read(name))
VENDOR
cp "$source_dir/packaging/authentactor.service" "$root/lib/systemd/system/"
cp "$source_dir/packaging/defaults" "$root/etc/default/authentactor"
cp "$source_dir/README.md" "$source_dir/LICENSE" "$source_dir/ARTWORK-LICENSE" "$source_dir/NOTICE" "$root/usr/share/doc/authentactor/"
cat > "$root/usr/bin/authentactor" <<'LAUNCHER'
#!/bin/sh
cd /usr/share/authentactor
exec /usr/bin/python3 -m authentactor "$@"
LAUNCHER
chmod 755 "$root/usr/bin/authentactor"
cat > "$root/DEBIAN/control" <<CONTROL
Package: authentactor
Version: $version
Section: web
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-flask (>= 3.0), python3-cryptography (>= 41), adduser
Maintainer: KagNode contributors <every-lemon@users.noreply.github.com>
Description: KagNode Authenticator personal encrypted vault
 Self-hosted email-based encrypted vaults for TOTP, passwords and backup codes.
 Stores the vault encrypted on disk and listens on port 80 by default.
CONTROL
printf '%s\n' '/etc/default/authentactor' > "$root/DEBIAN/conffiles"
cat > "$root/DEBIAN/postinst" <<'POSTINST'
#!/bin/sh
set -e
if [ "$1" = configure ]; then
    if ! getent passwd authentactor >/dev/null; then
        adduser --system --group --home /var/lib/authentactor --no-create-home --disabled-login authentactor
    fi
    install -d -m 0700 -o authentactor -g authentactor /var/lib/authentactor
    if [ -d /run/systemd/system ]; then
        systemctl daemon-reload
        systemctl enable authentactor.service
        if ! systemctl restart authentactor.service; then
            echo 'KagNode Authenticator could not start. Check whether port 80 is occupied and review /etc/default/authentactor.' >&2
        fi
    fi
fi
POSTINST
cat > "$root/DEBIAN/prerm" <<'PRERM'
#!/bin/sh
set -e
case "$1" in
    remove|deconfigure) if [ -d /run/systemd/system ]; then systemctl disable --now authentactor.service || true; fi ;;
    upgrade) if [ -d /run/systemd/system ]; then systemctl stop authentactor.service || true; fi ;;
esac
PRERM
cat > "$root/DEBIAN/postrm" <<'POSTRM'
#!/bin/sh
set -e
if [ -d /run/systemd/system ]; then systemctl daemon-reload; fi
# Never delete vault data, including on purge. The owner removes it explicitly.
POSTRM
chmod 755 "$root/DEBIAN/postinst" "$root/DEBIAN/prerm" "$root/DEBIAN/postrm"
find "$root" -type d -exec chmod 755 {} +
find "$root/usr/share" "$root/lib" "$root/etc" -type f -exec chmod 644 {} +
dpkg-deb --root-owner-group --build "$root" "$source_dir/authentactor_${version}_all.deb"
