'use strict';

(() => {
  const index = window.LN_PUBLICATION_INDEX || {};
  const stack = [];
  let pendingRestore = null, activeTarget = null, sequence = 0;
  const canonical = (value) => { try { return decodeURIComponent(value); } catch { return value; } };
  const equalHash = (a, b) => canonical(a) === canonical(b);
  const normalize = (value) => value.replace(/[‐‑–—－-．]/g, '.');
  const route = (course, section, anchor) => '#course/' + course + '/' + section + '/' + encodeURIComponent(anchor);
  const byId = (body, id) => [...body.querySelectorAll('[id]')].find((element) => element.id === id);
  const make = (tag, className, text) => { const element = document.createElement(tag); element.className = className; if (text) element.textContent = text; return element; };
  const returnButton = make('button', 'reference-return', '↩ 返回引用处');
  returnButton.type = 'button'; returnButton.hidden = true;
  document.querySelector('.workspace').append(returnButton);
  const updateReturn = () => { returnButton.hidden = !stack.length; };

  function resolve(course, section, kind, number) {
    const candidates = (index[course.id]?.targets || []).filter((entry) => entry.kind === kind && entry.number === normalize(number));
    const local = candidates.filter((entry) => entry.section === section.id);
    if (local.length === 1) return local[0];
    const chapter = candidates.filter((entry) => entry.group === section.group);
    if (chapter.length === 1) return chapter[0];
    return candidates.length === 1 ? candidates[0] : null;
  }

  function targetLabel(body, target, course, prefix) {
    const label = make('a', 'paper-target-label', prefix + target.number);
    label.href = route(course.id, target.section, target.anchor);
    label.title = '定位' + prefix + target.number;
    label.setAttribute('aria-label', prefix + target.number);
    return label;
  }

  function prepare(body, course, section) {
    const data = index[course.id]?.sections[section.id];
    if (!data) return;
    body.classList.add('publication-body');
    const equations = [...body.querySelectorAll('.math-block, .math.display')];
    equations.forEach((element, i) => {
      const target = data.equations[i];
      if (!target || element.classList.contains('paper-equation')) return;
      element.id = target.anchor;
      element.classList.add('paper-equation'); element.dataset.referenceKind = 'equation';
      // Move only the visual KaTeX tag; the mathematical expression and MathML are preserved.
      element.querySelectorAll('.katex-tag, .katex-html > .tag').forEach((tag) => tag.remove());
      const scroll = make('span', 'paper-equation-scroll');
      while (element.firstChild) scroll.append(element.firstChild);
      element.append(scroll);
      if (target.number) {
        const number = targetLabel(body, target, course, '');
        number.textContent = '(' + target.number + ')'; number.classList.add('equation-number');
        number.setAttribute('aria-label', '公式（' + target.number + '）');
        element.append(number); element.classList.add('is-numbered');
      }
    });
    [['figure', 'figures', 'figcaption', '图 '], ['table', 'tables', 'caption', '表 ']].forEach(([tag, key, captionTag, prefix]) => {
      [...body.querySelectorAll(tag)].forEach((element, i) => {
        const target = data[key][i];
        if (!target || element.dataset.referenceKind) return;
        element.id = target.anchor; element.dataset.referenceKind = tag; element.classList.add('paper-' + tag);
        let caption = element.querySelector(captionTag);
        if (!caption) {
          caption = document.createElement(captionTag);
          const heading = [...body.querySelectorAll('h2,h3,h4,h5')].filter((candidate) => candidate.compareDocumentPosition(element) & Node.DOCUMENT_POSITION_FOLLOWING).at(-1);
          caption.textContent = heading?.textContent || section.title;
          if (tag === 'table') element.prepend(caption); else element.append(caption);
        }
        if (tag === 'table' && !element.parentElement.classList.contains('table-scroll')) {
          const holder = make('div', 'table-scroll'); element.replaceWith(holder); holder.append(element);
        }
        const first = caption.firstChild;
        // An existing printed label remains authoritative; avoid printing it twice.
        if (first?.nodeType === Node.TEXT_NODE) first.textContent = first.textContent.replace(/^\s*(?:图|表)\s*(?:\d+|[A-Za-z])(?:[.\-]\d+)+\s*[：:.、]?\s*/, '');
        caption.prepend(targetLabel(body, target, course, prefix), document.createTextNode('　'));
      });
    });
    const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!/(?:公式|方程|式|图|表)\s*[（(]?\s*(?:\d+|[A-Z])[.．\-－]\d/.test(node.textContent)) return NodeFilter.FILTER_REJECT;
        return node.parentElement.closest('a, button, svg, math, annotation, .katex, .paper-equation, h2, h3, h4, h5, h6') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    const texts = []; while (walker.nextNode()) texts.push(walker.currentNode);
    texts.forEach((node) => {
      const regex = /(公式|方程|式|图|表)\s*[（(]?\s*((?:\d+|[A-Z])(?:[.．\-－]\d+)+(?:[a-z])?)\s*[)）]?/g;
      const fragment = document.createDocumentFragment(); let start = 0, changed = false;
      for (const match of node.textContent.matchAll(regex)) {
        const kind = match[1] === '图' ? 'figure' : match[1] === '表' ? 'table' : 'equation';
        const target = resolve(course, section, kind, match[2]);
        if (!target) continue; // Never guess among ambiguous or missing references.
        fragment.append(document.createTextNode(node.textContent.slice(start, match.index)));
        const link = make('a', 'paper-reference', match[0]);
        link.href = route(course.id, target.section, target.anchor); fragment.append(link);
        start = match.index + match[0].length; changed = true;
      }
      if (changed) { fragment.append(document.createTextNode(node.textContent.slice(start))); node.replaceWith(fragment); }
    });
    let counter = 0;
    body.querySelectorAll('a[href^="#course/"]').forEach((link) => {
      if (link.classList.contains('paper-target-label') || link.getAttribute('href').split('/').length < 4) return;
      link.classList.add('paper-reference');
      if (!link.id) link.id = 'paper-reference-' + (++counter);
    });
  }

  function rootTarget(body, anchor) {
    const [course, section] = body.dataset.lessonKey.split('/');
    const catalog = index[course]?.targets.find((entry) => entry.section === section && (entry.anchor === anchor || entry.aliases.includes(anchor)));
    const element = byId(body, catalog?.anchor || anchor);
    if (!element) return null;
    if (element.classList.contains('equation-anchor')) {
      const next = element.nextElementSibling;
      if (next?.classList.contains('paper-equation')) return next;
    }
    if (element.hasAttribute('data-definition-source')) return element;
    return element.closest('.paper-equation, figure, table') || element;
  }

  function markTarget(body, anchor, scroll = true) {
    const element = rootTarget(body, anchor);
    if (!element) return;
    body.querySelectorAll('.reference-target, .is-reference-return').forEach((node) => node.classList.remove('reference-target', 'is-reference-return'));
    element.classList.add('reference-target');
    if (!element.hasAttribute('tabindex')) element.tabIndex = -1;
    if (scroll) { element.scrollIntoView({ block: 'center', behavior: 'instant' }); element.focus({ preventScroll: true }); }
    activeTarget = element;
    if (stack.length && equalHash(location.hash, stack.at(-1).destination)) {
      const label = element.querySelector('.paper-target-label');
      if (label) { label.classList.add('is-reference-return'); label.title = '点击返回引用处'; label.setAttribute('aria-label', label.textContent + '，点击返回引用处'); }
    }
  }

  function restorePosition(body, frame) {
    const origin = byId(body, frame.focus);
    if (origin) {
      window.scrollBy({ left: 0, top: origin.getBoundingClientRect().top - frame.offset, behavior: 'instant' });
      origin.focus({ preventScroll: true }); origin.classList.add('reference-origin');
    } else window.scrollTo({ left: frame.x, top: frame.y, behavior: 'instant' });
  }

  function settle(body, anchor) {
    const restore = pendingRestore && equalHash(location.hash, pendingRestore.source) ? pendingRestore : null;
    if (!restore && !anchor) { updateReturn(); return; }
    const expected = body.dataset.lessonKey;
    document.fonts.ready.then(() => requestAnimationFrame(() => requestAnimationFrame(() => {
      if (!body.isConnected || body.dataset.lessonKey !== expected) return;
      if (restore) {
        pendingRestore = null;
        if (anchor) markTarget(body, anchor, false);
        restorePosition(body, restore);
      } else if (anchor && !anchor.startsWith('page-')) markTarget(body, anchor);
      updateReturn();
    })));
  }

  function onRoute() {
    activeTarget = null;
    if (pendingRestore && !equalHash(location.hash, pendingRestore.source)) pendingRestore = null;
    const frame = stack.at(-1);
    if (frame && equalHash(location.hash, frame.source)) { pendingRestore = stack.pop(); }
    else if (frame && !equalHash(location.hash, frame.destination)) stack.length = 0;
    const active = stack.at(-1);
    if (active?.changed && equalHash(location.hash, active.destination)) history.replaceState({ ...history.state, publicationReference: active.id }, '', location.href);
    updateReturn();
  }

  function goBack() {
    const frame = stack.pop();
    if (!frame) return;
    pendingRestore = frame; updateReturn();
    if (frame.changed && history.state?.publicationReference === frame.id) history.back();
    else if (!equalHash(location.hash, frame.source)) location.hash = frame.source;
    else { pendingRestore = null; restorePosition(document.querySelector('#lesson-body'), frame); }
  }
  function followReference(destination, origin) {
    const frame = { id: ++sequence, source: location.hash, destination, focus: origin.id, offset: origin.getBoundingClientRect().top, x: scrollX, y: scrollY, changed: !equalHash(location.hash, destination) };
    stack.push(frame); updateReturn();
    if (frame.changed) location.hash = destination;
    else markTarget(document.querySelector('#lesson-body'), canonical(destination.split('/').slice(3).join('/')));
  }
  returnButton.addEventListener('click', goBack);
  document.addEventListener('click', (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('.lesson a');
    if (!link) return;
    if (link.classList.contains('is-reference-return') && activeTarget?.contains(link) && stack.length) { event.preventDefault(); goBack(); return; }
    if (!link.classList.contains('paper-reference')) return;
    const destination = link.getAttribute('href');
    if (!destination?.startsWith('#course/') || destination.split('/').length < 4) return;
    event.preventDefault();
    followReference(destination, link);
  });
  window.LNPublication = { prepare, settle, onRoute, resolve, followReference };
})();
