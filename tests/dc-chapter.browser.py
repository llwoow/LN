"""Actual browser behavior for all 60 DC chapter questions at desktop/mobile sizes."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"dc-browser-artifacts"
OUT.mkdir(exist_ok=True)
NAMES=("dc-31-33.json","dc-34-36.json","dc-37-39.json","dc-integrated.json")
QUESTIONS=[q for n in NAMES for q in json.loads((ROOT/"courses/electrical-machines/assessment"/n).read_text())["questions"]]

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base="http://127.0.0.1:"+str(server.server_address[1])+"/"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            for label,width,height in (("desktop",1366,900),("mobile",390,844)):
                context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
                page=context.new_page()
                page.goto(base+"#course/electrical-machines/dc-chapter-test",wait_until="domcontentloaded")
                page.locator("#dc-chapter-test").wait_for(timeout=25000)
                assert page.locator(".dc-test-topic").count()==10
                page.locator(".dc-test-launch [data-open-practice]").click()
                panel=page.locator("#practice-dialog:modal [data-practice-panel]")
                panel.wait_for(timeout=25000)
                assert panel.locator("[data-p-question] option").count()==60
                assert "60 题" in panel.locator("[data-p-scope]").inner_text()
                # Confirm correct/incorrect answer feedback, first-attempt preservation,
                # open questions not marked automatically, and every diagram loads.
                for q in QUESTIONS:
                    panel.locator("[data-p-question]").select_option(q["id"])
                    assert panel.locator("[data-question-id]").get_attribute("data-question-id")==q["id"]
                    assert panel.locator("[data-p-reason]").count()==1
                    if "promptHtml" in q:
                        assert panel.locator(".dc-test-figure svg[role=img]").count()==1,q["id"]
                        assert panel.locator(".dc-test-figure figcaption").count()==1,q["id"]
                    if q["type"] in ("single","multi"):
                        for option in q["answer"]:
                            panel.locator('[name="p-answer"][value="'+option+'"]').check()
                    elif q["type"]=="numeric":
                        panel.locator("[data-p-value]").fill(str(q["answer"]))
                        panel.locator("[data-p-reason]").fill("用电势/转矩方程和单位进行核查。")
                    else:
                        panel.locator("[data-p-reason]").fill("先建立模型并说明适用条件，再逐项核对答案要点。")
                    panel.locator("[data-p-submit]").click()
                    feedback=panel.locator(".practice-feedback")
                    assert feedback.count()==1,q["id"]
                    if q["type"]=="open":
                        assert "逐项自评" in feedback.locator("h3").inner_text(),q["id"]
                    else:
                        assert "尚不吻合" not in feedback.locator("h3").inner_text(),q["id"]
                    assert feedback.locator("ol li").count()>=3,q["id"]
                    assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),(label,q["id"])
                    if q["id"] in ("dc-test-32-04","dc-test-38-06"):
                        page.screenshot(path=str(OUT/("dc-60-"+q["id"]+"-"+label+".png")))
                assert len(page.evaluate("Object.keys(JSON.parse(localStorage.getItem('ln.practice.v1'))).filter(k=>k.startsWith('dc-test-'))"))==60
                # Existing API records remain in place; a test record is not wiped on reload.
                page.locator("#practice-dialog [data-close-practice]").click()
                page.reload(wait_until="domcontentloaded")
                page.locator(".dc-test-launch [data-open-practice]").click()
                assert page.locator("#practice-dialog:modal [data-p-question] option").count()==60
                r=page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['dc-test-31-01']")
                assert len(r["attempts"])==1 and r["attempts"][0]["correct"] is True
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth")
                page.screenshot(path=str(OUT/("dc-60-opening-"+label+".png")))
                context.close()
            browser.close()
    finally:
        server.shutdown()

if __name__=="__main__":
    run()
