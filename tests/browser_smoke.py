"""Browser regression checks against an isolated, disposable vault only."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "test-artifacts"
VIEWS = (
    "overview",
    "authenticators",
    "passwords",
    "backup-codes",
    "favorites",
    "notes",
    "trash",
    "clients",
    "generator",
    "security",
    "settings",
)
EMAIL = "owner@browser.test"
PASSWORD = "Only-for-disposable-browser-tests!2048"


def check_quick_search(page, theme, width):
    page.keyboard.press("Control+k")
    field = page.locator("#global-search")
    field.wait_for(state="visible")
    assert field.evaluate("e=>document.activeElement===e")
    rows = page.locator("#global-results .quick-result")
    assert rows.count() > 1
    assert rows.first.evaluate("e=>getComputedStyle(e).display==='flex'")
    assert rows.first.evaluate(
        "e=>{let a=e.querySelector('strong').getBoundingClientRect(),b=e.querySelector('small').getBoundingClientRect();return b.top>=a.bottom}"
    )
    assert rows.first.evaluate("e=>e.clientWidth>e.parentElement.clientWidth-30")
    assert page.locator("#utility-dialog").evaluate("e=>e.scrollWidth<=e.clientWidth+1")
    first = field.get_attribute("aria-activedescendant")
    page.keyboard.press("ArrowDown")
    assert field.get_attribute("aria-activedescendant") != first
    field.fill("Google")
    assert rows.count() == 1
    page.keyboard.press("Enter")
    page.locator("#detail-dialog").wait_for(state="visible")
    page.locator("#detail-content .close-dialog").click()
    page.keyboard.press("Control+k")
    page.keyboard.press("Control+k")  # Reopening cannot clear the new dialog.
    field.wait_for(state="visible")
    field.fill("nothing-matches-this-test")
    page.locator(".no-search-results").wait_for(state="visible")
    assert field.get_attribute("aria-expanded") == "false"
    field.fill("")
    if width in (1440, 390):
        page.screenshot(path=str(ARTIFACTS / f"quick-search-{theme}-{width}.png"))
    page.keyboard.press("Escape")
    page.locator("#utility-dialog").wait_for(state="hidden")


def check(browser, base):
    errors, layouts = [], []
    for theme in ("dark", "light"):
        for width, height in ((1440, 1000), (820, 1100), (390, 844), (320, 740)):
            context = browser.new_context(
                viewport={"width": width, "height": height}, reduced_motion="reduce"
            )
            context.add_init_script(f"localStorage.setItem('kagnode-theme', '{theme}')")
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            for view in VIEWS:
                page.goto(f"{base}/{view}?demo=1")
                page.locator("#dashboard").wait_for(state="visible")
                page.wait_for_function('document.getElementById("loading").hidden')
                assert (
                    page.evaluate("document.documentElement.scrollWidth") <= width + 1
                ), (theme, width, view)
                assert (
                    page.locator(".nav-item.active").get_attribute("data-view") == view
                )
                assert page.locator("html").get_attribute("data-theme") == theme
                layouts.append(
                    {"theme": theme, "width": width, "view": view, "overflow": False}
                )
                if view == "overview":
                    check_quick_search(page, theme, width)
                if (width, view) in (
                    (1440, "overview"),
                    (390, "authenticators"),
                    (390, "settings"),
                ):
                    page.screenshot(
                        path=str(ARTIFACTS / f"{theme}-{width}-{view}.png"),
                        full_page=True,
                    )
            if width == 390:
                page.locator("#mobile-menu").click()
                assert (
                    page.locator("#mobile-menu").get_attribute("aria-expanded")
                    == "true"
                )
                page.keyboard.press("Escape")
                assert (
                    page.locator("#mobile-menu").get_attribute("aria-expanded")
                    == "false"
                )
                page.locator("#mobile-menu").click()
                page.locator('nav a[data-view="authenticators"]').click()
                assert "/authenticators?demo=1" in page.url
                assert (
                    page.locator("#mobile-menu").get_attribute("aria-expanded")
                    == "false"
                )
            context.close()

    context = browser.new_context(
        viewport={"width": 1440, "height": 1000}, reduced_motion="reduce"
    )
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + "/passwords")
    page.locator("#auth-screen").wait_for(state="visible")
    assert "/setup?next=%2Fpasswords" in page.url
    page.screenshot(path=str(ARTIFACTS / "dark-1440-setup.png"), full_page=True)
    page.locator("#auth-email").fill(EMAIL)
    page.locator("#master-password").fill(PASSWORD)
    page.locator("#confirm-password").fill(PASSWORD)
    page.locator(".auth-submit").click()
    page.wait_for_url("**/passwords")
    page.locator('nav a[data-view="authenticators"]').click()
    page.locator("#add-button").click()
    page.locator("#item-name").fill("KagNode QA account")
    page.locator("#item-username").fill("example@example.test")
    page.locator("#item-secret").fill("JBSWY3DPEHPK3PXP")
    page.locator("#item-backup-codes").fill("QA-RECOVERY-1234\nQA-RECOVERY-5678")
    page.locator("details.advanced summary").click()
    page.get_by_role("combobox", name="Digits", exact=True).click()
    page.get_by_role("option", name="8 digits", exact=True).click()
    page.locator("#save-item").click()
    page.locator("#item-dialog").wait_for(state="hidden")
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
    assert len(page.locator(".code-text").first.inner_text().replace(" ", "")) == 8
    page.reload()
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
    page.locator(".item-title").filter(has_text="KagNode QA account").click()
    assert "QA-RECOVERY-1234" not in page.locator("#detail-content").inner_text()
    page.get_by_role("button", name="Show backup code 1", exact=True).click()
    assert page.locator(".backup-code-value").first.inner_text() == "QA-RECOVERY-1234"
    page.evaluate(
        "Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async text=>window.__lastCopied=text,readText:async()=>window.__lastCopied}})"
    )
    page.get_by_role("button", name="Copy backup code 1", exact=True).click()
    page.wait_for_function('window.__lastCopied === "QA-RECOVERY-1234"')
    assert (
        page.locator(".backup-details-heading span").inner_text() == "2 of 2 available"
    )
    page.get_by_role("button", name="Mark used backup code 1", exact=True).click()
    page.locator(".backup-details-heading span").filter(
        has_text="1 of 2 available"
    ).wait_for()
    assert page.get_by_role(
        "button", name="Copy backup code 1", exact=True
    ).is_disabled()
    page.get_by_role("button", name="Mark available backup code 1", exact=True).click()
    page.locator(".backup-details-heading span").filter(
        has_text="2 of 2 available"
    ).wait_for()
    page.get_by_role("button", name="Mark used backup code 1", exact=True).click()
    page.locator(".backup-details-heading span").filter(
        has_text="1 of 2 available"
    ).wait_for()
    page.locator("#detail-edit").click()
    page.locator("#item-dialog").wait_for(state="visible")
    assert (
        page.locator("#item-backup-codes").input_value()
        == "QA-RECOVERY-1234\nQA-RECOVERY-5678"
    )
    page.locator("#item-notes").fill("An unrelated edit keeps code usage")
    page.locator("#save-item").click()
    page.locator("#item-dialog").wait_for(state="hidden")
    page.locator(".backup-summary").filter(
        has_text="1 of 2 backup codes available"
    ).wait_for()
    page.locator('nav a[data-view="settings"]').click()
    page.wait_for_url("**/settings")
    page.go_back()
    page.wait_for_url("**/authenticators")
    assert page.locator("#page-title").inner_text() == "Authenticators"
    page.go_forward()
    page.wait_for_url("**/settings")
    choice = page.get_by_role("combobox", name="Automatic lock timeout", exact=True)
    choice.focus()
    for key in ("ArrowDown", "Home", "Enter"):
        page.keyboard.press(key)
    page.get_by_text("Automatic lock updated", exact=True).wait_for()
    assert page.locator("#auto-lock").input_value() == "5"

    with page.expect_download() as downloaded:
        page.locator("#backup").click()
    backup = ARTIFACTS / "disposable-encrypted-backup.json"
    downloaded.value.save_as(backup)
    assert json.loads(backup.read_text())["format"] == "authentactor-encrypted-v1"
    assert "KagNode QA account" not in backup.read_text()
    page.locator("#restore-button").click()
    page.locator("#backup-file").set_input_files(str(backup))
    page.locator("#backup-password").fill(PASSWORD)
    page.get_by_role("button", name="Restore items", exact=True).click()
    page.get_by_text("0 items restored; 1 already present.", exact=True).wait_for()
    backup.unlink()  # Even synthetic encrypted vaults do not belong in artifacts.

    page.locator('nav a[data-view="backup-codes"]').click()
    page.wait_for_url("**/backup-codes")
    page.locator("#add-button").click()
    assert page.locator("#type-backup").get_attribute("aria-pressed") == "true"
    page.locator("#item-name").fill("Recovery-only example")
    page.locator("#item-backup-codes").fill(
        "LONG-" + "1234567890" * 8 + "\nSECOND-RECOVERY-4321"
    )
    page.locator("#save-item").click()
    page.locator("#item-dialog").wait_for(state="hidden")
    card = page.locator(".item-card").filter(has_text="Recovery-only example")
    card.wait_for()
    card.locator(".item-title").click()
    page.get_by_role("button", name="Show backup code 1", exact=True).click()
    for theme in ("dark", "light"):
        page.evaluate("theme=>document.documentElement.dataset.theme=theme", theme)
        for width in (1440, 390, 320):
            page.set_viewport_size(
                {"width": width, "height": 900 if width == 1440 else 844}
            )
            assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
            assert page.locator("#detail-dialog").evaluate(
                "d=>d.scrollWidth<=d.clientWidth+1"
            )
            page.screenshot(path=str(ARTIFACTS / f"backup-codes-{theme}-{width}.png"))
    page.set_viewport_size({"width": 1440, "height": 1000})
    for number in (1, 2):
        page.get_by_role(
            "button", name=f"Mark used backup code {number}", exact=True
        ).click()
        page.locator(".backup-details-heading span").filter(
            has_text=f"{2 - number} of 2 available"
        ).wait_for()
    page.locator("#detail-content .close-dialog").click()
    page.reload()
    page.locator(".item-card").filter(has_text="Recovery-only example").locator(
        ".backup-summary"
    ).filter(has_text="0 of 2").wait_for()
    page.locator('nav a[data-view="settings"]').click()

    # New Passwords features use the real disposable encrypted vault.
    page.locator('nav a[data-view="notes"]').click()
    page.locator("#add-button").click()
    assert page.locator("#type-note").get_attribute("aria-pressed") == "true"
    page.locator("#item-name").fill("Private test note")
    page.locator("#item-folder").fill("Personal")
    page.locator("#item-notes").fill("Synthetic secure note for browser validation.")
    page.locator("#save-item").click()
    page.locator("#item-dialog").wait_for(state="hidden")
    page.locator(".item-title").filter(has_text="Private test note").click()
    page.locator("#detail-delete").click()
    page.get_by_role("button", name="Move to Trash", exact=True).click()
    page.locator("#utility-dialog").wait_for(state="hidden")
    page.locator('nav a[data-view="trash"]').click()
    page.get_by_role("button", name="Restore", exact=True).click()
    page.get_by_text("Trash is empty.", exact=True).wait_for()
    page.locator('nav a[data-view="notes"]').click()
    page.locator(".item-title").filter(has_text="Private test note").wait_for()
    page.locator('nav a[data-view="clients"]').click()
    page.locator("#export-bitwarden").click()
    page.locator("#export-password").fill(PASSWORD)
    with page.expect_download() as exported:
        page.get_by_role("button", name="Export unencrypted JSON", exact=True).click()
    plain = ARTIFACTS / "temporary-synthetic-export.json"
    exported.value.save_as(plain)
    value = json.loads(plain.read_text())
    plain.unlink()
    note = next(item for item in value["items"] if item["name"] == "Private test note")
    assert note["type"] == 2
    assert note["folderId"] in {folder["id"] for folder in value["folders"]}
    page.locator("#utility-dialog").wait_for(state="hidden")
    for width in (1440, 390, 320):
        page.set_viewport_size({"width": width, "height": 900})
        assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
        page.screenshot(
            path=str(ARTIFACTS / f"passwords-clients-{width}.png"), full_page=True
        )
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.locator('nav a[data-view="settings"]').click()

    # Exercise the shared update controls without running a privileged updater.
    update_calls = []
    update_state = {
        "enabled": True,
        "installed": "fixture-old",
        "channel": "preview",
        "kind": "python",
        "can_apply": True,
    }

    def manager_response(route):
        if route.request.method != "POST":
            return route.continue_()
        data = route.request.post_data_json
        action = data.get("action", "")
        if not action.startswith("updates."):
            return route.continue_()
        assert route.request.headers.get("x-csrf-token")
        update_calls.append(action)
        if action == "updates.check":
            update_state["candidate"] = {
                "changed": True,
                "release_id": 42,
                "version": "fixture-new",
                "prerelease": True,
            }
        if action == "updates.apply":
            assert data["release_id"] == 42
            update_state["installed"] = "fixture-new"
            update_state["candidate"]["changed"] = False
            update_state["operation"] = {
                "phase": "complete",
                "message": "Fixture update complete",
            }
        route.fulfill(
            status=200, content_type="application/json", body=json.dumps(update_state)
        )

    page.route("**/api/kagnode-account", manager_response)
    page.evaluate("window.KagNodeAccounts.refresh()")
    panel = page.locator(".kn-update-panel")
    panel.get_by_role("button", name="Check for updates", exact=True).click()
    panel.get_by_role("button", name="Review update", exact=True).click()
    page.locator(".kn-update-dialog").get_by_role(
        "button", name="Cancel", exact=True
    ).click()
    assert "updates.apply" not in update_calls
    panel.get_by_role("button", name="Review update", exact=True).click()
    page.set_viewport_size({"width": 320, "height": 740})
    assert page.locator(".kn-update-dialog").evaluate(
        "e=>e.scrollWidth<=e.clientWidth+1"
    )
    page.locator(".kn-update-dialog").get_by_role(
        "button", name="Install update", exact=True
    ).click()
    panel.get_by_text(
        "This source release is already installed.", exact=True
    ).wait_for()
    assert update_calls.count("updates.apply") == 1
    page.unroute("**/api/kagnode-account", manager_response)
    page.set_viewport_size({"width": 1440, "height": 1000})

    page.locator("#change-master").click()
    page.locator("#current-master").fill(PASSWORD)
    changed = PASSWORD + "-changed"
    page.locator("#new-master").fill(changed)
    page.locator("#new-master-confirm").fill(changed)
    page.get_by_role("button", name="Update password", exact=True).click()
    page.get_by_text(
        "Master password updated. Other sessions are now locked.", exact=True
    ).wait_for()
    page.locator("#lock-button").click()
    page.wait_for_url("**/unlock?next=%2Fsettings")
    assert page.locator("#items .item-card").count() == 0
    assert page.locator("#item-backup-codes").input_value() == ""
    assert page.locator("#detail-content").inner_text() == ""
    page.locator("#auth-email").fill(EMAIL)
    page.locator("#master-password").fill(changed)
    page.locator(".auth-submit").click()
    page.wait_for_url("**/settings")
    page.reload()
    page.locator("#settings-view").wait_for(state="visible")
    assert page.locator("#auto-lock").input_value() == "5"

    # Delay only delivery to the page; the real backend response is retained.
    page.add_init_script("""
      const heldPath = new URLSearchParams(location.search).get('test-hold');
      const originalFetch = window.fetch.bind(window);
      window.__heldResponses = [];
      window.fetch = (...args) => {
        const response = originalFetch(...args);
        if (heldPath && new URL(args[0], location.href).pathname === '/api/' + heldPath) {
          return new Promise((resolve, reject) => response.then(value => {
            window.__heldResponses.push(() => resolve(value));
          }, reject));
        }
        return response;
      };
    """)
    page.goto(base + "/authenticators?test-hold=status")
    page.wait_for_function("window.__heldResponses.length === 1")
    rect = page.locator("#loading").bounding_box()
    assert rect == {"x": 0, "y": 0, "width": 1440, "height": 1000}, rect
    logo = page.locator(".loading-logo").bounding_box()
    assert abs(logo["x"] + logo["width"] / 2 - 720) < 1
    assert page.locator(".loading-strip").bounding_box()["y"] == 0
    page.screenshot(path=str(ARTIFACTS / "centered-loader.png"))
    page.evaluate("window.__heldResponses.splice(0).forEach(release => release())")
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()

    page.goto(base + "/authenticators?test-hold=items")
    page.wait_for_function("window.__heldResponses.length === 1")
    page.locator(".skeleton-card").first.wait_for()
    assert page.locator("#items").get_attribute("aria-busy") == "true"
    page.screenshot(path=str(ARTIFACTS / "vault-skeleton.png"))
    page.evaluate("window.__heldResponses.splice(0).forEach(release => release())")
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()

    page.route(
        "**/api/items",
        lambda route: route.fulfill(
            status=503,
            content_type="application/json",
            body='{"error":"Simulated unavailable response"}',
        ),
    )
    page.reload()
    page.locator("#vault-load-error").wait_for(state="visible")
    assert page.locator(".skeleton-card").count() == 0
    page.unroute("**/api/items")
    page.locator("#retry-items").click()
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()

    page.set_viewport_size({"width": 320, "height": 740})
    page.locator("#add-button").click()
    page.locator("details.advanced summary").click()
    page.get_by_role("combobox", name="Algorithm", exact=True).click()
    page.screenshot(path=str(ARTIFACTS / "dark-320-add-item.png"))
    assert page.evaluate("document.documentElement.scrollWidth") <= 321
    page.keyboard.press("Escape")
    assert page.locator("#item-dialog").is_visible()
    page.locator("#item-dialog .close-dialog").first.click()

    page.route(
        "**/api/status",
        lambda route: route.fulfill(
            status=503,
            content_type="application/json",
            body='{"error":"Simulated unavailable response"}',
        ),
    )
    page.reload()
    page.locator("#loading-retry").wait_for(state="visible")
    assert page.locator(".loading-logo").is_visible()
    assert not page.locator(".loading-strip").is_visible()
    page.unroute("**/api/status")
    page.locator("#loading-retry").click()
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
    # A second email gets a separate vault; changing its settings/password
    # must not alter or sign out the first account.
    second = browser.new_context(viewport={"width": 390, "height": 844})
    other = second.new_page()
    other.on("pageerror", lambda error: errors.append(str(error)))
    other.goto(base + "/unlock")
    other.locator("#auth-screen").wait_for(state="visible")
    other.locator("#auth-switch").click()
    other.locator("#auth-email").fill("second@browser.test")
    other_password = "Only another disposable account password!72"
    other.locator("#master-password").fill(other_password)
    other.locator("#confirm-password").fill(other_password)
    other.locator(".auth-submit").click()
    other.locator("#dashboard").wait_for(state="visible")
    assert other.locator(".item-card").count() == 0
    other.locator("#add-button").click()
    other.locator("#item-name").fill("Second account only")
    other.locator("#item-password").fill("Second account item secret!2048")
    other.locator("#save-item").click()
    other.locator("#item-dialog").wait_for(state="hidden")
    other.locator(".item-title").filter(has_text="Second account only").wait_for()
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(base + "/overview")
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
    assert (
        page.locator(".item-title").filter(has_text="Second account only").count() == 0
    )
    identifier = page.locator(".item-card").first.get_attribute("data-id")
    assert other.request.get(base + "/api/items/" + identifier).status == 404
    other.locator("#mobile-menu").click()
    other.locator('nav a[data-view="settings"]').click()
    assert other.locator("#account-email").inner_text() == "second@browser.test"
    other.get_by_role("combobox", name="Automatic lock timeout", exact=True).click()
    other.get_by_role("option", name="30 minutes", exact=True).click()
    other.get_by_text("Automatic lock updated", exact=True).wait_for()
    assert page.request.get(base + "/api/status").json()["settings"]["auto_lock"] == 5
    other.locator("#change-master").click()
    other.locator("#current-master").fill(other_password)
    other.locator("#new-master").fill(other_password + "-changed")
    other.locator("#new-master-confirm").fill(other_password + "-changed")
    other.get_by_role("button", name="Update password", exact=True).click()
    other.get_by_text(
        "Master password updated. Other sessions are now locked.", exact=True
    ).wait_for()
    assert page.request.get(base + "/api/items").status == 200
    page.locator("#lock-button").click()
    page.locator("#auth-screen").wait_for(state="visible")
    assert page.locator("#items .item-card").count() == 0
    for theme in ("dark", "light"):
        page.evaluate("theme=>document.documentElement.dataset.theme=theme", theme)
        for width in (1440, 390, 320):
            page.set_viewport_size({"width": width, "height": 900})
            assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
            page.screenshot(
                path=str(ARTIFACTS / f"account-signin-{theme}-{width}.png"),
                full_page=True,
            )
    page.locator("#auth-email").fill("second@browser.test")
    page.locator("#master-password").fill(other_password + "-changed")
    page.locator(".auth-submit").click()
    page.locator(".item-title").filter(has_text="Second account only").wait_for()
    assert (
        page.locator(".item-title").filter(has_text="KagNode QA account").count() == 0
    )
    second.close()
    context.close()
    assert not errors, errors
    result = {
        "layouts": layouts,
        "page_errors": errors,
        "workflows": [
            "create a secure note with a folder",
            "soft-delete and restore a note through Trash",
            "password-confirmed Bitwarden JSON download",
            "responsive compatible-client settings",
            "direct routes and reload",
            "setup and unlock return paths",
            "Back/Forward",
            "8-digit TOTP entry",
            "keyboard choice controls",
            "backup/merge restore",
            "master password rotation",
            "lock clears DOM",
            "saved lock preference",
            "mobile menu and Escape",
            "centered loader and top strip",
            "vault skeleton",
            "failed item load/retry",
            "failed initial load/retry",
            "small-screen form",
            "backup code paste/reveal/copy",
            "explicit use and undo",
            "usage preserved by edits",
            "backup-code-only items",
            "backup code mobile layouts and depleted groups",
            "second email signup",
            "cross-account item isolation",
            "independent account settings",
            "account password rotation isolation",
            "sign out and account switching",
            "email sign-in responsive layouts",
        ],
    }
    (ARTIFACTS / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"PASS: {len(layouts)} layouts and {len(result['workflows'])} workflows; no browser exceptions"
    )


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="kagnode-authenticator-test-") as data:
        env = {k: v for k, v in os.environ.items() if not k.startswith("AUTHENTACTOR_")}
        with (ARTIFACTS / "server.log").open("w") as log:
            server = subprocess.Popen(
                [
                    os.environ.get("AUTH_APP_PYTHON", sys.executable),
                    "-m",
                    "authentactor",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--data-dir",
                    data,
                    "--preview",
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(400):
                    if server.poll() is not None:
                        raise RuntimeError(
                            "Disposable server exited; inspect test-artifacts/server.log"
                        )
                    try:
                        with urlopen(base + "/api/status", timeout=1) as response:
                            assert not json.load(response)["initialized"]
                        break
                    except OSError:
                        time.sleep(0.05)
                else:
                    raise RuntimeError("Disposable server did not start")
                with sync_playwright() as playwright:
                    engine = getattr(
                        playwright, os.environ.get("KAGNODE_BROWSER_ENGINE", "chromium")
                    )
                    browser = engine.launch(
                        headless=True,
                        executable_path=os.environ.get("KAGNODE_BROWSER_EXECUTABLE")
                        or None,
                        args=["--no-sandbox", "--disable-dev-shm-usage"]
                        if os.environ.get("KAGNODE_BROWSER_ENGINE", "chromium")
                        == "chromium"
                        else [],
                    )
                    try:
                        check(browser, base)
                    finally:
                        browser.close()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == "__main__":
    main()
