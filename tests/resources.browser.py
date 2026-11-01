"""Resource discovery, honest execution scopes and real-specification model controls."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'courses/resources/catalog.json').read_text())
resources=data['resources'];baseline=json.loads((ROOT/'assets/practice/dc-specs/results.json').read_text())
Path('.preview').mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    checks=[]
    for width,height in [(1440,1000),(390,844),(320,568)]:
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page=context.new_page();errors=[];bad=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
        page.goto('http://127.0.0.1:4173/#resources')
        page.locator('[data-resource-results] .resource-entry').first.wait_for()
        assert page.locator('[data-resource-results] > .resource-entry').count()==len(resources)
        page.locator('[data-resource-code-only]').check()
        assert page.locator('[data-resource-results] > .resource-entry').count()==sum(bool(r['repository']) for r in resources)
        page.locator('[data-resource-code-only]').uncheck();page.locator('[data-resource-run-only]').check()
        assert page.locator('[data-resource-results] > .resource-entry').count()==sum(r['verification']['executed'] for r in resources)
        page.locator('[data-resource-run-only]').uncheck()
        courses=page.evaluate('LN_COURSES')
        for course in courses:
            page.locator('[data-resource-course-filter]').select_option(course['id'])
            assert page.locator('[data-resource-results] > .resource-entry').count()==sum(any(t['course']==course['id'] for t in r['targets']) for r in resources)
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,course['id'])
        page.locator('[data-resource-course-filter]').select_option('')
        page.locator('[data-resource-query]').fill('OpenMCT')
        entry=page.locator('[data-resource-id="openmct-measured-data"]');entry.locator(':scope > summary').click()
        assert '未运行' in entry.locator(':scope > summary').inner_text()
        assert '403' in entry.inner_text()
        page.screenshot(path='.preview/resources-disclosure-'+str(width)+'.png')

        page.goto('http://127.0.0.1:4173/#course/electrical-machines/dc-sec35/real-specification-lab')
        body=page.locator('#lesson-body[aria-busy="false"]');body.wait_for()
        page.locator('[data-dc-results]').wait_for()
        assert '+7.55%' in page.locator('[data-dc-results]').inner_text()
        actual=page.evaluate('LNResources.motorSteady(LN_RESOURCE_CATALOG.motorSpecification.nominal_torque_Nm)')
        assert abs(actual['rpm']-baseline['constant_friction_baseline_prediction']['rpm'])<1e-8
        page.locator('[data-dc-fit]').check()
        assert '+3.78%' in page.locator('[data-dc-results]').inner_text()
        actual=page.evaluate('LNResources.motorSteady(LN_RESOURCE_CATALOG.motorSpecification.nominal_torque_Nm,1,1,true)')
        assert abs(actual['rpm']-baseline['offset_calibrated_at_no_load_prediction']['rpm'])<1e-8
        assert page.locator('#real-specification-plot svg').count()==1
        assert page.locator('#real-specification-plot .paper-target-label').count()==1
        page.locator('[data-dc-r]').evaluate('(e)=>{e.value="1.2";e.dispatchEvent(new Event("input",{bubbles:true}));}')
        assert '+3.78%' not in page.locator('[data-dc-results]').inner_text()
        page.locator('[data-dc-reset]').click();assert '+7.55%' in page.locator('[data-dc-results]').inner_text()
        page.locator('[data-dc-results]').scroll_into_view_if_needed();page.evaluate('document.fonts.ready')
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        page.screenshot(path='.preview/motor-catalogue-'+str(width)+'.png')

        # Access from the fixed directory, then return without losing the reading position.
        position=page.evaluate('scrollY')
        page.locator('#reader-dock [data-reader-directory]').click()
        page.locator('#reader-directory-resource [data-open-resources]').click()
        page.locator('#resource-dialog[open]').wait_for()
        assert not page.locator('#reader-directory').is_visible()
        assert page.locator('#resource-dialog [data-resource-id="python-control"]').count()==1
        box=page.locator('#resource-dialog').bounding_box()
        assert box['x']>=0 and box['x']+box['width']<=width+1
        assert box['height']<=height
        page.screenshot(path='.preview/resources-reading-'+str(width)+'.png')
        page.keyboard.press('Escape');page.wait_for_function('!document.querySelector("#resource-dialog").open&&!document.body.classList.contains("resource-open")')
        assert abs(page.evaluate('scrollY')-position)<3
        assert page.locator('#reader-dock [data-reader-directory]').evaluate('e=>document.activeElement===e')
        for resource in resources:
            for download in resource['downloads']:
                assert page.request.get('http://127.0.0.1:4173/'+download['path']).status==200,download
        page.locator('#quick-theme').click()
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        assert not errors,errors
        assert not bad,bad
        checks.append(width);context.close()
    browser.close()
print(json.dumps({'viewports':checks,'resources':len(resources),'checks':['all ten course mappings','GitHub and execution filters','unrun/403 disclosure','manufacturer vs simulation residuals','calibration is not validation','responsive figure','fixed-directory access and exact return','all local artifacts','no browser errors']},ensure_ascii=False))
