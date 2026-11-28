"""Exercise actual built static app at the Pages base path with synthetic records."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import tempfile, threading, os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
def main():
    with tempfile.TemporaryDirectory() as temp:
        os.symlink(ROOT/'dist', Path(temp)/'LN', target_is_directory=True)
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=temp))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_port}/LN/'
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1280,'height':900})
                errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('dialog',lambda dialog:dialog.accept())
                page.goto(base+'#course/electromagnetic-compatibility/exam-review/test-a')
                page.locator('#emc-test-Q30').wait_for()
                page.locator('#emc-test-Q01 input[data-choice="0"]').check()
                page.locator('[data-action="submit"]').click()
                page.locator('.emc-test-feedback').first.wait_for()
                read="JSON.parse(localStorage.getItem('ln.practice.v1')).paperItems"
                assert page.evaluate(read+"['emc-ch1-A-Q01'].mistake")
                assert page.evaluate("Object.keys("+read+").length")==1
                page.reload()
                page.locator('.emc-test-feedback').first.wait_for()
                assert page.evaluate(read+"['emc-ch1-A-Q01'].attempts.length")==1
                page.locator('[data-action="reset"]').click()
                assert page.evaluate(read+"['emc-ch1-A-Q01'].attempts.length")==1
                page.goto(base+'#practice/electromagnetic-compatibility/mistakes')
                page.locator('[data-paper-record="emc-ch1-A-Q01"]').wait_for()
                page.locator('[data-paper-record="emc-ch1-A-Q01"] a').first.click()
                page.locator('#emc-test-Q01').wait_for()
                assert page.locator('.emc-test-question').count()==1
                assert page.locator('.emc-test-feedback').count()==0
                page.locator('#emc-test-Q01 input[data-choice="1"]').check()
                page.locator('[data-action="submit"]').click()
                assert page.evaluate(read+"['emc-ch1-A-Q01'].attempts.length")==2
                assert page.evaluate(read+"['emc-ch1-A-Q01'].mistake && "+read+"['emc-ch1-A-Q01'].reviewed")
                page.goto(base+'#course/electromagnetic-compatibility/exam-review/test-b2')
                page.locator('#emc-test-Q12').wait_for()
                page.locator('#emc-test-Q01 textarea').first.fill('test fixture')
                page.locator('[data-action="submit"]').click()
                assert not page.evaluate(read+"['emc-ch1-B2-Q01'].mistake")
                for i in range(3): page.locator(f'[data-mark="Q01-{i}"]').fill('0')
                assert page.evaluate(read+"['emc-ch1-B2-Q01'].mistake")
                page.locator('#ln-print-open').click()
                page.locator('[data-build]').click()
                page.locator('[data-print]:enabled').wait_for(timeout=30000)
                frame=page.frame_locator('[data-preview]')
                assert frame.locator('.ln-print-question').count()==12
                assert frame.get_by_text('参考答案与评分',exact=True).count()==0
                assert frame.locator('.ln-answer-space').count()>12
                page.locator('[data-mode]').select_option('combined')
                page.locator('[data-build]').click()
                page.locator('[data-print]:enabled').wait_for(timeout=30000)
                assert frame.locator('.ln-print-question').count()==24
                assert frame.get_by_text('参考答案与评分细则',exact=True).count()==1
                page.locator('[data-close]').click()
                page.goto(base+'#course/electromagnetic-compatibility/emc-3-1')
                page.locator('#lesson-body[data-print-ready="yes"]').wait_for()
                page.locator('#ln-print-open').click()
                page.locator('[data-build]').click()
                page.locator('[data-print]:enabled').wait_for(timeout=120000)
                frame=page.frame_locator('[data-preview]')
                assert frame.locator('.ln-print-unit').count()==4
                assert frame.locator('.ln-print-unit svg').count()>3
                assert frame.locator('.ln-print-unit input').count()==0
                assert frame.locator('.ln-print-unit .emc-lab-result').count()>3
                page.locator('[data-close]').click()
                page.set_viewport_size({'width':390,'height':844})
                page.locator('#ln-print-open').click()
                assert page.locator('.ln-print-dialog').evaluate('(e)=>e.getBoundingClientRect().width <= innerWidth')
                page.locator('[data-close]').click()
                assert not errors,errors
                browser.close()
        finally:
            server.shutdown();server.server_close()
    print('Unified EMC records, blank / combined paper, four-section export and mobile dialog verified.')
if __name__=='__main__':main()
