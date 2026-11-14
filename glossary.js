'use strict';

(() => {
  const catalog = window.LN_GLOSSARY || {};
  const sectionData = new WeakMap();
  let context = null, origin = null, serial = 0;
  const make = (tag, className, text) => { const e = document.createElement(tag); e.className = className; if (text) e.textContent = text; return e; };
  const clean = (text) => text.replace(/[\u200b\u200c\u200d\u2061\ufeff\s]/g, '').replace(/ϕ/g, 'φ').replace(/µ/g, 'μ');
  const displayKey = (text) => { const value = clean(text).replace(/′/g, "'"); const primes = (value.match(/'/g) || []).length; return value.replace(/[˙̇⋅¯ˉ‾→⃗^ˆ̂']/g, '') + "'".repeat(primes); };
  const equationOf = node => node.closest('.paper-equation')?.dataset.equation || '';
  const upperKey = value => {
    const text=clean(value).replace(/[−–]/g,'-').replace(/[∗⋆]/g,'*');
    if (/^[′']+$/.test(text)) return "'".repeat(text.length);
    return /^[+*-]$/.test(text) ? '^'+text : '';
  };
  const popup = make('div', 'definition-popover');
  popup.id = 'definition-popover'; popup.setAttribute('popover', 'auto'); popup.setAttribute('role', 'dialog'); popup.setAttribute('aria-labelledby', 'definition-title');
  document.querySelector('.workspace').append(popup);
  const opened = () => popup.matches(':popover-open');
  const entriesFor = (course) => catalog[course.id]?.entries || [];
  const shared = new Set(['B','H','bold:B','bold:H','μ','μ_0','μ_r','λ','cal:R','cal:F','Λ','L_sec','L_diff','M','ω','f']);

  function resolveSymbol(course, section, key, kind = 'symbol', equation = '') {
    const entries = entriesFor(course).filter((e) => e.kind === kind && e.keys.includes(key) && (!e.sections || e.sections.includes(section.id)) && (!e.equations || e.equations.includes(equation)));
    const exact = entries.filter(e=>e.equations?.includes(equation));
    if (exact.length) return exact.length===1 ? exact[0] : null;
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
    if (name === 'msubsup' && c.length >= 3) return atom(c[0]) + '_' + clean(plain(c[1])) + upperKey(plain(c[2]));
    if (name === 'msup' && c.length >= 2) return atom(c[0]) + upperKey(plain(c[1]));
    if (name === 'mover' && c.length >= 2) return (/[˙̇⋅.]/.test(plain(c[1])) ? 'dot:' : /[¯ˉ‾]/.test(plain(c[1])) ? 'bar:' : /[\^ˆ̂]/.test(plain(c[1])) ? 'hat:' : '') + atom(c[0]);
    if (name === 'munder' && c.length >= 2 && /[¯ˉ‾_]/.test(plain(c[1]))) return 'under:' + atom(c[0]);
    if (c.length === 1 && ['mrow','mstyle','mpadded','semantics','math'].includes(name)) return atom(c[0]);
    if (name==='mrow' && c.length>1 && c.every(n=>n.localName==='mi' && n.getAttribute('mathvariant')==='normal')) return clean(plain(node));
    return '';
  }
  function symbols(math, course, section) {
    const list = [];
    const equation=equationOf(math);
    function visit(node, inExponent = false) {
      if (['mi','mtext','msub','msup','msubsup','mover','munder'].includes(node.localName) || node.localName==='mrow' && node.children.length>1 && atom(node)) {
        const key = atom(node);
        const next = node.nextElementSibling;
        if (/^[fgh]$/.test(key) && next?.localName === 'mo' && next.textContent === '(') return;
        const power=['msup','msubsup'].includes(node.localName) ? node.lastElementChild : null;
        const exponential=node.localName==='msup' && atom(node.firstElementChild)==='e' && !upperKey(plain(power)) && /[A-Za-zα-ω]/u.test(plain(power));
        const entry = exponential ? null : resolveSymbol(course, section, key, 'symbol', equation);
        if (entry) list.push({ key, entry, node, inExponent, visible: displayKey(plain(node)) });
        else if (['msub','msubsup'].includes(node.localName) && node.children[1]) {
          const sub = clean(plain(node.children[1]));
          const notation = resolveSymbol(course, section, sub, 'subscript', equation);
          if (notation) list.push({ key: 'subscript:' + sub, entry: notation, node:node.children[1], inExponent, visible: displayKey(sub) });
        }
        if (power && !upperKey(plain(power))) {
          if (!atom(node.firstElementChild) && !exponential) visit(node.firstElementChild);
          visit(power, true);
        }
        return;
      }
      const children=[...node.children].filter((child)=>child.localName!=='annotation');
      for(let i=0;i<children.length;i++) {
        const child=children[i],next=children[i+1];
        if(plain(child)==='Δ' && next && ['mi','mtext','msub','msup','msubsup','mover','munder'].includes(next.localName)) {
          const key='delta:'+atom(next),entry=resolveSymbol(course,section,key,'symbol',equation);
          if(entry)list.push({key,entry,node:next,inExponent,visible:displayKey(plain(next))});
          i++;continue;
        }
        visit(child,inExponent);
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
      element.setAttribute('tabindex', '0'); element.setAttribute('role', 'link'); element.setAttribute('aria-haspopup', 'dialog');
      element.setAttribute('aria-label', '查看符号定义：' + entry.title);
    }
    element.title = '点击查看定义';
  }
  function equationTool(equation, entries) {
    const unique=[...new Map(entries.map(entry=>[entry.id,entry])).values()];
    if (!equation || !unique.length) return;
    const ids=unique.map(entry=>entry.id).join(' ');
    const expression=equation.querySelector('.paper-equation-scroll');
    if (expression) {
      expression.dataset.definitionList=ids;identity(expression);
      expression.classList.add('definition-expression');expression.tabIndex=0;
      expression.setAttribute('role','link');expression.setAttribute('aria-haspopup','dialog');
      expression.setAttribute('aria-label','查看本式符号与解释');
    }
    if (!equation.querySelector('.definition-formula-tool')) {
      const tool=make('button','definition-formula-tool','符号');tool.type='button';tool.dataset.definitionList=ids;identity(tool);
      tool.setAttribute('aria-label','查看本公式的符号定义');tool.setAttribute('aria-haspopup','dialog');equation.append(tool);
    }
  }
  function compositeParent(element, root) {
    for (let parent = element.parentElement; parent && parent !== root; parent = parent.parentElement) {
      if (parent.classList.contains('accent') || parent.classList.contains('overline') || parent.classList.contains('underline') || (parent.classList.contains('mord') && parent.querySelector(':scope > .msupsub'))) return parent;
    }
    return null;
  }

  // MathJax SVG retains its visual glyphs; read explicit MathML node metadata only.
  function svgGlyph(node) {
    return [...node.querySelectorAll('[data-c]')].map(g => String.fromCodePoint(parseInt(g.dataset.c,16))).join('').normalize('NFKC').replace(/ϕ/g,'φ');
  }
  function svgAtom(node) {
    const tag=node.dataset.mmlNode, c=[...node.children];
    if (['mi','mn','mo','mtext'].includes(tag)) return svgGlyph(node);
    if (tag==='msub' && c.length===2) return svgAtom(c[0])+'_'+svgGlyph(c[1]);
    if (tag==='msubsup' && c.length===3) {
      const upper=svgGlyph(c[1]),lower=svgGlyph(c[2]);
      // MathJax SVG orders the visual superscript before the subscript.
      return svgAtom(c[0])+'_'+lower+upperKey(upper);
    }
    if (tag==='msup' && c.length===2) return svgAtom(c[0])+upperKey(svgGlyph(c[1]));
    if (['mover','munder'].includes(tag) && c.length===2) {
      const accent=svgGlyph(c[1]);
      return (/[¯ˉ‾–]/u.test(accent)?'bar:':/[˙̇⋅]/u.test(accent)?'dot:':/[\^ˆ̂]/u.test(accent)?'hat:':'')+svgAtom(c[0]);
    }
    if (c.length===1) return svgAtom(c[0]);
    if (tag==='TeXAtom') return svgGlyph(node);
    return '';
  }
  function prepareSVG(body, course, section) {
    body.querySelectorAll('mjx-container').forEach(container => {
      const found=[];
      function visit(node) {
        const tag=node.dataset?.mmlNode;
        if (['mi','msub','msubsup','msup','mover','munder'].includes(tag)) {
          const key=svgAtom(node),power=['msup','msubsup'].includes(tag)?node.children[1]:null;
          const exponential=tag==='msup' && svgAtom(node.children[0])==='e' && power && !upperKey(svgGlyph(power)) && /[A-Za-zα-ω]/u.test(svgGlyph(power));
          const entry=exponential?null:resolveSymbol(course,section,key,'symbol',equationOf(container));
          // The new PDF has different notation; only its explicitly scoped definitions apply.
          if (entry?.sections?.includes(section.id)) { interactive(node,entry,true);node.dataset.definitionKey=key;found.push(entry); }
          if (tag==='msup' || tag==='msubsup') {
            if(power && !upperKey(svgGlyph(power))) visit(power);
          }
          return;
        }
        [...node.children].forEach(visit);
      }
      visit(container);
      const unique=[...new Map(found.map(entry=>[entry.id,entry])).values()];
      const equation=container.closest('.paper-equation');
      equationTool(equation,unique);
    });
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
          // A temperature difference and an absolute temperature can coexist.
          // Match the visible delta beside this occurrence, not every T in the formula.
          let leading=element;
          while (leading.parentElement!==visual && !leading.previousElementSibling && leading.parentElement) leading=leading.parentElement;
          const afterDelta=clean(leading.previousElementSibling?.textContent || '')==='Δ';
          if (item.key.startsWith('delta:') ? !afterDelta : afterDelta) return false;
          if (!item.key.startsWith('subscript:') && /^[A-Za-z]$/.test(item.visible) && (element.classList.contains('mathrm') || element.querySelector('.mathrm'))) return false;
          const accent = element.classList.contains('accent') || !!element.querySelector('.accent');
          const overline = element.classList.contains('overline') || !!element.querySelector('.overline') || [...element.querySelectorAll('.accent-body')].some(n=>/[¯ˉ‾]/.test(n.textContent));
          const underline = element.classList.contains('underline') || !!element.querySelector('.underline');
          if (item.key.startsWith('under:') ? !underline : underline) return false;
          const dot = accent && [...element.querySelectorAll('.accent-body')].some(n=>/[˙̇⋅]/.test(n.textContent));
          const hat = accent && [...element.querySelectorAll('.accent-body')].some(n=>/[\^ˆ̂]/.test(n.textContent));
          if (item.key.startsWith('bar:') ? !overline : item.key.startsWith('dot:') ? !dot || overline : item.key.startsWith('hat:') ? !hat : dot || overline || hat) return false;
          const baseKey = item.key.replace(/^(?:delta:)?(?:bar:|dot:|under:|hat:)?/, '');
          const script = element.classList.contains('mathcal') || !!element.querySelector('.mathcal');
          if (baseKey.startsWith('cal:') !== script) return false;
          const bold = element.classList.contains('boldsymbol') || element.classList.contains('mathbf') || !!element.querySelector('.boldsymbol,.mathbf');
          if (baseKey.startsWith('bold:') !== bold) return false;
          if (item.key.startsWith('subscript:')) return !!element.closest('.msupsub');
          return !compositeParent(element, visual) || item.inExponent && !!element.closest('.msupsub');
        });
        candidates.forEach((element) => { if (!element.closest('[data-definition]')) interactive(element, item.entry); });
      });
      if (wrapper && unique.length) {
        wrapper.dataset.definitionList = unique.map((e) => e.id).join(' '); identity(wrapper);
        wrapper.classList.add('definition-expression'); wrapper.tabIndex = 0; wrapper.setAttribute('role','link'); wrapper.setAttribute('aria-haspopup','dialog');
        wrapper.setAttribute('aria-label','查看表达式中的符号定义');
      }
      const equation = katex.closest('.paper-equation');
      equationTool(equation,unique);
    });
    // Native MathML is visible content, unlike KaTeX's hidden accessibility tree.
    body.querySelectorAll('math').forEach(math => {
      if (math.closest('.katex, mjx-container')) return;
      const items=symbols(math,course,section);
      items.forEach(item=>interactive(item.node,item.entry,true));
      const equation = math.closest('.paper-equation');
      equationTool(equation,items.map(item=>item.entry));
    });
    prepareSVG(body, course, section);
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
    const topLimit=(document.querySelector('.topbar')?.getBoundingClientRect().bottom || 0)+8;
    const bottomLimit=height-12;
    const below=rect.bottom+8;
    const top=below+box.height<=bottomLimit?Math.max(topLimit,below):Math.max(topLimit,Math.min(rect.top-box.height-8,bottomLimit-box.height));
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
    if(trigger===event.target&&trigger.tagName!=='BUTTON'&&['Enter',' '].includes(event.key)){event.preventDefault();activate(trigger);}
  });
  addEventListener('resize',position);
  addEventListener('scroll',(event)=>{
    if(!opened()||popup.contains(event.target))return;
    const rect=origin?.getBoundingClientRect(),top=document.querySelector('.topbar')?.getBoundingClientRect().bottom || 0;
    if(!rect||rect.bottom<top||rect.top>innerHeight-12)close();else position();
  },true);
  window.LNGlossary={prepare,onRoute:()=>{close();origin=null;context=null;},resolveSymbol,termAliases};
})();
