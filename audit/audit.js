(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const escape = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
  const fields = ['status','sourceKind','impact','evidenceType','revision','codePath',
    'buildResult','evidenceUrl','verifiedScope','reviewer','blocker','actualContent',
    'reproduction','missing','scope','acceptance','sourceDigest'];
  const labels = {
    progress: ['接入与验收', '源码接入率与人工核验率分开统计。接入数量不代表教学质量。'],
    catalog: ['内容清单与知识结构', '按课程、章节与实际存在的正文锚点逐级定位。'],
    skeleton: ['骨架内容清单', '明确标记 outline 或未找到登记正文入口的条目。'],
    derivation: ['推导与例题验收', '检查公式的假设、连等推理、单位与逐步例题；标记计数仅供定位。'],
    practice: ['习题与测试入口', '逐项核对题干、答案、计算、错题记录和入口操作。'],
    visual: ['图示与交互组件', '逐项核对方向、标注、缩放、控制反馈和窄屏显示。'],
    standards: ['规范差异', '与 LN 教学、排版、练习、来源及发布规范逐项对照。'],
    gaps: ['题库与交互缺口', '区分已证实缺口与尚待操作验证的条目。'],
    blockers: ['发布阻断问题', '仅显示有复现记录的严重问题或手动标记的发布阻断。'],
    priority: ['按影响排序的补齐清单', '发布阻断与复现问题优先，其次处理主线骨架及未核验内容。'],
    sequence: ['最小修改顺序', '先解决可复现阻断，再补正文与组件，最后审查及发布。'],
    edit: ['登记验收证据', '逐条记录实际内容、代码位置、命令、复现步骤、验收标准与证据。']
  };
  const state = { inventory: null, records: [], view: 'progress', course: '', query: '', selected: '' };
  const STORAGE_KEY = 'ln.audit.records.v1';
  const SOURCE_CLASSES = ['仓库实际内容', '文档声明', '推测', '未确认内容'];
  const statuses = ['已验证', '部分接入', '骨架状态', '明确存在的问题'];
  const recordFor = (row, anchor = '') => state.records.find((r) =>
    r.id === row.id && r.courseId === row.courseId && (r.anchor || '') === anchor);
  const recordKey = (rec) => rec.courseId + '/' + rec.id + (rec.anchor ? '#' + rec.anchor : '');
  const allRows = () => state.inventory ? state.inventory.sections : [];
  const lookup = (id, courseId) => allRows().find((row) => row.id === id && row.courseId === courseId);
  const fullId = (row, anchor = '') => row.courseId + '/' + row.id + (anchor ? '#' + anchor : '');
  const validUrl = (value) => /^https:\/\/[^\s/]+(?:\/|$)/i.test(value || '');
  const independent = (type) => ['测试运行', '浏览器实际操作', '学科人工核读'].includes(type);

  function verified(row, rec) {
    return !!(rec && rec.status === '已验证' && rec.sourceKind === '仓库实际内容'
      && independent(rec.evidenceType) && validUrl(rec.evidenceUrl)
      && /^[a-f0-9]{7,40}$/i.test(rec.revision || '')
      && rec.sourceDigest && row.sourceDigest && rec.sourceDigest === row.sourceDigest
      && rec.actualContent && rec.reproduction && rec.acceptance
      && rec.verifiedScope && rec.reviewer);
  }
  function confirmedIssue(rec) {
    return !!(rec && rec.status === '明确存在的问题'
      && rec.sourceKind === '仓库实际内容' && rec.codePath
      && rec.reproduction && rec.actualContent);
  }
  function status(row) {
    const rec = recordFor(row);
    if (verified(row, rec)) return '已验证';
    if (confirmedIssue(rec)) return '明确存在的问题';
    if (row.status === '明确存在的问题') return row.status;
    return row.status;
  }
  function visibleRows() {
    const query = state.query.trim().toLocaleLowerCase();
    return allRows().filter((row) =>
      (!state.course || row.courseId === state.course)
      && (!query || [row.title, row.id, row.group, row.sourcePath,
        ...row.subsections.map((s) => s.title)].join(' ').toLocaleLowerCase().includes(query)));
  }
  function courseLabel(id) {
    return state.inventory.courses.find((course) => course.id === id)?.label || id;
  }
  const courseLink = (row, sub) =>
    '../' + row.entryHash + (sub ? '/' + encodeURIComponent(sub) : '');
  const sourceLink = (row) => row.sourcePath ?
    'https://github.com/llwoow/LN/blob/' + encodeURIComponent(state.inventory.sourceRevision) + '/' +
    row.sourcePath.split('/').map(encodeURIComponent).join('/') : '';
  function compact(s) { return escape(String(s || '').slice(0, 300)); }
  function tag(s) { return '<span class="audit-tag">' + escape(s) + '</span>'; }
  function renderSummary(rows) {
    const counts = Object.fromEntries(statuses.map((s) => [s, 0]));
    rows.forEach((r) => { counts[status(r)] += 1; });
    $('#audit-summary').innerHTML = statuses.map((s) =>
      '<div class="audit-stat"><strong>' + counts[s] + '</strong><span>' + s + '</span></div>'
    ).join('');
  }
  function renderRow(row, type = 'catalog') {
    const rec = recordFor(row);
    const links = '<a class="audit-link" href="' + escape(courseLink(row)) +
      '" target="_blank" rel="noopener">打开 LN 正文</a>' +
      (row.sourcePath ? ' · <a class="audit-link" href="' + escape(sourceLink(row)) +
      '" target="_blank" rel="noopener">定位源码</a>' : '');
    const sub = (type === 'catalog' && row.subsections.length) ?
      '<details><summary class="audit-secondary">实际可定位小节 (' + row.subsections.length +
      ')</summary><ul class="audit-section-list">' +
      row.subsections.map((s) => '<li><a class="audit-link" href="' +
      escape(courseLink(row, s.id)) + '" target="_blank" rel="noopener">' +
      compact(s.title) + '</a> <span class="audit-code">#' + escape(s.id) +
      '</span> ' + (verified(row, recordFor(row, s.id)) ? tag('已验证') : '') +
      ' <button type="button" class="audit-link" data-review="' +
      escape(fullId(row, s.id)) + '">核验本小节</button></li>').join('') +
      '</ul></details>' : '';
    let signals = '';
    if (type === 'derivation' || type === 'visual' || type === 'practice') {
      signals = '<div class="audit-row-details">源码静态线索（不能证明可用）：' +
        Object.keys(row.signals).map((key) => escape(key) + ' ' + Number(row.signals[key] || 0)).join(' · ') +
        '；学科/浏览器验收：' + (status(row) === '已验证' ? '有已登记独立证据' : '未验证') + '</div>';
    }
    return '<div class="audit-row"><div class="audit-row-title">' +
      escape(row.title) + tag(status(row)) + '</div><div class="audit-row-details">' +
      escape(courseLabel(row.courseId)) + ' · ' + escape(row.group) + ' · <span class="audit-code">' +
      escape(row.sourcePath || '无独立正文路径') + '</span></div><div class="audit-row-details">' +
      escape(row.statusReason) + '</div>' +
      (rec ? '<div class="audit-row-details">人工记录：' + compact(rec.actualContent || rec.missing || rec.status) +
        ' · 信息性质：' + escape(rec.sourceKind || '未确认内容') +
        (rec.revision && rec.sourceDigest !== row.sourceDigest ?
          ' · <strong>源文件已变化，原证据需复核</strong>' : '') + '</div>' : '') +
      signals + '<div class="audit-row-details">' + links +
      ' · <button type="button" class="audit-link" data-review="' + escape(fullId(row)) +
      '">登记/查看证据</button></div>' + sub + '</div>';
  }
  function empty(message) { return '<div class="audit-empty">' + escape(message) + '</div>'; }
  function groupBy(rows, key) {
    const grouped = new Map();
    rows.forEach((row) => {
      const label = key(row);
      if (!grouped.has(label)) grouped.set(label, []);
      grouped.get(label).push(row);
    });
    return grouped;
  }
  function chapterGroups(rows, type) {
    const courses = groupBy(rows, (r) => r.courseId);
    if (!courses.size) return empty('没有符合当前筛选的条目。');
    return [...courses].map(([course, cr]) =>
      '<section class="audit-panel"><h2>' + escape(courseLabel(course)) + ' · ' + cr.length + '项</h2>' +
      '<a class="audit-link" href="../#course/' + escape(course) + '/map" target="_blank" rel="noopener">打开 LN 知识图谱</a>' +
      [...groupBy(cr, (r) => r.group)].map(([group, gr]) =>
        '<details class="audit-panel" ' + (rows.length < 30 ? 'open' : '') +
        '><summary>' + escape(group) + ' · ' + gr.length + '项</summary>' +
        gr.map((r) => renderRow(r, type)).join('') + '</details>').join('') + '</section>'
    ).join('');
  }
  function renderProgress(rows) {
    if (!rows.length) return empty('没有符合当前筛选的条目。');
    const groups = groupBy(rows, (r) => r.courseId + '||' + r.group);
    return '<p class="audit-notice">以下“接入率”只计算有源文件的条目；“已验证率”只计算保有有效、匹配源码版本的独立证据。不能将接入率写成内容完成度。</p>' +
      '<div class="audit-card-grid">' + [...groups].map(([key, rs]) => {
        const n = rs.length;
        const attached = rs.filter((r) => r.sourceExists).length;
        const verifiedCount = rs.filter((r) => status(r) === '已验证').length;
        const percentage = Math.round(attached / n * 100);
        return '<section class="audit-panel"><h2>' + escape(courseLabel(rs[0].courseId)) +
          '</h2><p class="audit-pill">' + escape(rs[0].group) + '</p><div class="audit-progress" role="img" aria-label="源码接入率 ' +
          percentage + '%"><span style="width:' + percentage + '%"></span></div>' +
          '<p>源码接入 ' + attached + '/' + n + '（' + percentage + '%） · 已验证 ' +
          verifiedCount + '/' + n + '</p><p class="audit-secondary">骨架 ' +
          rs.filter((r) => status(r) === '骨架状态').length + ' · 明确问题 ' +
          rs.filter((r) => status(r) === '明确存在的问题').length + '</p>' +
          '<button class="audit-link" data-course="' + escape(rs[0].courseId) +
          '" data-view="catalog">查看该课程清单</button></section>';
      }).join('') + '</div>';
  }
  function renderStandards(rows) {
    const items = [
      ['推导连续性与学科核对', '核查对象、假设、方向、单位、连等推导、公式符号解释、适用边界；不能按公式数量判定。', 'REQUIREMENTS.md · TEACHING.md'],
      ['例题与讲解质量', '复算原题数据及每一步数值代入；解释方法、条件变化和常见误区；逐段人工通读。', 'REQUIREMENTS.md · TEACHING.md'],
      ['练习与测试闭环', '实际操作进入题目、作答、批改、错题重做、收藏与来源链接；检查稳定 ID。', 'PRACTICE.md'],
      ['图示与交互', '核对电机绕组/相量方向、标注位置、缩放、触控与移动端；不因 SVG 存在就通过。', 'DESIGN.md'],
      ['发布与来源', '复查链接、许可、隐私、附件类型、构建目录与发布版本；检查不等于权利授权。', 'PUBLICATION.md'],
      ['技术与学科证据隔离', 'CI 测试通过只证实测试范围内的代码行为；文档、README、PR 说明不作为已验证证据。', 'REQUIREMENTS.md']
    ];
    const skeleton = rows.filter((r) => status(r) === '骨架状态');
    const problems = rows.filter((r) => status(r) === '明确存在的问题');
    const undocumented = rows.filter((r) => status(r) === '部分接入');
    const concrete = '<section class="audit-panel"><h2>仓库实际内容与目标的差距</h2>' +
      '<p>尚只有目录/骨架：' + skeleton.length + ' 项；存在代码但尚无独立验收证据：' +
      undocumented.length + ' 项；已定位或复现问题：' + problems.length + ' 项。</p>' +
      '<p class="audit-secondary">来源：manifest 类型、源文件存在性及人工复现记录。缺少学科核读证据不等于已经发现学术错误。</p>' +
      skeleton.slice(0, 12).map((row) => renderRow(row, 'standards')).join('') +
      (skeleton.length > 12 ? '<p class="audit-secondary">其余骨架请切换“骨架内容清单”查看。</p>' : '') + '</section>';
    return '<p class="audit-notice">当前选中 ' + rows.length +
      ' 个条目。以下为适用验收标准，不表示已经逐项人工核查。</p>' +
      concrete + items.map(([title, detail, file]) => '<section class="audit-panel"><h2>' + escape(title) +
        '</h2><p>' + escape(detail) + '</p><p class="audit-secondary">标准依据：' +
        escape(file) + ' · 逐项实际差异：待审查记录</p></section>').join('');
  }
  function renderGaps(rows) {
    const known = rows.filter((r) => {
      const rec = recordFor(r);
      return confirmedIssue(rec) && /题|练习|测|交互|组件|模型|动画|图示/.test(
        [rec.missing, rec.actualContent].join(' '));
    });
    const uncertain = rows.filter((r) => r.status === '部分接入' &&
      !known.includes(r) && status(r) !== '已验证');
    return '<h2>有复现记录的题库/交互缺口（' + known.length + '）</h2>' +
      (known.length ? chapterGroups(known, 'practice') : empty('当前没有已经录入可复现证据的题库或交互缺口。')) +
      '<h2>尚待实际操作核对（' + uncertain.length + '）</h2>' +
      '<p class="audit-secondary">未检查不等于不存在；以下条目还未通过相关浏览器与教学审查。</p>' +
      chapterGroups(uncertain, 'practice');
  }
  function renderBlockers(rows) {
    const blockers = rows.filter((row) => {
      const rec = recordFor(row);
      return confirmedIssue(rec) && rec.blocker === true ||
        (row.status === '明确存在的问题' && row.sourcePath && !row.sourceExists);
    });
    return blockers.length ? chapterGroups(blockers, 'catalog') :
      empty('当前未记录已确认的发布阻断问题。这不是“发布已经安全”的证明；仍须执行构建、浏览器、学科与隐私审查。');
  }
  function rank(row) {
    const rec = recordFor(row);
    let result = status(row) === '明确存在的问题' ? 400 :
      status(row) === '骨架状态' ? 200 : status(row) === '部分接入' ? 80 : 0;
    if (confirmedIssue(rec) && rec.blocker) result += 500;
    result += rec?.impact === '严重' ? 70 : rec?.impact === '重要' ? 35 : 0;
    return result;
  }
  function renderPriority(rows) {
    const todo = rows.filter((row) => status(row) !== '已验证')
      .sort((a, b) => rank(b) - rank(a));
    return '<p class="audit-notice">排序是待办启发式，不是自动判断缺失的推导或例题。确认问题/阻断优先，骨架其次，尚未核验的正文最后。</p>' +
      (todo.length ? todo.map((row, i) =>
        '<section class="audit-panel"><div class="audit-pill">优先级 ' + (i + 1) + ' · ' +
        (rank(row) >= 400 ? '先修复已确认问题' : rank(row) >= 200 ? '补主线正文' : '核查现有内容') +
        '</div>' + renderRow(row, 'priority') + '</section>').join('') :
        empty('当前筛选范围没有待办条目。'));
  }
  function renderSequence(rows) {
    const blockers = rows.filter((r) => status(r) === '明确存在的问题');
    const skeleton = rows.filter((r) => status(r) === '骨架状态');
    const partial = rows.filter((r) => status(r) === '部分接入');
    const steps = [
      ['01 · 复现并修复阻断', '先定位破损的源文件、路由与发布问题；形成失败前后证据。', blockers],
      ['02 · 补全真实课程正文', '按课程和小节补物理前提、连续推导、逐步例题，不批量套固定模板。', skeleton],
      ['03 · 修复练习及图示交互', '真实操作答题/批改、图谱、3D 模型、公式引用，并保留旧题身份。', partial],
      ['04 · 学科与浏览器验收', '逐条核算、移动端截图、复现步骤、链接与构建日志；记录准确验证范围。', []],
      ['05 · 发布前检查', '源文件检查 → Python/Node → 静态构建 → Playwright → 权利/隐私审核 → PR 审查。', []]
    ];
    return steps.map(([title, desc, tasks]) => '<section class="audit-panel"><h2>' +
      escape(title) + '</h2><p>' + escape(desc) + '</p>' +
      (tasks.length ? '<p class="audit-secondary">涉及 ' + tasks.length +
        ' 个条目；首批：</p><ul class="audit-section-list">' +
        tasks.slice(0, 8).map((row) => '<li><a class="audit-link" href="' +
          escape(courseLink(row)) + '" target="_blank" rel="noopener">' +
          compact(row.title) + '</a> · ' + escape(row.group) + '</li>').join('') +
        '</ul>' : '') + '</section>').join('');
  }
  function render() {
    if (!state.inventory) return;
    const rows = visibleRows();
    renderSummary(rows);
    $$('#audit-nav [data-view]').forEach((button) => {
      if (button.dataset.view === state.view) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    $('#view-title').textContent = labels[state.view][0];
    $('#view-description').textContent = labels[state.view][1];
    let content = '';
    switch (state.view) {
      case 'progress': content = renderProgress(rows); break;
      case 'catalog': content = chapterGroups(rows, 'catalog'); break;
      case 'skeleton': content = chapterGroups(rows.filter((r) => status(r) === '骨架状态'), 'catalog'); break;
      case 'derivation': content = chapterGroups(rows, 'derivation'); break;
      case 'practice': content = chapterGroups(rows, 'practice'); break;
      case 'visual': content = chapterGroups(rows, 'visual'); break;
      case 'standards': content = renderStandards(rows); break;
      case 'gaps': content = renderGaps(rows); break;
      case 'blockers': content = renderBlockers(rows); break;
      case 'priority': content = renderPriority(rows); break;
      case 'sequence': content = renderSequence(rows); break;
      case 'edit': content = ''; break;
    }
    $('#audit-body').innerHTML = content;
    if (state.view === 'edit') renderEditor();
  }
  function fillEditor(form, row, anchor = '') {
    const anchors = form.elements.anchor;
    anchors.innerHTML = '<option value="">整个阅读单元</option>' +
      row.subsections.map((s) => '<option value="' + escape(s.id) + '">' +
        compact(s.title) + '</option>').join('');
    anchors.value = anchor;
    const rec = recordFor(row, anchor) || {};
    form.elements.id.value = fullId(row);
    fields.forEach((name) => {
      const field = form.elements[name];
      if (!field) return;
      if (name === 'blocker') field.checked = rec.blocker === true;
      else if (name === 'sourceDigest') return;
      else if (name === 'status') field.value = rec.status || row.status;
      else field.value = rec[name] || (name === 'codePath' ? row.sourcePath : '') ||
        (name === 'sourceKind' ? '仓库实际内容' : '') ||
        (field.tagName === 'SELECT' ? field.options[0]?.value || '' : '');
    });
  }
  function renderEditor() {
    const template = $('#record-form-template');
    const form = template.content.cloneNode(true);
    const select = form.querySelector('[name=id]');
    select.innerHTML = allRows().map((row) => '<option value="' + escape(fullId(row)) +
      '">' + escape(courseLabel(row.courseId) + ' / ' + row.group + ' / ' + row.title) +
      '</option>').join('');
    $('#audit-body').append(form);
    const node = $('#record-form');
    const selection = state.selected.split('#');
    let selected = allRows().find((r) => fullId(r) === selection[0]);
    if (!selected) selected = visibleRows()[0] || allRows()[0];
    if (selected) fillEditor(node, selected, selection[1] || '');
    select.addEventListener('change', () => {
      const row = allRows().find((r) => fullId(r) === select.value);
      if (row) { state.selected = fullId(row); fillEditor(node, row); }
    });
    node.elements.anchor.addEventListener('change', () => {
      const row = allRows().find((r) => fullId(r) === select.value);
      if (row) {
        state.selected = fullId(row, node.elements.anchor.value);
        fillEditor(node, row, node.elements.anchor.value);
      }
    });
    node.addEventListener('submit', saveRecord);
    $('#audit-export').addEventListener('click', exportRecords);
    $('#audit-import').addEventListener('change', importRecords);
    $('#audit-delete').addEventListener('click', deleteRecord);
  }
  function saveRecord(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const row = allRows().find((r) => fullId(r) === form.elements.id.value);
    if (!row) return;
    const rec = { id: row.id, courseId: row.courseId, anchor: form.elements.anchor.value, sourceDigest: row.sourceDigest || '',
      updatedAt: new Date().toISOString() };
    fields.forEach((name) => {
      if (name === 'sourceDigest') return;
      const element = form.elements[name];
      rec[name] = name === 'blocker' ? element.checked : element.value.trim();
    });
    if (!statuses.includes(rec.status) || !SOURCE_CLASSES.includes(rec.sourceKind)) {
      $('#form-message').textContent = '状态或信息性质不正确。';
      return;
    }
    if (rec.status === '已验证' && !verified(row, rec)) {
      $('#form-message').textContent = '不能标为已验证：须提供与当前源码对应的独立运行/浏览器/学科证据、审查 SHA、有效链接、实际结果、步骤、范围、标准与审查者。';
      return;
    }
    if (rec.status === '明确存在的问题' && !confirmedIssue(rec)) {
      $('#form-message').textContent = '明确问题需要仓库代码位置、实际现象和可复现步骤；否则改为部分接入或未确认。';
      return;
    }
    const old = state.records.findIndex((r) => recordKey(r) === recordKey(rec));
    if (old >= 0) state.records[old] = rec;
    else state.records.push(rec);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state.records)); }
    catch { $('#form-message').textContent = '本机保存失败，请导出 JSON。'; return; }
    $('#form-message').textContent = '记录已保存在本机。导出 JSON 并提交到 audit/records.json 才能在 Git 中留存版本。';
    renderSummary(visibleRows());
  }
  function exportRecords() {
    const output = JSON.stringify({ schemaVersion: 1, sourceRevision: state.inventory.sourceRevision,
      exportedAt: new Date().toISOString(), records: state.records }, null, 2) + '\n';
    const url = URL.createObjectURL(new Blob([output], { type: 'application/json' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'ln-audit-records-' + new Date().toISOString().slice(0, 10) + '.json';
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 500);
  }
  async function importRecords(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      if (file.size > 2_000_000) throw new Error('文件过大');
      const data = JSON.parse(await file.text());
      if (data.schemaVersion !== 1 || !Array.isArray(data.records)) throw new Error('记录格式或版本不正确');
      const incoming = data.records.filter((r) => r && typeof r === 'object' &&
        lookup(r.id, r.courseId) && statuses.includes(r.status) &&
        SOURCE_CLASSES.includes(r.sourceKind));
      const unique = new Map(state.records.map((r) => [recordKey(r), r]));
      incoming.forEach((r) => unique.set(recordKey(r),
        Object.fromEntries(Object.entries(r).filter(([key]) =>
          ['id','courseId','anchor','updatedAt',...fields].includes(key)))));
      state.records = [...unique.values()];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.records));
      $('#form-message').textContent = '导入 ' + incoming.length + ' 条记录。旧版本证据仅在源码摘要和条件匹配时显示已验证。';
      const row = allRows().find((r) => fullId(r) === $('#record-form').elements.id.value);
      if (row) fillEditor($('#record-form'), row, $('#record-form').elements.anchor.value);
      renderSummary(visibleRows());
    } catch (err) {
      $('#form-message').textContent = '导入失败：' + err.message;
    }
    event.target.value = '';
  }
  function deleteRecord() {
    const form = $('#record-form');
    const key = form.elements.id.value + (form.elements.anchor.value ? '#' + form.elements.anchor.value : '');
    state.records = state.records.filter((r) => recordKey(r) !== key);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.records));
    const row = allRows().find((r) => fullId(r) === form.elements.id.value);
    if (row) fillEditor($('#record-form'), row, form.elements.anchor.value);
    $('#form-message').textContent = '仅删除本机记录；仓库记录仍需通过 Git 变更。';
    renderSummary(visibleRows());
  }
  function changeView(view) {
    state.view = view;
    render();
    $('#audit-main').scrollIntoView({ block: 'start' });
  }
  async function initialize() {
    try {
      const [sourceResponse, recordResponse] = await Promise.all([
        fetch('inventory.json'), fetch('records.json')
      ]);
      if (!sourceResponse.ok || !recordResponse.ok) throw new Error('审查清单或记录文件不存在');
      const inventory = await sourceResponse.json();
      const records = await recordResponse.json();
      if (inventory.schemaVersion !== 1 || !Array.isArray(inventory.sections) ||
          records.schemaVersion !== 1 || !Array.isArray(records.records)) {
        throw new Error('审查数据格式不符合 v1');
      }
      state.inventory = inventory;
      const merged = new Map(records.records.map((rec) => [recordKey(rec), rec]));
      try {
        const local = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        if (Array.isArray(local)) local.forEach((rec) => {
          if (rec && lookup(rec.id, rec.courseId)) merged.set(recordKey(rec), rec);
        });
      } catch {}
      state.records = [...merged.values()];
      $('#revision').textContent = '仓库版本 ' + inventory.sourceRevision.slice(0, 12) +
        ' · 自动扫描 ≠ 已验证';
      $('#course-filter').insertAdjacentHTML('beforeend', inventory.courses.map(
        (course) => '<option value="' + escape(course.id) + '">' + escape(course.label) + '</option>'
      ).join(''));
      $('#course-filter').addEventListener('change', (event) => { state.course = event.target.value; render(); });
      $('#audit-search').addEventListener('input', (event) => { state.query = event.target.value; render(); });
      $('#audit-nav').addEventListener('click', (event) => {
        const item = event.target.closest('button[data-view]');
        if (item) changeView(item.dataset.view);
      });
      $('#audit-body').addEventListener('click', (event) => {
        const review = event.target.closest('[data-review]');
        if (review) { state.selected = review.dataset.review; changeView('edit'); }
        const course = event.target.closest('[data-course]');
        if (course) { state.course = course.dataset.course; $('#course-filter').value = state.course; changeView(course.dataset.view || 'catalog'); }
      });
      render();
    } catch (err) {
      $('#audit-body').innerHTML = empty('验收数据加载失败：' + err.message + '。请确认以 HTTP 服务访问已构建站点，且 inventory.json 已生成。');
    }
  }
  initialize();
})();
