"""End-to-end checks for LN's shared practice UX across the real questions."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"practice-ux-artifacts"
OUT.mkdir(exist_ok=True)

def run():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url="http://127.0.0.1:"+str(server.server_address[1])+"/"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            for name,width in (("desktop",1440),("mobile",390),("compact",320)):
                ctx=browser.new_context(viewport={"width":width,"height":850},device_scale_factor=1)
                page=ctx.new_page()
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto(url+"#practice/electrical-machines")
                panel=page.locator("main [data-practice-panel]")
                panel.wait_for(timeout=30000)
                assert page.locator('[data-practice-mode="local"]').get_attribute("aria-pressed")=="true"
                assert panel.locator(".practice-session-modes button").count()==2
                assert panel.locator("[data-p-grid] button").count()>20
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth")
                page.screenshot(path=str(OUT/("practice-overview-"+name+".png")))
                # The answer is only marked after submission and inline at the chosen option.
                panel.locator('[data-p-question]').select_option("em-start")
                assert panel.locator(".practice-option-reason").count()==0
                panel.locator('[name="p-answer"][value="0"]').check()
                panel.locator("[data-p-confidence]").select_option("sure")
                panel.locator("[data-p-submit]").click()
                assert panel.locator(".practice-feedback").count()==1
                assert panel.locator(".practice-option-wrong").count()==1
                assert panel.locator(".practice-option-correct").count()==1
                assert panel.locator(".practice-option-reason").count()==3
                assert "我的选择" in panel.locator(".practice-answer-compare").inner_text()
                assert "正确选项" in panel.locator(".practice-answer-compare").inner_text()
                assert panel.locator(".practice-solution-steps li").count()>=3
                page.screenshot(path=str(OUT/("practice-inline-review-"+name+".png")))
                # A retry preserves the first wrong, confident attempt and marks the next one assisted.
                panel.locator("[data-p-redo]").click()
                panel.locator('[name="p-answer"][value="1"]').check()
                panel.locator("[data-p-submit]").click()
                history=page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-start'].attempts")
                assert history[0]["correct"] is False and history[0]["confidence"]=="sure"
                assert history[1]["correct"] is True and history[1]["assisted"] is True
                # Exam mode has distinct drafts, hides answers until whole-paper submission.
                panel.locator('[data-p-session="exam"]').click()
                assert panel.locator('[data-p-session="exam"]').get_attribute("aria-pressed")=="true"
                assert panel.locator(".practice-feedback").count()==0
                panel.locator('[data-p-question]').select_option("em-start")
                panel.locator('[name="p-answer"][value="1"]').check()
                assert panel.locator(".practice-option-reason").count()==0
                assert panel.locator("[data-p-reveal]").is_hidden()
                panel.locator("[data-p-submit]").click()
                assert panel.locator("[data-p-question]").input_value()!="em-start"
                panel.locator("[data-p-finish-exam]").click()
                assert "本次测试已交卷" in panel.locator("[data-p-exam-report]").inner_text()
                panel.locator('[data-p-question]').select_option("em-start")
                assert panel.locator(".practice-feedback").count()==1
                assert panel.locator(".practice-option-correct").count()==1
                assert panel.locator(".practice-session-footer [data-p-restart-exam]").is_visible()
                examBefore=page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1')).practiceExams['electrical-machines::all::local']")
                assert examBefore["submitted"] and examBefore["answers"]["em-start"]["selected"]==["1"]
                assert page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-start'].attempts[0].correct") is False
                page.screenshot(path=str(OUT/("practice-exam-review-"+name+".png")))
                page.reload()
                panel=page.locator("main [data-practice-panel]")
                panel.locator('[data-p-session="exam"]').click()
                assert "本次测试已交卷" in panel.locator("[data-p-exam-report]").inner_text()
                panel.locator("[data-p-restart-exam]").click()
                assert panel.locator(".practice-feedback").count()==0
                assert panel.locator('[data-p-question]').input_value()=="em-start"
                # Same component powers all courses; course filters remain reachable, not removed.
                panel.locator('[data-p-session="practice"]').click()
                panel.locator(".practice-filter-drawer summary").click()
                for value in [o.get_attribute("value") for o in panel.locator("[data-p-course] option").all()]:
                    panel.locator("[data-p-course]").select_option(value)
                    assert panel.locator("[data-p-scope]").count()==1
                    assert panel.locator("[data-p-grid]").count()==1
                panel.locator("[data-p-course]").select_option("electrical-machines")
                panel.locator("[data-p-question]").select_option("dc-test-31-01")
                assert panel.locator(".practice-prompt").count()==1
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth")
                page.evaluate("document.documentElement.dataset.theme='dark'")
                page.screenshot(path=str(OUT/("practice-dark-"+name+".png")))
                assert not errors,errors
                ctx.close()
            browser.close()
    finally:
        server.shutdown()

if __name__=="__main__":
    run()
