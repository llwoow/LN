"""CI-only check of LN under a repository Pages path, including lazy assets.

The static server exposes dist at /LN/ rather than the origin root. This catches
absolute root paths that work on the existing host but fail on GitHub Pages.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, runpy, tempfile, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
assignment = runpy.run_path(str(ROOT / 'scripts/build-reference-index.py'))['assignment']


def main():
    with tempfile.TemporaryDirectory(prefix='ln-pages-smoke-') as folder:
        mount = Path(folder)
        (mount / 'LN').symlink_to(ROOT / 'dist', target_is_directory=True)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(mount)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = 'http://127.0.0.1:' + str(server.server_address[1])
        base = origin + '/LN/'
        errors, failures, outside_prefix = [], [], []
        checked = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
                page.on('pageerror', lambda error: errors.append(str(error)))
                def response(res):
                    if res.status >= 400:
                        failures.append([res.status, res.url])
                    if res.url.startswith(origin + '/') and not res.url.startswith(base):
                        outside_prefix.append(res.url)
                page.on('response', response)
                page.goto(base + '#overview', wait_until='networkidle')
                assert page.locator('#course-list').count() == 1
                # All actual HTML courses are selected from source, including future merges.
                for path in sorted((ROOT / 'courses').glob('*/manifest.js')):
                    course = assignment(path)
                    readings = [s for s in course['sections'] if s.get('kind') == 'html']
                    if not readings:
                        continue
                    cid = course['id']
                    page.goto(base + '#course/' + cid + '/map', wait_until='networkidle')
                    assert page.locator('ln-knowledge-map').count() == 1, cid
                    # First and last readings exercise course bundles and lazy definition indexes.
                    for lesson in {s['id']: s for s in (readings[0], readings[-1])}.values():
                        page.goto(base + '#course/' + cid + '/' + lesson['id'], wait_until='networkidle')
                        body = page.locator('#lesson-body[data-lesson-key="' + cid + '/' + lesson['id'] + '"][aria-busy=false]')
                        body.wait_for(timeout=30000)
                        assert body.locator('h2').count(), (cid, lesson['id'])
                        assert not body.locator('p[role=alert]').count(), (cid, lesson['id'])
                        assert not body.locator('.katex-error').count(), (cid, lesson['id'])
                        checked.append(cid + '/' + lesson['id'])
                for route, title in [('resources', '实作与资料'), ('practice', '练习')]:
                    page.goto(base + '#' + route, wait_until='networkidle')
                    # Both catalogs are loaded relative to the repository path.
                    assert title in page.locator('main').inner_text(), route
                # References replace source files across affected readers and small viewports.
                affected = ['#course/electrical-machines/transformer-homework',
                            '#course/electrical-machines/transformer-quickref',
                            '#highschool/resources', '#course/hs-physics/physics-001',
                            '#course/hs-physics/physics-001-q15']
                evidence = ROOT / 'nov13-browser-artifacts'
                evidence.mkdir(exist_ok=True)
                for width in [1280, 390, 320]:
                    page.set_viewport_size({'width': width, 'height': 900})
                    for route in affected:
                        page.goto(base + route, wait_until='networkidle')
                        if route.startswith('#course/'):
                            page.locator('#lesson-body[aria-busy="false"]').wait_for()
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), (width, route)
                        assert not page.locator('img[src*="/originals/"]').count(), route
                        if route.endswith('physics-001-q15'):
                            assert page.locator('#figure-q15-caliper img').count() == 1
                            if width <= 390:
                                assert page.locator('.instrument-scroll').evaluate('e=>e.scrollWidth>e.clientWidth')
                            if width == 390:
                                page.locator('#figure-q15-caliper').screenshot(path=str(evidence / 'references-caliper-390.png'))
                        local_documents = page.locator('a[href]').evaluate_all(r"""nodes => nodes.map(a => new URL(a.href, location.href)).filter(u => u.origin === location.origin && /\.(pdf|xlsx?|docx?|pptx?|zip|7z|rar)$/i.test(u.pathname)).map(u => u.href)""")
                        assert not local_documents, (route, local_documents)
                        if width == 390 and route in ['#course/electrical-machines/transformer-quickref', '#highschool/resources', '#course/hs-physics/physics-001']:
                            page.screenshot(path=str(evidence / ('references-' + route.split('/')[-1] + '-390.png')), full_page=True)
                page.set_viewport_size({'width': 1280, 'height': 900})
                # Authored program downloads work at the /LN/ prefix. Source documents are external citations.
                for artifact in ['courses/robot-drive-engineering/files/c_foundations.c',
                                 'assets/practice/homework/reproduce.py']:
                    res = page.request.get(base + artifact)
                    assert res.ok, (artifact, res.status)
                    assert len(res.body()) > 100, artifact
                assert not errors, errors
                assert not failures, failures
                assert not outside_prefix, outside_prefix
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
    print(json.dumps({'base_path': '/LN/', 'readings': checked, 'ok': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
