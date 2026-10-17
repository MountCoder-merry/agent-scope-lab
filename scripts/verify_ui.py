"""Small browser smoke suite for the static AgentScope demo.

The script intentionally uses only synthetic data and a temporary import file.
It can run against an already started Vite server or the default local URL.
"""

import json
import os
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    base_url = os.environ.get("AGENTSCOPE_BASE_URL", "http://127.0.0.1:5173")
    imported = {
        "traceId": "tr_import_smoke",
        "scenario": "invalid-json",
        "title": "Imported smoke trace",
        "summary": "A trace imported by the browser smoke test.",
        "status": "failed",
        "startedAt": "2026-10-17T04:00:00.000Z",
        "durationMs": 10,
        "spans": [{"spanId": "sp_root", "name": "Smoke parser", "kind": "parser", "status": "error", "durationMs": 10, "detail": "Synthetic import", "error": "INVALID_JSON"}],
        "events": [{"eventId": "ev_smoke", "sequence": 0, "spanId": "sp_root", "type": "tool.failed", "label": "Import failed", "atMs": 10, "payload": "synthetic"}],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(imported, handle)
        import_path = handle.name

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
            page.goto(base_url, wait_until="networkidle")
            assert page.get_by_role("heading", name="Recorded traces").is_visible()
            assert page.get_by_role("heading", name="Tool timeout / weather lookup").is_visible()
            page.get_by_role("button", name="Invalid JSON / structured output").click()
            page.get_by_label("Replay event").fill("2")
            assert page.get_by_text("INVALID_JSON").is_visible()
            assert page.get_by_text("Parser called").is_visible()
            page.get_by_role("button", name="Tool timeout / weather lookup").click()
            page.get_by_text("Run mock").click()
            assert page.get_by_text("Bounded retry").count() >= 1
            page.get_by_role("link", name="Docs").click()
            page.wait_for_timeout(150)
            assert page.get_by_role("heading", name="Recorded replay, explained").is_visible()
            page.get_by_role("link", name="Failure lab").click()
            page.wait_for_timeout(150)
            assert page.get_by_text("What if we recover?").is_visible()
            page.get_by_role("link", name="Traces").click()
            page.wait_for_timeout(150)
            page.locator('input[type="file"]').set_input_files(import_path)
            page.get_by_text("Imported tr_import_smoke").wait_for(timeout=3000)
            page.get_by_role("heading", name="Imported smoke trace").wait_for(timeout=3000)
            page.close()

            mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
            mobile.goto(f"{base_url}/#/traces", wait_until="networkidle")
            assert mobile.get_by_role("heading", name="Recorded traces").is_visible()
            assert mobile.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            mobile.close()
            browser.close()
            print("ui-smoke: ok; routes/import/mobile verified")
    finally:
        Path(import_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
