"""Run with the local server on :4173 and system Chromium / Python Playwright."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:4173/'
Path('.preview').mkdir(exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    page=context.new_page();errors=[];bad=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
    page.on('request',lambda r:requests.append(r.url))
    page.goto(BASE);page.locator('#course-list .course-row').first.wait_for()
    assert page.locator('#course-list .course-row').count()==1
    assert page.locator('#sidebar-course-list [href^="#course/hs-"]').count()==0
    assert not any('/hs-' in url and 'glossary-index.js' in url for url in requests)
    page.screenshot(path='.preview/highschool-home-final.png')
    page.locator('.highschool-entry').click();page.locator('#page-title',has_text='高中').wait_for()
    assert page.locator('#course-list .course-row').count()==9
    page.get_by_role('button',name='语言',exact=True).click();assert page.locator('#course-list .course-row').count()==2
    page.get_by_role('button',name='数理化生',exact=True).click();assert page.locator('#course-list .course-row').count()==4
    page.get_by_role('button',name='政史地',exact=True).click();assert page.locator('#course-list .course-row').count()==3
    page.get_by_role('button',name='全部',exact=True).click()
    page.locator('#course-search').fill('海水');assert page.locator('#course-list a[href="#course/hs-chemistry"]').count()==1
    page.locator('#course-search').fill('');page.screenshot(path='.preview/highschool-library-desktop-final.png')
    courses=page.evaluate('LN_COURSES.filter(c=>c.level==="highschool")')
    def lesson(course,section):
        page.evaluate('(s)=>location.hash=s','#course/'+course+'/'+section)
        page.locator('#lesson-body[data-lesson-key="'+course+'/'+section+'"][aria-busy="false"]').wait_for()
    for course in courses:
        page.evaluate('(id)=>location.hash="#course/"+id+"/map"',course['id'])
        page.locator('ln-knowledge-map .map-canvas').wait_for()
        assert page.evaluate('document.querySelector("ln-knowledge-map").group')==0
        positions=page.evaluate('[...document.querySelector("ln-knowledge-map").nodes].map(n=>[n.x,n.y])')
        canvas=page.locator('.map-canvas');box=canvas.bounding_box()
        page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.mouse.move(box['x']+box['width']/2+40,box['y']+box['height']/2+30,steps=4);page.mouse.up()
        assert positions==page.evaluate('[...document.querySelector("ln-knowledge-map").nodes].map(n=>[n.x,n.y])')
        if course['id']=='hs-physics':page.screenshot(path='.preview/highschool-physics-map.png')
    smoke=[]
    for course in courses:
        for section in course['sections']:
            lesson(course['id'],section['id'])
            assert page.locator('#lesson-body h2').first.inner_text()==section['title']
            assert '课程加载失败' not in page.locator('#lesson-body').inner_text()
            assert page.locator('#reader-dock').is_visible()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(course['id'],section['id'])
            entries=page.evaluate('(id)=>LN_GLOSSARY[id].entries',course['id'])
            for entry in [e for e in entries if e['source']['section']==section['id']]:
                assert page.locator('[id="'+entry['source']['anchor']+'"]').count(),entry['id']
            smoke.append(course['id']+'/'+section['id'])
        # At least one working definition and its exact source/return in each subject.
        lesson(course['id'],course['sections'][0]['id'])
        trigger=page.locator('#lesson-body [data-definition]:visible').first
        assert trigger.count(),course['id']
        trigger.scroll_into_view_if_needed();trigger_id=trigger.get_attribute('id');y=trigger.bounding_box()['y'];trigger.click()
        popup=page.locator('#definition-popover:popover-open');popup.wait_for()
        assert page.locator('.definition-source-link').is_visible()
        page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for()
        page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
        assert abs(page.locator('[id="'+trigger_id+'"]').bounding_box()['y']-y)<3,course['id']
    # Difference/average marks retain their meaning and sources inside disclosures open.
    lesson('hs-physics','wl-01-k01')
    definitions=page.evaluate("LN_GLOSSARY['hs-physics'].entries")
    for key in ['bar:v','delta:x','delta:t']:
        entry=next(e for e in definitions if key in e.get('keys',[]))
        page.locator('[data-definition="'+entry['id']+'"]:visible').first.click()
        assert entry['description'] in page.locator('#definition-popover:popover-open').inner_text()
        page.locator('.definition-source-link').click();page.locator('.study-symbols[open] .reference-target').wait_for()
        page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
    reference=page.locator('a.paper-reference',has_text='1.1.1').first
    reference.click();page.locator('.paper-target-label.is-reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
    lesson('hs-chemistry','hx-03-k01')
    entry=next(e for e in page.evaluate("LN_GLOSSARY['hs-chemistry'].entries") if 'delta:H' in e.get('keys',[]))
    assert 'H' not in entry['keys']
    page.locator('[data-definition="'+entry['id']+'"]:visible').first.click()
    assert '反应焓变' in page.locator('#definition-popover:popover-open').inner_text()
    page.locator('.definition-close').click()
    page.evaluate('location.hash="#highschool/resources"');page.locator('h1',has_text='教材与来源').wait_for()
    assert page.locator('a[href$="hainan-2027-report.pdf"]').count()==1
    assert page.locator('a[href$="hainan-2027-index.xlsx"]').count()==1
    assert page.request.get(BASE+'courses/highschool/assets/hainan-2027-report.pdf').status==200
    assert page.request.get(BASE+'courses/highschool/assets/hainan-2027-index.xlsx').status==200
    assert page.locator('details',has=page.locator('summary',has_text='外研英语')).count()==1
    page.screenshot(path='.preview/highschool-resources-desktop.png')
    assert not errors,errors
    assert not bad,bad
    context.close()
    mobile=[]
    for width,height in [(390,844),(320,568)]:
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'#highschool');page.locator('#course-list .course-row').first.wait_for()
        assert page.locator('#course-list .course-row').count()==9
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        page.screenshot(path='.preview/highschool-library-'+str(width)+'.png')
        for course in courses:
            lesson(course['id'],course['sections'][0]['id'])
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),course['id']
        lesson('hs-physics',courses[3]['sections'][0]['id'])
        trigger=page.locator('#lesson-body [data-definition]:visible').first;trigger.click()
        popup=page.locator('#definition-popover:popover-open');popup.wait_for();box=popup.bounding_box()
        assert box['x']>=0 and box['x']+box['width']<=width
        assert box['y']>=0 and box['y']+box['height']<=height-60
        page.screenshot(path='.preview/highschool-definition-'+str(width)+'.png')
        page.locator('.definition-close').click()
        page.locator('#quick-theme').click();page.screenshot(path='.preview/highschool-reader-dark-'+str(width)+'.png')
        page.locator('#reader-dock [data-reader-directory]').click();assert page.locator('#reader-directory').is_visible();page.keyboard.press('Escape')
        page.evaluate('location.hash="#highschool/resources"');page.locator('h1',has_text='教材与来源').wait_for();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        mobile.append(width);context.close()
    assert not errors,errors
    print(json.dumps({'lessons':len(smoke),'subjects':len(courses),'mobile':mobile,'checks':['quiet entry','main and extension filters','knowledge search','fixed map nodes','all lesson sources','per-course glossary loading','definition and exact return in nine subjects','fixed reading controls','report downloads','dark mode','no browser errors']},ensure_ascii=False))
    browser.close()
