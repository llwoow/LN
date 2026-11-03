"""Reading controls share one header and preserve navigation at narrow widths."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
Path('.preview').mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 results=[]
 for width,height in [(1440,1000),(1280,690),(1100,800),(1099,800),(960,700),(720,640),(390,844),(320,700),(640,360)]:
  context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
  page=context.new_page();errors=[];bad=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
  if width==1280:context.add_init_script("localStorage.setItem('ln.sidebar','collapsed');localStorage.setItem('ln.preferences',JSON.stringify({mode:'dark',palette:'ink'}))")
  page.goto('http://127.0.0.1:4173/#course/electrical-machines/transformer-homework')
  page.locator('#lesson-body[aria-busy="false"]').wait_for();page.evaluate('document.fonts.ready')
  page.locator('#problem-2-2 .paper-equation').first.scroll_into_view_if_needed();page.mouse.wheel(0,120)
  header=page.locator('.topbar');dock=page.locator('#reader-dock')
  assert abs(header.bounding_box()['height']-(58 if width<=720 else 64))<1
  assert header.bounding_box()['y']==0
  assert dock.evaluate('e=>e.parentElement.classList.contains("topbar")')
  for button in dock.locator(':scope > *').all():
   rect=button.bounding_box();assert 0<=rect['x'] and rect['x']+rect['width']<=width+.5
   assert rect['y']>=0 and rect['y']+rect['height']<=64
   assert button.get_attribute('aria-label')
  assert not page.locator('#lesson-body .homework-navigation').count()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  # No second fixed/sticky control bar floats over the page while reading.
  extras=page.evaluate('''()=>[...document.querySelectorAll('.workspace *')].filter(e=>{
   const s=getComputedStyle(e),r=e.getBoundingClientRect();
   return s.display!=='none'&&s.visibility!=='hidden'&&r.width&&r.height&&['fixed','sticky'].includes(s.position)&&!e.closest('.topbar,.reader-outline')&&r.top<innerHeight&&r.bottom>0&&e.getAttribute('role')!=='status';
  }).map(e=>e.id||e.className)''')
  assert not extras,(width,extras)
  if width in [1280,390,640]:page.screenshot(path='.preview/reader-header-'+str(width)+'.png')
  origin=page.evaluate('scrollY')
  if width<1100:
   assert not page.locator('#homework-question').is_visible()
   dock.locator('[data-reader-directory]').click()
   assert page.locator('#reader-directory-question #homework-question').is_visible()
  else:assert page.locator('#reader-question-slot #homework-question').is_visible()
  page.locator('#homework-question').select_option('2-19')
  page.locator('#question-2-19.reference-target').wait_for()
  assert not page.locator('#reader-directory').is_visible()
  page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
  assert abs(page.evaluate('scrollY')-origin)<4
  # Responsive moves reuse the same control, without duplicate IDs or stale handlers.
  page.set_viewport_size({'width':1440 if width<1100 else 390,'height':height})
  assert page.locator('#homework-question').count()==1
  if width>=1100:dock.locator('[data-reader-directory]').click()
  assert page.locator('#homework-question').is_visible()
  if page.locator('#reader-directory').is_visible():page.keyboard.press('Escape')
  page.set_viewport_size({'width':width,'height':height})
  page.wait_for_timeout(100);origin=page.evaluate('scrollY')
  page.locator('#top-settings').click();page.locator('#settings-dialog[open]').wait_for();page.keyboard.press('Escape')
  assert abs(page.evaluate('scrollY')-origin)<4
  dock.locator('[data-reader-directory]').click();page.locator('#reader-directory[open]').wait_for();page.keyboard.press('Escape')
  assert dock.locator('[data-reader-directory]').evaluate('e=>e===document.activeElement')
  dock.locator('[data-reader-top]').click();page.wait_for_function('scrollY===0')
  dock.locator('a[aria-label="知识图谱"]').click();page.locator('ln-knowledge-map').wait_for()
  assert not dock.is_visible();assert not page.locator('#reader-question-slot').is_visible()
  assert not page.locator('#homework-question').count()
  # The same five controls work in ordinary course and high-school reading.
  for route in ['electrical-machines/transformer-sec21','hs-math/math-compulsory-1-sets']:
   if route.startswith('hs-'):
    route=page.evaluate('''()=>{const c=window.LN_COURSES.find(c=>c.level==='highschool');return c.id+'/'+c.sections[0].id}''')
   page.goto('http://127.0.0.1:4173/#course/'+route);page.locator('#lesson-body[aria-busy="false"]').wait_for()
   assert dock.is_visible() and dock.locator(':scope > *').count()==5
   assert not page.locator('#homework-question').count()
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  assert not errors,errors
  assert not bad,bad
  results.append({'width':width,'height':height,'single_header':True,'navigation_and_return':True});context.close()
 browser.close()
print(json.dumps(results))
