"""Check the high-school outline and legacy routes at desktop and mobile sizes."""
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:4173/'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    for width in [1440, 390, 320]:
        page = browser.new_page(viewport={'width': width, 'height': 900})
        requests, errors = [], []
        page.on('request', lambda request: requests.append(request.url))
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(BASE)
        assert page.locator('#course-list a[href^="#course/hs-"]').count() == 0
        if width<1100:page.locator('#sidebar-toggle').click()
        page.locator('.highschool-entry').click()
        page.wait_for_function('document.querySelectorAll("#course-list .course-row").length === 9')
        courses = page.evaluate("LN_COURSES.filter(c => c.level === 'highschool')")
        for course in courses:
            page.goto(BASE+'#course/'+course['id'])
            page.locator('ln-knowledge-map').wait_for()
            assert page.locator('.map-node').count() == len(course['sections'])
            assert bool(page.locator('[data-open-practice]').count()) == (course['id'] in {'hs-physics','hs-english'})
            assert bool(page.locator('[data-open-resources]').count()) == (course['id'] in {'hs-physics','hs-english'})
            page.locator('.map-node').first.click()
            body = page.locator('#lesson-body[aria-busy="false"]')
            body.wait_for()
            assert body.locator(':scope > *').count() == 1
            assert body.locator('h2').inner_text() == course['sections'][0]['title']
            assert page.locator('#reader-dock').is_visible()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        page.goto(BASE+'#course/hs-physics/wl-01-k01/definition-passage-2')
        page.locator('#lesson-body h2', has_text='运动的描述').wait_for()
        page.goto(BASE+'#practice/hs-physics')
        page.locator('[data-practice-mode="local"]').wait_for()
        page.goto(BASE+'#highschool/resources')
        page.locator('h1', has_text='教材与来源').wait_for()
        assert page.locator('.source-citation').count() == 1
        assert page.locator('a[href^="https:"]').count() >= 28
        assert not any('/hs-' in url and '/lessons/' in url for url in requests)
        assert not errors, errors
        page.close()
    browser.close()
