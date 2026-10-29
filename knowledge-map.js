'use strict';

(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const snapshots = new Map();
  let sequence = 0;
  const escape = (value) => String(value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const svg = (name, attributes = {}, text) => {
    const element = document.createElementNS(NS, name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const short = (value, length) => { const chars = Array.from(value); return chars.length > length ? chars.slice(0, length - 1).join('') + '…' : value; };
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  class KnowledgeMap extends HTMLElement {
    set course(value) { this._course = value; if (this.isConnected) this.mount(); }
    get course() { return this._course; }
    connectedCallback() { if (this.course) this.mount(); }
    disconnectedCallback() { this.release(); }

    release() {
      if (this.nodes && this.mountedCourseId) snapshots.set(this.mountedCourseId, {
        view: { ...this.view }, group: this.group, width: this.width, height: this.height
      });
      this.controller?.abort();
      this.observer?.disconnect();
    }

    mount() {
      this.release();
      const course = this.course;
      this.classList.toggle('school-map', course.level === 'highschool');
      this.mountedCourseId = course.id;
      const byId = new Map(course.sections.map((section) => [section.id, section]));
      this.groups = [...new Set(course.sections.map((section) => section.group))];
      const metadata = course.knowledgeMap;
      // Without authored semantic links, use an honest chapter/reading-order map.
      const definitions = metadata?.nodes?.length ? metadata.nodes : course.sections.map((section) => ({ section: section.id, title: section.title, note: section.group }));
      this.nodes = definitions.filter((node) => byId.has(node.section)).map((node) => ({ ...node, id: node.section, section: byId.get(node.section), group: this.groups.indexOf(byId.get(node.section).group) }));
      const counters = new Map();
      this.nodes.forEach((node) => {
        const row = counters.get(node.group) || 0;
        // Diagram coordinates are authored by the layout; gestures only change the viewport.
        Object.defineProperties(node, {
          x: { value: 48 + node.group * 400, enumerable: true },
          y: { value: 222 + row * 94, enumerable: true }
        });
        node.order = row + 1;
        counters.set(node.group, row + 1);
      });
      this.byNode = new Map(this.nodes.map((node) => [node.id, node]));
      this.edges = [];
      this.groups.forEach((_, index) => {
        const lane = this.nodes.filter((node) => node.group === index);
        lane.slice(1).forEach((node, i) => this.edges.push({ from: lane[i].id, to: node.id, type: 'order', label: '阅读顺序' }));
      });
      (metadata?.links || []).forEach((edge) => {
        if (this.byNode.has(edge.from) && this.byNode.has(edge.to)) this.edges.push({ ...edge, type: 'relation' });
      });
      const saved = snapshots.get(course.id);
      this.group = saved?.group ?? (course.level === 'highschool' || matchMedia('(max-width: 720px)').matches ? 0 : -1);
      this.view = saved?.view ? { ...saved.view } : { x: 0, y: 0, k: 1 };
      this.width = saved?.width || 0; this.height = saved?.height || 0;
      this.pointers = new Map(); this.gesture = null; this.query = ''; this.selected = null; this.showRelations = false;
      this.classList.remove('show-all-relations');
      this.uid = 'ln-map-' + (++sequence);
      this.controller = new AbortController();
      const signal = this.controller.signal;
      const link = (section, text) => '<a href="#course/' + escape(course.id) + '/' + escape(section.id) + '">' + escape(text || section.title) + '</a>';
      this.innerHTML = '<section class="knowledge-map" aria-label="' + escape(course.title) + '知识图谱">' +
        '<div class="map-toolbar"><div class="map-groups" role="group" aria-label="图谱章节"><button data-map-group="-1">全部</button>' + this.groups.map((group, i) => '<button title="' + escape(group) + '" data-map-group="' + i + '">' + escape(group.replace(/^第\d+章\s*/, '')) + '</button>').join('') + '</div>' +
        '<label class="map-relation-toggle"><input type="checkbox" aria-label="显示全部知识联系">全部联系</label><label class="map-search"><span class="map-search-label">查找节点</span><input type="search" aria-label="查找图谱知识点" placeholder="查找知识点…"></label></div>' +
        '<div class="map-canvas-wrap"><svg class="map-canvas" tabindex="0" role="group" aria-label="可交互知识图谱，拖动画布移动，滚轮或双指缩放，点击节点阅读。方向键移动，加减号缩放，Home 适应全图。"></svg>' +
        '<div class="map-zoom" role="group" aria-label="图谱缩放"><button data-map-action="out" aria-label="缩小图谱" title="缩小">−</button><output aria-label="缩放比例">100%</output><button data-map-action="in" aria-label="放大图谱" title="放大">+</button><button data-map-action="fit" class="map-fit">适应全图</button><button data-map-action="reset" title="回到当前章节起点">归位</button></div></div>' +
        '<div class="map-footer"><p>拖动平移 · 滚轮 / 双指缩放 · 点击进入正文</p><div class="map-legend"><span class="map-order-key">阅读顺序</span><span class="map-relation-key">知识联系</span></div></div>' +
        '<p class="map-status" role="status" aria-live="polite"></p><div class="map-node-context" aria-live="polite"><span>指向或聚焦节点，查看它与其他知识的联系。</span></div>' +
        '<details class="map-connections"><summary>跨知识联系 <span>' + (metadata?.links?.length || 0) + '</span></summary><ul>' + (metadata?.links || []).map((edge) => '<li><div>' + link(byId.get(edge.from), this.byNode.get(edge.from).title) + '<span aria-hidden="true"> → </span>' + link(byId.get(edge.to), this.byNode.get(edge.to).title) + '</div><p>' + escape(edge.description) + '</p></li>').join('') + '</ul></details>' +
        '<details class="map-directory"><summary>全部章节与资料 <span>' + course.sections.length + '</span></summary><div class="map-directory-groups">' + this.groups.map((group) => '<section><h3>' + escape(group) + '</h3><ul>' + course.sections.filter((section) => section.group === group).map((section) => '<li>' + link(section) + '</li>').join('') + '</ul></section>').join('') + '</div></details></section>';
      if (!metadata?.links?.length) this.querySelector('.map-connections').hidden = true;
      this.canvas = this.querySelector('.map-canvas');
      this.layer = svg('g', { class: 'map-world' });
      const defs = svg('defs');
      ['order', 'relation'].forEach((type) => {
        const marker = svg('marker', { id: this.uid + '-' + type, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' });
        marker.append(svg('path', { d: 'M 1 1 L 9 5 L 1 9 Z', class: 'map-arrow-' + type })); defs.append(marker);
      });
      this.canvas.append(defs, this.layer);
      this.rootElement = svg('g', { class: 'map-course-root' });
      const rootX = 48 + (this.groups.length - 1) * 200;
      const rootCenter = rootX + 139;
      const tree = svg('path', { class: 'map-hierarchy-edge', d: 'M' + rootCenter + ' 70 V90' + this.groups.map((_, index) => ' M' + rootCenter + ' 90 H' + (187 + index * 400) + ' V112').join('') });
      this.rootElement.append(tree, svg('rect', { x: rootX, y: 12, width: 278, height: 58, rx: 10 }));
      this.rootElement.append(svg('text', { x: rootCenter, y: 37, 'text-anchor': 'middle', class: 'map-root-title' }, course.title));
      this.rootElement.append(svg('text', { x: rootCenter, y: 56, 'text-anchor': 'middle', class: 'map-root-note' }, this.groups.length + (course.level === 'highschool' ? ' 册 · ' : ' 章 · ') + this.nodes.length + ' 个知识点'));
      this.layer.append(this.rootElement);
      this.groupElements = this.groups.map((title, index) => {
        const heading = svg('g', { class: 'map-group-heading' });
        const x = 48 + index * 400;
        const description = metadata?.chapters?.find((chapter) => chapter.group === title)?.description || this.nodes.filter((node) => node.group === index).length + ' 个知识点 · 按章节阅读';
        heading.append(svg('path', { class: 'map-hierarchy-edge', d: 'M' + (x + 139) + ' 184 V222', 'marker-end': 'url(#' + this.uid + '-order)' }));
        heading.append(svg('rect', { x, y: 112, width: 278, height: 72, rx: 10 }));
        heading.append(svg('text', { x: x + 16, y: 140 }, title));
        heading.append(svg('text', { x: x + 16, y: 164, class: 'map-group-count' }, short(description, 21)));
        this.layer.append(heading); return heading;
      });
      this.edges.forEach((edge) => {
        edge.element = svg('g', { class: 'map-edge map-edge-' + edge.type });
        edge.path = svg('path', { 'marker-end': 'url(#' + this.uid + '-' + edge.type + ')', 'vector-effect': 'non-scaling-stroke' });
        edge.label = svg('text', { class: 'map-edge-label', 'text-anchor': 'middle' }, edge.label);
        edge.element.append(edge.path, edge.label); this.layer.append(edge.element);
      });
      this.nodes.forEach((node) => {
        const anchor = svg('a', { href: '#course/' + course.id + '/' + node.id, class: 'map-node', 'data-node': node.id, tabindex: 0, 'aria-label': node.title + '，打开' + node.section.title });
        anchor.append(svg('title', {}, node.title + '：' + (node.note || node.section.title) + '。点击阅读；拖动平移整张图，节点位置固定。'));
        anchor.append(svg('rect', { width: 278, height: 78, rx: 11 }));
        anchor.append(svg('text', { x: 16, y: 22, class: 'map-node-number' }, String(node.order).padStart(2, '0')));
        anchor.append(svg('text', { x: 44, y: 30, class: 'map-node-title' }, short(node.title, 11)));
        anchor.append(svg('text', { x: 16, y: 59, class: 'map-node-note' }, short(node.note || node.section.title, 20)));
        anchor.append(svg('path', { d: 'M247 20h12v12m0-12-13 13', class: 'map-node-open' }));
        this.layer.append(anchor); node.element = anchor;
      });
      this.updateGeometry(); this.updateVisibility();
      this.addEventListener('click', (event) => {
        const group = event.target.closest('[data-map-group]');
        if (group) { this.group = Number(group.dataset.mapGroup); this.updateVisibility(); this.fit(true); }
        const action = event.target.closest('[data-map-action]')?.dataset.mapAction;
        if (action === 'in') this.zoomAt(this.view.k * 1.25);
        if (action === 'out') this.zoomAt(this.view.k / 1.25);
        if (action === 'fit') this.fit(false);
        if (action === 'reset') this.fit(true);
      }, { signal });
      this.querySelector('.map-relation-toggle input').addEventListener('change', (event) => {
        this.showRelations = event.target.checked;
        this.classList.toggle('show-all-relations', this.showRelations);
      }, { signal });
      this.querySelector('.map-search input').addEventListener('input', (event) => {
        this.query = event.target.value.trim().toLowerCase();
        this.updateVisibility(); this.fit(true);
      }, { signal });
      this.canvas.addEventListener('pointerover', (event) => { const node = event.target.closest('[data-node]'); if (node && !this.gesture) this.highlight(node.dataset.node); }, { signal });
      this.canvas.addEventListener('focusin', (event) => {
        const node = event.target.closest('[data-node]');
        if (node) { this.highlight(node.dataset.node); this.ensureVisible(this.byNode.get(node.dataset.node)); }
      }, { signal });
      this.canvas.addEventListener('wheel', (event) => {
        event.preventDefault();
        const box = this.canvas.getBoundingClientRect();
        this.zoomAt(this.view.k * Math.exp(-event.deltaY * 0.0015), event.clientX - box.left, event.clientY - box.top);
      }, { passive: false, signal });
      this.canvas.addEventListener('pointerdown', (event) => this.pointerDown(event), { signal });
      this.canvas.addEventListener('pointermove', (event) => this.pointerMove(event), { signal });
      this.canvas.addEventListener('pointerup', (event) => this.pointerEnd(event), { signal });
      this.canvas.addEventListener('pointercancel', (event) => this.pointerEnd(event, true), { signal });
      this.canvas.addEventListener('keydown', (event) => {
        // Native anchors retain Enter and normal link behavior.
        const steps = { ArrowLeft: [60, 0], ArrowRight: [-60, 0], ArrowUp: [0, 60], ArrowDown: [0, -60] };
        if (steps[event.key]) { event.preventDefault(); this.view.x += steps[event.key][0]; this.view.y += steps[event.key][1]; this.transform(); }
        if (['+', '=', '-', 'Home'].includes(event.key)) {
          event.preventDefault();
          if (event.key === 'Home') this.fit(false);
          else this.zoomAt(this.view.k * (event.key === '-' ? 0.8 : 1.25));
        }
      }, { signal });
      this.observer = new ResizeObserver(() => {
        const box = this.canvas.getBoundingClientRect();
        const oldWidth = this.width, oldHeight = this.height;
        this.width = box.width; this.height = box.height;
        if (!this.width || !this.height) return;
        if (!oldWidth || !oldHeight) this.fit(true);
        else { this.view.x += (this.width - oldWidth) / 2; this.view.y += (this.height - oldHeight) / 2; this.transform(); }
      });
      this.observer.observe(this.canvas);
    }

    visibleNodes() { return this.nodes.filter((node) => this.group < 0 || node.group === this.group); }
    updateVisibility() {
      const visible = this.visibleNodes();
      const matches = visible.filter((node) => [node.title, node.note, node.section.title, ...(node.keywords || [])].join(' ').toLowerCase().includes(this.query));
      this.matches = matches;
      const visibleIds = new Set(visible.map((node) => node.id));
      this.nodes.forEach((node) => {
        node.element.style.display = visibleIds.has(node.id) ? '' : 'none';
        node.element.classList.toggle('is-search-dim', !!this.query && !matches.includes(node));
      });
      this.edges.forEach((edge) => { edge.element.style.display = visibleIds.has(edge.from) && visibleIds.has(edge.to) ? '' : 'none'; });
      this.rootElement.style.display = this.group < 0 ? '' : 'none';
      this.groupElements.forEach((element, i) => { element.style.display = this.group < 0 || this.group === i ? '' : 'none'; });
      this.querySelectorAll('[data-map-group]').forEach((button) => button.setAttribute('aria-pressed', String(Number(button.dataset.mapGroup) === this.group)));
      this.querySelector('.map-status').textContent = this.query ? (matches.length ? matches.length + ' 个匹配知识点' : '当前章节没有匹配的知识点，可切换“全部”查找。') : visible.length + ' 个知识点 · ' + this.edges.filter((edge) => visibleIds.has(edge.from) && visibleIds.has(edge.to)).length + ' 条连接';
      this.highlight(null);
    }

    updateGeometry() {
      this.nodes.forEach((node) => node.element.setAttribute('transform', 'translate(' + node.x + ' ' + node.y + ')'));
      this.edges.forEach((edge) => {
        const a = this.byNode.get(edge.from), b = this.byNode.get(edge.to);
        let x1, y1, x2, y2, d;
        if (edge.type === 'order') {
          x1 = a.x + 139; y1 = a.y + 78; x2 = b.x + 139; y2 = b.y;
          const mid = (y1 + y2) / 2;
          d = `M${x1} ${y1} C${x1} ${mid},${x2} ${mid},${x2} ${y2}`;
        } else {
          const right = b.x >= a.x;
          x1 = a.x + (right ? 278 : 0); y1 = a.y + 39;
          x2 = b.x + (right ? 0 : 278); y2 = b.y + 39;
          if (a.group === b.group) {
            const gutter = a.x + 306 + this.edges.indexOf(edge) % 3 * 12;
            x1 = a.x + 278; x2 = b.x + 278;
            d = `M${x1} ${y1} H${gutter} V${y2} H${x2}`;
            edge.label.setAttribute('x', gutter + 8);
            edge.label.setAttribute('y', (y1 + y2) / 2);
          } else if (Math.abs(a.group - b.group) === 1) {
            const gutter = (x1 + x2) / 2;
            d = `M${x1} ${y1} H${gutter} V${y2} H${x2}`;
            edge.label.setAttribute('x', gutter);
            edge.label.setAttribute('y', (y1 + y2) / 2 - 8);
          } else {
            const startGutter = x1 + (right ? 42 : -42);
            const endGutter = x2 - (right ? 42 : -42);
            const rail = 198 + this.edges.indexOf(edge) % 3 * 5;
            d = `M${x1} ${y1} H${startGutter} V${rail} H${endGutter} V${y2} H${x2}`;
            edge.label.setAttribute('x', (startGutter + endGutter) / 2);
            edge.label.setAttribute('y', rail - 8);
          }
        }
        edge.path.setAttribute('d', d);
        if (edge.type === 'order') {
          edge.label.setAttribute('x', (x1 + x2) / 2);
          edge.label.setAttribute('y', (y1 + y2) / 2 - 8);
        }
      });
    }

    transform() {
      this.layer.setAttribute('transform', `translate(${this.view.x} ${this.view.y}) scale(${this.view.k})`);
      this.querySelector('.map-zoom output').value = Math.round(this.view.k * 100) + '%';
    }
    zoomAt(scale, x = this.width / 2, y = this.height / 2) {
      const next = clamp(scale, 0.2, 2.5), ratio = next / this.view.k;
      this.view.x = x - (x - this.view.x) * ratio;
      this.view.y = y - (y - this.view.y) * ratio;
      this.view.k = next; this.transform();
    }
    fit(readable) {
      const nodes = this.query && this.matches.length ? this.matches : this.visibleNodes();
      if (!nodes.length || !this.width) return;
      const left = Math.min(...nodes.map((node) => node.x)) - 22;
      const right = Math.max(...nodes.map((node) => node.x + 278)) + 22;
      const top = this.query ? Math.min(...nodes.map((node) => node.y)) - 22 : (this.group < 0 ? 0 : 96);
      const bottom = Math.max(...nodes.map((node) => node.y + 78)) + 32;
      const widthScale = (this.width - 24) / (right - left);
      const heightScale = (this.height - 65) / (bottom - top);
      const k = clamp(Math.min(widthScale, readable ? (heightScale >= 0.8 ? heightScale : 1) : heightScale), 0.2, readable ? 1 : 1.5);
      this.view = { k, x: (this.width - (right - left) * k) / 2 - left * k, y: 20 - top * k };
      this.transform();
    }
    ensureVisible(node) {
      const left = node.x * this.view.k + this.view.x, top = node.y * this.view.k + this.view.y;
      if (left < 10 || top < 10 || left + 278 * this.view.k > this.width - 10 || top + 78 * this.view.k > this.height - 65) {
        this.view.x = this.width / 2 - (node.x + 139) * this.view.k;
        this.view.y = this.height / 2 - (node.y + 39) * this.view.k;
        this.transform();
      }
    }
    highlight(id) {
      this.selected = id;
      const connected = new Set(id ? [id] : []);
      this.edges.forEach((edge) => {
        const related = !!id && (edge.from === id || edge.to === id);
        edge.element.classList.toggle('is-related', related);
        if (related) { connected.add(edge.from); connected.add(edge.to); }
      });
      this.nodes.forEach((node) => {
        node.element.classList.toggle('is-selected', node.id === id);
        node.element.classList.toggle('is-neighbor', !!id && node.id !== id && connected.has(node.id));
      });
      const context = this.querySelector('.map-node-context');
      if (!id) { context.innerHTML = '<span>指向或聚焦节点，查看它与其他知识的联系。</span>'; return; }
      const node = this.byNode.get(id);
      const relations = this.edges.filter((edge) => edge.type === 'relation' && (edge.from === id || edge.to === id));
      context.innerHTML = '<strong>' + escape(node.title) + '</strong>' + (relations.length ? '<ul>' + relations.map((edge) => {
        const other = this.byNode.get(edge.from === id ? edge.to : edge.from);
        return '<li><a href="#course/' + escape(this.course.id) + '/' + escape(other.id) + '">' + escape(other.title) + '</a><span>' + escape(edge.description) + '</span></li>';
      }).join('') + '</ul>' : '<span>' + escape(node.note || node.section.title) + '，沿实线按章节顺序学习。</span>');
    }

    point(event) { return { x: event.clientX, y: event.clientY }; }
    pointerDown(event) {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      this.pointers.set(event.pointerId, this.point(event));
      this.canvas.setPointerCapture(event.pointerId);
      if (this.pointers.size === 2) { this.beginPinch(); return; }
      const id = event.target.closest('[data-node]')?.dataset.node;
      this.gesture = { id, start: this.point(event), view: { ...this.view }, moved: false };
      this.canvas.classList.add('is-dragging');
      if (id) this.highlight(id);
    }
    beginPinch() {
      const [a, b] = [...this.pointers.values()];
      const box = this.canvas.getBoundingClientRect();
      const center = { x: (a.x + b.x) / 2 - box.left, y: (a.y + b.y) / 2 - box.top };
      this.gesture = { pinch: true, moved: true, distance: Math.max(1, Math.hypot(a.x - b.x, a.y - b.y)), scale: this.view.k, world: { x: (center.x - this.view.x) / this.view.k, y: (center.y - this.view.y) / this.view.k } };
    }
    pointerMove(event) {
      if (!this.pointers.has(event.pointerId) || !this.gesture) return;
      this.pointers.set(event.pointerId, this.point(event));
      const gesture = this.gesture;
      if (this.pointers.size >= 2 && gesture.pinch) {
        const [a, b] = [...this.pointers.values()];
        const box = this.canvas.getBoundingClientRect();
        const k = clamp(gesture.scale * Math.hypot(a.x - b.x, a.y - b.y) / gesture.distance, 0.2, 2.5);
        this.view = { k, x: (a.x + b.x) / 2 - box.left - gesture.world.x * k, y: (a.y + b.y) / 2 - box.top - gesture.world.y * k };
        this.transform(); return;
      }
      if (gesture.pinch) return;
      const dx = event.clientX - gesture.start.x, dy = event.clientY - gesture.start.y;
      if (Math.hypot(dx, dy) > 5) gesture.moved = true;
      if (!gesture.moved) return;
      this.view.x = gesture.view.x + dx;
      this.view.y = gesture.view.y + dy;
      this.transform();
    }
    pointerEnd(event, cancelled = false) {
      if (!this.pointers.has(event.pointerId)) return;
      const gesture = this.gesture;
      this.pointers.delete(event.pointerId);
      if (this.canvas.hasPointerCapture(event.pointerId)) this.canvas.releasePointerCapture(event.pointerId);
      if (!cancelled && this.pointers.size === 0 && gesture?.id && !gesture.moved) location.hash = 'course/' + this.course.id + '/' + gesture.id;
      if (this.pointers.size === 1) {
        this.gesture = { start: [...this.pointers.values()][0], view: { ...this.view }, moved: true };
      } else if (!this.pointers.size) {
        this.gesture = null; this.canvas.classList.remove('is-dragging');
      }
    }
  }
  customElements.define('ln-knowledge-map', KnowledgeMap);
})();
