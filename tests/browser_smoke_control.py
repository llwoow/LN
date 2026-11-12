"""Browser smoke checks for the edition-3 LN automatic-control course.

Uses the real static site and Chromium; never needs production deployment.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "control-browser-artifacts"
OUT.mkdir(exist_ok=True)


def run() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = "http://127.0.0.1:" + str(server.server_address[1]) + "/"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
            for name, width, height in [("desktop", 1366, 900), ("mobile", 390, 844)]:
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.goto(base + "#course/automatic-control/ac-3-6", wait_until="domcontentloaded")
                page.locator("#ac-dynamic-error").wait_for(timeout=20000)
                page.evaluate('document.fonts.ready')
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                assert "动态误差系数" in page.locator("#ac-dynamic-error").inner_text()
                assert page.locator(".ac-equation math").count() >= 3
                selector = page.locator("[data-ac-disturbance-select]")
                selector.wait_for(timeout=10000)
                selector.select_option("after")
                assert "−0.3" in page.locator("[data-ac-disturbance-status]").inner_text()
                selector.select_option("before")
                assert "eₛₛ,ₙ=0" in page.locator("[data-ac-disturbance-status]").inner_text()
                page.screenshot(path=str(OUT / ("automatic-control-" + name + "-error.png")), full_page=True)

                page.goto(base + "#course/automatic-control/ac-3-5", wait_until="domcontentloaded")
                page.locator("[data-ac-k-input]").wait_for(timeout=20000)
                slider = page.locator("[data-ac-k-input]")
                slider.evaluate("(el) => {el.value='2';el.dispatchEvent(new Event('input',{bubbles:true}));}")
                assert "不能判为渐近稳定" in page.locator("[data-ac-routh-status]").inner_text()
                slider.evaluate("(el) => {el.value='1';el.dispatchEvent(new Event('input',{bubbles:true}));}")
                assert "闭环渐近稳定" in page.locator("[data-ac-routh-status]").inner_text()

                page.goto(base + "#course/automatic-control/ac-homework3", wait_until="domcontentloaded")
                page.locator("#question-3-13").wait_for(timeout=20000)
                assert "第3版3-20" in page.locator("#question-3-13").inner_text()
                assert "第3版3-21" in page.locator("#question-3-14").inner_text()
                assert "不同于第3版3-18" in page.locator("#question-3-18").inner_text()
                if not page.locator('[data-homework-jump]').is_visible():
                    page.locator('[data-reader-directory]').click()
                page.locator('[data-homework-jump]').select_option('3-16')
                page.locator('#question-3-16.reference-target').wait_for()
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                page.screenshot(path=str(OUT / ("automatic-control-" + name + "-homework.png")), full_page=True)

                page.goto(base + "#course/automatic-control/ac-3-3", wait_until="domcontentloaded")
                symbol = page.locator('math [data-definition="ac-natural-frequency"]').first
                symbol.wait_for(); symbol.scroll_into_view_if_needed()
                y = symbol.bounding_box()['y']; symbol.click(force=True)
                popup = page.locator('#definition-popover:popover-open'); popup.wait_for()
                assert 'rad/s' in popup.inner_text()
                page.locator('.definition-source-link').click()
                page.locator('.reference-target[data-definition-source]').wait_for()
                page.locator('.reference-return').click()
                page.wait_for_function('document.querySelector(".reference-return").hidden')
                page.wait_for_timeout(100)
                assert abs(page.locator('math [data-definition="ac-natural-frequency"]').first.bounding_box()['y'] - y) < 4
                page.goto(base + "#course/automatic-control/ac-4-2-2", wait_until="domcontentloaded")
                plot = page.locator("[data-ac-root-locus]")
                plot.wait_for(timeout=20000)
                page.locator("[data-ac-root-values] li").first.wait_for()
                assert page.locator("[data-ac-root-values] li").count() == 4
                if width < 560:
                    assert page.locator('.ac-root-plot-wrapper').evaluate('(n)=>n.scrollWidth>n.clientWidth')
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                page.locator("[data-ac-set-k='8.16']").click()
                assert "临界稳定" in page.locator("[data-ac-root-status]").inner_text()
                page.locator("[data-ac-root-wrong-toggle]").click()
                assert page.locator("[data-ac-root-wrong-toggle]").get_attribute("aria-pressed") == "true"
                assert page.locator("[data-ac-root-wrong] path").first.is_visible()
                page.locator("[data-ac-set-k='0']").click()
                assert page.locator("[data-ac-root-moving] circle[fill='#1676b5']").count() == 2
                page.locator("[data-ac-set-k='5']").click()
                page.screenshot(path=str(OUT / ("automatic-control-" + name + "-root-locus.png")), full_page=True)
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run()
    print("Automatic-control desktop/mobile browser smoke tests passed.")
