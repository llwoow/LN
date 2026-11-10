"""LN integration: actual media, manipulation, safe notes and honest reference records."""
from pathlib import Path
import json,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.preview/physics001';OUT.mkdir(parents=True,exist_ok=True)
BASE=os.environ.get('LN_TEST_URL','http://127.0.0.1:4173/')
def route(i,anchor=''):
 return BASE+'#course/hs-physics/physics-001-q'+str(i).zfill(2)+('/'+anchor if anchor else '')
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in [1440,390,320]:
  context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
  page=context.new_page();errors=[];bad=[];requests=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:bad.append([r.status,r.url]) if r.status>=400 else None)
  page.on('request',lambda r:requests.append(r.url))
  for i in range(1,19):
   page.goto(route(i));body=page.locator('#lesson-body[aria-busy=false]');body.wait_for()
   assert body.locator('h2').inner_text().startswith(f'第{i}题')
   assert body.locator('.katex-error').count()==0
   assert body.locator('video').count()==(2 if i in [14,18] else 1)
   assert body.locator('video[autoplay]').count()==0
   assert body.locator('[data-gif] img[src]').count()==0
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),('overflow',i,width)
   assert body.locator('#step-1').is_visible()
   if i in [3,7,8,9,10,11,12,13,15,16,17,18]:
    lab=body.locator('[data-physics-lab]');assert lab.locator('svg').count()==1
    slider=lab.locator('input[type=range]').first;slider.focus();slider.press('End')
    assert lab.locator('svg').count()==1
   if i in [7,13,15,18]:
    body.locator('#step-1').scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'q{i:02d}-{width}.png'))
  assert not any('/gifs/' in r for r in requests)
  # Video really decodes H264, seeks and pauses; GIF is only fetched on explicit expansion.
  page.goto(route(7,'motion-q07'));page.locator('#lesson-body[aria-busy=false]').wait_for()
  video=page.locator('video');video.evaluate('(v)=>{v.preload="auto";v.load()}')
  page.wait_for_function('document.querySelector("video").readyState>=2 && document.querySelector("video").seekable.length>0 && document.querySelector("video").seekable.end(0)>1.5')
  assert video.evaluate('(v)=>v.duration')>0
  video.evaluate('(v)=>{v.currentTime=1.5}')
  page.wait_for_function('Math.abs(document.querySelector("video").currentTime-1.5)<0.1')
  video.evaluate('(v)=>v.play()');page.wait_for_function('document.querySelector("video").currentTime>1.6')
  video.evaluate('(v)=>v.pause()');assert video.evaluate('(v)=>v.paused')
  gif=page.locator('[data-gif]');gif.locator('summary').click();page.wait_for_function('document.querySelector("[data-gif] img").naturalWidth>0')
  gif.locator('[data-stop-gif]').click();assert not gif.locator('img[src]').count()
  # Viewing worked analysis then choosing redo cannot turn a later answer into an independent first answer.
  page.goto(route(13));page.locator('#lesson-body[aria-busy=false]').wait_for()
  page.locator('#lesson-body [data-open-practice]').click();dialog=page.locator('#practice-dialog')
  assert dialog.locator('[data-question-id]').get_attribute('data-question-id')=='hs-physics001-13'
  dialog.locator('[data-p-redo]').click()
  for option in ['A','B','D']:dialog.locator('[name=p-answer][value='+option+']').check()
  dialog.locator('[data-p-submit]').click()
  r=page.evaluate('JSON.parse(localStorage.getItem("ln.practice.v1"))["hs-physics001-13"]')
  assert r['attempts'][0]['correct'] is True and r['attempts'][0]['assisted'] is True
  dialog.locator('[data-p-favorite]').click();dialog.locator('[data-p-mistake]').click()
  dialog.locator('[data-close-practice]').click()
  before=page.evaluate('localStorage.getItem("ln.practice.v1")')
  page.goto(BASE+'#course/hs-physics/physics-001');page.locator('[data-notes-import]').wait_for()
  data={'assessment':'physics-001','records':{'7':{'rating':1,'note':'<img src=x onerror=alert(1)> 还要检查绳长','updatedAt':'2026-11-10T00:00:00Z'},'19':{'rating':3,'note':'invalid','updatedAt':'2026-11-10T00:00:00Z'}}}
  page.locator('[data-notes-import]').set_input_files({'name':'old-notes.json','mimeType':'application/json','buffer':json.dumps(data).encode()})
  page.wait_for_function('document.querySelector("[data-notes-status]").textContent.includes("合并 1")')
  assert page.locator('[data-notes-list] img').count()==0
  assert page.evaluate('localStorage.getItem("ln.practice.v1")')==before
  with page.expect_download() as info:page.locator('[data-notes-export]').click()
  exported=json.loads(Path(info.value.path()).read_text());assert exported['records']['7']['rating']==1
  page.goto(route(7));page.locator('#lesson-body[aria-busy=false]').wait_for();assert page.locator('[data-note-rating]').input_value()=='1'
  assert page.locator('[data-note-text]').input_value()==data['records']['7']['note']
  # Theme contrast uses shared tokens, fixed-background scientific SVG stays readable in night mode.
  page.evaluate('document.documentElement.dataset.theme="dark"');page.locator('#step-4').scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'q07-dark-{width}.png'))
  assert not errors,errors
  assert not bad,bad
  results.append({'width':width,'questions':18,'errors':errors,'badResponses':bad,'videoDecodeSeekPause':True,'notesImportIsolated':True,'referenceAttemptAssisted':True})
  context.close()
 browser.close()
(OUT/'browser-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('Physics001 integration verified at 1440, 390 and 320 px.')
