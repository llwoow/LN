"""Exercise genuine answers, assisted attempts, saved drafts and reading return."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
questions=json.loads((ROOT/'courses/practice/bank.json').read_text())['questions']
Path('.preview').mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in [1440,390,320]:
        context=browser.new_context(viewport={'width':width,'height':900})
        page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8765/#practice/electrical-machines')
        assert page.locator('[data-practice-mode="sources"]').get_attribute('aria-pressed')=='true'
        page.locator('[data-practice-mode="local"]').click()
        panel=page.locator('main [data-practice-panel]')
        panel.locator('[data-p-submit]').click();assert panel.locator('[data-p-error]').inner_text()
        # A confident incorrect first attempt is retained after a correct retry.
        panel.locator('[data-p-confidence]').select_option('sure')
        panel.locator('[name="p-answer"][value="0"]').check();panel.locator('[data-p-submit]').click()
        assert '尚不吻合' in panel.locator('.practice-feedback h3').inner_text()
        panel.locator('[name="p-answer"][value="1"]').check();panel.locator('[data-p-submit]').click()
        r=page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["em-start"]')
        assert r['attempts'][0]['correct'] is False and r['attempts'][1]['assisted'] is True
        panel.locator('[data-p-review]').check();assert '自信误判' in panel.locator('[data-p-question]').inner_text()
        panel.locator('[data-p-review]').uncheck()
        panel.locator('[data-p-favorite]').click()
        page.locator('[data-practice-mode="favorites"]').click()
        assert page.locator('[data-p-question] option').count()==1
        page.locator('[data-p-redo]').click()
        assert page.locator('.practice-feedback').count()==0
        page.locator('[name="p-answer"][value="1"]').check();page.locator('[data-p-submit]').click()
        page.locator('[data-practice-mode="mistakes"]').click()
        assert page.locator('[data-p-question] option').count()==1
        page.locator('[data-practice-mode="local"]').click()
        panel=page.locator('main [data-practice-panel]')
        # Every authored question is answerable with its exact target and feedback.
        for q in questions:
            panel.locator('[data-p-course]').select_option(q['course'])
            panel.locator('[data-p-question]').select_option(q['id'])
            assert panel.locator('.practice-feedback').count()==(1 if q['id']=='em-start' else 0)
            if q['type'] in ('single','multi'):
                for option in q['answer']:panel.locator('[name="p-answer"][value="'+option+'"]').check()
            elif q['type']=='numeric':
                for invalid in ['', '12abc', 'Infinity']:
                    panel.locator('[data-p-value]').fill(invalid);panel.locator('[data-p-submit]').click()
                    assert panel.locator('[data-p-error]').inner_text()
                panel.locator('[data-p-value]').fill(str(q['answer']))
                panel.locator('[data-p-reason]').fill('先建立约束，再检查单位与守恒。')
            else:
                panel.locator('[data-p-submit]').click();assert panel.locator('[data-p-error]').inner_text()
                panel.locator('[data-p-reason]').fill('区分已给观察、假设与竞争解释，并提出可检验的新证据。')
            panel.locator('[data-p-submit]').click()
            assert panel.locator('.practice-feedback').count()==1
            if q['type']!='open':assert '吻合' in panel.locator('.practice-feedback h3').inner_text() and '尚不吻合' not in panel.locator('.practice-feedback h3').inner_text()
            else:
                assert '逐项自评' in panel.locator('.practice-feedback h3').inner_text()
                panel.locator('[data-p-rubric]').first.check()
            assert panel.locator('.practice-feedback ol li').count()>=3
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,q['id'])
        # Selection order, drafts and self-check survive reload without changing the result.
        before=page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["hi-change"]')
        page.reload();page.locator('[data-practice-mode="local"]').click();panel=page.locator('main [data-practice-panel]')
        panel.locator('[data-p-course]').select_option('hs-history');panel.locator('[data-p-question]').select_option('hi-change')
        assert panel.locator('[data-p-reason]').input_value()==before['reason']
        assert panel.locator('[data-p-rubric]:checked').count()==1
        # Filter by kind and capability rather than awarding a fake mastery score.
        panel.locator('[data-p-type]').select_option('open');panel.locator('[data-p-skill]').select_option('迁移设计')
        assert panel.locator('[data-p-question] option').count()>0
        # Hints/direct reference analysis do not create independent first-answer evidence.
        page.goto('http://127.0.0.1:8765/#practice/hs-math');page.evaluate('localStorage.removeItem("ln.practice.v1")');page.reload();page.locator('[data-practice-mode="local"]').click()
        panel=page.locator('main [data-practice-panel]');panel.locator('[data-p-hint]').click()
        panel.locator('[name="p-answer"][value="1"]').check();panel.locator('[data-p-submit]').click()
        assert page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["ma-logic"].attempts[0].assisted')
        panel.locator('[data-p-question]').select_option('ma-domain');panel.locator('[data-p-reveal]').click()
        panel.locator('[name="p-answer"][value="1"]').check();panel.locator('[data-p-submit]').click()
        assert page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["ma-domain"].attempts[0].assisted')
        page.screenshot(path='.preview/practice-'+str(width)+'.png')
        page.locator('[data-practice-mode="sources"]').click()
        page.locator('[data-source-course]').select_option('electrical-machines')
        entry=page.locator('[data-source-id="mit-machines-ps1"]')
        entry.locator('[data-source-save="mistake"]').click()
        assert '先填写' in entry.locator('[data-source-status]').inner_text()
        entry.locator('[data-source-ref]').fill('Problem 1')
        entry.locator('[data-source-note]').fill('有限厚度的磁链平均还需重推。')
        entry.locator('[data-source-save="mistake"]').click()
        entry.locator('[data-source-save="favorite"]').click()
        page.locator('[data-practice-mode="mistakes"]').click()
        assert 'Problem 1' in page.locator('.external-review h4').inner_text()
        assert page.locator('.external-review a[href^="#course/"]').count()>=1
        page.locator('[data-external-review]').click()
        assert '已手动标记复习' in page.locator('.external-review').inner_text()
        page.locator('[data-practice-mode="favorites"]').click()
        assert page.locator('.external-review').count()==1
        page.reload();page.locator('[data-practice-mode="favorites"]').click()
        page.locator('[data-source-course]').select_option('electrical-machines')
        assert '有限厚度' in page.locator('.external-review').inner_text()
        page.locator('[data-practice-mode="sources"]').click()
        page.screenshot(path='.preview/practice-sources-'+str(width)+'.png')
        # Open from a fixed reading action, then return to the exact scroll and focus.
        page.goto('http://127.0.0.1:8765/#course/electrical-machines/dc-sec35')
        page.wait_for_selector('#lesson-body[aria-busy="false"]')
        page.evaluate('scrollTo(0,1400)');position=page.evaluate('scrollY')
        page.locator('#reader-dock [data-reader-directory]').click()
        page.locator('#reader-directory [data-open-practice]').click()
        page.locator('#practice-dialog[open]').wait_for()
        assert not page.locator('#reader-directory').is_visible()
        page.locator('#practice-dialog [data-practice-mode="local"]').click()
        assert '本节关联练习' in page.locator('#practice-dialog [data-p-scope]').inner_text()
        box=page.locator('#practice-dialog').bounding_box();assert box['x']>=0 and box['x']+box['width']<=width+1
        page.evaluate('document.documentElement.dataset.theme="dark"')
        page.screenshot(path='.preview/practice-dialog-'+str(width)+'.png')
        page.keyboard.press('Escape');assert abs(page.evaluate('scrollY')-position)<3
        assert page.locator('#reader-dock [data-reader-directory]').evaluate('e=>e===document.activeElement')
        assert not errors,errors
        context.close()
    browser.close()
print(json.dumps({'questions':len(questions),'widths':[1440,390,320],'checks':['choice/multiselect/numeric/open feedback','all answer keys','invalid and blank responses','first answer retained','assisted attempts excluded','drafts and self-check persistence','filters','real reading links','modal exact return','no overflow or browser errors']}))
