"""Chromium verification for every EMC lesson + four lesson-local models.

Starts a real HTTP server from the checked-out LN branch. No deployment required.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "emc-browser-artifacts"
OUT.mkdir(exist_ok=True)
META = json.loads((ROOT / "courses/electromagnetic-compatibility/curriculum.json").read_text())
SELECTED = ("emc-2-2", "emc-4-4", "emc-5-4", "emc-10-3")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = "http://127.0.0.1:" + str(server.server_address[1]) + "/"
    audit = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            for name, width, height in (("desktop", 1440, 900), ("mobile", 390, 844), ("mobile-small", 320, 690)):
                page = browser.new_page(viewport={"width":width,"height":height}, reduced_motion="reduce")
                errors, http_errors = [], []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("response", lambda r: http_errors.append([r.status,r.url]) if r.status >= 400 else None)
                for record in META["sections"]:
                    id = record["id"]
                    page.goto(base + "#course/electromagnetic-compatibility/" + id, wait_until="domcontentloaded")
                    lesson = page.locator('#lesson-body[data-lesson-key="electromagnetic-compatibility/'+id+'"][aria-busy="false"]')
                    lesson.wait_for(timeout=30000)
                    page.evaluate("document.fonts.ready")
                    assert lesson.locator("h2").count() > 0, (id,"missing title")
                    assert lesson.locator('.katex-error').count() == 0, (id,"math parse")
                    assert lesson.locator('p[role="alert"]').count() == 0, (id,"load failed")
                    assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), (id,width,"horizontal overflow")
                    if id in SELECTED:
                        assert lesson.locator(".paper-equation.is-numbered").count() >= 3, (id,"unindexed formula")
                        assert lesson.locator("figure").count() > 0, (id,"missing figures")
                        assert lesson.locator(".emc-lab-ui input[type=range]").count() >= 2, (id,"lab missing")
                        status = lesson.locator(".emc-lab-result")
                        original = status.inner_text()
                        slider = lesson.locator(".emc-lab-field input[type=range]").first
                        slider.evaluate("(el)=>{el.value = el.max; el.dispatchEvent(new Event('input',{bubbles:true}));}")
                        assert status.inner_text() != original, (id,"interactive model does not respond")
                        page.screenshot(path=str(OUT / (id+"-"+name+".png")), full_page=True)
                    audit.append({"section":id, "viewport":name, "ok":True})
                assert not errors, errors
                assert not http_errors, http_errors
                # Exercise every new EMC diagnostic through actual radio/checkbox/numeric controls.
                emc_questions = [q for q in json.loads((ROOT / "courses/practice/bank.json").read_text())["questions"]
                                 if q["course"] == "electromagnetic-compatibility"]
                page.goto(base + "#practice/electromagnetic-compatibility", wait_until="domcontentloaded")
                page.locator('[data-practice-mode="local"]').click()
                panel = page.locator("main [data-practice-panel]")
                for q in emc_questions:
                    panel.locator("[data-p-question]").select_option(q["id"])
                    if q["type"] in ("single", "multi"):
                        for option in q["answer"]:
                            panel.locator('[name="p-answer"][value="' + option + '"]').check()
                    elif q["type"] == "numeric":
                        panel.locator("[data-p-value]").fill(str(q["answer"]))
                        panel.locator("[data-p-reason]").fill("按题给模型独立复算，并核对参考单位。")
                    else:
                        panel.locator("[data-p-reason]").fill("写出模型、条件与可检验的工程结论。")
                    panel.locator("[data-p-submit]").click()
                    assert panel.locator(".practice-feedback").count() == 1, (q["id"],name)
                    assert panel.locator(".practice-feedback ol li").count() >= 3, (q["id"],"missing steps")
                    assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), (q["id"],width)
                page.screenshot(path=str(OUT / ("emc-practice-" + name + ".png")),full_page=True)
                page.goto(base + "#course/automatic-control/ac-3-6")
                page.locator("#lesson-body[data-lesson-key='automatic-control/ac-3-6'][aria-busy=false]").wait_for()
                assert "动态误差系数" in page.locator("#lesson-body").inner_text()
                page.goto(base + "#course/electrical-machines/transformer-4")
                page.locator("#lesson-body[data-lesson-key='electrical-machines/transformer-4'][aria-busy=false]").wait_for()
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (OUT / "audit.json").write_text(json.dumps({"checks":len(audit),"viewports":["desktop","mobile","mobile-small"],"lessons":len(META["sections"]),"practiceQuestions":11},ensure_ascii=False,indent=2))
    print(f"Verified {len(audit)} rendered reading states in real Chromium.")


if __name__ == "__main__":
    main()
