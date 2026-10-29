'use strict';

(() => {
  const catalog = window.LN_GLOSSARY || {};
  const sectionData = new WeakMap();
  let context = null, origin = null, serial = 0;
  const make = (tag, className, text) => { const e = document.createElement(tag); e.className = className; if (text) e.textContent = text; return e; };
  const clean = (text) => text.replace(/[\u200b\u200c\u200d\ufeff\s]/g, '').replace(/ϕ/g, 'φ').replace(/µ/g, 'μ');
  const displayKey = (text) => { const value = clean(text).replace(/′/g, "'"); const primes = (value.match(/'/g) || []).length; return value.replace(/[˙̇⋅¯ˉ‾→⃗']/g, '') + "'".repeat(primes); };
  const popup = make('div', 'definition-popover');
  popup.id = 'definition-popover'; popup.setAttribute('popover', 'auto'); popup.setAttribute('role', 'dialog'); popup.setAttribute('aria-labelledby', 'definition-title');
  document.querySelector('.workspace').append(popup);
  const opened = () => popup.matches(':popover-open');
  const entriesFor = (course) => catalog[course.id]?.entries || [];
  const shared = new Set(['B','H','bold:B','bold:H','μ','μ_0','μ_r','λ','cal:R','cal:F','Λ','L_sec','L_diff','M','ω','f']);

  function resolveSymbol(course, section, key, kind = 'symbol') {
    const entries = entriesFor(course).filter((e) => e.kind === kind && e.keys.includes(key) && (!e.sections || e.sections.includes(section.id)));
    const scoped = entries.filter((e) => e.sections?.includes(section.id));
    if (scoped.length) return scoped.length === 1 ? scoped[0] : null;
    const local = entries.filter((e) => e.group === section.group);
    if (local.length === 1) return local[0];
    if (!local.length && shared.has(key)) return entries.find((e) => e.source.section === 'magnetic-overview') || null;
    return null;
  }
  function termAliases(course, section) {
    const choices=new Map();
    entriesFor(course).filter(e=>e.kind==='term').forEach(entry=>{
      const local=!entry.sections || entry.sections.includes(section.id);
      const aliases=local?entry.aliases:entry.reuseAliases||[];
      const rank=entry.source.section===section.id?0:local?1:2;
      aliases.forEach(text=>{
        const key=text.toLowerCase(),options=choices.get(key)||[];
        options.push({text,entry,rank,caseSensitive:entry.caseSensitiveAliases?.includes(text)});choices.set(key,options);
      });
    });
    return [...choices.values()].flatMap(options=>{
      const best=options.filter(a=>a.rank===Math.min(...options.map(a=>a.rank)));
      return new Set(best.map(a=>a.entry.id)).size===1?[best[0]]:[];
    }).sort((a,b)=>b.text.length-a.text.length);
  }
  function plain(node) { return node.textContent; }
  function atom(node) {
    const c = [...node.children], name = node.localName;
    if (name === 'mi' || name === 'mtext') {
      const value = clean(plain(node));
      const variant = node.getAttribute('mathvariant') || '';
      if (['script','double-struck'].includes(variant)) return 'cal:' + value;
      if (variant.includes('bold')) return 'bold:' + value;
      // Roman unit letters are not the italic physical variables with the same spelling.
      if (node.getAttribute('mathvariant') === 'normal' && /^[A-Za-z]$/.test(value)) return '';
      return value;
    }
    if (name === 'msub' && c.length >= 2) return atom(c[0]) + '_' + clean(plain(c[1]));
    if (name === 'msubsup' && c.length >= 3) return atom(c[0]) + '_' + clean(plain(c[1])) + (/[′']/.test(plain(c[2])) ? "'" : '');
    if (name === 'msup' && c.length >= 2) return atom(c[0]) + (/[′']/.test(plain(c[1])) ? "'" : '');
    if (name === 'mover' && c.length >= 2) return (/[˙̇⋅.]/.test(plain(c[1])) ? 'dot:' : /[¯ˉ‾]/.test(plain(c[1])) ? 'bar:' : '') + atom(c[0]);
    if (c.length === 1 && ['mrow','mstyle','mpadded','semantics','math'].includes(name)) return atom(c[0]);
    return '';
  }
  function symbols(math, course, section) {
    const list = [];
    function visit(node) {
      if (['mi','mtext','msub','msup','msubsup','mover'].includes(node.localName)) {
        const key = atom(node);
        const next = node.nextElementSibling;
        if (/^[fgh]$/.test(key) && next?.localName === 'mo' && next.textContent === '(') return;
        const entry = resolveSymbol(course, section, key);
        if (entry) list.push({ key, entry, visible: displayKey(plain(node)) });
        else if (['msub','msubsup'].includes(node.localName) && node.children[1]) {
          const sub = clean(plain(node.children[1]));
          const notation = resolveSymbol(course, section, sub, 'subscript');
          if (notation) list.push({ key: 'subscript:' + sub, entry: notation, visible: displayKey(sub) });
        }
        return;
      }
      const children=[...node.children].filter((child)=>child.localName!=='annotation');
      for(let i=0;i<children.length;i++) {
        const child=children[i],next=children[i+1];
        if(plain(child)==='Δ' && next && ['mi','mtext','msub','msup','msubsup','mover'].includes(next.localName)) {
          const key='delta:'+atom(next),entry=resolveSymbol(course,section,key);
          if(entry)list.push({key,entry,visible:displayKey(plain(next))});
          i++;continue;
        }
        visit(child);
      }
    }
    visit(math); return list;
  }
  function identity(element) {
    if (!element.id) element.id = 'definition-occurrence-' + (++serial);
  }
  function interactive(element, entry, accessible = false) {
    element.classList.add('definition-symbol'); element.dataset.definition = entry.id; identity(element);
    if (accessible) {
      element.tabIndex = 0; element.setAttribute('role', 'link'); element.setAttribute('aria-haspopup', 'dialog');
      element.setAttribute('aria-label', '查看符号定义：' + entry.title);
    }
    element.title = '点击查看定义';
  }
  function compositeParent(element, root) {
    for (let parent = element.parentElement; parent && parent !== root; parent = parent.parentElement) {
      if (parent.classList.contains('accent') || parent.classList.contains('overline') || (parent.classList.contains('mord') && parent.querySelector(':scope > .msupsub'))) return parent;
    }
    return null;
  }

  function prepare(body, course, section) {
    const entries = entriesFor(course);
    if (!entries.length) return;
    sectionData.set(body, { course, section }); serial = 0;
    const passages = [...body.querySelectorAll('p,h2,h3,h4,li,td')];
    const tables = [...body.querySelectorAll('table')];
    entries.filter((e) => e.source.section === section.id).forEach((entry) => {
      const source = entry.source;
      const target = source.row !== undefined ? tables[source.table]?.rows[source.row] : passages[source.passage];
      if (target) { if (!target.id) target.id = source.anchor; target.dataset.definitionSource = ''; }
    });
    body.querySelectorAll('.katex').forEach((katex) => {
      const math = katex.querySelector('.katex-mathml math'), visual = katex.querySelector('.katex-html');
      if (!math || !visual) return;
      const items = symbols(math, course, section).sort((a,b) => b.visible.length - a.visible.length);
      const unique = [...new Map(items.map((item) => [item.entry.id, item.entry])).values()];
      const wrapper = katex.closest('.math-inline,.math.inline');
      if (wrapper && unique.length === 1 && items.some((item) => displayKey(visual.textContent) === item.visible)) {
        interactive(wrapper, unique[0], true); return;
      }
      items.forEach((item) => {
        const candidates = [...visual.querySelectorAll('.mord,.mop,.mathnormal,.mathcal')].filter((element) => {
          if (element.closest('[data-definition]') || element.querySelector('[data-definition]')) return false;
          if (displayKey(element.textContent) !== item.visible) return false;
          if (!item.key.startsWith('subscript:') && /^[A-Za-z]$/.test(item.visible) && (element.classList.contains('mathrm') || element.querySelector('.mathrm'))) return false;
          const accent = element.classList.contains('accent') || !!element.querySelector('.accent');
          const overline = element.classList.contains('overline') || !!element.querySelector('.overline') || [...element.querySelectorAll('.accent-body')].some(n=>/[¯ˉ‾]/.test(n.textContent));
          const dot = accent && [...element.querySelectorAll('.accent-body')].some(n=>/[˙̇⋅]/.test(n.textContent));
          if (item.key.startsWith('bar:') ? !overline : item.key.startsWith('dot:') ? !dot || overline : dot || overline) return false;
          const baseKey = item.key.replace(/^(?:delta:)?(?:bar:|dot:)?/, '');
          const script = element.classList.contains('mathcal') || !!element.querySelector('.mathcal');
          if (baseKey.startsWith('cal:') !== script) return false;
          const bold = element.classList.contains('boldsymbol') || element.classList.contains('mathbf') || !!element.querySelector('.boldsymbol,.mathbf');
          if (baseKey.startsWith('bold:') !== bold) return false;
          if (item.key.startsWith('subscript:')) return !!element.closest('.msupsub');
          return !compositeParent(element, visual);
        });
        candidates.forEach((element) => { if (!element.closest('[data-definition]')) interactive(element, item.entry); });
      });
      if (wrapper && unique.length) {
        wrapper.dataset.definitionList = unique.map((e) => e.id).join(' '); identity(wrapper);
        wrapper.classList.add('definition-expression'); wrapper.tabIndex = 0; wrapper.setAttribute('role','link'); wrapper.setAttribute('aria-haspopup','dialog');
        wrapper.setAttribute('aria-label','查看表达式中的符号定义');
      }
      const equation = katex.closest('.paper-equation');
      if (equation && unique.length && !equation.querySelector('.definition-formula-tool')) {
        const tool = make('button','definition-formula-tool','符号'); tool.type='button'; tool.dataset.definitionList=unique.map((e)=>e.id).join(' ');
        tool.setAttribute('aria-label','查看本公式的物理符号定义'); tool.setAttribute('aria-haspopup','dialog'); identity(tool); equation.append(tool);
      }
    });
    const aliases = termAliases(course, section);
    if (!aliases.length) return;
    const regexEscape = (value) => value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    const regex = new RegExp(aliases.map((alias) => regexEscape(alias.text)).join('|'),'gi');
    const walker = document.createTreeWalker(body,NodeFilter.SHOW_TEXT,{acceptNode(node){
      return node.parentElement.closest('a,button,svg,math,annotation,.katex,.paper-equation,h2,h3,h4,h5,h6,[data-definition],[data-definition-list]') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
    }});
    const texts=[];while(walker.nextNode())texts.push(walker.currentNode);
    texts.forEach((node)=>{
      const text=node.textContent,fragment=document.createDocumentFragment();let cursor=0,changed=false;
      for(const match of text.matchAll(regex)){
        const alias=aliases.find((candidate)=>candidate.text.toLowerCase()===match[0].toLowerCase()&&(!candidate.caseSensitive||candidate.text===match[0]));
        if(!alias)continue;
        if(/^[A-Za-z]/.test(match[0]) && (/[A-Za-z]/.test(text[match.index-1]||'') || /[A-Za-z]/.test(text[match.index+match[0].length]||'')))continue;
        fragment.append(document.createTextNode(text.slice(cursor,match.index)));
        const link=make('a','definition-term',match[0]);link.href='#course/'+course.id+'/'+alias.entry.source.section+'/'+encodeURIComponent(alias.entry.source.anchor);
        link.dataset.definition=alias.entry.id;link.setAttribute('aria-haspopup','dialog');link.title='点击查看释义';identity(link);fragment.append(link);
        cursor=match.index+match[0].length;changed=true;
      }
      if(changed){fragment.append(document.createTextNode(text.slice(cursor)));node.replaceWith(fragment);}
    });
  }

  function safeHtml(html) {
    const template=document.createElement('template');template.innerHTML=html;
    template.content.querySelectorAll('script,style,iframe,object,embed,form,input,button').forEach((e)=>e.remove());
    template.content.querySelectorAll('*').forEach((element)=>{
      [...element.attributes].forEach((a)=>{if(a.name.startsWith('on')||['id','href','src','srcdoc','tabindex','autofocus'].includes(a.name))element.removeAttribute(a.name);});
    });return template.content;
  }
  function position() {
    if(!opened()||!origin?.isConnected)return;
    const rect=origin.getBoundingClientRect(),width=innerWidth,height=innerHeight;
    const box=popup.getBoundingClientRect();
    const left=Math.max(12,Math.min(rect.left,width-box.width-12));
    const bottomLimit=height-84;
    const below=rect.bottom+8;
    const top=below+box.height<=bottomLimit?below:Math.max(12,Math.min(rect.top-box.height-8,bottomLimit-box.height));
    popup.style.left=left+'px';popup.style.top=top+'px';
  }
  function close(restore=false) {
    if(opened())popup.hidePopover();
    if(restore&&origin?.isConnected)origin.focus({preventScroll:true});
  }
  function shell(title) {
    popup.replaceChildren();
    const header=make('div','definition-header'),heading=make('h2','',title);heading.id='definition-title';
    const dismiss=make('button','definition-close','×');dismiss.type='button';dismiss.setAttribute('aria-label','关闭解释');dismiss.addEventListener('click',()=>close(true));
    header.append(heading,dismiss);popup.append(header);
    return make('div','definition-content');
  }
  function show() {
    if(!opened())popup.showPopover();position();popup.querySelector('.definition-close').focus({preventScroll:true});
  }
  function entryById(id){return entriesFor(context.course).find((entry)=>entry.id===id);}
  function sourceExcerpt(entry, label) {
    const excerpt=make('details','definition-excerpt');excerpt.append(make('summary','',label));
    const copy=make('div','definition-copy');copy.append(safeHtml(entry.definitionHtml));excerpt.append(copy);
    excerpt.addEventListener('toggle',position);return excerpt;
  }
  function showEntry(entry) {
    if(!entry)return;
    const content=shell(entry.kind==='term'?entry.title:'符号定义');
    if(entry.kind!=='term') {
      const symbol=make('div','definition-symbol-title');symbol.append(safeHtml(entry.symbolHtml));content.append(symbol);
      if (entry.source.passage !== undefined && entry.description) {
        content.append(make('p','definition-copy',entry.description));
        content.append(sourceExcerpt(entry,'原文定义'));
      } else {
        content.append(make('p','definition-label','原文定义'));
        const text=make('div','definition-copy');text.append(safeHtml(entry.definitionHtml));content.append(text);
      }
      if(entry.unitHtml){content.append(make('p','definition-label','单位与约定'));const unit=make('div','definition-copy');unit.append(safeHtml(entry.unitHtml));content.append(unit);}
    } else {
      content.append(make('p','definition-english',entry.english));content.append(make('p','definition-copy',entry.description));
      content.append(sourceExcerpt(entry,'相关原文'));
    }
    content.append(make('p','definition-context',entry.group));popup.append(content);
    const footer=make('div','definition-footer'),source=make('a','definition-source-link',entry.kind==='term'?'查看原文位置 ↗':'查看原定义 ↗');
    source.href='#course/'+context.course.id+'/'+entry.source.section+'/'+encodeURIComponent(entry.source.anchor);
    source.addEventListener('click',(event)=>{
      if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
      event.preventDefault();const start=origin;close();window.LNPublication.followReference(source.getAttribute('href'),start);
    });footer.append(source);popup.append(footer);show();
  }
  function showList(ids) {
    const content=shell('本表达式的符号');
    ids.map(entryById).filter(Boolean).forEach((entry)=>{
      const button=make('button','definition-choice');button.type='button';button.append(make('strong','',entry.title),make('span','',entry.description));
      button.addEventListener('click',()=>showEntry(entry));content.append(button);
    });popup.append(content);show();
  }
  function activate(trigger) {
    const body=trigger.closest('#lesson-body');context=sectionData.get(body);
    if(!context)return;origin=trigger;
    if(trigger.dataset.definition)showEntry(entryById(trigger.dataset.definition));
    else showList(trigger.dataset.definitionList.split(' '));
  }
  document.addEventListener('click',(event)=>{
    if(event.defaultPrevented||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    const trigger=event.target.closest('[data-definition],[data-definition-list]');
    if(trigger){event.preventDefault();activate(trigger);}
  });
  document.addEventListener('keydown',(event)=>{
    const trigger=event.target.closest('[data-definition],[data-definition-list]');
    if(trigger&&trigger.tagName!=='BUTTON'&&['Enter',' '].includes(event.key)){event.preventDefault();activate(trigger);}
  });
  addEventListener('resize',position);
  addEventListener('scroll',(event)=>{
    if(!opened()||popup.contains(event.target))return;
    const rect=origin?.getBoundingClientRect();if(!rect||rect.bottom<58||rect.top>innerHeight-60)close();else position();
  },true);
  window.LNGlossary={prepare,onRoute:()=>{close();origin=null;context=null;},resolveSymbol,termAliases};
})();
