"""CI browser evidence for the combined PRs; content accuracy reviewed separately."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,runpy,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'nov13-browser-artifacts';OUT.mkdir(exist_ok=True)
a=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
bank=json.loads((ROOT/'courses/practice/bank.json').read_text());allq={q['id']:q for q in bank['questions']}
MATERIAL='electrical-materials';PSD='power-semiconductors';DC='electrical-machines'
VISUAL={'vdmos-structure','vdmos-conduction','vdmos-output','vdmos-blocking','thyristors','junction-termination','device-selection','em-2-1','em-2-2','em-2-3','em-2-4','em-2-5','em-test-summary','em-test-fill','em-test-short','em-test-review','dc-sec32','dc-quickref','dc-worked','dc-answers'}
def main():
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1])+'/'
 audit=[];legacy=next(q for q in bank['questions'] if q['type']=='single' and q['course']==DC)
 original={'version':1,'order':[o['id'] for o in legacy['options']],'selected':[],'value':'','reason':'existing saved analysis','confidence':'sure','checks':[],'attempts':[{'correct':False,'assisted':False,'confidence':'sure'}],'hinted':False,'revealed':False,'favorite':True}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for name,w,h in [('desktop',1440,900),('mobile',390,844),('small',320,690)]:
    page=browser.new_page(viewport={'width':w,'height':h},reduced_motion='reduce');errors=[];http=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:http.append([r.status,r.url]) if r.status>=400 else None)
    page.add_init_script('if(!localStorage.getItem("ln.practice.v1"))localStorage.setItem("ln.practice.v1",'+json.dumps(json.dumps({legacy['id']:original}))+');')
    def visit(cid,sid):
     page.goto(base+'#course/'+cid+'/'+sid,wait_until='domcontentloaded');body=page.locator('#lesson-body[data-lesson-key="'+cid+'/'+sid+'"][aria-busy=false]');body.wait_for(timeout=30000);page.evaluate('document.fonts.ready');return body
    for cid in [PSD,MATERIAL,DC]:
     course=a(ROOT/'courses'/cid/'manifest.js');sections=[s for s in course['sections'] if s['kind']=='html' and (cid!=DC or s['id'] in {'dc-sec32','dc-quickref','dc-worked','dc-answers'})]
     for s in sections:
      sid=s['id'];body=visit(cid,sid);assert body.locator('h2').count(),sid
      assert not body.locator('.katex-error').count(),sid
      assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(sid,w,'page overflow')
      for img in body.locator('img.original-diagram').all():
       img.scroll_into_view_if_needed();page.wait_for_function('(e)=>e.complete&&e.naturalWidth>0',arg=img.element_handle())
      if cid!=DC:
       for fig in body.locator('figure').all():assert fig.locator('figcaption').count(),(sid,'caption')
      if sid in VISUAL and (w!=320 or sid in {'thyristors','vdmos-blocking','em-2-2','em-2-5','em-test-short','dc-sec32'}):page.screenshot(path=str(OUT/(sid+'-'+name+'.png')),full_page=True)
      page.evaluate('scrollTo(0,document.body.scrollHeight)');rect=page.locator('#reader-dock').bounding_box();assert rect and 0<=rect['y']<h,(sid,'fixed dock')
      audit.append({'course':cid,'section':sid,'viewport':name})
    # The textbook's unfinished chapter stays an empty outline, not invented prose.
    body=visit(MATERIAL,'em-1-1');assert body.locator('h2').count()==1;assert body.locator('.math').count()==0
    page.goto(base+'#course/'+MATERIAL+'/map');page.locator('ln-knowledge-map').wait_for();page.get_by_role('link',name='章节阅读',exact=True).click();page.locator('#lesson-body[data-lesson-key="electrical-materials/em-2-1"][aria-busy=false]').wait_for()
    # New model uses the same declared parallel-branch physics at each viewport.
    body=visit(DC,'dc-sec32');page.locator('[data-dc-value=branches]').wait_for();assert page.locator('[data-dc-value=emf]').inner_text()=='240.0 V'
    page.locator('[data-dc-winding]').select_option('wave');assert page.locator('[data-dc-value=branches]').inner_text()=='2';assert page.locator('[data-dc-value=emf]').inner_text()=='480.0 V'
    if w<=390:assert page.locator('[data-dc-diagram]').evaluate('n=>n.scrollWidth>n.clientWidth')
    # Each of the new course bundles supplies actual definition popups and source return.
    for cid,sid in [(MATERIAL,'em-2-4'),(PSD,'vdmos-output'),(DC,'dc-sec32')]:
     body=visit(cid,sid);symbol=body.locator('.katex-html [data-definition]:visible, math [data-definition]:visible').first;symbol.wait_for();symbol.scroll_into_view_if_needed();symbol.click(force=True)
     pop=page.locator('#definition-popover:popover-open');pop.wait_for();assert len(pop.inner_text())>20
     page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for();page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden')
    # All five DC diagnostics use native records rather than an unpersisted local answer checker.
    body=visit(DC,'dc-answers');assert body.locator('[data-practice-question]').count()==5
    q=allq['dc-branch-wave-six'];body.locator('[data-practice-question="'+q['id']+'"]').click();dialog=page.locator('#practice-dialog:modal');panel=dialog.locator('[data-practice-panel]');assert panel.locator('[data-p-question]').input_value()==q['id']
    wrong=next(o['id'] for o in q['options'] if o['id'] not in q['answer']);panel.locator('[name=p-answer][value="'+wrong+'"]').check();panel.locator('[data-p-submit]').click()
    assert panel.locator('.practice-feedback h3').inner_text()=='答案尚不吻合，检查下面的推理'
    panel.locator('[data-p-favorite]').click();panel.locator('[data-p-redo]').click();panel.locator('[name=p-answer][value="'+q['answer'][0]+'"]').check();panel.locator('[data-p-submit]').click()
    assert panel.locator('.practice-feedback h3').inner_text()=='选择吻合，请继续核对理由'
    dialog.locator('[data-close-practice]').click();page.reload();page.locator('#lesson-body[aria-busy=false]').wait_for();page.locator('[data-practice-question="'+q['id']+'"]').click();dialog=page.locator('#practice-dialog:modal')
    saved=page.evaluate('(id)=>JSON.parse(localStorage.getItem("ln.practice.v1"))[id]',q['id']);assert saved['favorite'];assert saved['attempts'][0]['correct'] is False;assert saved['attempts'][-1]['correct'] is True;assert saved['attempts'][-1]['assisted'] is True
    dialog.locator('[data-practice-mode=mistakes]').click();dialog.locator('[data-p-question]').select_option(q['id']);assert dialog.locator('[data-question-id="'+q['id']+'"]').count()==1
    dialog.locator('[data-practice-mode=favorites]').click();dialog.locator('[data-p-question]').select_option(q['id']);assert dialog.locator('[data-question-id="'+q['id']+'"]').count()==1
    dialog.locator('[data-close-practice]').click()
    # Supplied open questions retain manual review, source anchors and collection persistence.
    body=visit(MATERIAL,'em-test-fill');qid='materials-photo-fill-1';body.locator('[data-practice-question="'+qid+'"]').click();dialog=page.locator('#practice-dialog:modal');panel=dialog.locator('[data-practice-panel]');assert panel.locator('[data-p-question]').input_value()==qid
    panel.locator('[data-p-reason]').fill('从势能极小与稳定性条件分析，并与参考解释核对。');panel.locator('[data-p-submit]').click();assert panel.locator('.practice-feedback h3').inner_text()=='请逐项自评论证'
    panel.locator('[data-p-favorite]').click();panel.locator('[data-p-mistake]').click();dialog.locator('[data-close-practice]').click();page.reload();page.locator('#lesson-body[aria-busy=false]').wait_for()
    saved=page.evaluate('(id)=>JSON.parse(localStorage.getItem("ln.practice.v1"))[id]',qid);assert saved['favorite'] and saved['selfMistake'];assert saved['attempts'][0]['correct'] is None
    preserved=page.evaluate('(id)=>JSON.parse(localStorage.getItem("ln.practice.v1"))[id]',legacy['id']);assert preserved==original,('legacy record changed',preserved)
    assert not errors,errors;assert not http,http;page.close()
   # Print the reviewed standalone answer in CI. The source PDF remains untouched locally.
   page=browser.new_page(viewport={'width':1440,'height':1100});page.goto(base+'answers/power-semiconductors/chapter-2/答案.html',wait_until='networkidle');page.evaluate('document.fonts.ready');assert page.locator('.sheet').count()==9;assert not page.locator('.katex-error').count();assert '未重新核分' in page.locator('#review').inner_text()
   page.screenshot(path=str(OUT/'standalone-answer-desktop.png'),full_page=True)
   page.pdf(path=str(OUT/'answer-reviewed.pdf'),prefer_css_page_size=True,print_background=True)
   browser.close()
 finally:server.shutdown();server.server_close()
 (OUT/'audit.json').write_text(json.dumps({'commit':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'readings':audit,'legacyRecordsPreserved':True,'nativeCollections':True,'openManualReview':True},ensure_ascii=False,indent=2))
 print('Verified',len(audit),'reading states, native collections, source returns and printable answer.')
if __name__=='__main__':main()
