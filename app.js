'use strict';

(() => {
  const courses = window.LN_COURSES;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const icon = (name) => '<svg class="icon" aria-hidden="true"><use href="#i-' + name + '"/></svg>';
  const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
  const categories = { science: '理学', engineering: '工学', computing: '计算机' };
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
  let collapsed = document.documentElement.dataset.sidebar === 'collapsed';
  let mobileOpen = false;
  let currentView = 'overview';
  let category = '全部';
  let query = '';
  let toastTimer;

  function applyTheme() {
    const theme = preferences.mode === 'system' ? (systemTheme.matches ? 'dark' : 'light') : preferences.mode;
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.palette = preferences.palette;
    $('meta[name="theme-color"]').content = theme === 'dark' ? '#202020' : '#ffffff';
    $('#quick-theme').innerHTML = icon(theme === 'dark' ? 'sun' : 'moon');
    $('#quick-theme').setAttribute('aria-label', '切换到' + (theme === 'dark' ? '日间' : '夜间') + '模式');
    $$('[data-mode]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.mode === preferences.mode)));
    $$('[data-palette-choice]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.paletteChoice === preferences.palette)));
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
  }

  function favoriteButton(course, detail = false) {
    const saved = favorites.has(course.id);
    return '<button class="' + (detail ? 'secondary-button' : 'icon-button bookmark-button') + '" data-favorite="' + course.id + '" aria-label="' + (saved ? '取消收藏' : '收藏') + escapeHTML(course.title) + '" aria-pressed="' + saved + '">' + icon('star') + (detail ? (saved ? '已收藏' : '收藏') : '') + '</button>';
  }

  function courseRow(course) {
    return '<li class="course-row"><a class="course-link" href="#course/' + course.id + '"><span class="course-symbol">' + icon('book') + '</span><div class="course-text"><h2>' + escapeHTML(course.title) + '</h2><p>' + course.topics.map(escapeHTML).join(' · ') + '</p></div><span class="course-category">' + escapeHTML(course.category) + '</span></a>' + favoriteButton(course) + '</li>';
  }

  function renderRows() {
    const matching = courses.filter((course) => (currentView !== 'favorites' || favorites.has(course.id)) && (category === '全部' || course.category === category) && [course.title, course.category, ...course.topics].join(' ').toLowerCase().includes(query.toLowerCase().trim()));
    $('#result-count').textContent = matching.length + ' 门 · 示例';
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
    const title = currentView === 'favorites' ? '收藏' : '课程';
    main.innerHTML = '<section aria-labelledby="page-title"><div class="page-heading"><div><h1 id="page-title">' + title + '</h1><p class="page-meta" id="result-count"></p></div><label class="course-search">' + icon('search') + '<input id="course-search" type="search" aria-label="搜索课程或知识点" placeholder="搜索课程…" value="' + escapeHTML(query) + '" autocomplete="off"></label></div><div class="filter-row" aria-label="筛选学科">' + ['全部', ...Object.values(categories)].map((name) => '<button class="filter-button" data-filter="' + name + '" aria-pressed="' + (name === category) + '">' + name + '</button>').join('') + '</div><ul class="course-list" id="course-list" aria-live="polite" aria-label="课程列表"></ul></section>';
    renderRows();
    $('#course-search').addEventListener('input', (event) => { query = event.target.value; renderRows(); });
  }

  function renderCourse(id) {
    const course = courses.find((course) => course.id === id);
    if (!course) {
      main.innerHTML = '<div class="empty-state"><h2>课程不存在</h2><a class="secondary-button" href="#overview">返回课程</a></div>';
      return '课程';
    }
    main.innerHTML = '<a class="back-link" href="#overview">' + icon('back') + '课程</a><section class="course-heading"><div><h1>' + escapeHTML(course.title) + '</h1><p class="page-meta">' + escapeHTML(course.category) + ' · 示例</p></div>' + favoriteButton(course, true) + '</section><div class="detail-content"><aside class="course-outline" aria-label="目录"><h2>目录</h2><p>暂无章节</p></aside><section class="empty-state detail-empty">' + icon('file') + '<h2>待添加材料</h2></section></div>';
    return course.title;
  }

  function renderRoute() {
    const [view, id] = location.hash.slice(1).split('/');
    currentView = ['favorites', 'course'].includes(view) ? view : 'overview';
    category = view === 'category' ? (categories[id] || '全部') : '全部';
    let title = currentView === 'favorites' ? '收藏' : (category === '全部' ? '课程' : category);
    if (currentView === 'course') title = renderCourse(id);
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
    mobileOpen = false;
    updateSidebar();
  }

  function openSettings() {
    if (mobile.matches && mobileOpen) setSidebar(false);
    if (!dialog.open) dialog.showModal();
  }

  function focusSearch() {
    if (['overview', 'favorites'].includes(currentView)) {
      if (mobile.matches && mobileOpen) setSidebar(false);
      $('#course-search').focus();
    } else {
      addEventListener('hashchange', () => $('#course-search')?.focus(), { once: true });
      location.hash = 'overview';
    }
  }

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
    if (dialog.open) return;
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
