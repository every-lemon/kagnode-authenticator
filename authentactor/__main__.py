"""Source entry point; legacy environment and data paths remain compatible."""
import argparse
import ipaddress
import os

from waitress import serve

from .server import create_app

def proxy_address(value):
    try:
        return str(ipaddress.ip_address(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use the exact IP address of your reverse proxy.") from exc


def main():
    parser = argparse.ArgumentParser(description="KagNode Authenticator — email-based encrypted vaults")
    parser.add_argument("--host", default=os.environ.get("AUTHENTACTOR_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("AUTHENTACTOR_PORT", "80")))
    parser.add_argument("--data-dir", default=os.environ.get("AUTHENTACTOR_DATA", "/var/lib/authentactor"))
    parser.add_argument("--preview", action="store_true", help="Display the test-credentials notice")
    parser.add_argument("--trusted-proxy", type=proxy_address, default=os.environ.get("AUTHENTACTOR_TRUSTED_PROXY") or None,
                        help="Trust HTTPS/host headers only from this exact proxy IP; disabled by default")
    parser.add_argument("--legacy-email", default=os.environ.get("AUTHENTACTOR_LEGACY_EMAIL") or None, help="Assign an existing single-owner vault to this email without changing its encrypted contents")
    args = parser.parse_args()
    app = create_app(args.data_dir, preview=args.preview, legacy_email=args.legacy_email)
    proxy = {}
    if args.trusted_proxy:
        proxy = {"trusted_proxy": args.trusted_proxy, "trusted_proxy_count": 1,
                 "trusted_proxy_headers": {"x-forwarded-proto", "x-forwarded-host"}}
    print(f"KagNode Authenticator listening on http://{args.host}:{args.port}", flush=True)
    serve(app, host=args.host, port=args.port, threads=6, max_request_body_size=16_000_000,
          clear_untrusted_proxy_headers=True, expose_tracebacks=False, **proxy)


if __name__ == "__main__":
    main()
