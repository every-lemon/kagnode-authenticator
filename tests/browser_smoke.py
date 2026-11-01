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
VIEWS = ("overview", "authenticators", "passwords", "favorites", "generator", "security", "settings")
PASSWORD = "Only-for-disposable-browser-tests!2048"


def check(browser, base):
    errors, layouts = [], []
    for theme in ("dark", "light"):
        for width, height in ((1440, 1000), (820, 1100), (390, 844), (320, 740)):
            context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
            context.add_init_script(f"localStorage.setItem('kagnode-theme', '{theme}')")
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            for view in VIEWS:
                page.goto(f"{base}/{view}?demo=1")
                page.locator("#dashboard").wait_for(state="visible")
                page.wait_for_function('document.getElementById("loading").hidden')
                assert page.evaluate("document.documentElement.scrollWidth") <= width + 1, (theme, width, view)
                assert page.locator(".nav-item.active").get_attribute("data-view") == view
                assert page.locator("html").get_attribute("data-theme") == theme
                layouts.append({"theme": theme, "width": width, "view": view, "overflow": False})
                if (width, view) in ((1440, "overview"), (390, "authenticators"), (390, "settings")):
                    page.screenshot(path=str(ARTIFACTS / f"{theme}-{width}-{view}.png"), full_page=True)
            if width == 390:
                page.locator("#mobile-menu").click()
                assert page.locator("#mobile-menu").get_attribute("aria-expanded") == "true"
                page.keyboard.press("Escape")
                assert page.locator("#mobile-menu").get_attribute("aria-expanded") == "false"
                page.locator("#mobile-menu").click()
                page.locator('nav a[data-view="authenticators"]').click()
                assert "/authenticators?demo=1" in page.url
                assert page.locator("#mobile-menu").get_attribute("aria-expanded") == "false"
            context.close()

    context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + "/passwords")
    page.locator("#auth-screen").wait_for(state="visible")
    assert "/setup?next=%2Fpasswords" in page.url
    page.screenshot(path=str(ARTIFACTS / "dark-1440-setup.png"), full_page=True)
    page.locator("#master-password").fill(PASSWORD)
    page.locator("#confirm-password").fill(PASSWORD)
    page.locator(".auth-submit").click()
    page.wait_for_url("**/passwords")
    page.locator('nav a[data-view="authenticators"]').click()
    page.locator("#add-button").click()
    page.locator("#item-name").fill("KagNode QA account")
    page.locator("#item-username").fill("example@example.test")
    page.locator("#item-secret").fill("JBSWY3DPEHPK3PXP")
    page.locator("details.advanced summary").click()
    page.get_by_role("combobox", name="Digits", exact=True).click()
    page.get_by_role("option", name="8 digits", exact=True).click()
    page.locator("#save-item").click()
    page.locator("#item-dialog").wait_for(state="hidden")
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
    assert len(page.locator(".code-text").first.inner_text().replace(" ", "")) == 8
    page.reload()
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
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

    page.locator("#change-master").click()
    page.locator("#current-master").fill(PASSWORD)
    changed = PASSWORD + "-changed"
    page.locator("#new-master").fill(changed)
    page.locator("#new-master-confirm").fill(changed)
    page.get_by_role("button", name="Update password", exact=True).click()
    page.get_by_text("Master password updated. Other sessions are now locked.", exact=True).wait_for()
    page.locator("#lock-button").click()
    page.wait_for_url("**/unlock?next=%2Fsettings")
    assert page.locator("#items .item-card").count() == 0
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
    page.wait_for_function('window.__heldResponses.length === 1')
    rect = page.locator("#loading").bounding_box()
    assert rect == {"x": 0, "y": 0, "width": 1440, "height": 1000}, rect
    logo = page.locator(".loading-logo").bounding_box()
    assert abs(logo["x"] + logo["width"] / 2 - 720) < 1
    assert page.locator(".loading-strip").bounding_box()["y"] == 0
    page.screenshot(path=str(ARTIFACTS / "centered-loader.png"))
    page.evaluate('window.__heldResponses.splice(0).forEach(release => release())')
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()

    page.goto(base + "/authenticators?test-hold=items")
    page.wait_for_function('window.__heldResponses.length === 1')
    page.locator(".skeleton-card").first.wait_for()
    assert page.locator("#items").get_attribute("aria-busy") == "true"
    page.screenshot(path=str(ARTIFACTS / "vault-skeleton.png"))
    page.evaluate('window.__heldResponses.splice(0).forEach(release => release())')
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()

    page.route("**/api/items", lambda route: route.fulfill(status=503, content_type="application/json", body='{"error":"Simulated unavailable response"}'))
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

    page.route("**/api/status", lambda route: route.fulfill(status=503, content_type="application/json", body='{"error":"Simulated unavailable response"}'))
    page.reload()
    page.locator("#loading-retry").wait_for(state="visible")
    assert page.locator(".loading-logo").is_visible()
    assert not page.locator(".loading-strip").is_visible()
    page.unroute("**/api/status")
    page.locator("#loading-retry").click()
    page.locator(".item-title").filter(has_text="KagNode QA account").wait_for()
    context.close()
    assert not errors, errors
    result = {"layouts": layouts, "page_errors": errors, "workflows": [
        "direct routes and reload", "setup and unlock return paths", "Back/Forward", "8-digit TOTP entry",
        "keyboard choice controls", "backup/merge restore", "master password rotation", "lock clears DOM",
        "saved lock preference", "mobile menu and Escape", "centered loader and top strip", "vault skeleton",
        "failed item load/retry", "failed initial load/retry", "small-screen form"]}
    (ARTIFACTS / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(layouts)} layouts and {len(result['workflows'])} workflows; no browser exceptions")


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="kagnode-authenticator-test-") as data:
        env = {k: v for k, v in os.environ.items() if not k.startswith("AUTHENTACTOR_")}
        with (ARTIFACTS / "server.log").open("w") as log:
            server = subprocess.Popen([os.environ.get("AUTH_APP_PYTHON", sys.executable), "-m", "authentactor",
                                       "--host", "127.0.0.1", "--port", str(port), "--data-dir", data, "--preview"],
                                      cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError("Disposable server exited; inspect test-artifacts/server.log")
                    try:
                        with urlopen(base + "/api/status", timeout=1) as response:
                            assert not json.load(response)["initialized"]
                        break
                    except OSError:
                        time.sleep(0.05)
                else:
                    raise RuntimeError("Disposable server did not start")
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True,
                        executable_path=os.environ.get("KAGNODE_BROWSER_EXECUTABLE") or None,
                        args=["--no-sandbox", "--disable-dev-shm-usage"])
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
