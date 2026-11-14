"""CI interactions for brief references and exact local symbol meanings.

This checks interface behavior. It does not assert full-course teaching quality.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'nov13-browser-artifacts';OUT.mkdir(exist_ok=True)
def main():
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'dist')))
 threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1])+'/'
 evidence=[]
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for width in [1440,390,320]:
    page=browser.new_page(viewport={'width':width,'height':900},reduced_motion='reduce');errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def visit(cid,sid):
     page.goto(base+'#course/'+cid+'/'+sid,wait_until='domcontentloaded')
     body=page.locator('#lesson-body[data-lesson-key="'+cid+'/'+sid+'"][aria-busy=false]');body.wait_for(timeout=30000);page.evaluate('document.fonts.ready')
     assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(cid,sid,width,'page overflow')
     return body
    def entry(cid,sid,key,eq):
     result=page.evaluate('''a=>{const c=LN_COURSES.find(c=>c.id===a.cid);return LNGlossary.resolveSymbol(c,c.sections.find(s=>s.id===a.sid),a.key,'symbol',a.eq)}''',{'cid':cid,'sid':sid,'key':key,'eq':eq})
     assert result,(sid,key,eq,'no exact definition');return result
    def open_symbol(cid,sid,key,eq,expected):
     body=visit(cid,sid);definition=entry(cid,sid,key,eq)
     assert expected in definition['description'],(sid,key,definition)
     equation=body.locator('.paper-equation[data-equation="'+eq+'"]')
     assert equation.count()==1,(sid,eq,'equation missing')
     symbol=equation.locator('.katex-html [data-definition="'+definition['id']+'"], math [data-definition="'+definition['id']+'"]')
     # Native MathML and the visible KaTeX tree must both expose real click targets.
     symbol=symbol.first;symbol.wait_for();symbol.scroll_into_view_if_needed();y=symbol.bounding_box()['y'];symbol.click(force=True)
     popup=page.locator('#definition-popover:popover-open');popup.wait_for();assert expected in popup.inner_text()
     box=popup.bounding_box();assert box['x']>=0 and box['x']+box['width']<=width+1,(sid,width,box)
     page.locator('.definition-source-link').click();page.locator('.reference-target[data-definition-source]').wait_for()
     assert definition['source']['anchor'] in page.url,(sid,key,'source not exact')
     page.locator('.reference-return').click();page.wait_for_function('document.querySelector(".reference-return").hidden');page.wait_for_timeout(100)
     assert abs(symbol.bounding_box()['y']-y)<5,(sid,key,'reading position changed')
     evidence.append({'width':width,'section':sid,'equation':eq,'key':key,'definition':definition['id']})
    EMC='electromagnetic-compatibility';RD='robot-drive-engineering';AC='automatic-control'
    for key,meaning in [('U_扰','受扰端口'),('Z_共','共用回流'),('I_回','共用回流'),('M','互感'),('I_邻','相邻干扰'),('j','虚数单位'),('ω','角频率')]:open_symbol(EMC,'emc-1-1',key,'D.1.1.1',meaning)
    body=visit(EMC,'emc-1-1');eq=body.locator('.paper-equation[data-equation="D.1.1.1"]');expression=eq.locator('.paper-equation-scroll');expression.focus();page.keyboard.press('Enter')
    popup=page.locator('#definition-popover:popover-open');popup.wait_for();assert popup.locator('.definition-choice').count()==7
    page.keyboard.press('Escape');page.screenshot(path=str(OUT/('symbols-emc-'+str(width)+'.png')),full_page=True)
    # Same glyph, two actual meanings in one reading.
    open_symbol(EMC,'emc-6-2','S','D.6.2.1','磁芯')
    open_symbol(EMC,'emc-6-2','S','D.6.2.3','接收天线')
    open_symbol(EMC,'emc-8-1','R','D.8.1.1','理想电阻')
    open_symbol(EMC,'emc-8-1','R','D.8.1.4','串联损耗')
    open_symbol(EMC,'emc-7-2','t','D.7.2.1','时间')
    open_symbol(EMC,'emc-4-4','t','D.4.4.3','厚度')
    open_symbol(EMC,'emc-8-2','V^+','D.8.2.2','入射')
    open_symbol(EMC,'emc-8-2','V^-','D.8.2.2','反射')
    # Upper signs and hats carry meaning; matching only the base letter is wrong.
    open_symbol(RD,'rd-cascade-control','u_k^*','R.4.8','未限幅')
    open_symbol(RD,'rd-cascade-control','u_k','R.4.8','裁剪后')
    open_symbol(RD,'rd-edge-inference','hat:y_n','R.6.4','预测')
    open_symbol(RD,'rd-edge-inference','b','R.6.4','偏置')
    open_symbol(RD,'rd-edge-inference','b','R.5.4','输入电压')
    open_symbol(AC,'ac-4-1','K','U.4.1.1','增益')
    # Brief references only: do not relocate a detailed citation to the end.
    for cid,sid in [(EMC,'emc-1-2'),('electrical-materials','em-2-2'),(AC,'ac-homework3'),(RD,'rd-start'),('power-semiconductors','carrier-basics'),('hs-physics','physics-001-q01')]:
     body=visit(cid,sid);text=body.inner_text()
     for forbidden in ['教材依据：','课件对应：','原创教学讲解','核读资料与适用范围','ISBN','印刷第']:
      assert forbidden not in text,(sid,forbidden)
    assert not errors,errors;page.close()
   browser.close()
 finally:server.shutdown();server.server_close()
 (OUT/'reading-policy-interactions.json').write_text(json.dumps({'scope':'interface and local definitions, not a full content-quality certification','cases':evidence},ensure_ascii=False,indent=2))
 print('Brief references, local meanings, formula surfaces, keyboard and return positions verified.')
if __name__=='__main__':main()
