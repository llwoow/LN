"""Exercise every primary explanation, including PDF/model pages, at reading widths."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

Path('.preview').mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    results=[]
    for width,height in [(1440,1000),(390,844),(320,568)]:
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page=context.new_page();errors=[];bad=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('response',lambda response:bad.append((response.status,response.url)) if response.status>=400 else None)
        page.goto('http://127.0.0.1:4173/')
        courses=page.evaluate('LN_COURSES')
        count=0
        for course in courses:
            for section in course['sections']:
                key=course['id']+'/'+section['id']
                page.evaluate('(key)=>location.hash="course/"+key',key)
                page.locator('#lesson-body[data-lesson-key="'+key+'"][aria-busy="false"]').wait_for()
                page.evaluate('document.fonts.ready')
                sequence=page.locator('.learning-sequence')
                assert sequence.count()==1,key
                assert sequence.locator('[data-learning-step]').count()==7,key
                assert sequence.locator('[data-learning-step="example"] > ol > li').count()>=3,key
                assert not sequence.locator('details,[hidden],.katex-error').count(),key
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,key)
                assert page.locator('#reader-dock').is_visible(),key
                assert not sequence.evaluate('e=>["[","("].some(c=>e.textContent.includes(String.fromCharCode(92)+c))'),key
                assert sequence.locator('.paper-equation.is-numbered').evaluate_all('(nodes)=>nodes.every(e=>Math.abs(e.getBoundingClientRect().right-e.querySelector(".equation-number").getBoundingClientRect().right)<2)'),key
                if key in ['electrical-machines/transformer-1','electrical-machines/dc-sec34','hs-math/sx-04-k02','hs-english/yy-07-k04']:
                    page.screenshot(path='.preview/understanding-'+section['id']+'-'+str(width)+'.png')
                count+=1
        assert count==288,count
        assert not errors,errors
        assert not bad,bad
        results.append({'width':width,'lessons':count});context.close()
    browser.close()
print(json.dumps({'visible_steps_and_examples':results,'checks':['all registered units','PDF and 3D introductions','no raw LaTeX','no horizontal page overflow','right-edge formula labels','fixed reading controls','no browser errors']}))
