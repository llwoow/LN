"""Run in GitHub Actions Chromium; inspect real static build, not managed preview."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'robot-drive-browser-artifacts';OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'courses/robot-drive-engineering/manuscript.json').read_text());COURSE=D['course']
def main():
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1])+'/'
 audit=[]
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for name,w,h in [('desktop',1440,900),('mobile',390,844),('mobile-small',320,690)]:
    page=browser.new_page(viewport={'width':w,'height':h},reduced_motion='reduce');errors=[];http=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:http.append([r.status,r.url]) if r.status>=400 else None)
    for l in D['lessons']:
     sid=l['id'];page.goto(base+'#course/'+COURSE+'/'+sid,wait_until='domcontentloaded')
     body=page.locator('#lesson-body[data-lesson-key="'+COURSE+'/'+sid+'"][aria-busy=false]');body.wait_for();page.evaluate('document.fonts.ready')
     assert body.locator('h2').count(),sid
     assert not body.locator('.katex-error').count(),sid
     assert not body.locator('p[role=alert]').count(),sid
     assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(sid,w,'overflow')
     for fig in body.locator('figure').all():
      assert fig.locator('figcaption').count(),(sid,'caption')
      for svg in fig.locator('svg').all():assert svg.locator('title').count(),(sid,'alternative')
     for lab in body.locator('[data-rd-lab]').all():
      result=lab.locator('.rd-lab-result');before=result.inner_text();slider=lab.locator('input[type=range]').first
      if w<=390:
       plot=lab.locator('.rd-lab-plot');assert plot.evaluate('n=>n.scrollWidth>n.clientWidth'),(sid,'readable plot pan')
      slider.evaluate("el=>{el.value=el.max;el.dispatchEvent(new Event('input',{bubbles:true}))}");assert before!=result.inner_text(),sid
     page.screenshot(path=str(OUT/(sid+'-'+name+'.png')),full_page=True)
     # A dock in the page header remains reachable after a long scroll.
     page.evaluate('scrollTo(0,document.body.scrollHeight)');rect=page.locator('#reader-dock').bounding_box()
     assert rect and rect['y']>=0 and rect['y']<h,(sid,'reader dock')
     audit.append({'lesson':sid,'viewport':name})
    # Source-backed glossary popup, source navigation and return.
    page.goto(base+'#course/'+COURSE+'/rd-current-sense');body=page.locator('#lesson-body[aria-busy=false]');body.wait_for()
    symbol=body.locator('[data-definition]').first;symbol.wait_for();symbol.scroll_into_view_if_needed();y=symbol.bounding_box()['y'];symbol.click(force=True)
    popup=page.locator('#definition-popover:popover-open');popup.wait_for();assert len(popup.inner_text())>20
    page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for();page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
    # Native exercise modes preserve mistake, favorite and redo storage flows.
    page.goto(base+'#practice/'+COURSE);page.locator('[data-practice-mode=local]').click();panel=page.locator('main [data-practice-panel]')
    for q in D['questions']:
     panel.locator('[data-p-question]').select_option(q['id'])
     if q['type'] in ('single','multi'):
      for opt in q['answer']:panel.locator('[name=p-answer][value="'+opt+'"]').check()
     elif q['type']=='numeric':panel.locator('[data-p-value]').fill(str(q['answer']));panel.locator('[data-p-reason]').fill('核对物理模型、单位与适用条件。')
     else:panel.locator('[data-p-reason]').fill('写出推理、边界与可检验的结论。')
     panel.locator('[data-p-submit]').click();assert panel.locator('.practice-feedback ol li').count()>=3,q['id']
     assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(q['id'],w)
    page.screenshot(path=str(OUT/('practice-'+name+'.png')),full_page=True)
    page.goto(base+'#course/'+COURSE+'/map');page.locator('ln-knowledge-map').wait_for();page.screenshot(path=str(OUT/('map-'+name+'.png')),full_page=True)
    # Actual legacy content remains reachable through the new source tree.
    for cid,sid in [('automatic-control','ac-3-6'),('electrical-machines','transformer-4'),('electrical-machines','transformer-homework')]:
     page.goto(base+'#course/'+cid+'/'+sid);page.locator('#lesson-body[data-lesson-key="'+cid+'/'+sid+'"][aria-busy=false]').wait_for()
    assert not errors,errors;assert not http,http;page.close()
   browser.close()
 finally:server.shutdown();server.server_close()
 (OUT/'audit.json').write_text(json.dumps({'renderedStates':len(audit),'lessons':len(D['lessons']),'viewports':3,'questions':len(D['questions']),'checks':audit},ensure_ascii=False,indent=2))
 print('Verified',len(audit),'reading states and native interactions in Chromium.')
if __name__=='__main__':main()
