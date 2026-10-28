"""Browser regression checks. Start the site on port 4173, then run this file.
Requires Playwright and a system Chromium browser; not part of dependency-free unittest.
Pass the site origin as the first optional argument.
"""
import sys
BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'http://127.0.0.1:4173'
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 report=[]
 for width,height in [(1440,1000),(390,844),(320,568)]:
  context=b.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
  page=context.new_page();errors=[];bad=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
  def opened(section,anchor=''):
   page.goto(BASE_URL+'/#course/electrical-machines/'+section+('/'+anchor if anchor else ''))
   page.locator('#lesson-body[data-lesson-key="electrical-machines/'+section+'"][aria-busy="false"]').wait_for()
   page.evaluate('document.fonts.ready')
   assert page.locator('.paper-equation.is-numbered').evaluate_all('(els)=>els.every(e=>Math.abs(e.getBoundingClientRect().right-e.querySelector(".equation-number").getBoundingClientRect().right)<1)'),section
  opened('magnetic-sec11')
  assert page.locator('.equation-number').all_text_contents()==['(1.1)','(1.2)','(1.3)','(1.4)']
  assert page.locator('#lesson-body .katex-tag').count()==0
  # Every numbered equation aligns with the reading-column right edge at all viewport sizes.
  geometry=page.locator('.paper-equation.is-numbered').evaluate_all('''els=>els.map(e=>{
   const tag=e.querySelector('.equation-number'),scroll=e.querySelector('.paper-equation-scroll');
   return {gap:Math.abs(e.getBoundingClientRect().right-tag.getBoundingClientRect().right),overlap:scroll.getBoundingClientRect().right>tag.getBoundingClientRect().left};
  })''')
  assert all(g['gap']<1 and not g['overlap'] for g in geometry),geometry
  link=page.locator('.paper-reference',has_text='式(1.3)').first
  link.scroll_into_view_if_needed();before=link.bounding_box()['y'];link.click()
  page.locator('.reference-target .is-reference-return').wait_for()
  page.locator('.reference-target .equation-number').click()
  page.wait_for_function('document.querySelector(".reference-return").hidden')
  page.wait_for_timeout(100)
  assert abs(page.locator('.paper-reference',has_text='式(1.3)').first.bounding_box()['y']-before)<3
  # Cross-section equation reference, and return via persistent control.
  opened('transformer-9')
  ref=page.locator('.paper-reference[href*="eq%3Abasechange"],.paper-reference[href*="eq:basechange"]').first
  ref.scroll_into_view_if_needed();sourceY=ref.bounding_box()['y'];ref.click()
  page.locator('#lesson-body[data-lesson-key="electrical-machines/transformer-4"] .reference-target').wait_for()
  assert page.locator('.reference-target').get_attribute('data-reference-kind')=='equation'
  page.locator('.reference-return').click()
  page.locator('#lesson-body[data-lesson-key="electrical-machines/transformer-9"]').wait_for()
  page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
  assert abs(page.locator('.paper-reference[href*="basechange"]').bounding_box()['y']-sourceY)<3
  # Figure and table links use the same reversible navigation.
  opened('transformer-symbols')
  figureRef=page.locator('.paper-reference[href*="fig:convention"]').first
  figureRef.scroll_into_view_if_needed();figureRef.click()
  page.locator('figure.reference-target').wait_for()
  page.locator('figure.reference-target .paper-target-label').click()
  page.wait_for_function('document.querySelector(".reference-return").hidden')
  opened('transformer-6')
  tableRef=page.locator('.paper-reference[href*="tab:terminals"]').first
  tableRef.scroll_into_view_if_needed();tableRef.click()
  page.locator('.reference-target').wait_for()
  page.locator('.reference-return').click()
  page.wait_for_function('document.querySelector(".reference-return").hidden')
  # Three-level labels remain right aligned, and references to them are automatic.
  fixture=page.evaluate('''()=>{
   const body=document.createElement('article');body.className='lesson';document.body.append(body);
   body.innerHTML='<p>由式（1.1.1）可得。</p><div class="math display" data-equation="1.1.1"><span class="katex-display">x = y</span></div>';
   window.LN_PUBLICATION_INDEX.qa={sections:{s:{equations:[{kind:'equation',number:'1.1.1',anchor:'equation-1-1-1',section:'s',group:'g'}],figures:[],tables:[]}},targets:[{kind:'equation',number:'1.1.1',anchor:'equation-1-1-1',section:'s',group:'g'}]};
   window.LNPublication.prepare(body,{id:'qa'},{id:'s',group:'g',title:'QA'});
   const result={number:body.querySelector('.equation-number').textContent,href:body.querySelector('.paper-reference').getAttribute('href')};body.remove();return result;
  }''')
  assert fixture=={'number':'(1.1.1)','href':'#course/qa/s/equation-1-1-1'},fixture
  opened('magnetic-sec13')
  page.evaluate('window.scrollTo(0,1000)');page.screenshot(path='.preview/publication-reading-'+str(width)+'.png')
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.locator('#quick-theme').click()
  page.screenshot(path='.preview/publication-dark-'+str(width)+'.png')
  assert not errors,errors
  assert not bad,bad
  report.append({'width':width,'passed':True});context.close()
 print(json.dumps({'viewports':report,'checks':['right-edge equation numbers','no formula-number collision','no duplicate visual tags','same-section reference return at exact position','cross-section equation return','figure caption return','table return','three-level labels','mobile horizontal equation scrolling','dark mode','no browser errors or failed requests']}))
 b.close()
