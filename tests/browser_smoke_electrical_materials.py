"""Initial real-browser review of the new LN Electrical Materials course."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical-materials-browser-artifacts"
OUT.mkdir(exist_ok=True)
COURSE = "electrical-materials"
LESSONS = ["em-2-1", "em-2-2", "em-2-3", "em-2-4", "em-2-5", "em-test-summary", "em-test-fill", "em-test-short", "em-test-review"]
SIZES = [("desktop", 1440, 900), ("phone", 390, 844), ("phone-small", 320, 690)]

def main():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist")),
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:" + str(server.server_address[1]) + "/"
    rendered = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            for name, width, height in SIZES:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    reduced_motion="reduce"
                )
                errors, missing = [], []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("response", lambda r: missing.append([r.status, r.url]) if r.status >= 400 else None)
                for sid in LESSONS:
                    page.goto(base + "#course/" + COURSE + "/" + sid, wait_until="domcontentloaded")
                    body = page.locator(
                        '#lesson-body[data-lesson-key="' + COURSE + "/" + sid + '"][aria-busy=false]'
                    )
                    body.wait_for(timeout=30000)
                    assert body.locator("h2").count(), sid
                    assert not body.locator(".katex-error").count(), sid
                    assert not body.locator("p[role=alert]").count(), sid
                    assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), (sid, name, "horizontal overflow")
                    for fig in body.locator("figure").all():
                        assert fig.locator("figcaption").count(), (sid, "missing figure caption")
                        for svg in fig.locator("svg").all():
                            assert svg.locator("title").count(), (sid, "missing SVG accessibility title")
                    if sid == "em-2-4":
                        assert body.locator("math").count() >= 2, "Missing chapter 2 thermal equations"
                    page.screenshot(path=str(OUT / (sid + "-" + name + ".png")), full_page=True)
                    rendered.append({"lesson": sid, "viewport": name})
                page.goto(base + "#course/" + COURSE + "/map")
                page.locator("ln-knowledge-map").wait_for(timeout=30000)
                page.screenshot(path=str(OUT / ("map-" + name + ".png")), full_page=True)
                page.goto(base + "#practice/" + COURSE)
                page.locator("[data-practice-mode=local]").click()
                panel = page.locator("main [data-practice-panel]")
                panel.locator("[data-p-question]").select_option("emat-2-thermal")
                panel.locator("[data-p-value]").fill("2")
                panel.locator("[data-p-reason]").fill("Rth=L/(lambda*A), dimensions in SI, steady 1D case.")
                panel.locator("[data-p-submit]").click()
                assert panel.locator(".practice-feedback ol li").count() >= 3
                page.screenshot(path=str(OUT / ("practice-" + name + ".png")), full_page=True)
                assert not errors, errors
                assert not missing, missing
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (OUT / "audit.json").write_text(json.dumps({
        "course": COURSE,
        "lessonCount": len(LESSONS),
        "viewports": [name for name, _, _ in SIZES],
        "renderedStates": len(rendered),
        "screenshots": rendered,
        "limitations": "Initial smoke test, not a full chapter-by-chapter scientific review or learner study."
    }, ensure_ascii=False, indent=2))
    print("Verified", len(rendered), "lesson/viewport states, knowledge maps and first-pass practice.")

if __name__ == "__main__":
    main()
