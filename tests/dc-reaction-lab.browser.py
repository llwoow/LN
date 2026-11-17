"""Browser-only review of DC courseware augmentation: functionality and layout, not a hardware validation."""
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
            for name, width, height in (("desktop", 1366, 900), ("mobile", 390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(url + "#course/electrical-machines/dc-sec32", wait_until="domcontentloaded")
                page.locator("#dc-courseware-16").wait_for(timeout=25000)
                assert page.locator("#dc-winding16-figure svg").count() == 1
                assert page.locator("[data-dc-winding-lab]").count() == 1
                assert page.locator("#dc-winding16-figure figcaption").count() == 1
                assert page.locator("#dc-courseware-16").inner_text()
                assert page.locator("#lesson-body [data-dc-supp-tex] .katex").count() >= 5
                page.locator("#dc-courseware-16 + p").count()  # content follows heading
                details = page.locator("#dc-courseware-16").locator("xpath=following-sibling::details[1]")
                details.locator("summary").click()
                assert details.locator("tbody tr").count() == 16
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                page.screenshot(path=str(OUT / ("dc-16-winding-" + name + ".png")), full_page=False)
                page.goto(url + "#course/electrical-machines/dc-sec33", wait_until="domcontentloaded")
                slider = page.locator("[data-dc-reaction-lab] [data-q]")
                slider.wait_for(timeout=25000)
                assert page.locator("[data-dc-reaction-lab] svg").count() == 1
                assert page.locator("#dc-reaction-figure figcaption").count() == 1
                assert page.locator("#lesson-body [data-dc-supp-tex] .katex").count() >= 2
                assert page.locator("[data-dc-reaction-lab] [data-result]").inner_text()
                slider.evaluate("(e)=>{e.value='0.6';e.dispatchEvent(new Event('input',{bubbles:true}));}")
                saturated = page.locator("[data-dc-reaction-lab] [data-result]").inner_text()
                assert "0.6" not in saturated  # result reports angle and flux, not raw q
                assert "80.7%" in saturated
                page.locator("[data-dc-reaction-lab] [data-sat]").uncheck()
                assert "100.0%" in page.locator("[data-dc-reaction-lab] [data-result]").inner_text()
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                page.screenshot(path=str(OUT / ("dc-reaction-" + name + ".png")), full_page=False)
                page.close()
            browser.close()
    finally:
        server.shutdown()

if __name__ == "__main__":
    run()
