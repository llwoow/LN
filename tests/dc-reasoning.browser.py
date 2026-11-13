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
                page.locator('[data-practice-question="dc-branch-wave-six"]').click()
                dialog = page.locator('#practice-dialog:modal')
                panel = dialog.locator('[data-practice-panel]')
                panel.locator('input[value="divide-poles"]').check()
                panel.locator('[data-p-submit]').click()
                assert panel.locator('.practice-feedback h3').inner_text() == '答案尚不吻合，检查下面的推理'
                panel.locator('[data-p-redo]').click()
                panel.locator('input[value="two-paths"]').check()
                panel.locator('[data-p-submit]').click()
                assert panel.locator('.practice-feedback h3').inner_text() == '选择吻合，请继续核对理由'
                panel.locator('[data-p-favorite]').click()
                state = page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["dc-branch-wave-six"]')
                assert state['favorite'] and state['attempts'][0]['correct'] is False
                assert state['attempts'][-1]['correct'] is True
                dialog.locator('[data-close-practice]').click()
                assert page.locator('#dc-concept-diagnostics [data-practice-question]').count() == 5
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
