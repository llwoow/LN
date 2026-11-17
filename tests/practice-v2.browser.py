"""End-to-end shared LN practice redesign: answer-in-place, exam isolation, all courses, mobile."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"practice-v2-artifacts"
OUT.mkdir(exist_ok=True)

def check():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    base="http://127.0.0.1:"+str(server.server_address[1])+"/"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            for width in (1366,390,320):
                name="desktop" if width==1366 else "mobile-"+str(width)
                context=browser.new_context(viewport={"width":width,"height":860},device_scale_factor=1)
                page=context.new_page()
                errors=[]
                page.on("pageerror",lambda exc: errors.append(str(exc)))
                page.goto(base+"#practice/electrical-machines",wait_until="domcontentloaded")
                page.locator("[data-practice-mode=local]").wait_for()
                assert page.locator("[data-practice-mode=local]").get_attribute("aria-pressed")=="true"
                assert page.locator("[data-practice-mode=exam]").count()==1
                panel=page.locator("main [data-practice-panel]")
                assert panel.locator("[data-p-number-state]").count()>0
                panel.locator("[data-p-question]").select_option("em-start")
                assert panel.locator("[data-p-submit]").count()==1
                panel.locator('[name="p-answer"][value="0"]').check()
                panel.locator("[data-p-submit]").click()
                assert "尚不吻合" in panel.locator(".practice-verdict h3").inner_text()
                assert panel.locator('[data-p-option-state="wrong"]').count()==1
                assert panel.locator('[data-p-option-state="missed"]').count()==1
                assert panel.locator(".practice-answer-line").count()==1
                assert panel.locator("[data-p-overview]").count()==1
                assert panel.locator(".practice-choice-detail").count()==2
                page.screenshot(path=str(OUT/("practice-choice-"+name+".png")))
                panel.locator('[name="p-answer"][value="1"]').check()
                panel.locator("[data-p-submit]").click()
                assert "选择吻合" in panel.locator(".practice-verdict h3").inner_text()
                assert panel.locator('[data-p-option-state="correct"]').count()==1
                record=page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-start']")
                assert record["attempts"][0]["correct"] is False
                assert record["attempts"][1]["correct"] is True and record["attempts"][1]["assisted"] is True
                panel.locator("[data-p-question]").select_option("em-power")
                panel.locator("[data-p-value]").fill("0")
                panel.locator("[data-p-submit]").click()
                assert panel.locator(".practice-numeric-compare").count()==1
                assert "参考答案" in panel.locator(".practice-numeric-compare").inner_text()
                assert "88" in panel.locator(".practice-numeric-compare").inner_text()
                panel.locator("[data-p-question]").select_option("em-flux")
                panel.locator('[name="p-answer"][value="0"]').check()
                panel.locator("[data-p-submit]").click()
                assert "部分选项吻合" in panel.locator(".practice-verdict h3").inner_text()
                assert panel.locator('[data-p-option-state="missed"]').count()==1
                panel.locator("[data-p-question]").select_option("em-test-design")
                panel.locator("[data-p-reason]").fill("我的假设和验证方案会测量不同转速和负载。")
                panel.locator("[data-p-submit]").click()
                assert "逐项自评" in panel.locator(".practice-verdict h3").inner_text()
                panel.locator("[data-p-rubric]").first.check()
                panel.locator("[data-p-filter-box] summary").click()
                panel.locator("[data-p-type]").select_option("numeric")
                assert panel.locator("[data-p-question] option").count()>0
                panel.locator("[data-p-type]").select_option("")
                panel.locator("[data-p-map] summary").click()
                panel.locator("[data-p-number-state]").first.click()
                assert panel.locator("[data-question-id]").count()==1
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),("practice",width)
                # Chapter tests use separate drafts and never show feedback until final submission.
                page.locator("[data-practice-mode=exam]").click()
                page.locator('[data-e-start="10"]').click()
                exam=page.locator("[data-exam-content]")
                assert exam.locator("[data-e-question]").count()==1
                assert exam.locator(".practice-feedback").count()==0
                assert exam.locator(".practice-choice-detail").count()==0
                first=exam.locator("[data-e-question]").get_attribute("data-e-question")
                firstQ=page.evaluate("(id)=>window.LN_PRACTICE_BANK.questions.find(q=>q.id===id)",first)
                if firstQ["options"]:
                    exam.locator('[name="e-answer"][value="'+firstQ["answer"][0]+'"]').check()
                elif firstQ["type"]=="numeric":
                    exam.locator("[data-e-value]").fill(str(firstQ["answer"]))
                else:
                    exam.locator("[data-e-reason]").fill("先建立模型再核查边界条件")
                exam.locator("[data-e-next]").click()
                assert exam.locator(".practice-feedback").count()==0
                assert "ln.practice.exam.v1" in page.evaluate("Object.keys(localStorage)")
                page.reload(wait_until="domcontentloaded")
                page.locator("[data-practice-mode=exam]").click()
                exam=page.locator("[data-exam-content]")
                assert exam.locator("[data-e-question]").count()==1
                assert exam.locator("[data-e-question]").get_attribute("data-e-question")!=first
                exam.locator("[data-e-finish]").click()
                exam.locator("[data-e-confirm]").click()
                assert "章节测试结果" in exam.inner_text()
                assert exam.locator(".practice-exam-metrics").count()==1
                assert exam.locator("[data-e-review]").count()==10
                exam.locator("[data-e-review]").first.click()
                assert exam.locator(".practice-feedback").count()==1
                assert exam.locator(".practice-answer-line").count()==1
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),("exam",width)
                page.screenshot(path=str(OUT/("practice-exam-review-"+name+".png")))
                page.locator("[data-practice-mode=sources]").click()
                assert page.locator('[data-source-id="mit-machines-ps1"]').count()==1
                page.locator('[data-practice-mode=local]').click()
                # The shared layout must render data from other actual LN courses, not a DC-only branch.
                for course in ("automatic-control","electromagnetic-compatibility","electrical-materials","power-semiconductors","robot-drive-engineering"):
                    page.goto(base+"#practice/"+course,wait_until="domcontentloaded")
                    panel=page.locator("main [data-practice-panel]")
                    panel.wait_for(timeout=12000)
                    assert panel.locator("[data-p-question] option").count()>0,course
                    assert panel.locator(".practice-question").count()==1,course
                    assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),(course,width)
                # Reader opening must preserve focus/scroll and not trap the entire page horizontally.
                page.goto(base+"#course/electrical-machines/dc-sec35",wait_until="domcontentloaded")
                page.locator('#lesson-body[aria-busy="false"]').wait_for(timeout=16000)
                page.locator("#reader-dock [data-reader-directory]").click()
                page.locator('#reader-directory [data-open-practice]').click()
                dialog=page.locator("#practice-dialog:modal")
                dialog.wait_for(timeout=10000)
                assert dialog.locator("[data-practice-mode=local]").get_attribute("aria-pressed")=="true"
                bbox=dialog.bounding_box()
                assert bbox["x"]>=-1 and bbox["x"]+bbox["width"]<=width+1,(width,bbox)
                page.evaluate("document.documentElement.dataset.theme='dark'")
                page.screenshot(path=str(OUT/("practice-dialog-dark-"+name+".png")))
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth")
                dialog.locator("[data-close-practice]").click()
                assert not errors,errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    check()
    print("Universal practice and exam browser checks passed: desktop, 390px and 320px.")
