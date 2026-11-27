"""CI-only check of LN under a repository Pages path, including lazy assets.

The static server exposes dist at /LN/ rather than the origin root. This catches
absolute root paths that work on the existing host but fail on GitHub Pages.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, runpy, shutil, tempfile, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
assignment = runpy.run_path(str(ROOT / 'scripts/build-reference-index.py'))['assignment']


def main():
    with tempfile.TemporaryDirectory(prefix='ln-pages-smoke-') as folder:
        mount = Path(folder)
        try:
            (mount / 'LN').symlink_to(ROOT / 'dist', target_is_directory=True)
        except OSError:
            shutil.copytree(ROOT / 'dist', mount / 'LN')
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(mount)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = 'http://127.0.0.1:' + str(server.server_address[1])
        base = origin + '/LN/'
        errors, failures, outside_prefix = [], [], []
        checked = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, channel=os.environ.get('LN_BROWSER_CHANNEL') or None, args=['--no-sandbox'])
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
                for width in (1280, 390, 320):
                    page.set_viewport_size({'width': width, 'height': 900})
                    page.goto(base + '#course/electromagnetic-compatibility/exam-review/emc-2-3')
                    page.locator('#exam-emc-2-3 .katex').first.wait_for()
                    assert page.locator('#emc-review-chapter').input_value() == '2'
                    assert not page.locator('#emc-exam-review [data-math-fallback]').count()
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), width
                    page.locator('#exam-emc-2-3').get_by_role('link', name='回查本节正文').click()
                    page.locator('#lesson-body .emc-review-inline').wait_for()
                    page.locator('#lesson-body .emc-review-inline').get_by_role('link').click()
                    page.locator('#exam-emc-2-3').wait_for()
                page.set_viewport_size({'width': 1280, 'height': 900})
                page.goto(base + '#overview', wait_until='networkidle')
                # New universal search: works from any route without leaving it.
                page.get_by_role('button', name='打开全站搜索').click()
                universal = page.get_by_role('searchbox', name='全站搜索关键词')
                universal.fill('FFT')
                page.locator('#ln-search-results a').first.wait_for()
                assert page.url.endswith('#overview')
                page.get_by_label('搜索范围', exact=True).select_option('higher')
                page.get_by_label('搜索类型', exact=True).select_option('课程')
                page.locator('#ln-search-results a[href="#course/digital-signal-processing"]').wait_for()
                page.get_by_role('button', name='关闭搜索').click()
                assert page.locator('[data-library-group="控制与信号"]').count() == 1
                search = page.get_by_role('searchbox', name='搜索课程或知识点')
                for width in (1280, 390, 320):
                    page.set_viewport_size({'width': width, 'height': 900})
                    search.fill('极零相消')
                    page.get_by_label('知识类型').select_option('公式')
                    result = page.get_by_role('link', name='公式 U.3.4.1', exact=False)
                    assert result.get_attribute('href') == '#course/automatic-control/ac-3-4/dominant-pole-response'
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), width
                    result.click()
                    page.locator('#dominant-pole-response.reference-target .equation-number').wait_for()
                    image = page.get_by_role('link', name='放大三项暂态贡献图').locator('img')
                    assert image.evaluate('img => img.getBoundingClientRect().width <= img.closest("figure").clientWidth')
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), width
                    page.locator('#dominant-pole-response [data-definition]').first.click()
                    page.locator('#definition-popover:popover-open').wait_for()
                    page.go_back()
                    assert search.input_value() == '极零相消'
                    page.get_by_label('知识类型').select_option('研究')
                    search.fill('GaN 动态导通电阻')
                    page.get_by_role('link', name='GaN 器件研究', exact=False).click()
                    page.locator('#gan-dynamic-ron.reference-target').wait_for()
                    page.go_back()
                    page.get_by_label('知识类型').select_option('习题')
                    search.fill('LC 低通 谐振电压增益')
                    page.get_by_role('link', name='计算 LC 低通的谐振电压增益', exact=False).click()
                    assert page.locator('[data-p-question]').input_value() == 'emc-lc-natural-frequency-gain'
                    page.locator('[data-p-value]').fill('6.02')
                    page.locator('[data-p-submit]').click()
                    assert '吻合' in page.locator('.practice-verdict').inner_text()
                    page.get_by_role('link', name='回查 · 5.2 反射式滤波器').click()
                    page.locator('#emc-lc-peaking.reference-target').wait_for()
                    page.goto(base + '#course/automatic-control/ac-5-1')
                    page.locator('#control-bode-reading').wait_for()
                    next_section = page.locator('#reader-dock').get_by_role('link', name='下一节', exact=False)
                    assert next_section.get_attribute('href') == '#course/automatic-control/ac-5-6-9'
                    next_section.click()
                    page.locator('#control-delay-budget').wait_for()
                    page.goto(base + '#course/automatic-control/ac-5-2')
                    page.locator('#lesson-body').get_by_role('link', name='从正弦测量到伯德图').wait_for()
                    page.goto(base + '#overview', wait_until='networkidle')
                page.set_viewport_size({'width': 1280, 'height': 900})
                page.goto(base + '#practice/automatic-control/ac-3-4')
                page.locator('[data-practice-mode="sources"]').click()
                source = page.locator('[data-source-id="mit-dynamics-2-004-ps6"]')
                assert source.get_by_role('link', name='原题').get_attribute('href').endswith('/ps6/')
                assert source.get_by_role('link', name='课程解答').get_attribute('href').endswith('/ps6soln/')
                # Cross-course network: real links, filter, reader anchor and return.
                for width in (1280, 390, 320):
                    page.set_viewport_size({'width': width, 'height': 900})
                    page.goto(base + '#knowledge', wait_until='networkidle')
                    page.locator('ln-knowledge-map .map-node').first.wait_for()
                    expected_nodes = page.evaluate('LN_CROSS_KNOWLEDGE_DATA.nodes.length')
                    assert page.locator('ln-knowledge-map .map-node').count() == expected_nodes
                    assert page.locator('ln-knowledge-map .map-edge-order').count() == 0
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                    page.locator('#cross-course-filter').select_option('power-semiconductors')
                    page.wait_for_url('**/#knowledge/power-semiconductors')
                    page.locator('ln-knowledge-map .map-node').first.wait_for()
                    expected_filtered = page.evaluate("LNCrossKnowledge.graphCourse('power-semiconductors').sections.length")
                    assert 0 < expected_filtered < expected_nodes
                    assert page.locator('ln-knowledge-map .map-node').count() == expected_filtered
                    page.locator('ln-knowledge-map .map-node[href*="cross-oxide-device"]').evaluate("el => { location.hash = el.getAttribute('href'); }")
                    body=page.locator('#lesson-body[data-lesson-key="power-semiconductors/vdmos-structure"][aria-busy=false]')
                    body.wait_for(timeout=30000)
                    body.locator('#cross-oxide-device').wait_for()
                    body.locator('#cross-link-oxide-device-oxide-emc').click()
                    target=page.locator('#lesson-body[data-lesson-key="electromagnetic-compatibility/emc-1-4"][aria-busy=false]')
                    target.wait_for(timeout=30000)
                    target.locator('#cross-oxide-emc').wait_for()
                    page.go_back()
                    body.wait_for(timeout=30000)
                    body.locator('#cross-oxide-device').wait_for()
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                page.set_viewport_size({'width': 1280, 'height': 900})
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
                # Source-backed audit remains under the same Pages subdirectory.
                page.goto(base + 'audit/', wait_until='networkidle')
                page.locator('.audit-stat').first.wait_for(timeout=15000)
                assert page.locator('.audit-stat').count() == 4
                assert '接入与验收' in page.locator('main').inner_text()
                assert page.locator('option[value="hs-chinese"]').count()
                # A claim imported from README/PR-style documentation never counts as verification.
                page.evaluate("""() => localStorage.setItem('ln.audit.records.v1',
                    JSON.stringify([{id:'ac-3-5',courseId:'automatic-control',status:'已验证',
                      sourceKind:'文档声明',evidenceType:'文档描述',evidenceUrl:'https://example.org/plan',
                      revision:'89fde344661ea22751b1ff87880f9433087224eb'}]))""")
                page.reload(wait_until='networkidle')
                assert page.locator('.audit-stat').first.locator('strong').inner_text() == '0'
                page.evaluate("() => localStorage.removeItem('ln.audit.records.v1')")
                page.reload(wait_until='networkidle')
                page.screenshot(path=str(evidence / 'audit-1280.png'), full_page=True)
                page.locator('#audit-nav [data-view="catalog"]').click()
                assert page.locator('a[href*="/map"]').count(), 'knowledge map links must exist'
                page.locator('#audit-nav [data-view="skeleton"]').click()
                assert '骨架内容清单' in page.locator('h1').inner_text()
                page.locator('#audit-nav [data-view="edit"]').click()
                assert page.locator('#record-form select[name="id"] option').count() > 100
                page.locator('#record-form select[name="id"]').select_option('electrical-machines/transformer-sec27')
                assert page.locator('#record-form select[name="anchor"] option').count() > 1
                assert page.locator('#record-form select[name="impact"]').input_value() == '一般'
                assert page.locator('#record-form select[name="evidenceType"]').input_value() == '未提供'
                page.locator('#record-form select[name="anchor"]').select_option(index=1)
                page.locator('#record-form select[name="status"]').select_option('明确存在的问题')
                page.locator('#record-form textarea[name="actualContent"]').fill('Browser test fixture, not a course finding.')
                page.locator('#record-form textarea[name="reproduction"]').fill('Browser fixture: save then delete this local record.')
                page.locator('#record-form button[type="submit"]').click()
                assert page.evaluate("JSON.parse(localStorage.getItem('ln.audit.records.v1')).length") == 1
                page.locator('#audit-delete').click()
                assert page.evaluate("JSON.parse(localStorage.getItem('ln.audit.records.v1')).length") == 0
                assert page.locator('#record-form select[name="status"]').input_value() == '部分接入'
                page.set_viewport_size({'width': 390, 'height': 900})
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), 'audit viewport overflow'
                page.screenshot(path=str(evidence / 'audit-390.png'), full_page=True)
                page.set_viewport_size({'width': 1280, 'height': 900})
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
