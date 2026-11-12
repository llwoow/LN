'use strict';

(() => {
  const courses = window.LN_COURSES;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const icon = (name) => '<svg class="icon" aria-hidden="true"><use href="#i-' + name + '"/></svg>';
  const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
  const categories = Object.fromEntries(Object.entries({ science: '理学', engineering: '工学', computing: '计算机' }).filter(([, name]) => courses.some((course) => course.category === name)));
  const palettes = [
    { id: 'ink', name: '黑白', color: '#414141' },
    { id: 'sage', name: '鼠尾草', color: '#65876b' },
    { id: 'indigo', name: '雾靛', color: '#727aa8' },
    { id: 'sand', name: '暖沙', color: '#a1875c' },
    { id: 'rose', name: '灰玫瑰', color: '#a47b88' }
  ];
  function readStored(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) ?? fallback; }
    catch { return fallback; }
  }
  function writeStored(key, value) {
    try { localStorage.setItem(key, value); }
    catch { $('#settings-storage-note').hidden = false; }
  }
  const stored = readStored('ln.preferences', {});
  const preferences = {
    mode: ['light', 'dark', 'system'].includes(stored?.mode) ? stored.mode : 'system',
    palette: palettes.some((palette) => palette.id === stored?.palette) ? stored.palette : 'ink'
  };
  const storedFavorites = readStored('ln.favorites', []);
  const favorites = new Set(Array.isArray(storedFavorites) ? storedFavorites.filter((id) => courses.some((course) => course.id === id)) : []);
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  const mobile = matchMedia('(max-width: 720px)');
  const main = $('#main');
  const sidebar = $('#sidebar');
  const dialog = $('#settings-dialog');
  const readerDock = $('#reader-dock');
  const readerDirectory = $('#reader-directory');
  const wideReader = matchMedia('(min-width: 1100px)');
  let questionNavigation = null;
  let collapsed = document.documentElement.dataset.sidebar === 'collapsed';
  let mobileOpen = false;
  let currentView = 'overview';
  let category = '全部';
  let query = '';
  let lastLibrary = 'overview';
  const isHighSchool = (course) => course.level === 'highschool';
  const courseHome = (course) => isHighSchool(course) ? '#highschool' : '#overview';
  const inHighSchool = () => currentView === 'highschool' || (['course','resources','practice'].includes(currentView) && isHighSchool(courses.find(c => c.id === location.hash.split('/')[1]) || {}));
  let toastTimer;
  const scriptLoads = new Map();
  const styleLoads = new Map();

  function loadScript(src) {
    if (!scriptLoads.has(src)) {
      const promise = new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = () => { script.remove(); scriptLoads.delete(src); reject(new Error('无法加载课程')); };
        document.head.append(script);
      });
      scriptLoads.set(src, promise);
    }
    return scriptLoads.get(src);
  }

  function loadStyle(href) {
    if (!styleLoads.has(href)) {
      const promise = new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet'; link.href = href;
        link.onload = resolve;
        link.onerror = () => { link.remove(); styleLoads.delete(href); reject(new Error('无法加载公式样式')); };
        document.head.append(link);
      });
      styleLoads.set(href, promise);
    }
    return styleLoads.get(href);
  }

  function applyTheme() {
    const theme = preferences.mode === 'system' ? (systemTheme.matches ? 'dark' : 'light') : preferences.mode;
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.palette = preferences.palette;
    $('meta[name="theme-color"]').content = theme === 'dark' ? '#202020' : '#ffffff';
    $('#quick-theme').innerHTML = icon(theme === 'dark' ? 'sun' : 'moon');
    $('#quick-theme').setAttribute('aria-label', '切换到' + (theme === 'dark' ? '日间' : '夜间') + '模式');
    $$('[data-mode]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.mode === preferences.mode)));
    $$('[data-palette-choice]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.paletteChoice === preferences.palette)));
    $('motor-winding-viewer')?.viewer?.invalidate();
  }

  function updateSidebar() {
    const open = mobile.matches ? mobileOpen : !collapsed;
    document.documentElement.dataset.sidebar = collapsed ? 'collapsed' : 'expanded';
    document.body.classList.toggle('sidebar-open', mobile.matches && mobileOpen);
    $('#sidebar-backdrop').hidden = !(mobile.matches && mobileOpen);
    sidebar.inert = !open;
    $('.workspace').inert = mobile.matches && mobileOpen;
    $('#sidebar-toggle').setAttribute('aria-expanded', String(open));
    $('#collapse-sidebar').setAttribute('aria-expanded', String(open));
    $('#sidebar-toggle').setAttribute('aria-label', open ? '收起侧栏' : '展开侧栏');
  }

  function setSidebar(open) {
    if (mobile.matches) mobileOpen = open;
    else {
      collapsed = !open;
      writeStored('ln.sidebar', collapsed ? 'collapsed' : 'expanded');
    }
    updateSidebar();
    if (open && mobile.matches) $('#collapse-sidebar').focus();
    else if (!open) $('#sidebar-toggle').focus();
  }

  function notify(message) {
    clearTimeout(toastTimer);
    $('#toast').textContent = message;
    $('#toast').classList.add('visible');
    toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 1800);
  }

  function updateFavoritesCount() {
    $('#favorite-count').textContent = favorites.size || '';
    renderSidebarCourses();
  }

  function renderSidebarCourses() {
    const selectedId = location.hash.split('/')[1];
    const row = (course) => '<a class="sidebar-course-link" href="#course/' + course.id + '"' + (currentView === 'course' && selectedId === course.id ? ' aria-current="page"' : '') + '>' + icon('book') + '<span class="sidebar-course-name">' + escapeHTML(course.title) + '</span>' + '</a>';
    const models = (course) => course.sections.filter((section) => section.kind === 'model').map((section) => '<a class="sidebar-model-link" href="#course/' + course.id + '/' + section.id + '"' + (selectedId === course.id && location.hash.split('/')[2] === section.id ? ' aria-current="page"' : '') + '>' + icon('cube') + '<span>' + escapeHTML(section.title) + '</span></a>').join('');
    $('#sidebar-course-list').innerHTML = courses.filter(course => isHighSchool(course) === inHighSchool()).map((course) => row(course) + models(course)).join('');
    $('#subject-nav').closest('.subject-group').hidden = inHighSchool();
    const saved = courses.filter((course) => favorites.has(course.id));
    $('#sidebar-favorites').hidden = !saved.length;
    $('#sidebar-favorite-list').innerHTML = saved.map(row).join('');
  }

  function favoriteButton(course, detail = false) {
    const saved = favorites.has(course.id);
    return '<button class="' + (detail ? 'secondary-button' : 'icon-button bookmark-button') + '" data-favorite="' + course.id + '" aria-label="' + (saved ? '取消收藏' : '收藏') + escapeHTML(course.title) + '" aria-pressed="' + saved + '">' + icon('star') + (detail ? (saved ? '已收藏' : '收藏') : '') + '</button>';
  }

  function courseRow(course) {
    return '<li class="course-row"><a class="course-link" href="#course/' + course.id + '"><span class="course-symbol">' + icon('book') + '</span><div class="course-text"><h2>' + escapeHTML(course.title) + '</h2><p>' + course.topics.map(escapeHTML).join(' · ') + '</p></div><span class="course-category">' + escapeHTML(isHighSchool(course) ? course.track : course.category) + '</span></a><a class="course-map-shortcut" href="#course/' + course.id + '/map" aria-label="打开' + escapeHTML(course.title) + '知识图谱">' + icon('network') + '<span>图谱</span></a>' + favoriteButton(course) + '</li>';
  }

  function renderRows() {
    const matching = courses.filter((course) => (currentView === 'favorites' || isHighSchool(course) === (currentView === 'highschool')) && (currentView !== 'favorites' || favorites.has(course.id)) && (category === '全部' || (currentView === 'highschool' ? course.track : course.category) === category) && [course.title, course.category, ...course.topics, ...(course.sections || []).flatMap((section) => [section.title, ...(section.keywords || [])])].join(' ').toLowerCase().includes(query.toLowerCase().trim()));
    $('#result-count').textContent = matching.length + ' 门' + (currentView === 'highschool' ? ' · 海南2027届' : '');
    const emptyFavorites = currentView === 'favorites' && !favorites.size;
    $('#course-list').innerHTML = matching.length ? matching.map(courseRow).join('') : '<li class="empty-state">' + icon(emptyFavorites ? 'star' : 'search') + '<h2>' + (emptyFavorites ? '暂无收藏' : '没有匹配的课程') + '</h2>' + (emptyFavorites ? '<a class="secondary-button" href="#overview">浏览课程</a>' : '<button class="secondary-button" data-clear-search>清除筛选</button>') + '</li>';
    $$('.filter-button').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    $$('[data-category]').forEach((link) => {
      const active = currentView === 'overview' && link.dataset.category === category;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }

  function renderOverview() {
    const title = currentView === 'highschool' ? '高中' : currentView === 'favorites' ? '收藏' : '课程';
    const filters = currentView === 'highschool' ? ['全部', '语言', '数理化生', '政史地'] : ['全部', ...Object.values(categories)];
    const libraryLink = currentView === 'highschool' ? '<a class="library-link" href="#highschool/resources">教材与来源</a>' : '';
    main.innerHTML = '<section aria-labelledby="page-title"><div class="page-heading"><div><h1 id="page-title">' + title + '</h1><p class="page-meta" id="result-count"></p></div>' + libraryLink + '<label class="course-search">' + icon('search') + '<input id="course-search" type="search" aria-label="搜索课程或知识点" placeholder="搜索课程…" value="' + escapeHTML(query) + '" autocomplete="off"></label></div><div class="filter-row"' + (filters.length < 3 ? ' hidden' : '') + ' aria-label="筛选学科">' + filters.map((name) => '<button class="filter-button" data-filter="' + name + '" aria-pressed="' + (name === category) + '">' + name + '</button>').join('') + '</div><ul class="course-list" id="course-list" aria-live="polite" aria-label="课程列表"></ul></section>';
    renderRows();
    $('#course-search').addEventListener('input', (event) => { query = event.target.value; renderRows(); });
  }

  function renderCourse(id, sectionId, anchor) {
    const course = courses.find((course) => course.id === id);
    if (!course) {
      main.innerHTML = '<div class="empty-state"><h2>课程不存在</h2><a class="secondary-button" href="#overview">返回课程</a></div>';
      return '课程';
    }
    if (!sectionId || sectionId === 'map') renderKnowledgeMap(course);
    else renderReader(course, sectionId, anchor);
    return course.title;
  }

  function courseViewNav(course, active) {
    const first = course.id === 'automatic-control'
      ? (course.sections.find(section => section.kind !== 'outline') || course.sections[0])
      : course.sections[0];
    const model = course.sections.find((section) => section.kind === 'model');
    const modelActive = model && location.hash.split('/')[2] === model.id;
    const material = course.sections.find(section=>section.supplement);
    const materialLink = material ? '<a href="#course/'+course.id+'/'+material.id+'">试卷讲解</a>' : '';
    const modelLink = model ? '<a href="#course/' + course.id + '/' + model.id + '"' + (modelActive ? ' aria-current="page"' : '') + '>' + icon('cube') + '3D 模型</a>' : '';
    return '<nav class="course-view-nav" aria-label="课程视图"><a href="#course/' + course.id + '/map"' + (active === 'map' ? ' aria-current="page"' : '') + '>' + icon('network') + '知识图谱</a><a href="#course/' + course.id + '/' + first.id + '"' + (active === 'reader' && !modelActive ? ' aria-current="page"' : '') + '>' + icon('book') + (course.outlineOnly ? '章节目录' : '章节阅读') + '</a>' + modelLink + materialLink + window.LNResources.button(course) + window.LNPractice.button(course) + '</nav>';
  }

  function renderKnowledgeMap(course) {
    main.classList.add('course-main', 'map-main');
    main.innerHTML = '<a class="back-link" href="' + courseHome(course) + '">' + icon('back') + (isHighSchool(course) ? '高中' : '课程') + '</a><section class="course-heading"><div><h1>' + escapeHTML(course.title) + '</h1><p class="page-meta">' + escapeHTML(course.category) + ' · ' + new Set(course.sections.filter(s=>!s.supplement).map((section) => section.group)).size + (isHighSchool(course) ? '册' : '章') + '</p></div>' + favoriteButton(course, true) + '</section>' + courseViewNav(course, 'map') + '<ln-knowledge-map></ln-knowledge-map>';
    $('ln-knowledge-map', main).course = course;
  }

  function renderReader(course, sectionId, anchor) {
    const selected = course.sections.find((section) => section.id === sectionId) || (!sectionId ? course.sections[0] : null);
    const groups = [...new Set(course.sections.map((section) => section.group))];
    main.classList.add('course-main');
    const sectionLink = section => '<a href="#course/' + course.id + '/' + section.id + '"' + (selected?.id === section.id ? ' aria-current="page"' : '') + '>' + escapeHTML(section.title) + '</a>';
    const outline = groups.map(group => {
      const items=course.sections.filter(s=>s.group===group),references=items.filter(s=>s.referenceOnly);
      return '<details class="outline-group"'+(selected?.group===group?' open':'')+'><summary>'+escapeHTML(group)+'</summary><nav aria-label="'+escapeHTML(group)+'">'+items.filter(s=>!s.referenceOnly).map(sectionLink).join('')+'</nav>'+(references.length?'<details class="outline-references"'+(selected?.group===group&&selected.referenceOnly?' open':'')+'><summary>专题、原题与资料</summary><nav aria-label="专题与资料">'+references.map(sectionLink).join('')+'</nav></details>':'')+'</details>';
    }).join('');
    main.innerHTML = '<a class="back-link" href="' + courseHome(course) + '">' + icon('back') + (isHighSchool(course) ? '高中' : '课程') + '</a><section class="course-heading"><div><h1>' + escapeHTML(course.title) + '</h1><p class="page-meta">' + escapeHTML(course.category) + ' · ' + new Set(course.sections.filter(s=>!s.supplement).map(s=>s.group)).size + (isHighSchool(course) ? '册' : '章') + '</p></div>' + favoriteButton(course, true) + '</section>' + courseViewNav(course, 'reader') + '<div class="reader-layout"><details class="reader-outline" id="reader-outline"' + (matchMedia('(min-width: 961px)').matches ? ' open' : '') + '><summary>目录</summary>' + outline + '</details><section class="lesson-column"><div class="lesson-tools" id="lesson-tools"></div><article class="lesson" id="lesson-body" data-lesson-key="' + (selected ? course.id + '/' + selected.id : '') + '" aria-busy="true">' + (selected ? '<p class="loading-state" role="status">加载中…</p>' : '<h2>章节不存在</h2>') + '</article><nav class="lesson-pagination" id="lesson-pagination" aria-label="章节翻页"></nav></section></div>';
    if (selected) {
      renderReaderDock(course, selected, outline);
      void loadLesson(course, selected, anchor);
    }
    else $('#lesson-body').setAttribute('aria-busy', 'false');
  }

  function readingSections(course, selected) { return selected.supplement ? course.sections.filter(s=>s.supplement===selected.supplement) : selected.referenceOnly ? course.sections : course.sections.filter(s=>!s.referenceOnly&&!s.supplement); }

  function renderReaderDock(course, selected, outline) {
    const sequence=readingSections(course,selected),index = sequence.indexOf(selected);
    const step = (section, label, symbol) => section ? '<a class="reader-dock-item" href="#course/' + course.id + '/' + section.id + '" aria-label="' + label + '：' + escapeHTML(section.title) + '" title="' + escapeHTML(section.title) + '">' + icon(symbol) + '<span>' + label + '</span></a>' : '<button class="reader-dock-item" disabled aria-label="' + label + '，已到课程边界">' + icon(symbol) + '<span>' + label + '</span></button>';
    readerDock.innerHTML = '<button class="reader-dock-item" data-reader-directory aria-label="目录与选题" title="目录与选题" aria-haspopup="dialog" aria-controls="reader-directory">' + icon('list') + '<span>目录</span></button><a class="reader-dock-item" href="#course/' + course.id + '/map" aria-label="知识图谱" title="知识图谱">' + icon('network') + '<span>图谱</span></a>' + step(sequence[index - 1], '上一节', 'back') + step(sequence[index + 1], '下一节', 'chevron') + '<button class="reader-dock-item" data-reader-top aria-label="回到顶部" title="回到顶部">' + icon('up') + '<span>顶部</span></button>';
    readerDock.hidden = false;
    document.body.classList.add('is-reading');
    $('#reader-directory-title').textContent = course.title + ' · 目录';
    $('#reader-directory-content').innerHTML = outline;
    $('#reader-directory-resource').innerHTML = window.LNResources.button(course, selected, '本节实作与资料') + window.LNPractice.button(course, selected, '本节练习');
  }

  function placeQuestionNavigation() {
    if (!questionNavigation) return;
    const header = $('#reader-question-slot'), directory = $('#reader-directory-question');
    (wideReader.matches ? header : directory).append(questionNavigation);
    header.hidden = !wideReader.matches;
    directory.hidden = wideReader.matches;
  }
  wideReader.addEventListener('change', placeQuestionNavigation);

  function openReaderDirectory() {
    if (!readerDirectory.open) readerDirectory.showModal();
    document.body.classList.add('directory-open');
    const content = $('#reader-directory-content');
    const current = $('[aria-current="page"]', content);
    if (current) {
      content.scrollTop += current.getBoundingClientRect().top - content.getBoundingClientRect().top - content.clientHeight / 2;
      current.focus({ preventScroll: true });
    }
  }

  function renderPdf(payload, body, anchor) {
    const initial = /^page-\d+$/.test(anchor || '') ? Number(anchor.slice(5)) - 1 : 0;
    let page = Math.max(0, Math.min(payload.pages.length - 1, initial));
    body.innerHTML = (payload.html || '') + '<h2>第二章作业</h2><div class="pdf-toolbar"><button class="secondary-button" data-pdf-prev aria-label="上一页">' + icon('back') + '</button><label>页码 <select id="pdf-page">' + payload.pages.map((_, i) => '<option value="' + i + '">' + (i + 1) + ' / ' + payload.pages.length + '</option>').join('') + '</select></label><button class="secondary-button" data-pdf-next aria-label="下一页">' + icon('chevron') + '</button><a class="secondary-button" href="' + payload.pdf + '" target="_blank" rel="noopener">原 PDF</a><a class="secondary-button" href="' + payload.pdf + '" download>下载</a></div><label class="question-jump">按题定位 <select id="homework-question">' + payload.questions.map((question) => '<option value="' + question.number + '">' + question.number + ' ' + escapeHTML(question.title) + '</option>').join('') + '</select></label><figure class="pdf-page"><a id="pdf-zoom" target="_blank" rel="noopener" aria-label="打开原尺寸作业页面" title="打开原尺寸"><img id="pdf-image" alt="第二章变压器作业" decoding="async"></a></figure><details class="review-notes"><summary>核查说明</summary><p>保留原题、原图和解答。第2-22题采用串联励磁支路参数，不能与并联铁耗、磁化参数混用；4.12% 是舍入结果。</p><p>第2-25题按题面和同阻抗角假设复算约70.10 A，原件也列出了教材68.79 A的差异。未取得教材详细解法，保留该差异。</p><p>第2-4题的励磁电流指净安匝对应的等效电流，不专指并联电抗支路的无功分量。负载时不能无条件用空载电流代替。</p></details>';
    const update = (requested, questionNumber) => {
      page = Math.max(0, Math.min(payload.pages.length - 1, requested));
      const image = $('#pdf-image', body), resource = payload.pages[page];
      $('#pdf-zoom', body).href = resource.src;
      image.src = resource.src; image.width = resource.width; image.height = resource.height;
      image.alt = '第二章变压器作业，第' + (page + 1) + '页，共' + payload.pages.length + '页';
      $('#pdf-page', body).value = String(page);
      $('[data-pdf-prev]', body).disabled = page === 0;
      $('[data-pdf-next]', body).disabled = page === payload.pages.length - 1;
      const question = payload.questions.find((question) => question.number === questionNumber) || payload.questions.find((question) => question.page === page + 1) || payload.questions.findLast((question) => question.page <= page + 1);
      if (question) $('#homework-question', body).value = question.number;
    };
    $('#pdf-page', body).addEventListener('change', (event) => update(Number(event.target.value)));
    $('#homework-question', body).addEventListener('change', (event) => {
      const question = payload.questions.find((question) => question.number === event.target.value);
      update(question.page - 1, question.number);
    });
    $('[data-pdf-prev]', body).addEventListener('click', () => update(page - 1));
    $('[data-pdf-next]', body).addEventListener('click', () => update(page + 1));
    update(page);
  }

  async function loadWindingAssets() {
    await loadScript('courses/electrical-machines/model/motor-winding-model.js');
    await loadScript('courses/electrical-machines/model/motor-winding-viewer.js');
  }

  function bindInlineModels(body) {
    $$('[data-inline-model]', body).forEach((details) => {
      const slot = $('.inline-model-slot', details);
      let revision = 0;
      const update = async () => {
        const current = ++revision;
        slot.replaceChildren();
        if (!details.open) return;
        const loading = document.createElement('p'); loading.setAttribute('role', 'status'); loading.textContent = '加载模型…';
        slot.append(loading);
        try {
          await loadWindingAssets();
          if (current !== revision || !details.open || !details.isConnected) return;
          const viewer = document.createElement('motor-winding-viewer');
          viewer.setAttribute('compact', '');
          slot.replaceChildren(viewer);
        } catch {
          if (current !== revision || !details.isConnected) return;
          slot.textContent = '模型加载失败。';
          const retry = document.createElement('button'); retry.className = 'secondary-button'; retry.textContent = '重试';
          retry.addEventListener('click', update); slot.append(retry);
        }
      };
      details.addEventListener('toggle', update);
    });
  }

  async function loadLesson(course, selected, anchor) {
    const key = course.id + '/' + selected.id;
    try {
      const outline = selected.kind === 'outline';
      if (!outline) await Promise.all([loadScript(selected.src), loadStyle('assets/katex/katex.min.css'), course.glossary ? loadScript(course.glossary) : Promise.resolve()]);
      if (selected.kind === 'model') await loadWindingAssets();
      if (selected.id.startsWith('transformer-')) await loadStyle('courses/electrical-machines/model/transformer-lesson.css');
      if (selected.supplement === 'physics-001') await Promise.all([loadScript('courses/hs-physics/physics-001/models.js'), loadScript('courses/hs-physics/physics-001/reader.js'), loadStyle('courses/hs-physics/physics-001/reader.css')]);
      const body = $('#lesson-body');
      if (!body || body.dataset.lessonKey !== key) return;
      const payload = outline ? {} : window.LN_LESSONS[key];
      if (outline) body.innerHTML = '<h2>' + escapeHTML(selected.title) + '</h2>';
      else if (selected.kind === 'pdf') renderPdf(payload, body, anchor);
      else if (selected.kind === 'document') {
        body.innerHTML = (payload.html || '') + '<h2>' + escapeHTML(selected.title) + '</h2><p><a class="secondary-button" href="' + payload.pdf + '" target="_blank" rel="noopener">原 PDF</a> <a class="secondary-button" href="' + payload.pdf + '" download>下载</a></p>' + payload.pages.map((page, index) => '<figure class="pdf-page pdf-reference-page"><a href="' + page.src + '" target="_blank" rel="noopener" aria-label="打开原尺寸速查页"><img src="' + page.src + '" width="' + page.width + '" height="' + page.height + '" loading="lazy" decoding="async" alt="变压器公式速查，第' + (index + 1) + '页"></a></figure>').join('');
      } else body.innerHTML = payload.html;
      body.querySelectorAll(':scope > [role="tabpanel"][hidden]').forEach(panel => { panel.hidden = false; });
      if (selected.id === 'transformer-sec21' || selected.id === 'transformer-sec28') {
        await loadScript('courses/electrical-machines/model/transformer-structure.js');
        if (selected.id === 'transformer-sec21') window.LN_MOUNT_TRANSFORMER_MODELS?.();
        if (selected.id === 'transformer-sec28') window.LN_MOUNT_TRANSFORMER_QUIZ?.();
      }
      const questionJump=body.querySelector('[data-homework-jump]');
      if (questionJump && anchor?.startsWith('question-')) questionJump.value=anchor.slice(9);
      questionJump?.addEventListener('change', event => {
        const question=payload.questions?.find(q=>q.number===event.target.value);
        if (question) {
          if (readerDirectory.open) readerDirectory.close();
          window.LNPublication.followReference('#course/'+course.id+'/'+selected.id+'/'+question.anchor,body);
        }
      });
      questionNavigation = questionJump?.closest('.homework-navigation') || null;
      placeQuestionNavigation();
      if (payload.html) {
        window.LNPublication.prepare(body, course, selected);
        window.LNGlossary.prepare(body, course, selected);
        window.LNResources.mountLesson(body);
        if (course.id === 'automatic-control') {
          await loadStyle('courses/automatic-control/control-lab.css');
          if (!body.isConnected || body.dataset.lessonKey !== key) return;
          if (['ac-3-3', 'ac-3-5', 'ac-3-6'].includes(selected.id)) {
            await loadScript('courses/automatic-control/control-lab.js');
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            window.LN_MOUNT_CONTROL_LABS?.(body);
          }
          if (selected.id === 'ac-4-2-2') {
            await Promise.all([
              loadStyle('courses/automatic-control/root-locus-lab.css'),
              loadScript('courses/automatic-control/root-locus-lab.js')
            ]);
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            window.LN_MOUNT_ROOT_LOCUS?.(body);
          }
        }
        bindInlineModels(body);
        if (course.id === 'electromagnetic-compatibility' && body.querySelector('[data-emc-lab]')) {
          // Educational models are optional; keep the static lesson readable if loading fails.
          try {
            await Promise.all([
              loadScript('courses/electromagnetic-compatibility/model/emc-labs.js'),
              loadStyle('courses/electromagnetic-compatibility/model/emc-labs.css')
            ]);
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            window.LN_MOUNT_EMC_LABS?.(body);
          } catch (error) {
            // Leave the source-backed explanation and static calculation visible.
          }
        }
        if (selected.supplement === 'physics-001') window.LNPhysics001.mount(body, payload);
      }
      body.setAttribute('aria-busy', 'false');
      body.classList.toggle('model-lesson', selected.kind === 'model');
      body.classList.toggle('pdf-lesson', selected.kind === 'pdf' || selected.kind === 'document');
      const resource = course.resources[selected.group];
      $('#lesson-tools').innerHTML = resource.links ? '<span>' + escapeHTML(selected.group) + '</span>' + resource.links.map(link => '<a href="' + escapeHTML(link.href) + '"' + (link.href.startsWith('https:') ? ' target="_blank" rel="noopener"' : '') + '>' + escapeHTML(link.label) + '</a>').join('') : '<span>' + escapeHTML(selected.group) + '</span><a href="courses/electrical-machines/files/' + resource.guide + '" target="_blank" rel="noopener">' + escapeHTML(resource.guideLabel || '讲义 PDF') + '</a><a href="courses/electrical-machines/files/' + resource.quickref + '" target="_blank" rel="noopener">速查 PDF</a>';
      const sequence=readingSections(course,selected),index = sequence.indexOf(selected);
      $('#lesson-pagination').innerHTML = (index > 0 ? '<a href="#course/' + course.id + '/' + sequence[index - 1].id + '">' + icon('back') + '上一节</a>' : '<span></span>') + (index < sequence.length - 1 ? '<a href="#course/' + course.id + '/' + sequence[index + 1].id + '">下一节' + icon('chevron') + '</a>' : '');
      window.LNPublication.settle(body, anchor);
    } catch (error) {
      const body = $('#lesson-body');
      if (body?.dataset.lessonKey === key) {
        body.setAttribute('aria-busy', 'false');
        body.innerHTML = '<p role="alert">课程加载失败。</p><button class="secondary-button" data-retry-lesson>重试</button>';
        $('[data-retry-lesson]', body).addEventListener('click', () => { void loadLesson(course, selected, anchor); });
      }
    }
  }

  function renderRoute() {
    window.LNPhysics001?.onRoute();
    window.LNPractice.onRoute();
    window.LNResources.onRoute();
    window.LNPublication.onRoute();
    window.LNGlossary.onRoute();
    const [view, id, sectionId, rawAnchor] = location.hash.slice(1).split('/');
    let anchor = rawAnchor;
    try { anchor = rawAnchor ? decodeURIComponent(rawAnchor) : ''; } catch { anchor = ''; }
    if (readerDirectory.open) readerDirectory.close();
    readerDock.hidden = true;
    readerDock.innerHTML = '';
    questionNavigation = null;
    for (const slot of [$('#reader-question-slot'), $('#reader-directory-question')]) {
      slot.replaceChildren(); slot.hidden = true;
    }
    document.body.classList.remove('is-reading', 'directory-open');
    main.classList.remove('course-main', 'map-main');
    currentView = ['favorites', 'course', 'highschool', 'resources', 'practice'].includes(view) ? view : 'overview';
    if (currentView !== 'course' && currentView !== 'favorites') {
      if (lastLibrary !== currentView) query = '';
      lastLibrary = currentView;
    }
    category = view === 'category' ? (categories[id] || '全部') : '全部';
    let title = currentView === 'highschool' ? '高中' : currentView === 'favorites' ? '收藏' : (category === '全部' ? '课程' : category);
    const outlineCourse = courses.find(course => course.id === id && course.outlineOnly);
    if (currentView === 'course') title = renderCourse(id, sectionId, anchor);
    else if (outlineCourse && ['practice', 'resources'].includes(currentView)) {
      title = outlineCourse.title;
      main.innerHTML = '<h1>' + escapeHTML(title) + '</h1><p>当前仅保留目录。</p><a class="secondary-button" href="#course/' + id + '">打开目录</a>';
    }
    else if (currentView === 'practice') { main.innerHTML = window.LNPractice.pageHtml(id); window.LNPractice.mount(main, id, sectionId); title = '练习'; }
    else if (currentView === 'resources') { main.innerHTML = window.LNResources.pageHtml(id); window.LNResources.bindPage(main, id, sectionId); title = '实作与资料'; }
    else if (currentView === 'highschool' && id === 'resources') { main.innerHTML = window.LNHighSchool.resourcesHtml(); title = '教材与来源'; }
    else renderOverview();
    $('#breadcrumb-current').textContent = title;
    document.title = title === '课程' ? 'LN' : title + ' · LN';
    $$('[data-nav]').forEach((link) => {
      if ((link.dataset.nav === currentView || (link.dataset.nav === 'highschool' && currentView === 'course' && inHighSchool())) && category === '全部') link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    if (currentView === 'course') {
      $$('[data-category]').forEach((link) => { link.classList.remove('active'); link.removeAttribute('aria-current'); });
    }
    renderSidebarCourses();
    mobileOpen = false;
    updateSidebar();
  }

  function openSettings() {
    if (mobile.matches && mobileOpen) setSidebar(false);
    if (!dialog.open) dialog.showModal();
  }

  function focusSearch() {
    if (['overview', 'favorites', 'highschool'].includes(currentView) && $('#course-search')) {
      if (mobile.matches && mobileOpen) setSidebar(false);
      $('#course-search').focus();
    } else {
      addEventListener('hashchange', () => $('#course-search')?.focus(), { once: true });
      location.hash = inHighSchool() ? 'highschool' : 'overview';
    }
  }

  readerDock.addEventListener('click', (event) => {
    if (event.target.closest('[data-reader-directory]')) openReaderDirectory();
    if (event.target.closest('[data-reader-top]')) {
      window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
      main.focus({ preventScroll: true });
    }
  });
  $('#close-reader-directory').addEventListener('click', () => readerDirectory.close());
  readerDirectory.addEventListener('close', () => document.body.classList.remove('directory-open'));
  readerDirectory.addEventListener('click', (event) => {
    if (event.target.closest('a')) { readerDirectory.close(); return; }
    if (event.target !== readerDirectory) return;
    const box = readerDirectory.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) readerDirectory.close();
  });
  $('#subject-nav').innerHTML = Object.entries(categories).map(([id, name]) => '<a class="nav-link subject-nav-link" href="#category/' + id + '" data-category="' + name + '"><span class="subject-dot" aria-hidden="true"></span>' + name + '</a>').join('');
  $('#palette-options').innerHTML = palettes.map((palette) => '<button class="palette-choice" data-palette-choice="' + palette.id + '" aria-pressed="false"><span class="palette-swatch" style="--swatch:' + palette.color + '">' + icon('check') + '</span>' + palette.name + '</button>').join('');
  $('#collapse-sidebar').addEventListener('click', () => setSidebar(false));
  $('#sidebar-toggle').addEventListener('click', () => setSidebar(mobile.matches ? !mobileOpen : collapsed));
  $('#sidebar-backdrop').addEventListener('click', () => setSidebar(false));
  sidebar.addEventListener('click', (event) => {
    if (event.target.closest('a') && mobile.matches && mobileOpen) {
      mobileOpen = false;
      updateSidebar();
      main.focus({ preventScroll: true });
    }
  });
  $('#search-shortcut').addEventListener('click', focusSearch);
  $('#open-settings').addEventListener('click', openSettings);
  $('#top-settings').addEventListener('click', openSettings);
  $('#close-settings').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  $('#quick-theme').addEventListener('click', () => {
    preferences.mode = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme();
    writeStored('ln.preferences', JSON.stringify(preferences));
  });
  $('#mode-options').addEventListener('click', (event) => {
    const button = event.target.closest('[data-mode]');
    if (!button) return;
    preferences.mode = button.dataset.mode;
    applyTheme();
    writeStored('ln.preferences', JSON.stringify(preferences));
  });
  $('#palette-options').addEventListener('click', (event) => {
    const button = event.target.closest('[data-palette-choice]');
    if (!button) return;
    preferences.palette = button.dataset.paletteChoice;
    applyTheme();
    writeStored('ln.preferences', JSON.stringify(preferences));
  });
  main.addEventListener('click', (event) => {
    const filter = event.target.closest('[data-filter]');
    if (filter) { category = filter.dataset.filter; renderRows(); }
    const button = event.target.closest('[data-favorite]');
    if (button) {
      const course = courses.find((course) => course.id === button.dataset.favorite);
      const saved = !favorites.has(course.id);
      saved ? favorites.add(course.id) : favorites.delete(course.id);
      writeStored('ln.favorites', JSON.stringify([...favorites]));
      updateFavoritesCount();
      if (currentView === 'favorites') {
        renderRows();
        ($('[data-favorite]', main) || $('.empty-state a', main) || $('#course-search')).focus();
      } else {
        button.setAttribute('aria-pressed', String(saved));
        button.setAttribute('aria-label', (saved ? '取消收藏' : '收藏') + course.title);
        if (currentView === 'course') button.innerHTML = icon('star') + (saved ? '已收藏' : '收藏');
      }
      notify(saved ? '已收藏' : '已取消收藏');
    }
    if (event.target.closest('[data-clear-search]')) {
      category = '全部';
      query = '';
      $('#course-search').value = '';
      renderRows();
      $('#course-search').focus();
    }
  });
  document.addEventListener('keydown', (event) => {
    if (dialog.open || readerDirectory.open || $('#resource-dialog').open || $('#practice-dialog').open) return;
    if (event.key === 'Escape' && mobileOpen) { setSidebar(false); return; }
    if (event.target.closest('input, textarea, select, [contenteditable]')) return;
    if (event.key === '/' || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k')) {
      event.preventDefault();
      focusSearch();
    }
    if (event.key === 'Tab' && mobileOpen) {
      const targets = $$('a, button, summary', sidebar).filter((element) => element.getClientRects().length);
      const first = targets[0], last = targets[targets.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  addEventListener('hashchange', () => { renderRoute(); window.scrollTo(0, 0); main.focus({ preventScroll: true }); });
  systemTheme.addEventListener('change', () => { if (preferences.mode === 'system') applyTheme(); });
  mobile.addEventListener('change', () => {
    mobileOpen = false;
    const wasInsideSidebar = sidebar.contains(document.activeElement);
    updateSidebar();
    if (wasInsideSidebar && sidebar.inert) $('#sidebar-toggle').focus();
  });
  updateFavoritesCount();
  applyTheme();
  renderRoute();
})();
