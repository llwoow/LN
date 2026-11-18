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
                height=740 if width==320 else 860
                context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
                page=context.new_page()
                errors=[]
                page.on("pageerror",lambda exc: errors.append(str(exc)))
                page.goto(base+"#practice/electrical-machines",wait_until="domcontentloaded")
                page.locator("[data-practice-mode=local]").wait_for()
                assert page.locator("[data-practice-mode=local]").get_attribute("aria-pressed")=="true"
                assert page.locator("[data-practice-mode=exam]").count()==1
                panel=page.locator("main [data-practice-panel]")
                assert panel.locator("[data-p-number-state]").count()>0
                if width<=390:
                    modes=page.locator("main .practice-modes")
                    assert modes.evaluate("(el)=>el.scrollWidth<=el.clientWidth")
                    controls=panel.locator('[data-p-question], [data-p-map]>summary, [data-p-filter-box]>summary').all()
                    assert len({round(el.bounding_box()["y"]) for el in controls})==1
                    assert panel.locator(".practice-choice").first.bounding_box()["y"] < height-100
                    page.screenshot(path=str(OUT/("practice-start-"+name+".png")))
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
                assert not panel.locator("[data-p-map]").evaluate("(node)=>node.open")
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),("practice",width)
                # Exam grading must leave the corresponding regular-practice draft intact.
                panel.locator("[data-p-question]").select_option("em-start")
                panel.locator(".practice-thinking summary").click()
                panel.locator("[data-p-reason]").fill("逐题练习的草稿")
                before=page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-start']")
                page.locator("[data-practice-mode=exam]").click()
                page.locator('[data-e-start="10"]').click()
                exam=page.locator("[data-exam-content]")
                assert exam.locator(".practice-feedback,.practice-choice-detail").count()==0
                assert exam.locator("[data-e-question]").get_attribute("data-e-question")=="em-start"
                order=exam.locator('[name="e-answer"]').evaluate_all("(options)=>options.map(el=>el.value)")
                exam.locator('[name="e-answer"][value="0"]').check()
                assert "已答 1 / 10" in exam.locator("[data-e-progress]").inner_text()
                exam.locator("[data-e-next]").click()
                page.reload(wait_until="domcontentloaded")
                page.locator("[data-practice-mode=exam]").click()
                assert exam.locator("[data-e-question]").get_attribute("data-e-question")=="em-load"
                assert exam.locator(".practice-feedback,.practice-choice-detail").count()==0
                exam.locator("[data-e-prev]").click()
                assert exam.locator('[name="e-answer"]').evaluate_all("(options)=>options.map(el=>el.value)")==order
                assert exam.locator('[name="e-answer"][value="0"]').is_checked()
                exam.locator(".practice-number-map summary").click()
                exam.locator('[data-e-jump="6"]').click()
                exam.locator("[data-e-value]").fill("88 W")
                assert "有效数值" in exam.locator("[data-e-invalid]").inner_text()
                assert "已答 1 / 10" in exam.locator("[data-e-progress]").inner_text()
                exam.locator(".practice-number-map summary").click()
                exam.locator('[data-e-jump="8"]').click()
                exam.locator("[data-e-reason]").fill("先建立模型再核查边界条件。")
                assert "已答 2 / 10" in exam.locator("[data-e-progress]").inner_text()
                exam.locator("[data-e-finish]").click()
                confirm=exam.locator(".practice-exam-confirm:modal")
                assert confirm.locator("[data-e-cancel]").evaluate("(el)=>el===document.activeElement")
                page.keyboard.press("Escape")
                assert not confirm.count()
                assert exam.locator("[data-e-finish]").evaluate("(el)=>el===document.activeElement")
                exam.locator("[data-e-finish]").click()
                confirm.locator("[data-e-confirm]").click()
                assert exam.locator("[data-e-report-title]").evaluate("(el)=>el===document.activeElement")
                assert "章节测试结果" in exam.inner_text()
                assert exam.locator(".practice-exam-metrics").count()==1
                assert exam.locator("[data-e-review]").count()==10
                after=page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-start']")
                assert after["attempts"][:-1]==before["attempts"]
                assert after["attempts"][-1]["examId"] and after["attempts"][-1]["correct"] is False
                for field in ("selected","value","reason","submitted","lastCorrect","confidence"):
                    assert after.get(field)==before.get(field),(field,after)
                exam.locator('[data-e-filter="pending"]').click()
                assert exam.locator("[data-e-review]:visible").count()==1
                exam.locator('[data-e-review="em-test-design"]').click()
                for criterion in exam.locator("[data-p-rubric]").all():
                    criterion.check()
                exam.locator("[data-e-back]").click()
                assert exam.locator("[data-e-review]:visible").count()==0
                exam.locator('[data-e-filter="wrong"]').click()
                assert exam.locator("[data-e-review]:visible").count()==1
                page.screenshot(path=str(OUT/("practice-exam-filter-"+name+".png")))
                exam.locator('[data-e-review="em-start"]').click()
                assert exam.locator(".practice-feedback").count()==1
                assert exam.locator(".practice-answer-line").count()==1
                assert exam.locator('[name="p-answer"][value="0"]').is_checked()
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),("exam",width)
                page.screenshot(path=str(OUT/("practice-exam-review-"+name+".png")))
                exam.locator("[data-e-back]").click()
                exam.locator('[data-e-filter="skipped"]').click()
                assert exam.locator("[data-e-review]:visible").count()==8
                exam.locator('[data-e-review="em-load"]').click()
                assert exam.locator(".practice-feedback").count()==1
                page.locator("[data-practice-mode=sources]").click()
                assert page.locator('[data-source-id="mit-machines-ps1"]').count()==1
                page.locator("[data-practice-mode=local]").click()
                panel.locator("[data-p-question]").select_option("em-load")
                correct_id=page.evaluate("LN_PRACTICE_BANK.questions.find(q=>q.id==='em-load').answer[0]")
                panel.locator('[name="p-answer"][value="'+correct_id+'"]').check()
                panel.locator("[data-p-submit]").click()
                assert page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-load'].attempts[0].assisted")
                page.reload(wait_until="domcontentloaded")
                page.locator("[data-practice-mode=exam]").click()
                exam.locator(".practice-exam-review").wait_for()
                assert page.evaluate("JSON.parse(localStorage.getItem('ln.practice.v1'))['em-start'].attempts.length")==len(after["attempts"])
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
                page.wait_for_timeout(220)
                # Verify cards are readable with the actual dark theme, not in a transition frame.
                dark_rgb=dialog.locator(".practice-choice").first.evaluate(
                    "(e) => getComputedStyle(e).backgroundColor.match(/\\d+/g).map(Number)")
                assert max(dark_rgb[:3])<150,(width,dark_rgb)
                page.screenshot(path=str(OUT/("practice-dialog-dark-"+name+".png")))
                dialog.locator("[data-practice-mode=exam]").click()
                assert dialog.locator("[data-e-start]").evaluate_all("(buttons)=>buttons.map(b=>b.dataset.eStart)")==["10","14"]
                dialog.locator('[data-e-start="10"]').click()
                dialog.locator('[data-e-finish]').click()
                assert dialog.locator(".practice-exam-confirm:modal").count()==1
                dialog.locator('[data-e-cancel]').click()
                assert dialog.count()==1
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
