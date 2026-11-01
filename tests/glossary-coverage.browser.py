"""Source coverage, local notation scopes and direct clicks on complex KaTeX symbols."""
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1440,1000),(390,844),(320,568)]:
  page=b.new_page(viewport={'width':width,'height':height},reduced_motion='reduce');errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def section(s):
   page.goto('http://127.0.0.1:4173/#course/electrical-machines/'+s)
   page.locator('#lesson-body[data-lesson-key="electrical-machines/'+s+'"][aria-busy="false"]').wait_for();page.evaluate('document.fonts.ready')
  popup=page.locator('#definition-popover:popover-open')
  section('transformer-3')
  for id,expected in [('transformer-current-ports','一次电流'),('transformer-referred-current','除以匝数比'),('transformer-induced-voltage','感应电压')]:
   trigger=page.locator('[data-definition="'+id+'"]').first
   assert trigger.count(),id
   trigger.click();assert expected in popup.inner_text()
   if id=='transformer-referred-current':
    popup.locator('summary',has_text='原文定义').click();assert '定义二次量折算' in popup.inner_text();popup.locator('summary',has_text='原文定义').click()
   box=popup.bounding_box();assert box['x']>=0 and box['x']+box['width']<=width and box['y']>=0 and box['y']+box['height']<=height
   if id=='transformer-referred-current':page.screenshot(path='.preview/definition-referred-'+str(width)+'.png')
   page.locator('.definition-close').click()
  # Scoped reading meanings do not bleed into zero-sequence / other chapter notation.
  assert page.evaluate('''()=>{const c=LN_COURSES[0],s=c.sections.find(s=>s.id==='transformer-7');return LNGlossary.resolveSymbol(c,s,'U_0')===null&&LNGlossary.resolveSymbol(c,s,'I_0')===null}''')
  section('dc-sec32');page.locator('[data-definition="dc-coil-count"]').first.click();assert '线圈' in popup.inner_text() and '槽数' in popup.inner_text();page.locator('.definition-close').click()
  for id,phrase in [('dc-commutation-time','换向时间'),('dc-commutation-inductance','等效换向电感'),('dc-commutation-current','线圈电流')]:
   section('dc-sec39');target=page.locator('[data-definition="'+id+'"]').first;target.scroll_into_view_if_needed();target.click();assert phrase in popup.inner_text()
   if id=='dc-commutation-time':
    y=target.bounding_box()['y'];page.screenshot(path='.preview/definition-commutation-'+str(width)+'.png');page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for();page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');assert abs(page.locator('[data-definition="'+id+'"]').first.bounding_box()['y']-y)<3
   else:page.locator('.definition-close').click()
  section('magnetic-sec12');page.locator('[data-definition="magnetic-coercivity"]').first.click();assert '矫顽力' in popup.inner_text();page.locator('.definition-close').click()
  page.locator('a.definition-term[data-definition="eddy-current"]').first.click();assert 'Eddy current' in popup.inner_text();page.locator('.definition-close').click()
  assert not errors,errors
  page.close()
 # Every HTML lesson keeps its original MathML and actual source targets after enhancement.
 page=b.new_page();page.goto('http://127.0.0.1:4173/');page.wait_for_function('window.LNGlossary&&window.LN_COURSES');page.evaluate('''()=>{const prepare=LNGlossary.prepare;window.mathChecks=[];LNGlossary.prepare=(body,c,s)=>{const before=[...body.querySelectorAll('.katex-mathml')].map(n=>n.outerHTML);prepare(body,c,s);mathChecks.push({section:s.id,unchanged:JSON.stringify(before)===JSON.stringify([...body.querySelectorAll('.katex-mathml')].map(n=>n.outerHTML))});}}''')
 sections=page.evaluate('LN_COURSES[0].sections.filter(s=>s.kind==="html").map(s=>s.id)');counts={}
 for sid in sections:
  page.evaluate('(s)=>{location.hash="#course/electrical-machines/"+s}',sid);page.locator('#lesson-body[data-lesson-key="electrical-machines/'+sid+'"][aria-busy="false"]').wait_for()
  missing=page.evaluate('''(s)=>LN_GLOSSARY['electrical-machines'].entries.filter(e=>e.source.section===s&&!document.getElementById(e.source.anchor)).map(e=>e.id)''',sid)
  assert not missing,(sid,missing)
  counts[sid]=page.locator('#lesson-body [data-definition]').count()
 assert page.evaluate('mathChecks.every(c=>c.unchanged)')
 print(json.dumps({'viewports':[1440,390,320],'source_targets':'all present','original_mathml':'preserved','lesson_counts':counts},ensure_ascii=False))
 b.close()
