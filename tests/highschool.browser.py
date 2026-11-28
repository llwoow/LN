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
        assert page.locator('#course-list .course-link[href^="#course/hs-"]').count() == 9
        page.get_by_role('button', name='高中', exact=True).click()
        page.wait_for_function('document.querySelectorAll("#course-list .course-row").length === 9')
        courses = page.evaluate("LN_COURSES.filter(c => c.level === 'highschool')")
        for course in courses:
            page.goto(BASE+'#course/'+course['id'])
            page.locator('ln-knowledge-map').wait_for()
            assert page.locator('.map-node').count() == len(course['sections'])
            assert page.locator('[data-open-practice]').count() > 0
            assert page.locator('[data-open-resources]').count() > 0
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
        for course in courses:
            page.goto(BASE+'#course/'+course['id'])
            study = next(section for section in course['sections'] if section.get('supplement') == 'study')
            page.get_by_role('link', name='专题学习').click()
            body = page.locator(f'#lesson-body[data-lesson-key="{course["id"]}/{study["id"]}"][aria-busy="false"]')
            body.wait_for()
            assert body.locator('h2').count() == 1
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), (width, course['id'])
            launch = body.locator('a[data-open-practice]')
            question = launch.get_attribute('href').rsplit('/', 1)[1]
            launch.click()
            assert page.locator('[data-p-question]').input_value() == question
            page.get_by_role('link', name='返回正文').click()
            body.wait_for()
            page.wait_for_function('id => document.activeElement?.getAttribute("href")?.endsWith("/" + id)', arg=question)
        assert not errors, errors
        page.close()
    browser.close()
