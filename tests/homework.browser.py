"""Native solved exercises: math, original diagrams, exact links and local review records."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
Path('.preview').mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 results=[]
 for width,height in [(1440,1000),(390,844),(320,700)]:
  c=b.new_context(viewport={'width':width,'height':height},reduced_motion='reduce');page=c.new_page();errors=[];bad=[];pdf=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
  page.on('request',lambda r:pdf.append(r.url) if r.url.endswith('transformer-homework.pdf') else None)
  def read(anchor=''):
   page.goto('http://127.0.0.1:4173/#course/electrical-machines/transformer-homework'+('/'+anchor if anchor else ''))
   page.locator('#lesson-body[data-lesson-key="electrical-machines/transformer-homework"][aria-busy="false"]').wait_for();page.evaluate('document.fonts.ready')
  read()
  assert page.locator('.homework-problem').count()==13
  assert page.locator('.homework-problem .homework-prompt').count()==13
  assert page.locator('.homework-problem math').count()>80
  assert not page.locator('#pdf-image,iframe,embed,object,.katex-error').count()
  assert page.locator('.homework-diagram').count()==7
  page.wait_for_function('[...document.querySelectorAll(".homework-diagram")].every(i=>i.complete&&i.naturalWidth>0)')
  for problem in page.locator('.homework-problem').all():
   problem.locator('h3').first.scroll_into_view_if_needed()
   assert problem.locator('.homework-prompt').inner_text().strip()
   assert problem.locator('.homework-knowledge a').count()>0
   assert not problem.locator('details').count()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  assert page.locator('#reader-dock').is_visible()
  assert page.locator('.paper-equation.is-numbered').evaluate_all('(ns)=>ns.every(e=>Math.abs(e.getBoundingClientRect().right-e.querySelector(".equation-number").getBoundingClientRect().right)<2)')
  # Header/directory selection reaches the title without a second floating toolbar.
  page.locator('#question-2-19').scroll_into_view_if_needed();page.mouse.wheel(0,200);page.wait_for_timeout(100);origin=page.evaluate('scrollY')
  assert not page.locator('#lesson-body .homework-navigation').count()
  assert page.locator('#reader-dock').bounding_box()['y']<64
  if width<1100:page.locator('[data-reader-directory]').click()
  page.locator('#homework-question').select_option('2-25')
  page.wait_for_function('location.hash.endsWith("question-2-25")&&document.querySelector("#lesson-body").getAttribute("aria-busy")==="false"')
  page.locator('#question-2-25.reference-target').wait_for()
  assert page.locator('#homework-question').input_value()=='2-25'
  assert not page.locator('#reader-directory').is_visible()
  page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
  assert abs(page.evaluate('scrollY')-origin)<4
  # An underlined current is a phasor and retains its source-backed definition.
  underline=page.locator('#problem-2-19 .definition-symbol[data-definition="homework-current"]:has(.underline)').first
  assert underline.count()>0
  underline.scroll_into_view_if_needed();before=underline.bounding_box()['y'];position=page.evaluate('scrollY');underline.click(force=True)
  popup=page.locator('#definition-popover:popover-open');popup.wait_for();assert '流向负载' in popup.inner_text()
  assert abs(page.evaluate('scrollY')-position)<3
  page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for()
  page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
  assert abs(page.locator('#problem-2-19 .definition-symbol[data-definition="homework-current"]:has(.underline)').first.bounding_box()['y']-before)<4
  # The original figure reference reaches the preserved wiring, then returns.
  link=page.locator('#problem-2-20 .homework-prompt .paper-reference').first;link.scroll_into_view_if_needed();y=link.bounding_box()['y'];link.click()
  page.locator('#figure-2-61.reference-target').wait_for()
  page.locator('#figure-2-61').screenshot(path='.preview/homework-wiring-'+str(width)+'.png')
  page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
  assert abs(page.locator('#problem-2-20 .homework-prompt .paper-reference').first.bounding_box()['y']-y)<4
  # Each exercise opens its own stable record, supporting favorite, mistake and redo.
  button=page.locator('#problem-2-22 [data-practice-question="hw-2-22"]');button.scroll_into_view_if_needed();y=page.evaluate('scrollY');button.click()
  dialog=page.locator('#practice-dialog[open]');dialog.wait_for();assert dialog.locator('[data-p-question]').input_value()=='hw-2-22'
  dialog.locator('[data-p-reason]').fill('用空载和短路数据区分励磁支路与串联阻抗，再统一基准并复算效率。')
  dialog.locator('[data-p-submit]').click();dialog.locator('[data-p-favorite]').click();dialog.locator('[data-p-mistake]').click()
  record=page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["hw-2-22"]');assert record['favorite'] and record['selfMistake'] and len(record['attempts'])==1
  dialog.locator('[data-p-redo]').click();assert dialog.locator('[data-p-reason]').input_value()==''
  assert len(page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["hw-2-22"].attempts'))==1
  dialog.locator('[data-practice-mode="favorites"]').click();assert dialog.locator('[data-p-question]').input_value()=='hw-2-22'
  dialog.locator('[data-practice-mode="mistakes"]').click();assert dialog.locator('[data-p-question]').input_value()=='hw-2-22'
  dialog.locator('[data-close-practice]').click();page.wait_for_function('!document.querySelector("#practice-dialog").open');assert abs(page.evaluate('scrollY')-y)<4
  # Old PDF page bookmarks still lead into native content.
  read('page-8');page.wait_for_function('document.querySelector("#page-8").classList.contains("reference-target")')
  page.locator('#question-2-19').scroll_into_view_if_needed();page.screenshot(path='.preview/homework-reading-'+str(width)+'.png')
  page.evaluate('document.documentElement.dataset.theme="dark"');page.locator('#problem-2-22 .paper-equation').first.scroll_into_view_if_needed()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  assert not errors,errors
  assert not bad,bad
  assert not pdf,pdf
  results.append({'width':width,'questions':13,'diagrams':7,'native_math':True,'links_and_records':True});c.close()
 b.close()
print(json.dumps(results))
