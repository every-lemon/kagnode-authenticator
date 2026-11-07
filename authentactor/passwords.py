"""Portable vault fields and explicit, user-requested Bitwarden JSON export.

The existing encrypted store is not the Bitwarden protocol. Compatible clients
connect to the separately installed Vaultwarden engine, never this Flask API.
"""

from urllib.parse import urlencode
from uuid import NAMESPACE_URL, uuid5


def bitwarden_export(items):
    active = [item for item in items if not item.get("deleted_at")]
    folders = sorted({item.get("folder", "") for item in active} - {""})
    folder_ids = {
        name: str(uuid5(NAMESPACE_URL, "kagnode-folder:" + name)) for name in folders
    }
    result = []
    for item in active:
        notes = item.get("notes", "")
        codes = item.get("backup_codes", [])
        if codes:
            notes += "\n\nBackup codes (retain Used status):\n" + "\n".join(
                ("[Used] " if code.get("used") else "[Available] ") + code["code"]
                for code in codes
            )
        login = bool(item.get("password") or item.get("secret"))
        entry = {
            "id": item["id"],
            "organizationId": None,
            "folderId": folder_ids.get(item.get("folder")),
            "type": 1 if login else 2,
            "name": item["name"],
            "notes": notes or None,
            "favorite": bool(item.get("favorite")),
            "reprompt": 0,
        }
        if login:
            otp = None
            if item.get("secret"):
                otp = (
                    "otpauth://totp/"
                    + "KagNode?"
                    + urlencode(
                        {
                            "secret": item["secret"],
                            "algorithm": item.get("algorithm", "SHA1"),
                            "digits": item.get("digits", 6),
                            "period": item.get("period", 30),
                        }
                    )
                )
            entry["login"] = {
                "username": item.get("username", ""),
                "password": item.get("password", ""),
                "totp": otp,
                "uris": [{"uri": item["url"], "match": None}]
                if item.get("url")
                else [],
            }
        else:
            entry["secureNote"] = {"type": 0}
            metadata = [
                f"{label}: {item[key]}"
                for key, label in (("username", "Account"), ("url", "Website"))
                if item.get(key)
            ]
            if metadata:
                entry["notes"] = "\n".join(metadata) + "\n\n" + (entry["notes"] or "")
        result.append(entry)
    return {
        "encrypted": False,
        "folders": [{"id": folder_ids[name], "name": name} for name in folders],
        "items": result,
    }
