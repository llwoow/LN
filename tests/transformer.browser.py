"""Read all fourteen textbook units and exercise local symbols and practice access."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in [1440,390,320]:
        context=b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
        page=context.new_page();errors=[];bad=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
        for i in range(1,15):
            id='transformer-sec2'+str(i)
            page.goto('http://127.0.0.1:4173/#course/electrical-machines/'+id)
            page.locator('#lesson-body[data-lesson-key="electrical-machines/'+id+'"][aria-busy="false"]').wait_for()
            page.evaluate('document.fonts.ready')
            assert page.locator('.learning-sequence [data-learning-step]').count()==7
            assert not page.locator('.learning-sequence .katex-error').count()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,id)
            assert page.locator('.paper-equation.is-numbered').evaluate_all('(els)=>els.every(e=>Math.abs(e.getBoundingClientRect().right-e.querySelector(".equation-number").getBoundingClientRect().right)<2)')
            if i<14:assert 'transformer-sec2'+str(i+1) in page.locator('#lesson-pagination a').last.get_attribute('href')
            else:assert 'dc-overview' in page.locator('#lesson-pagination a').last.get_attribute('href')
            assert not page.locator('#reader-outline .outline-references').evaluate('e=>e.open')
            if i in [1,4,10]:page.screenshot(path='.preview/transformer-'+str(i)+'-'+str(width)+'.png')
        page.goto('http://127.0.0.1:4173/#course/electrical-machines/transformer-sec210')
        page.locator('#lesson-body[aria-busy="false"]').wait_for()
        symbol=page.locator('.definition-symbol[data-definition="tang5-10-sequences"]').first
        symbol.scroll_into_view_if_needed();position=page.evaluate('scrollY');symbol.click(force=True)
        page.locator('#definition-popover:popover-open').wait_for()
        assert '零序' in page.locator('#definition-popover').inner_text()
        assert abs(page.evaluate('scrollY')-position)<3
        page.keyboard.press('Escape')
        page.locator('#reader-dock [data-reader-directory]').click()
        page.locator('#reader-directory [data-open-practice]').click()
        page.locator('#practice-dialog [data-practice-mode="local"]').click()
        assert '本节关联练习' in page.locator('#practice-dialog [data-p-scope]').inner_text()
        assert page.locator('#practice-dialog [data-p-question] option').count()>=1
        page.keyboard.press('Escape');assert abs(page.evaluate('scrollY')-position)<3
        page.goto('http://127.0.0.1:4173/#course/electrical-machines/transformer-9')
        page.locator('#lesson-body[aria-busy="false"]').wait_for()
        assert page.locator('#reader-outline .outline-references').evaluate('e=>e.open')
        assert page.locator('.paper-reference[href*="basechange"]').count()==1
        page.evaluate('document.documentElement.dataset.theme="dark"')
        assert not errors,errors
        assert not bad,bad
        context.close()
    b.close()
print(json.dumps({'sections':14,'widths':[1440,390,320],'checks':['complete mainline and old references','rendered equations and diagrams','local sequence-current popup','exact reading return','chapter practice','no overflow or request errors']}))
