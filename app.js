'use strict';

(() => {
  const courses = window.LN_COURSES;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const icon = (name) => '<svg class="icon" aria-hidden="true"><use href="#i-' + name + '"/></svg>';
  const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
  const isHighSchool = (course) => course.level === 'highschool';
  const groupFor = course => isHighSchool(course) ? '高中' : course.libraryGroup;
  const categories = Object.fromEntries(Object.entries({ science: '理学', engineering: '工学', computing: '计算机' }).filter(([, name]) => courses.some((course) => course.category === name)));
  const libraryGroups = Object.fromEntries(Object.entries({
    electrical: '电气工程', control: '控制与信号', electronics: '电子与嵌入式',
    materials: '材料与能源', general: '通用能力', mathematics: '数学与建模', highschool: '高中'
  }).filter(([, name]) => courses.some(course => groupFor(course) === name)));
  for (const course of courses) {
    if (!Object.values(libraryGroups).includes(groupFor(course)))
      libraryGroups['group-' + course.id] = groupFor(course);
  }
  const matchesCategory = (course, value) => value === '全部' || groupFor(course) === value || course.category === value;
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
  const practiceReturn = $('[data-practice-return]');
  const wideReader = matchMedia('(min-width: 1100px)');
  let questionNavigation = null;
  let collapsed = document.documentElement.dataset.sidebar === 'collapsed';
  let mobileOpen = false;
  let currentView = 'overview';
  let category = '全部';
  let query = '';
  let lastLibrary = 'overview';
  const knowledgeKinds = ['概念', '公式', '方法', '习题', '难点', '跨学科', '研究'];
  const knowledgePageSize = 12;
  let knowledgeEntries;
  let knowledgeKind = '';
  let knowledgeLimit = knowledgePageSize;
  const courseHome = (course) => isHighSchool(course) ? '#category/highschool' : '#overview';
  const navState = readStored('ln.navigation.v1', {});
  const openGroups = new Set(Array.isArray(navState?.groups) ? navState.groups : []);
  let sidebarMode = 'courses';
  let lastSidebarRoute = '';
  let recent = readStored('ln.recent.v1', []);
  if (!Array.isArray(recent)) recent = [];
  const saveGroups = () => writeStored('ln.navigation.v1', JSON.stringify({groups:[...openGroups]}));
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
    const selected = courses.find(c => c.id === selectedId);
    const groupNames = Object.values(libraryGroups);
    const sidebarRoute = currentView === 'course' ? 'course/' + selectedId : currentView;
    if (lastSidebarRoute !== sidebarRoute) {
      lastSidebarRoute = sidebarRoute;
      if (currentView === 'course' && selected) {
        openGroups.add(groupFor(selected));
        sidebarMode = 'directory';
        saveGroups();
      } else sidebarMode = 'courses';
    }
    if (!Array.isArray(navState?.groups) && !openGroups.size && groupNames.length) openGroups.add(groupNames[0]);
    const sectionId = location.hash.split('/')[2];
    const directory = selected && currentView === 'course' ? listedSections(selected) : [];
    const activeGroup = directory.find(section => section.id === sectionId)?.group ?? directory[0]?.group;
    const useDirectory = sidebarMode === 'directory' && directory.length;
    $('#sidebar-nav-mode').hidden = !directory.length;
    for (const btn of $$('[data-sidebar-mode]')) btn.setAttribute('aria-pressed', String(btn.dataset.sidebarMode === sidebarMode));
    $('#sidebar-course-list').innerHTML = useDirectory
      ? '<div class="ln-sidebar-directory"><a class="sidebar-course-link" href="#course/' + selected.id + '/map">' + icon('network') + '知识图谱</a>' +
        (selected.id === 'electromagnetic-compatibility' ? '<a class="sidebar-course-link" href="#course/' + selected.id + '/exam-review">考试复习</a>' : '') +
        (selected.workedExercises?.length ? '<a class="sidebar-course-link" href="#course/' + selected.id + '/worked-exercises">已做题详解</a>' : '') +
        (!selected.outlineOnly ? '<a class="sidebar-course-link" href="#practice/' + selected.id + '">习题自测</a><a class="sidebar-course-link" href="#resources/' + selected.id + '">实作与资料</a>' : '') +
        [...new Set(directory.map(s => s.group))].map(group => '<details class="ln-course-group"' + (activeGroup === group ? ' open' : '') + '><summary>' + escapeHTML(group) + '</summary><nav>' + directory.filter(s => s.group === group).map(s => '<a class="ln-section-link" href="#course/' + selected.id + '/' + s.id + '"' + (sectionId === s.id ? ' aria-current="page"' : '') + '>' + escapeHTML(s.title) + '</a>').join('') + '</nav></details>').join('') + '</div>'
      : groupNames.map(group => {
        const groupCourses = courses.filter(course => groupFor(course) === group);
        return '<details class="ln-course-group" data-library-group="' + escapeHTML(group) + '"' + (openGroups.has(group) ? ' open' : '') + '><summary>' + escapeHTML(group) + '<small>' + groupCourses.length + '</small></summary><nav>' + groupCourses.map(c => row(c) + models(c)).join('') + '</nav></details>';
      }).join('');
    $('#subject-nav').closest('.subject-group').hidden = true;
    const historyList = $('#ln-recent-list');
    historyList.innerHTML = recent.filter(r => courses.some(c => c.id === r.course && c.sections.some(s => s.id === r.section))).slice(0,3).map(r => {
      const c = courses.find(c => c.id === r.course), s = c.sections.find(s => s.id === r.section);
      return '<a class="ln-section-link" href="#course/' + c.id + '/' + s.id + '"><strong>' + escapeHTML(c.title) + '</strong><small>' + escapeHTML(s.title) + '</small></a>';
    }).join('');
    $('#ln-recent').hidden = !historyList.children.length;
    const saved = courses.filter((course) => favorites.has(course.id));
    $('#sidebar-favorites').hidden = !saved.length;
    $('#sidebar-favorite-list').innerHTML = saved.map(row).join('');
  }

  function favoriteButton(course, detail = false) {
    const saved = favorites.has(course.id);
    return '<button class="' + (detail ? 'secondary-button' : 'icon-button bookmark-button') + '" data-favorite="' + course.id + '" aria-label="' + (saved ? '取消收藏' : '收藏') + escapeHTML(course.title) + '" aria-pressed="' + saved + '">' + icon('star') + (detail ? (saved ? '已收藏' : '收藏') : '') + '</button>';
  }

  function courseRow(course) {
    return '<li class="course-row"><a class="course-link" href="#course/' + course.id + '"><span class="course-symbol">' + icon('book') + '</span><div class="course-text"><h2>' + escapeHTML(course.title) + '</h2><p>' + course.topics.map(escapeHTML).join(' · ') + '</p></div><span class="course-category">' + escapeHTML(groupFor(course)) + '</span></a><a class="course-map-shortcut" href="#course/' + course.id + '/map" aria-label="打开' + escapeHTML(course.title) + '知识图谱">' + icon('network') + '<span>图谱</span></a>' + favoriteButton(course) + '</li>';
  }

  function buildKnowledgeEntries() {
    const index = window.LN_PUBLICATION_INDEX || {};
    const questions = window.LN_PRACTICE_BANK.questions;
    const questionKinds = { single: '单选 选择题', multi: '多选 选择题', numeric: '计算 数值', open: '问答 分析' };
    return courses.flatMap(course => {
      const rows = [];
      const sections = new Map(course.sections.map(section => [section.id, section]));
      const add = (section, kind, title, route, terms = '') => {
        const label = section.kind === 'outline' ? '目录' : kind;
        rows.push({ course, section, kind, label, title, route,
          titleKey: title.normalize('NFKC').toLowerCase(),
          search: [title, kind, terms, section.title, section.group, course.title].join(' ').normalize('NFKC').toLowerCase() });
      };
      for (const section of listedSections(course)) {
        const route = '#course/' + course.id + '/' + section.id;
        add(section, '概念', section.title, route, (section.keywords || []).join(' '));
        const reading = index[course.id]?.sections[section.id];
        for (const item of reading?.headings || []) {
          if (item.title !== section.title || item.kind !== '概念') add(section, item.kind, item.title, route + '/' + encodeURIComponent(item.anchor), item.terms);
        }
        for (const formula of reading?.equations || []) {
          if (formula.number) add(section, '公式', formula.number, route + '/' + encodeURIComponent(formula.anchor), [formula.terms || '', formula.number.replaceAll('.', '-')].join(' '));
        }
      }
      for (const question of questions.filter(item => item.course === course.id)) {
        const section = sections.get(question.readingSection || question.sections[0]);
        if (!section) continue;
        add(section, '习题', question.title, '#practice/' + course.id + '/' + section.id + '/' + encodeURIComponent(question.id),
          [questionKinds[question.type], ...question.skills, question.prompt].join(' '));
      }
      return rows;
    });
  }

  function renderKnowledgeResults() {
    const results = $('#knowledge-search-results');
    const text = query.trim().normalize('NFKC').toLowerCase();
    results.hidden = !text;
    if (!text) return 0;
    knowledgeEntries ||= buildKnowledgeEntries();
    const tokens = text.split(/\s+/);
    const matches = knowledgeEntries.filter(row =>
      (currentView !== 'favorites' || favorites.has(row.course.id)) &&
      matchesCategory(row.course, category) &&
      (!knowledgeKind || row.kind === knowledgeKind) && tokens.every(token => row.search.includes(token)));
    const rank = row => row.titleKey === text ? 0 : row.titleKey.includes(text) ? 1 : row.route.endsWith('/' + row.section.id) ? 3 : 2;
    matches.sort((a, b) => rank(a) - rank(b));
    $('#knowledge-result-count').textContent = matches.length ? '找到 ' + matches.length + ' 项' : '没有匹配的知识项';
    $('#knowledge-result-list').innerHTML = matches.slice(0, knowledgeLimit).map(row => '<li><a href="' + escapeHTML(row.route) + '"><span class="knowledge-result-kind">' + escapeHTML(row.label) + '</span><span><strong>' + escapeHTML(row.title) + '</strong><small>' + escapeHTML(row.course.title + ' · ' + row.section.title) + '</small></span></a></li>').join('');
    $('[data-more-knowledge]', results).hidden = matches.length <= knowledgeLimit;
    return matches.length;
  }

  function renderRows() {
    const matching = courses.filter((course) => (currentView !== 'favorites' || favorites.has(course.id)) && matchesCategory(course, category) && [course.title, course.category, groupFor(course), course.track, ...course.topics, ...(course.sections || []).flatMap((section) => [section.title, ...(section.keywords || [])])].join(' ').toLowerCase().includes(query.toLowerCase().trim()));
    const highSchoolFilter = currentView === 'overview' && category === libraryGroups.highschool;
    $('#result-count').textContent = matching.length + ' 门' + (highSchoolFilter ? ' · 海南2027届' : '');
    $('#highschool-sources').hidden = !highSchoolFilter;
    const emptyFavorites = currentView === 'favorites' && !favorites.size;
    const knowledgeMatches = renderKnowledgeResults();
    $('#result-count').hidden = !matching.length && !!knowledgeMatches;
    $('#course-list').innerHTML = matching.length ? matching.map(courseRow).join('') : knowledgeMatches ? '' : '<li class="empty-state">' + icon(emptyFavorites ? 'star' : 'search') + '<h2>' + (emptyFavorites ? '暂无收藏' : '没有匹配的课程') + '</h2>' + (emptyFavorites ? '<a class="secondary-button" href="#overview">浏览课程</a>' : '<button class="secondary-button" data-clear-search>清除筛选</button>') + '</li>';
    $$('.filter-button').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    $$('[data-category]').forEach((link) => {
      const active = currentView === 'overview' && link.dataset.category === category;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }

  function renderOverview() {
    const title = currentView === 'favorites' ? '收藏' : '课程';
    const filters = [...new Set(['全部', ...Object.values(libraryGroups), category])];
    const libraryLink = '<a id="highschool-sources" class="library-link" href="#highschool/resources" hidden>教材与来源</a>';
    main.innerHTML = '<section aria-labelledby="page-title"><div class="page-heading"><div><h1 id="page-title">' + title + '</h1><p class="page-meta" id="result-count"></p></div>' + libraryLink + '<label class="course-search">' + icon('search') + '<input id="course-search" type="search" aria-label="搜索课程或知识点" placeholder="搜索课程、知识点…" value="' + escapeHTML(query) + '" autocomplete="off"></label></div><div class="filter-row"' + (filters.length < 3 ? ' hidden' : '') + ' aria-label="筛选学科">' + filters.map((name) => '<button class="filter-button" data-filter="' + name + '" aria-pressed="' + (name === category) + '">' + name + '</button>').join('') + '</div><section id="knowledge-search-results" aria-labelledby="knowledge-results-title" hidden><div class="knowledge-results-head"><h2 id="knowledge-results-title">相关知识</h2><select id="knowledge-kind" aria-label="知识类型"><option value="">所有类型</option>' + knowledgeKinds.map(kind => '<option>' + kind + '</option>').join('') + '</select></div><p id="knowledge-result-count" class="page-meta" role="status"></p><ul id="knowledge-result-list"></ul><button class="secondary-button" data-more-knowledge hidden>显示更多</button></section><ul class="course-list" id="course-list" aria-live="polite" aria-label="课程列表"></ul></section>';
    $('#knowledge-kind').value = knowledgeKind;
    renderRows();
    $('#course-search').addEventListener('input', (event) => { query = event.target.value; knowledgeLimit = knowledgePageSize; renderRows(); });
    $('#knowledge-kind').addEventListener('change', (event) => { knowledgeKind = event.target.value; knowledgeLimit = knowledgePageSize; renderRows(); });
    $('[data-more-knowledge]').addEventListener('click', () => {
      const firstNewRow = knowledgeLimit;
      knowledgeLimit += knowledgePageSize;
      renderKnowledgeResults();
      $$('#knowledge-result-list a')[firstNewRow]?.focus();
    });
  }

  function renderCourse(id, sectionId, anchor) {
    const course = courses.find((course) => course.id === id);
    if (!course) {
      main.innerHTML = '<div class="empty-state"><h2>课程不存在</h2><a class="secondary-button" href="#overview">返回课程</a></div>';
      return '课程';
    }
    if (!sectionId || sectionId === 'map') renderKnowledgeMap(course);
    else if (sectionId === 'exam-review' && course.id === 'electromagnetic-compatibility') renderEmcExam(course, anchor);
    else if (sectionId === 'worked-exercises') renderWorkedExercises(course);
    else renderReader(course, sectionId, anchor);
    return course.title;
  }

  function courseViewNav(course, active) {
    const first = course.sections.find(section => section.id === course.defaultSection) || (course.id === 'automatic-control'
      ? (course.sections.find(section => section.kind !== 'outline') || course.sections[0])
      : course.sections[0]);
    const model = course.sections.find((section) => section.kind === 'model');
    const selectedId = location.hash.split('/')[2];
    const modelActive = model && selectedId === model.id;
    const material = course.sections.find(section=>section.supplement === 'physics-001');
    const study = course.sections.find(section=>section.supplement === 'study');
    const english = course.sections.find(section=>section.supplement === 'english-2027');
    const supplement = course.sections.find(section=>section.id === selectedId)?.supplement;
    const supplementalLink = (section, label) => section ? '<a href="#course/' + course.id + '/' + section.id + '"' + (supplement === section.supplement ? ' aria-current="page"' : '') + '>' + label + '</a>' : '';
    const materialLink = supplementalLink(material, '试卷讲解');
    const studyLink = supplementalLink(study, '专题学习');
    const englishLink = supplementalLink(english, '英语讲义');
    const examLink = course.id === 'electromagnetic-compatibility' ? '<a href="#course/' + course.id + '/exam-review"' + (active === 'exam' ? ' aria-current="page"' : '') + '>考试复习</a>' : '';
    const workedLink = course.workedExercises?.length ? '<a href="#course/' + course.id + '/worked-exercises"' + (active === 'worked' ? ' aria-current="page"' : '') + '>已做题详解</a>' : '';
    const modelLink = model ? '<a href="#course/' + course.id + '/' + model.id + '"' + (modelActive ? ' aria-current="page"' : '') + '>' + icon('cube') + '3D 模型</a>' : '';
    return '<nav class="course-view-nav" aria-label="课程视图"><a href="#course/' + course.id + '/map"' + (active === 'map' ? ' aria-current="page"' : '') + '>' + icon('network') + '知识图谱</a><a href="#course/' + course.id + '/' + first.id + '"' + (active === 'reader' && !modelActive && !supplement ? ' aria-current="page"' : '') + '>' + icon('book') + (first.kind === 'outline' ? '章节目录' : '章节阅读') + '</a>' + examLink + workedLink + modelLink + studyLink + materialLink + englishLink + window.LNResources.button(course) + window.LNPractice.button(course) + '</nav>';
  }

  function loadEmcReviewMath() {
    return Promise.all([loadStyle('assets/katex/katex.min.css'), loadScript('assets/katex/katex.runtime.js')]);
  }

  function renderEmcExam(course, anchor) {
    main.classList.add('course-main');
    main.innerHTML = '<a class="back-link" href="#course/' + course.id + '">' + icon('back') + '课程图谱</a><section class="course-heading"><h1>电磁兼容 · 考试复习</h1></section>' + courseViewNav(course, 'exam') + '<div class="lesson emc-exam-review" id="emc-exam-review"></div>';
    window.LNEmcExam.render($('#emc-exam-review'), anchor, loadEmcReviewMath);
  }

  function renderWorkedExercises(course) {
    main.classList.add('course-main');
    const sections = (course.workedExercises || []).map(id => course.sections.find(section => section.id === id)).filter(Boolean);
    main.innerHTML = '<a class="back-link" href="' + courseHome(course) + '">' + icon('back') + '课程</a><section class="course-heading"><h1>' + escapeHTML(course.title) + ' · 已做题详解</h1></section>' + courseViewNav(course, 'worked') + '<ul class="course-list" aria-label="已做题详解">' + sections.map(section => '<li class="course-row"><a class="course-link" href="#course/' + course.id + '/' + section.id + '"><span class="course-symbol">' + icon('book') + '</span><div class="course-text"><h2>' + escapeHTML(section.title) + '</h2><p>' + escapeHTML(section.group) + '</p></div></a></li>').join('') + '</ul>';
  }

  function renderKnowledgeMap(course) {
    main.classList.add('course-main', 'map-main');
    const reference = escapeHTML(course.reference || '');
    const referenceLabel = course.referenceUrl
      ? '<a href="' + escapeHTML(course.referenceUrl) + '" target="_blank" rel="noopener">' + reference + '</a>'
      : reference;
    main.innerHTML = '<a class="back-link" href="' + courseHome(course) + '">' + icon('back') + (isHighSchool(course) ? '高中' : '课程') + '</a><section class="course-heading"><div><h1>' + escapeHTML(course.title) + '</h1><p class="page-meta">' + escapeHTML(course.category) + ' · ' + new Set(course.sections.filter(s=>!s.supplement).map((section) => section.group)).size + (isHighSchool(course) ? '册' : '章') + '</p></div>' + favoriteButton(course, true) + '</section>' + courseViewNav(course, 'map') + (referenceLabel ? '<p class="page-meta course-reference">参考：' + referenceLabel + '</p>' : '') + '<ln-knowledge-map></ln-knowledge-map>';
    $('ln-knowledge-map', main).course = course;
    if (window.LNCrossKnowledge.hasCourse(course.id)) main.insertAdjacentHTML('beforeend', window.LNCrossKnowledge.coursePanel(course));
  }

  function renderReader(course, sectionId, anchor) {
    const selected = course.sections.find((section) => section.id === sectionId) || (!sectionId ? course.sections[0] : null);
    const sections = listedSections(course);
    const groups = [...new Set(sections.map((section) => section.group))];
    main.classList.add('course-main');
    const sectionLink = section => '<a href="#course/' + course.id + '/' + section.id + '"' + (selected?.id === section.id ? ' aria-current="page"' : '') + '>' + escapeHTML(section.title) + '</a>';
    const outline = groups.map(group => {
      const items=sections.filter(s=>s.group===group),references=items.filter(s=>s.referenceOnly);
      return '<details class="outline-group"'+(selected?.group===group?' open':'')+'><summary>'+escapeHTML(group)+'</summary><nav aria-label="'+escapeHTML(group)+'">'+items.filter(s=>!s.referenceOnly).map(sectionLink).join('')+'</nav>'+(references.length?'<details class="outline-references"'+(selected?.group===group&&selected.referenceOnly?' open':'')+'><summary>专题、原题与资料</summary><nav aria-label="专题与资料">'+references.map(sectionLink).join('')+'</nav></details>':'')+'</details>';
    }).join('');
    main.innerHTML = '<a class="back-link" href="' + courseHome(course) + '">' + icon('back') + (isHighSchool(course) ? '高中' : '课程') + '</a><section class="course-heading"><div><h1>' + escapeHTML(course.title) + '</h1><p class="page-meta">' + escapeHTML(course.category) + ' · ' + new Set(course.sections.filter(s=>!s.supplement).map(s=>s.group)).size + (isHighSchool(course) ? '册' : '章') + '</p></div>' + favoriteButton(course, true) + '</section>' + courseViewNav(course, 'reader') + '<div class="reader-layout"><details class="reader-outline" id="reader-outline"' + (matchMedia('(min-width: 961px)').matches ? ' open' : '') + '><summary>目录</summary>' + outline + '</details><section class="lesson-column"><div class="lesson-tools" id="lesson-tools"></div><article class="lesson" id="lesson-body" data-lesson-key="' + (selected ? course.id + '/' + selected.id : '') + '" aria-busy="true">' + (selected ? '<p class="loading-state" role="status">加载中…</p>' : '<h2>章节不存在</h2>') + '</article><nav class="lesson-pagination" id="lesson-pagination" aria-label="章节翻页"></nav></section></div>';
    if (selected) {
      renderReaderDock(course, selected, outline);
      void loadLesson(course, selected, anchor);
    }
    else $('#lesson-body').setAttribute('aria-busy', 'false');
  }

  function listedSections(course) {
    return course.hideOutlineEntries ? course.sections.filter(section => section.kind !== 'outline') : course.sections;
  }

  function readingSections(course, selected) {
    const sections = listedSections(course);
    if (selected.supplement) return sections.filter(section => section.supplement === selected.supplement);
    return selected.referenceOnly ? sections : sections.filter(section => !section.referenceOnly && !section.supplement);
  }

  function renderReaderDock(course, selected, outline) {
    const sequence=readingSections(course,selected),index = sequence.indexOf(selected);
    const step = (section, label, symbol) => section ? '<a class="reader-dock-item" href="#course/' + course.id + '/' + section.id + '" aria-label="' + label + '：' + escapeHTML(section.title) + '" title="' + escapeHTML(section.title) + '">' + icon(symbol) + '<span>' + label + '</span></a>' : '<button class="reader-dock-item" disabled aria-label="' + label + '，已到课程边界">' + icon(symbol) + '<span>' + label + '</span></button>';
    readerDock.innerHTML = '<button class="reader-dock-item" data-reader-directory aria-label="目录与选题" title="目录与选题" aria-haspopup="dialog" aria-controls="reader-directory">' + icon('list') + '<span>目录</span></button><a class="reader-dock-item" href="#course/' + course.id + '/map" aria-label="知识图谱" title="知识图谱">' + icon('network') + '<span>图谱</span></a>' + step(sequence[index - 1], '上一节', 'back') + step(index >= 0 && sequence[index + 1], '下一节', 'chevron') + '<button class="reader-dock-item" data-reader-top aria-label="回到顶部" title="回到顶部">' + icon('up') + '<span>顶部</span></button>';
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
      if (selected.supplement === 'english-2027') await Promise.all([loadScript('courses/hs-english/review-2027/reader.js'), loadStyle('courses/hs-english/review-2027/reader.css')]);
      const body = $('#lesson-body');
      if (!body || body.dataset.lessonKey !== key) return;
      const payload = outline ? {} : window.LN_LESSONS[key];
      if (outline) {
        body.innerHTML = '<h2>' + escapeHTML(selected.title) + '</h2>';
        if (course.hideOutlineEntries) {
          const first = listedSections(course).find(section => section.group === selected.group);
          body.insertAdjacentHTML('beforeend', '<p>这是旧目录条目。' + (first
            ? '当前主题从<a href="#course/' + course.id + '/' + first.id + '">' + escapeHTML(first.title) + '</a>开始。'
            : '<a href="#course/' + course.id + '/map">查看课程图谱</a>。') + '</p>');
        }
      }
      else if (selected.kind === 'pdf') renderPdf(payload, body, anchor);
      else if (selected.kind === 'document') {
        body.innerHTML = (payload.html || '') + '<h2>' + escapeHTML(selected.title) + '</h2><p><a class="secondary-button" href="' + payload.pdf + '" target="_blank" rel="noopener">原 PDF</a> <a class="secondary-button" href="' + payload.pdf + '" download>下载</a></p>' + payload.pages.map((page, index) => '<figure class="pdf-page pdf-reference-page"><a href="' + page.src + '" target="_blank" rel="noopener" aria-label="打开原尺寸速查页"><img src="' + page.src + '" width="' + page.width + '" height="' + page.height + '" loading="lazy" decoding="async" alt="变压器公式速查，第' + (index + 1) + '页"></a></figure>').join('');
      } else body.innerHTML = payload.html;
      window.LNCrossKnowledge.mountLesson(body, course, selected);
      window.LNPractice.prepareLesson(body);
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
        // This lesson renders TeX after loading; attach definitions only to real KaTeX atoms.
        if (!(course.id === 'automatic-control' && selected.id === 'ac-4-3-1')) {
          window.LNGlossary.prepare(body, course, selected);
        }
        window.LNResources.mountLesson(body);
        if (course.id === 'automatic-control') {
          await loadStyle('courses/automatic-control/control-lab.css');
          if (!body.isConnected || body.dataset.lessonKey !== key) return;
          if (['ac-3-3', 'ac-3-5', 'ac-3-6'].includes(selected.id)) {
            await loadScript('courses/automatic-control/control-lab.js');
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            window.LN_MOUNT_CONTROL_LABS?.(body);
          }

          if (selected.id === 'ac-4-3-1') {
            await Promise.all([
              loadStyle('courses/automatic-control/root-locus-synthesis.css'),
              loadScript('courses/automatic-control/root-locus-synthesis.js'),
              loadScript('assets/katex/katex.runtime.js')
            ]);
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            // Render this supplement's original TeX on demand; preserve readable fallback
            // when KaTeX is unavailable or a formula cannot be rendered.
            if (window.katex?.render) {
              body.querySelectorAll('[data-ac-tex]').forEach(element => {
                try {
                  window.katex.render(element.dataset.acTex, element, {
                    displayMode: element.dataset.acDisplay === 'true',
                    throwOnError: true, strict: 'error',
                    trust: false, output: 'htmlAndMathml'
                  });
                } catch (error) {
                  console.error('Automatic-control synthesis formula:', error);
                }
              });
            }
            window.LNGlossary.prepare(body, course, selected);
            window.LN_MOUNT_AC_SYNTHESIS?.(body);
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
        if (course.id === 'robot-drive-engineering') {
          await loadStyle('courses/robot-drive-engineering/model/drive-labs.css');
          if (!body.isConnected || body.dataset.lessonKey !== key) return;
          if (body.querySelector('[data-rd-lab]')) {
            try {
              await loadScript('courses/robot-drive-engineering/model/drive-labs.js');
              if (!body.isConnected || body.dataset.lessonKey !== key) return;
              window.LN_MOUNT_DRIVE_LABS?.(body);
            } catch (error) { /* Keep the static calculation readable. */ }
          }
        }
        if (course.id === 'electrical-machines' && selected.id === 'dc-homework-review') {
          // Only this reviewed homework lesson needs the KaTeX runtime; other lessons remain static.
          try {
            await loadScript('assets/katex/katex.runtime.js');
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            if (!window.katex?.render) throw new Error('KaTeX unavailable');
            body.querySelectorAll('[data-dc-tex]').forEach(element => {
              window.katex.render(element.dataset.dcTex, element, {
                displayMode: element.dataset.dcDisplay === 'block',
                throwOnError: true, strict: 'error',
                trust: false, output: 'htmlAndMathml'
              });
            });
          } catch (error) {
            // Original explanatory steps stay readable if the math library is unavailable.
            body.querySelectorAll('.dc-hw-math-fallback').forEach(el => {
              el.textContent = '公式暂未完成排版，请参考相邻的文字计算过程';
            });
            console.error('LN DC homework KaTeX rendering failed', error);
          }
        }
        if (course.id === 'electrical-materials' && selected.id === 'em-4-3') {
          try {
            await loadScript('courses/electrical-materials/mobility-lab.js');
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            window.LN_MobilityLab?.mount(body);
          } catch { /* The static diagram and derivation stay available. */ }
        }
        bindInlineModels(body);
        // Keep the original winding 3D model intact; the comparison lab is a separate idealized model.
        if (course.id === 'electrical-machines' && body.querySelector('.dc-reasoning')) {
          try {
            await loadStyle('courses/electrical-machines/model/dc-learning-lab.css');
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            if (body.querySelector('[data-dc-winding-lab], [data-dc-question]')) {
              await loadScript('courses/electrical-machines/model/dc-learning-lab.js');
              if (!body.isConnected || body.dataset.lessonKey !== key) return;
              window.LN_DCMachinesLabs?.mount(body);
            }
          } catch (error) {
            // Keep the noninteractive reasoning and equations readable when an asset fails.
          }
        }
        if (course.id === 'electrical-machines' && ['dc-sec31', 'dc-sec32', 'dc-sec33'].includes(selected.id)) {
          try {
            await loadStyle('courses/electrical-machines/model/dc-reaction-lab.css');
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            if (body.querySelector('[data-dc-supp-tex]')) {
              await loadScript('assets/katex/katex.runtime.js');
              if (!body.isConnected || body.dataset.lessonKey !== key) return;
              if (window.katex?.render) {
                body.querySelectorAll('[data-dc-supp-tex]').forEach((element) => {
                  try { window.katex.render(element.dataset.dcSuppTex, element, {
                    displayMode: false, throwOnError: true, strict: 'error',
                    trust: false, output: 'htmlAndMathml'
                  }); } catch (error) { console.error('DC supplement math:', error); }
                });
                window.LNGlossary.prepare(body, course, selected);
              }
            }
            if (selected.id === 'dc-sec33' && body.querySelector('[data-dc-reaction-lab]')) {
              await loadScript('courses/electrical-machines/model/dc-reaction-lab.js');
              if (!body.isConnected || body.dataset.lessonKey !== key) return;
              window.LN_DCReactionLab?.mount(body);
            }
          } catch (error) {
            // Without JavaScript the declared model and reading guidance remain visible.
          }
        }
        if (course.id === 'electrical-machines' && body.querySelector('[data-induction-lab]')) {
          try { await loadScript('courses/electrical-machines/model/induction-frequency-lab.js'); if (!body.isConnected || body.dataset.lessonKey !== key) return; window.LN_InductionLab?.mount(body); } catch { /* Static derivation remains available. */ }
        }
        if (course.id === 'electrical-machines' && body.querySelector('[data-mmf-lab]')) {
          try {
            await Promise.all([
              loadScript('courses/electrical-machines/model/rotating-mmf-lab.js'),
              loadStyle('courses/electrical-machines/model/rotating-mmf-lab.css')
            ]);
            if (!body.isConnected || body.dataset.lessonKey !== key) return;
            window.LN_RotatingMMFLab?.mount(body);
          } catch {
            // The static derivation stays usable if the optional model fails to load.
          }
        }
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
        if (selected.supplement === 'english-2027') window.LNEnglish2027.mount(body, payload);
      }
      body.setAttribute('aria-busy', 'false');
      body.classList.toggle('model-lesson', selected.kind === 'model');
      body.classList.toggle('pdf-lesson', selected.kind === 'pdf' || selected.kind === 'document');
      const resource = course.resources?.[selected.group];
      $('#lesson-tools').innerHTML = !resource ? '<span>' + escapeHTML(selected.group) + '</span>' : resource.links ? '<span>' + escapeHTML(selected.group) + '</span>' + resource.links.map(link => '<a href="' + escapeHTML(link.href) + '"' + (link.href.startsWith('https:') ? ' target="_blank" rel="noopener"' : '') + '>' + escapeHTML(link.label) + '</a>').join('') : '<span>' + escapeHTML(selected.group) + '</span><a href="courses/electrical-machines/files/' + resource.guide + '" target="_blank" rel="noopener">' + escapeHTML(resource.guideLabel || '讲义 PDF') + '</a><a href="courses/electrical-machines/files/' + resource.quickref + '" target="_blank" rel="noopener">速查 PDF</a>';
      // Keep exact per-lesson technical URLs accessible without repeating a references footer in the teaching article.
      // The original elements are MOVED, not hidden or duplicated, so links and provenance remain intact.
      const specificSources = [...body.querySelectorAll(':scope > details.reading-references, :scope > details.rd-sources')];
      if (specificSources.length) {
        const toolShelf = $('#lesson-tools');
        specificSources.forEach(source => {
          source.classList.add('lesson-source-tool');
          const summary = source.querySelector(':scope > summary');
          if (summary) summary.textContent = '本节资料';
          toolShelf.append(source);
        });
      }
      const sequence=readingSections(course,selected),index = sequence.indexOf(selected);
      $('#lesson-pagination').innerHTML = index < 0 ? '' : (index > 0 ? '<a href="#course/' + course.id + '/' + sequence[index - 1].id + '">' + icon('back') + '上一节</a>' : '<span></span>') + (index < sequence.length - 1 ? '<a href="#course/' + course.id + '/' + sequence[index + 1].id + '">下一节' + icon('chevron') + '</a>' : '');
      window.LNEmcExam.mountLesson(body, course, selected, loadEmcReviewMath);
      window.LNPublication.settle(body, anchor);
      restorePracticePosition(body);
    } catch (error) {
      const body = $('#lesson-body');
      if (body?.dataset.lessonKey === key) {
        body.setAttribute('aria-busy', 'false');
        body.innerHTML = '<p role="alert">课程加载失败。</p><button class="secondary-button" data-retry-lesson>重试</button>';
        $('[data-retry-lesson]', body).addEventListener('click', () => { void loadLesson(course, selected, anchor); });
      }
    }
  }

  function restorePracticePosition(root) {
    const frame = history.state?.practiceReadingPosition;
    if (frame?.hash !== location.hash) return;
    document.fonts.ready.then(() => requestAnimationFrame(() => requestAnimationFrame(() => {
      if (!root.isConnected || history.state?.practiceReadingPosition?.hash !== frame.hash || location.hash !== frame.hash) return;
      const trigger = frame.directory ? $('[data-reader-directory]', readerDock) : $$('[data-open-practice]', main)[frame.triggerIndex];
      if (trigger && !frame.directory) {
        for (let parent = trigger.parentElement; parent && parent !== main; parent = parent.parentElement) {
          if (parent instanceof HTMLDetailsElement) parent.open = true;
        }
      }
      if (trigger?.getClientRects().length && !frame.directory) {
        window.scrollBy({ top: trigger.getBoundingClientRect().top - frame.offset, behavior: 'instant' });
      } else {
        window.scrollTo({ left: frame.x, top: frame.y, behavior: 'instant' });
      }
      if (trigger?.getClientRects().length) trigger.focus({ preventScroll: true });
    })));
  }

  function renderPractice(id, sectionId, questionId) {
    const course = courses.find(course => course.id === id);
    const section = course?.sections.find(section => section.id === sectionId);
    const origin = history.state?.practiceReadingOrigin;
    const destination = origin || (course ? '#course/' + id + '/' + (section?.id || 'map') : '');
    practiceReturn.hidden = !destination;
    if (destination) {
      practiceReturn.href = destination;
      const originSection = destination.split('/')[2];
      $('span', practiceReturn).textContent = originSection && originSection !== 'map' ? '返回正文' : '返回课程';
    }
    main.classList.add('course-main', 'practice-main');
    main.innerHTML = window.LNPractice.pageHtml();
    window.LNPractice.mount(main, id, section?.id, questionId);
  }

  function renderRoute() {
    window.LNPhysics001?.onRoute();
    window.LNEnglish2027?.onRoute();
    window.LNPractice.onRoute?.();
    window.LNResources.onRoute();
    window.LNPublication.onRoute();
    window.LNGlossary.onRoute();
    let [view, id, sectionId, rawAnchor] = location.hash.slice(1).split('/');
    if (view === 'highschool' && !id) {
      view = 'category';
      id = 'highschool';
      history.replaceState(history.state, '', '#category/highschool');
    }
    let anchor = rawAnchor;
    try { anchor = rawAnchor ? decodeURIComponent(rawAnchor) : ''; } catch { anchor = ''; }
    if (readerDirectory.open) readerDirectory.close();
    practiceReturn.hidden = true;
    readerDock.hidden = true;
    readerDock.innerHTML = '';
    questionNavigation = null;
    for (const slot of [$('#reader-question-slot'), $('#reader-directory-question')]) {
      slot.replaceChildren(); slot.hidden = true;
    }
    document.body.classList.remove('is-reading', 'directory-open');
    main.classList.remove('course-main', 'map-main', 'practice-main');
    currentView = ['favorites', 'course', 'highschool', 'resources', 'practice', 'knowledge'].includes(view) ? view : 'overview';
    if (['overview', 'favorites'].includes(currentView)) {
      if (lastLibrary !== currentView) { query = ''; knowledgeKind = ''; knowledgeLimit = knowledgePageSize; }
      lastLibrary = currentView;
    }
    category = view === 'category' ? (libraryGroups[id] || categories[id] || '全部') : '全部';
    let title = currentView === 'favorites' ? '收藏' : (category === '全部' ? '课程' : category);
    const outlineCourse = courses.find(course => course.id === id && course.outlineOnly);
    if (currentView === 'course') {
      title = renderCourse(id, sectionId, anchor);
      if (courses.find(c => c.id === id)?.sections.some(s => s.id === sectionId)) {
        recent = [{course:id, section:sectionId}, ...recent.filter(r => r.course !== id || r.section !== sectionId)].slice(0,12);
        writeStored('ln.recent.v1', JSON.stringify(recent));
      }
    }
    else if (outlineCourse && ['practice', 'resources'].includes(currentView)) {
      title = outlineCourse.title;
      main.innerHTML = '<h1>' + escapeHTML(title) + '</h1><p>当前仅保留目录。</p><a class="secondary-button" href="#course/' + id + '">打开目录</a>';
    }
    else if (currentView === 'knowledge') { window.LNCrossKnowledge.render(main,id); title = '跨课程知识网络'; }
    else if (currentView === 'practice') { renderPractice(id, sectionId, anchor); title = '练习'; }
    else if (currentView === 'resources') { main.innerHTML = window.LNResources.pageHtml(id); window.LNResources.bindPage(main, id, sectionId); title = '实作与资料'; }
    else if (currentView === 'highschool' && id === 'resources') { main.innerHTML = window.LNHighSchool.resourcesHtml(); title = '教材与来源'; }
    else renderOverview();
    $('#breadcrumb-current').textContent = title;
    document.title = title === '课程' ? 'LN' : title + ' · LN';
    $$('[data-nav]').forEach((link) => {
      if (link.dataset.nav === currentView && category === '全部') link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    if (currentView === 'course') {
      $$('[data-category]').forEach((link) => { link.classList.remove('active'); link.removeAttribute('aria-current'); });
    }
    renderSidebarCourses();
    mobileOpen = false;
    updateSidebar();
    if (currentView === 'course' && !$('#lesson-body', main)) restorePracticePosition(main.firstElementChild);
  }

  function navigateRoute() {
    renderRoute();
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    main.focus({ preventScroll: true });
  }

  function openSettings() {
    if (mobile.matches && mobileOpen) setSidebar(false);
    if (!dialog.open) dialog.showModal();
  }

  const globalSearch = $('#ln-global-search');
  const globalInput = $('#ln-search-input');
  const normalizeSearch = value => String(value ?? '').normalize('NFKC').toLowerCase().replace(/\\(?:left|right|mathrm|mathbf|mathit|operatorname)\b/g, '').replace(/\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}/g, '$1/$2').replace(/[{}]/g, '').trim();
  const aliases = [['bode','伯德图','波特图','bode图'],['fft','快速傅里叶变换'],['dft','离散傅里叶变换'],['emc','电磁兼容'],['routh','劳斯'],['fir','有限冲激响应'],['iir','无限冲激响应'],['esd','静电放电'],['旋转磁场','旋转磁动势'],['3d','三维']];
  let fullSearchEntries = [];
  let fullSearchLoaded = false;
  let searchLoading = null;
  let searchLimit = 40;
  let searchHistory = readStored('ln.search-history.v1', []);
  if (!Array.isArray(searchHistory)) searchHistory = [];
  const rememberSearch = () => {
    const q = globalInput.value.trim();
    if (q) { searchHistory = [q, ...searchHistory.filter(v => v !== q)].slice(0,8); writeStored('ln.search-history.v1', JSON.stringify(searchHistory)); }
  };
  function highlightSearch(value, q) {
    const s = String(value), at = s.toLowerCase().indexOf(q.toLowerCase());
    return at < 0 || !q ? escapeHTML(s) : escapeHTML(s.slice(0,at)) + '<mark>' + escapeHTML(s.slice(at,at+q.length)) + '</mark>' + escapeHTML(s.slice(at+q.length));
  }
  function renderGlobalSearch() {
    const q = globalInput.value.trim(), normalized = normalizeSearch(q);
    const type = $('#ln-search-kind').value, scope = $('#ln-search-scope').value;
    const list = $('#ln-search-results'), status = $('#ln-search-status');
    if (!normalized) {
      status.textContent = searchHistory.length ? '最近搜索' : '输入课程、知识点、公式或习题';
      list.innerHTML = searchHistory.map(v => '<li><button class="ln-history-query" data-recent-query="' + escapeHTML(v) + '">' + escapeHTML(v) + '</button></li>').join('');
      $('#ln-search-more').hidden = true; return;
    }
    knowledgeEntries ||= buildKnowledgeEntries();
    const base = courses.map(course => ({course, kind:'课程', label:'课程', title:course.title, route:'#course/'+course.id, search:[course.title,groupFor(course),...course.topics].join(' ')}));
    const terms = normalized.split(/\s+/).map(t => [t, ...aliases.filter(a => a.includes(t)).flat()]);
    const rows = [...base, ...knowledgeEntries, ...fullSearchEntries].filter(row => {
      if (type && row.kind !== type && row.label !== type) return false;
      if (scope === 'higher' && isHighSchool(row.course) || scope === 'highschool' && !isHighSchool(row.course)) return false;
      const hay = normalizeSearch(row.search);
      const compact = hay.replace(/\s+/g,'');
      return terms.every(group => group.some(t => hay.includes(t) || compact.includes(t.replace(/\s+/g,''))));
    });
    const score = row => {
      const title = normalizeSearch(row.title);
      return title === normalized ? 0 : title.includes(normalized) ? 1 : row.kind === '正文' ? 5 : row.kind === '课程' ? 3 : 2;
    };
    rows.sort((a,b) => score(a)-score(b));
    const unique = [...new Map(rows.map(r => [r.kind+'|'+r.route+(r.kind==='公式'?'|'+r.title:''),r])).values()];
    status.textContent = '找到 ' + unique.length + ' 项' + (!fullSearchLoaded ? ' · 正文索引尚未加载' : '');
    list.innerHTML = unique.slice(0,searchLimit).map(row => '<li><a href="' + escapeHTML(row.route) + '"><span class="knowledge-result-kind">' + escapeHTML(row.label || row.kind) + '</span><span><strong>' + highlightSearch(row.title,q) + '</strong><small>' + escapeHTML(row.course.title + (row.section ? ' · '+row.section.title : '')) + '</small></span></a></li>').join('');
    $('#ln-search-more').hidden = unique.length <= searchLimit;
  }
  function focusSearch() {
    if (mobile.matches && mobileOpen) setSidebar(false);
    if (!globalSearch.open) globalSearch.showModal();
    globalInput.focus(); globalInput.select();
    renderGlobalSearch();
    if (!searchLoading && !fullSearchLoaded) searchLoading = fetch('courses/search-content.json').then(r => {if(!r.ok) throw Error('索引不可用'); return r.json();}).then(rows => {
      fullSearchEntries = rows.flatMap(row => {
        const course = courses.find(c => c.id === row.course);
        const section = course?.sections.find(s => s.id === row.section);
        if (!section) return [];
        return [{course,section,kind:row.kind,label:row.kind,title:row.title || section.title,route:'#course/'+course.id+'/'+section.id+(row.anchor?'/'+encodeURIComponent(row.anchor):''),search:[row.text,row.title,section.title,course.title].join(' ')}];
      });
      fullSearchLoaded = true;
      if (globalSearch.open) renderGlobalSearch();
    }).catch(() => {searchLoading = null;});
  }
  globalInput.addEventListener('input', () => {searchLimit=40; renderGlobalSearch();});
  for (const id of ['ln-search-kind','ln-search-scope']) $('#'+id).addEventListener('change', () => {searchLimit=40; renderGlobalSearch();});
  $('#ln-search-more').addEventListener('click', () => {searchLimit+=40; renderGlobalSearch();});
  $('#ln-search-close').addEventListener('click', () => globalSearch.close());
  $('#ln-search-results').addEventListener('click', event => {
    const recent = event.target.closest('[data-recent-query]');
    if (recent) {globalInput.value=recent.dataset.recentQuery; searchLimit=40; renderGlobalSearch(); globalInput.focus(); return;}
    if (event.target.closest('a')) { rememberSearch(); globalSearch.close(); }
  });
  globalInput.addEventListener('keydown', event => {
    if(event.key==='Enter' || event.key==='ArrowDown') {
      const first=$('#ln-search-results a');
      if(first){event.preventDefault(); if(event.key==='Enter')first.click(); else first.focus();}
    }
  });
  globalSearch.addEventListener('close', () => rememberSearch());
  $('#ln-top-search').addEventListener('click', focusSearch);
  $('#sidebar-nav-mode').addEventListener('click', event => {
    const button=event.target.closest('[data-sidebar-mode]');
    if (button) {sidebarMode=button.dataset.sidebarMode; renderSidebarCourses();}
  });
  $('#sidebar-course-list').addEventListener('toggle', event => {
    const group=event.target.dataset.libraryGroup;
    if (!group || !event.target.isConnected) return;
    if (event.target.open) openGroups.add(group); else openGroups.delete(group);
    saveGroups();
  }, true);

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
    if (filter) { category = filter.dataset.filter; knowledgeLimit = knowledgePageSize; renderRows(); }
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
      knowledgeKind = '';
      knowledgeLimit = knowledgePageSize;
      $('#course-search').value = '';
      $('#knowledge-kind').value = '';
      renderRows();
      $('#course-search').focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    if (event.target.closest('[data-practice-return]') && history.state?.practiceReadingOrigin === practiceReturn.hash) {
      event.preventDefault();
      history.back();
      return;
    }
    const trigger = event.target.closest('a[data-open-practice]');
    if (!trigger || currentView !== 'course') return;
    event.preventDefault();
    const position = {
      hash: location.hash,
      x: window.scrollX,
      y: window.scrollY,
      offset: trigger.getBoundingClientRect().top,
      directory: readerDirectory.contains(trigger),
      triggerIndex: $$('[data-open-practice]', main).indexOf(trigger)
    };
    history.replaceState({ ...history.state, practiceReadingPosition: position }, '');
    history.pushState({ practiceReadingOrigin: location.hash }, '', trigger.hash);
    navigateRoute();
  });
  document.addEventListener('keydown', (event) => {
    if (globalSearch.open || dialog.open || readerDirectory.open || $('#resource-dialog').open || $('dialog.practice-exam-confirm:modal')) return;
    if (event.key === 'Escape' && mobileOpen) { setSidebar(false); return; }
    const shortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k';
    if (!shortcut && event.target.closest('input, textarea, select, [contenteditable]')) return;
    if (event.key === '/' || shortcut) {
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
  addEventListener('hashchange', navigateRoute);
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
