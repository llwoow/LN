"""Generate the explicitly authored A/B2 training papers from a clean browser.
No learner data. Outputs are CI artifacts, not automatically deployed to Pages.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import tempfile, threading, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'pdf-output'
OUT.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as temp:
    os.symlink(ROOT/'dist',Path(temp)/'LN',target_is_directory=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=temp))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/LN/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':900,'height':1200})
            page.goto(base+'#course/electromagnetic-compatibility/exam-review/test-a')
            page.locator('#emc-test-Q30').wait_for()
            for version in ['A','B2']:
                for mode in ['exam','answer','combined']:
                    doc=page.evaluate("""async ([version,mode])=>LNPrint.build({type:'paper',version,mode,paper:'A4',figures:true},{cancelled:false},()=>{})""",[version,mode])
                    target=browser.new_page(viewport={'width':900,'height':1200})
                    target.set_content('<!doctype html><html lang="zh-CN" data-theme="light" data-palette="default"><head><meta charset="utf-8"><base href="'+base+'">' + ''.join('<link rel="stylesheet" href="'+x+'">' for x in doc['css'])+'<style>@page{size:A4;margin:16mm 14mm 18mm}</style></head><body class="ln-print-document"><main class="ln-print-main lesson publication-body">'+doc['body']+'</main></body></html>',wait_until='networkidle')
                    target.evaluate('document.fonts.ready')
                    assert target.locator('.ln-print-question').count()==(30 if version=='A' else 12)*(2 if mode=='combined' else 1)
                    if mode=='exam':assert target.get_by_text('参考答案与评分',exact=True).count()==0
                    path=OUT/f'LN-EMC-CH1-{version}-{mode}.pdf'
                    target.pdf(path=str(path),prefer_css_page_size=True,print_background=True,display_header_footer=True,
                        header_template='<span></span>',footer_template='<div style="font-size:9px;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>')
                    assert path.stat().st_size>5000
                    target.close()
            browser.close()
    finally:server.shutdown();server.server_close()
