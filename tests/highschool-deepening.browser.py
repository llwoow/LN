"""Worked reasoning, learning-path navigation and cross-lesson definition return."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
targets=[]
for slug in ['math','physics','chemistry','biology']:
    authored=json.loads((ROOT/'courses'/('hs-'+slug)/'content.json').read_text())
    for lesson in authored['lessons']:
        for example in lesson.get('workedExamples',[]):targets.append(('hs-'+slug,lesson['id'].lower(),example))
assert len(targets)==16,'All sixteen reviewed examples must be present before this regression runs.'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width,height in [(1440,1000),(390,844),(320,568)]:
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page=context.new_page();errors=[];bad=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
        page.goto('http://127.0.0.1:4173/#course/hs-physics/map');page.locator('.map-canvas').wait_for()
        positions=page.evaluate('document.querySelector("ln-knowledge-map").nodes.map(n=>[n.x,n.y])')
        page.locator('.map-study-paths > summary').click()
        assert page.locator('.map-path-list > section').count()==3
        assert page.locator('.map-path-list li').count()>=10
        assert positions==page.evaluate('document.querySelector("ln-knowledge-map").nodes.map(n=>[n.x,n.y])')
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        page.screenshot(path='.preview/highschool-pathways-'+str(width)+'.png')
        first=page.locator('.map-path-list a').first;destination=first.get_attribute('href');first.click()
        page.locator('#lesson-body[aria-busy="false"]').wait_for();assert page.url.endswith(destination)
        assert page.locator('.study-pathways').count()>0
        def lesson(course,section):
            page.evaluate('(hash)=>location.hash=hash','#course/'+course+'/'+section)
            page.locator('#lesson-body[data-lesson-key="'+course+'/'+section+'"][aria-busy="false"]').wait_for()
            page.evaluate('document.fonts.ready')
        # The visible occurrence now points back to its definition in an earlier book.
        for course,section,source,title in [
            ('hs-biology','sw-02-k04','sw-01-k02','DNA'),
            ('hs-biology','sw-01-k04','sw-01-k05','ATP'),
            ('hs-chemistry','hx-05-k01','hx-02-k03','官能团'),
            ('hs-math','sx-02-k05','sx-05-k02','条件概率'),
            ('hs-geography','dl-01-k06','dl-01-k06','GIS'),
            ('hs-geography','dl-02-k04','dl-01-k06','GIS')]:
            lesson(course,section)
            entry=page.evaluate('([course,title])=>LN_GLOSSARY[course].entries.find(e=>e.kind==="term"&&e.title===title)',[course,title])
            if not page.locator('a.definition-term[data-definition="'+entry['id']+'"]:visible').count():
                page.locator('#lesson-body .study-answer').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=true)')
            trigger=page.locator('a.definition-term[data-definition="'+entry['id']+'"]:visible').first
            assert trigger.count(),(course,title)
            trigger.scroll_into_view_if_needed();origin_id=trigger.get_attribute('id');y=trigger.bounding_box()['y'];trigger.click()
            popup=page.locator('#definition-popover:popover-open');popup.wait_for();assert title in popup.inner_text()
            if title=='GIS':
                assert 'Geographic Information System' in popup.inner_text()
                assert '地理信息系统' in popup.inner_text()
            assert page.evaluate('scrollY')>=0
            page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for()
            assert '/'+source+'/' in page.url
            page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
            page.locator('#lesson-body[data-lesson-key="'+course+'/'+section+'"][aria-busy="false"]').wait_for()
            page.wait_for_function('(id)=>document.activeElement?.id===id',arg=origin_id)
            assert '/'+section in page.url
            assert abs(page.locator('[id="'+origin_id+'"]').bounding_box()['y']-y)<3,(course,title)
        lesson('hs-physics','wl-05-k03')
        assert '方向随时间周期性反向' in page.locator('#lesson-body').inner_text()
        assert '方向或大小随时间作周期变化' not in page.locator('#lesson-body').inner_text()
        page.locator('a.definition-term',has_text='有效值').first.click()
        page.locator('#definition-popover .definition-excerpt > summary').click()
        assert '脉动直流' in page.locator('#definition-popover .definition-copy').last.inner_text()
        page.locator('.definition-close').click()
        for course,section,example in targets:
            lesson(course,section)
            block=page.locator('[data-worked-example="'+example['id']+'"]')
            assert block.count()==1
            assert block.locator('.worked-solution').get_attribute('open') is None
            block.locator('.worked-solution > summary').click()
            assert block.locator('.worked-steps > li').count()==len(example['steps'])
            if example['id']=='oblique-pull-two-stages':
                pull=block.locator('.worked-solution [data-definition="wl-01-k04-applied-pull"]').first
                pull.scroll_into_view_if_needed();pull_id=pull.get_attribute('id');offset=pull.bounding_box()['y'];pull.click()
                popup=page.locator('#definition-popover:popover-open')
                assert '外加拉力的大小，给定为8.0 N' in popup.inner_text()
                assert 'Fpull' in popup.locator('.definition-symbol-title').inner_text()
                page.locator('.definition-source-link').click()
                page.locator('.reference-target[data-definition-source]').wait_for()
                page.locator('.reference-return').click()
                # A visual KaTeX glyph is a pointer target, not a keyboard tab stop.
                page.locator('[id="'+pull_id+'"].reference-origin').wait_for()
                assert abs(page.locator('[id="'+pull_id+'"]').bounding_box()['y']-offset)<3
                assert block.locator('.worked-solution').get_attribute('open') is not None
            assert block.locator('.worked-solution h4',has_text='结果与核查').is_visible()
            assert block.locator('.worked-solution h4',has_text='易错点').is_visible()
            assert '\\(' not in block.inner_text() and '\\[' not in block.inner_text()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,course,section)
            assert block.evaluate('e=>[...e.querySelectorAll(".paper-equation")].every(n=>{const label=n.querySelector(".paper-target-label");return !label||Math.abs(label.getBoundingClientRect().right-n.getBoundingClientRect().right)<3})'),(course,section)
            block.locator(':scope > .study-answer > summary').click()
            block.locator(':scope > .study-answer details > summary').click()
            assert block.locator(':scope > .study-answer details').get_attribute('open') is not None
            if course=='hs-physics' and section=='wl-05-k02':
                block.scroll_into_view_if_needed();page.screenshot(path='.preview/highschool-worked-'+str(width)+'.png')
        assert not errors,errors
        assert not bad,bad
        context.close()
    browser.close()
print('Sixteen worked examples, fixed-node learning paths and reviewed cross-lesson definitions passed at 1440/390/320px.')
