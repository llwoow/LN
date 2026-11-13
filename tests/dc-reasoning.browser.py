"""Desktop/mobile browser smoke checks for DC winding reasoning (not a physics validation)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dc-browser-artifacts"
OUT.mkdir(exist_ok=True)


def run():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = "http://127.0.0.1:" + str(server.server_address[1]) + "/"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            for label, width, height in (("desktop", 1366, 900), ("mobile", 390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.goto(url + "#course/electrical-machines/dc-sec32", wait_until="domcontentloaded")
                branches = page.locator('[data-dc-value="branches"]')
                branches.wait_for(timeout=20000)
                assert branches.inner_text() == "4"
                assert page.locator('[data-dc-value="emf"]').inner_text() == "240.0 V"

                page.locator("[data-dc-winding]").select_option("wave")
                assert branches.inner_text() == "2"
                assert page.locator('[data-dc-value="seriesConductors"]').inner_text() == "240"
                assert page.locator('[data-dc-value="emf"]').inner_text() == "480.0 V"
                page.locator("[data-dc-poles]").select_option("6")
                assert branches.inner_text() == "2"
                page.locator("[data-dc-winding]").select_option("lap")
                assert branches.inner_text() == "6"
                assert page.locator('[data-dc-value="seriesConductors"]').inner_text() == "80"
                page.locator("[data-dc-poles]").select_option("4")
                page.locator("[data-dc-current]").evaluate("(e) => {e.value = '80'; e.dispatchEvent(new Event('input', { bubbles: true }));}")
                assert page.locator('[data-dc-value="branchCurrent"]').inner_text() == "20.00 A"
                assert page.locator("[data-dc-diagram] svg").count() == 1
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                page.screenshot(path=str(OUT / ("dc-branch-" + label + ".png")), full_page=True)

                page.goto(url + "#course/electrical-machines/dc-answers", wait_until="domcontentloaded")
                question = page.locator('[data-dc-question="wave6"]')
                question.wait_for(timeout=20000)
                question.locator('input[value="a"]').check()
                question.locator("[data-dc-check]").click()
                assert "不正确" in question.locator("[data-dc-feedback]").inner_text()
                question.locator('input[value="b"]').check()
                question.locator("[data-dc-check]").click()
                assert "正确" in question.locator("[data-dc-feedback]").inner_text()
                assert page.locator('[data-dc-question]').count() == 5
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                page.screenshot(path=str(OUT / ("dc-diagnostics-" + label + ".png")), full_page=True)

                page.goto(url + "#course/electrical-machines/dc-worked/dc-example-313-review", wait_until="domcontentloaded")
                section = page.locator("#dc-example-313-review")
                section.wait_for(timeout=20000)
                assert "356.52" in section.inner_text()
                assert "待确认" in section.inner_text()
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run()
    print("DC reasoning desktop/mobile browser smoke checks passed.")
