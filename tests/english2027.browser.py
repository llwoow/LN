"""English integration under a Pages subdirectory; technical, not learning-effect evidence."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,os,runpy,tempfile,threading,sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.preview/english2027';OUT.mkdir(parents=True,exist_ok=True)
WEB=ROOT/'dist' if '--dist' in sys.argv else ROOT
assignment=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
course=assignment(ROOT/'courses/hs-english/manifest.js')
questions=[q for q in json.loads((ROOT/'courses/practice/bank.json').read_text())['questions'] if q.get('collection')=='english-2027']
RangeHandler=runpy.run_path(str(ROOT/'tests/serve.py'))['Handler']
class Quiet(RangeHandler):
    def log_message(self,*args):pass
    def copyfile(self,*args):
        try:super().copyfile(*args)
        except (BrokenPipeError,ConnectionResetError):pass

with tempfile.TemporaryDirectory(prefix='ln-english-') as folder:
    (Path(folder)/'LN').symlink_to(WEB,target_is_directory=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=folder))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)+'/LN/'
    errors=[];bad=[];checks=[]
    try:
        with sync_playwright() as pw:
            executable=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').is_file() else None)
            browser=pw.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:bad.append([r.status,r.url]) if r.status>=400 else None)
            def read(code):
                page.goto(base+'#course/hs-english/english-2027-'+code.lower())
                body=page.locator('#lesson-body[aria-busy=false]');body.wait_for();return body
            def panel():return page.locator('#practice-dialog [data-practice-panel]')
            def record(id):return page.evaluate('(id)=>JSON.parse(localStorage.getItem("ln.practice.v1"))[id]','hs-english2027-'+id)
            def practice(id):
                if page.locator('#practice-dialog').evaluate('(d)=>d.open'):
                    page.locator('#practice-dialog [data-close-practice]').click()
                page.evaluate('(id)=>{const b=document.createElement("button");b.dataset.testOpen="";b.dataset.openPractice="";b.dataset.practiceCourse="hs-english";b.dataset.practiceQuestion="hs-english2027-"+id;b.textContent="打开练习";document.querySelector("main").append(b);}',id)
                page.locator('[data-test-open]').click();page.locator('[data-test-open]').evaluate('(b)=>b.remove()')
                panel().locator('[data-question-id="hs-english2027-'+id+'"]').wait_for()
            def answer(q,value=None):
                box=panel()
                if q['type'] in ['single','multi']:
                    for option in q['answer']:box.locator('[name=p-answer][value="'+option+'"]').check()
                elif q['type']=='fill':box.locator('[data-p-value]').fill(value or q['answer'][0])
                else:box.locator('[data-p-reason]').fill('A draft for human review of content, structure and language.')
                box.locator('[data-p-submit]').click();box.locator('.practice-feedback').wait_for()
            # Existing course entry, native graph and all supplied chapters.
            page.goto(base+'#highschool');page.locator('a[href="#course/hs-english"]').first.click()
            page.locator('ln-knowledge-map svg').wait_for()
            page.get_by_role('link',name='英语讲义',exact=True).click();page.locator('[data-english-records]').wait_for()
            for section in course['sections']:
                if section.get('supplement')!='english-2027':continue
                body=read(section['id'].removeprefix('english-2027-'))
                assert body.locator('.english2027').count()==1,section['id']
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),section['id']
                assert body.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)'),section['id']
            checks.append('all 55 reading units, native graph and entry load')
            read('home');page.evaluate('localStorage.removeItem("ln.practice.v1")');page.reload();page.locator('[data-english-records]').wait_for()
            practice('G08');box=panel();box.locator('[data-p-value]').fill('and');box.locator('[data-p-submit]').click()
            box.locator('[data-p-redo]').click();box.locator('[data-p-value]').fill('but');box.locator('[data-p-submit]').click()
            r=record('G08');assert r['attempts'][0]['correct'] is False and not r['attempts'][0]['assisted'] and r['attempts'][1]['correct'] and r['attempts'][1]['assisted']
            checks.append('wrong first response preserved after correction')
            box.locator('[data-p-favorite]').click();page.locator('#practice-dialog [data-close-practice]').click()
            # Legacy import is scoped and does not trust a supplied correctness flag.
            old={'assessment':'hainan-english-2027-v1','records':{'G08':{'reason':'legacy reason','value':'but','selected':'','attempts':[{'answer':'and','correct':True,'time':'2026-11-01T00:00:00Z'}]},'M13':{'reason':'<img src=x onerror="window.injected=1">','value':'that','selected':'','attempts':[{'answer':'that','correct':True,'time':'2026-11-01T00:00:00Z'}]}}}
            page.locator('[data-english-import]').set_input_files({'name':'legacy.json','mimeType':'application/json','buffer':json.dumps(old).encode()})
            page.wait_for_function('document.querySelector("[data-english-status]").textContent.includes("合并 2")')
            r=record('G08');assert r['attempts'][0]['answer']=='and' and not r['attempts'][0]['correct'] and not r['attempts'][-1]['correct'] and r['attempts'][-1]['assisted']
            practice('M13');assert panel().locator('[data-p-reason]').input_value().startswith('<img src=x') and not page.evaluate('Boolean(window.injected)')
            page.locator('#practice-dialog [data-close-practice]').click()
            checks.append('legacy import retains first response, recomputes result, escapes notes')
            # All authored inputs reach shared feedback; this is not an independent answer-key validation.
            for q in questions:
                practice(q['sourceQuestion']);answer(q)
                assert record(q['sourceQuestion'])['attempts'][-1]['correct'] is (None if q['type']=='open' else True),q['id']
            for id,value in [('M13','which'),('M19','could join'),('M19','might join'),('M20','should leave'),('G10','usable')]:
                practice(id);answer(next(q for q in questions if q['sourceQuestion']==id),value)
                assert record(id)['attempts'][-1]['correct']
            checks.append('91 entries submit, valid alternatives accepted, writing remains open')
            # Revealing then hiding feedback never restores independent conditions.
            practice('M24');box=panel();box.locator('[data-p-reveal]').click();box.locator('[data-p-redo]').click();box.locator('[data-p-value]').fill("haven't");box.locator('[data-p-submit]').click();assert record('M24')['attempts'][-1]['assisted']
            practice('S01');panel().locator('[name=p-answer][value=B]').check();assert 'S01 This makes' in panel().locator('.practice-prompt').inner_text()
            page.locator('#practice-dialog [data-close-practice]').click()
            read('P17');practice('G01');assert record('G01')['feedbackSeen'];page.locator('#practice-dialog [data-close-practice]').click()
            checks.append('reference and seven-select context behavior retained')
            for id in ['K06','K09','T02','T03','T07']:
                body=read(id);lab=body.locator('[data-english-lab]');before=lab.locator('[data-english-scene]').inner_text();lab.locator('[data-state="1"]').click();assert before!=lab.locator('[data-english-scene]').inner_text()
            # Terminology uses LN's existing popup with a real definition destination.
            body=read('K09');term=body.locator('[data-definition]').first;term.click();popup=page.locator('#definition-popover:popover-open');popup.wait_for();assert '非谓语' in popup.inner_text();page.keyboard.press('Escape')
            checks.append('five interactions and shared terminology popup work')
            read('home')
            for id in ['L01','L02','L03','L04','L05','L06','L09','L12','L15','L18']:
                practice(id);audio=panel().locator('audio');print('Audio check',id,flush=True);audio.evaluate('(a)=>{a.preload="auto";a.load()}')
                page.wait_for_function('(()=>{let a=document.querySelector("#practice-dialog audio");return a&&a.readyState>=2&&a.duration>0})()')
                audio.evaluate('(a)=>a.play()');page.wait_for_function('document.querySelector("#practice-dialog audio").currentTime>0.05');audio.evaluate('(a)=>{a.pause();a.currentTime=1}')
                page.wait_for_function('(()=>{let a=document.querySelector("#practice-dialog audio");return a.paused&&Math.abs(a.currentTime-1)<0.2})()')
            panel().locator('[data-practice-transcript] summary').click();page.wait_for_timeout(80)
            assert all(record(id)['feedbackSeen'] for id in ['L18','L19','L20'])
            page.locator('#practice-dialog [data-close-practice]').click()
            assert not page.locator('#practice-dialog audio[src]').count()
            checks.append('ten audio clips load/play/pause/seek; close releases audio')
            # New grammar records participate in LN collections and export.
            page.goto(base+'#practice/hs-english');page.locator('main [data-practice-mode=favorites]').click();assert page.locator('main [data-p-question] option[value="hs-english2027-G08"]').count()==1
            page.locator('main [data-practice-mode=mistakes]').click();assert page.locator('main [data-p-question] option[value="hs-english2027-G08"]').count()==1
            read('home')
            with page.expect_download() as info:page.locator('[data-english-export]').click()
            exported=json.loads(Path(info.value.path()).read_text());assert exported['records']['G08']['attempts'][0]['answer']=='and'
            before=record('G08');page.locator('[data-english-import]').set_input_files({'name':'roundtrip.json','mimeType':'application/json','buffer':json.dumps(exported).encode()});page.wait_for_function('document.querySelector("[data-english-status]").textContent.includes("合并")');assert record('G08')['attempts'][0]==before['attempts'][0]
            checks.append('shared mistakes/favorites and export/import preserve records')
            # Existing physics/electrical records continue to function with unchanged IDs/version.
            page.goto(base+'#practice/hs-physics');page.locator('main [data-practice-mode=local]').click();page.locator('main [data-p-question]').select_option('hs-physics001-13')
            for id in ['A','B','D']:page.locator('main [name=p-answer][value='+id+']').check()
            page.locator('main [data-p-submit]').click();assert page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["hs-physics001-13"].attempts[0].correct')
            checks.append('existing physics multi-select still uses stable IDs')
            for width in [390,320]:
                page.set_viewport_size({'width':width,'height':844})
                for code in ['home','K00','K03','K09','K21','T02','T07','P01','P08','P13','P20']:
                    read(code);assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,code)
                practice('G08');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
                page.locator('#practice-dialog [data-close-practice]').click()
                read('K09');page.evaluate('document.documentElement.dataset.theme="dark"');page.screenshot(path=str(OUT/f'mobile-{width}.png'),full_page=True)
            page.set_viewport_size({'width':1440,'height':1000});page.evaluate('document.documentElement.dataset.theme="light"');read('K09');page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
            checks.append('390/320px reader and practice fit without document overflow')
            assert not errors,errors
            assert not bad,bad
            browser.close()
        (OUT/'browser-results.json').write_text(json.dumps({'checks':checks,'errors':errors,'badResponses':bad,'basePath':'/LN/','scope':'Technical integration only; no learner trial or independent language review.'},ensure_ascii=False,indent=2)+'\n')
        print('English LN integration:',len(checks),'behavior groups; no JS errors or HTTP failures.')
    finally:server.shutdown();server.server_close()
