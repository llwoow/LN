"""Browser regression: source definitions, semantic disambiguation and reading-position return."""
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 results=[]
 for width,height in [(1440,1000),(390,844),(320,568)]:
  context=b.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
  page=context.new_page();errors=[];bad=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
  def section(id):
   page.goto('http://127.0.0.1:4173/#course/electrical-machines/'+id)
   page.locator('#lesson-body[data-lesson-key="electrical-machines/'+id+'"][aria-busy="false"]').wait_for()
   page.evaluate('document.fonts.ready')
  section('magnetic-sec11')
  trigger=page.locator('[data-definition="symbol-magnetic-overview-1"]').first
  trigger.scroll_into_view_if_needed();y=page.evaluate('scrollY');triggerY=trigger.bounding_box()['y'];trigger.click()
  popup=page.locator('#definition-popover:popover-open');popup.wait_for()
  assert '磁通' in popup.inner_text() and 'Wb' in popup.inner_text()
  assert page.evaluate('scrollY')==y,'Opening the popup changed reading position'
  box=popup.bounding_box();assert box['x']>=0 and box['x']+box['width']<=width and box['y']>=0 and box['y']+box['height']<=height,box
  page.screenshot(path='.preview/definition-symbol-'+str(width)+'.png')
  page.locator('.definition-source-link').click()
  page.locator('.reference-target[data-definition-source]').wait_for()
  assert 'magnetic-overview/' in page.url
  page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
  assert abs(page.locator('[data-definition="symbol-magnetic-overview-1"]').first.bounding_box()['y']-triggerY)<3
  # Bold magnetization M must not be confused with scalar mutual inductance M.
  assert page.locator('[data-definition="magnetization"]').count()>0
  page.locator('[data-definition="magnetization"]').first.click()
  assert '磁化强度' in popup.inner_text()
  page.locator('.definition-close').click()
  # Keyboard-accessible expression list preserves the accessible mathematical expression.
  tool=page.locator('.definition-formula-tool').first;tool.focus();page.keyboard.press('Enter')
  assert popup.locator('.definition-choice').count()>0
  popup.locator('.definition-choice').first.click();assert page.locator('.definition-source-link').is_visible()
  page.keyboard.press('Escape');page.wait_for_function('!document.querySelector("#definition-popover").matches(":popover-open")')
  section('transformer-9')
  ct=page.locator('a.definition-term[data-definition="ct"]').first
  ct.click();assert 'Current Transformer' in popup.inner_text() and '二次不应开路' in popup.inner_text()
  page.screenshot(path='.preview/definition-term-'+str(width)+'.png')
  page.locator('.definition-close').click()
  vt=page.locator('a.definition-term[data-definition="vt"]').first;vt.click()
  assert 'Voltage Transformer' in popup.inner_text() and '二次不应短路' in popup.inner_text()
  page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for()
  page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
  # Chapter-specific definitions resolve identical symbols correctly.
  resolved=page.evaluate('''()=>{
   const c=window.LN_COURSES[0],t=c.sections.find(s=>s.id==='transformer-3'),d=c.sections.find(s=>s.id==='dc-sec35');
   return {transformer:window.LNGlossary.resolveSymbol(c,t,'a').description,dc:window.LNGlossary.resolveSymbol(c,d,'a').description,omegaT:window.LNGlossary.resolveSymbol(c,t,'ω').description,omegaD:window.LNGlossary.resolveSymbol(c,d,'ω').description};
  }''')
  assert '匝数比' in resolved['transformer'] and '支路对数' in resolved['dc']
  assert '电角频率' in resolved['omegaT'] and '机械角速度' in resolved['omegaD']
  section('dc-sec35')
  compound=page.locator('[data-definition="symbol-dc-overview-2"]').first;compound.click()
  assert '电枢电流' in popup.inner_text()
  page.locator('.definition-close').click()
  page.locator('#quick-theme').click();compound.click()
  page.screenshot(path='.preview/definition-dark-'+str(width)+'.png')
  page.locator('.definition-close').click()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.locator('.course-view-nav a',has_text='知识图谱').click()
  assert page.locator('#definition-popover').is_hidden()
  assert not errors,errors
  assert not bad,bad
  results.append({'width':width,'passed':True});context.close()
 print(json.dumps({'viewports':results,'checks':['source-backed symbol popup','units and conditions','no reading-position change','link to exact original definition','return to origin','bold M vs scalar M','keyboard and formula symbol list','Escape and close','CT/VT expansions and conditions','chapter-scoped a and omega','compound armature-current symbol','dark mode','320px popup bounds','no browser errors']}))
 b.close()
