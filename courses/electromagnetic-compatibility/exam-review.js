'use strict';
(() => {
  const courseId = 'electromagnetic-compatibility';
  const prefix = '#course/' + courseId + '/';
  const chapters = window.LN_EMC_EXAM_REVIEW.chapters;
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const formulas = row => row.formulas.map(f => '<div class="emc-review-formula" data-review-tex="' + esc(f.tex) + '">' + esc(f.plain) + '</div>').join('');
  const rowHTML = (r, inline = false) => '<section class="emc-review-row"'+(inline?'':' id="exam-'+esc(r.id)+'"')+'><h3>'+esc(r.id.replace('emc-','').replace('-','.'))+' '+esc(r.title)+'</h3>'+ formulas(r) + '<p><strong>方法与条件：</strong>'+esc(r.method)+'</p><p><strong>易错：</strong>'+esc(r.trap)+'</p>'+ (inline?'':'<a href="'+prefix+esc(r.id)+'">回查本节正文</a>')+'</section>';
  const enhance = async (root, loadMath) => {
    try {
      await loadMath();
      if (!root.isConnected || !window.katex) return;
      for (const el of root.querySelectorAll('[data-review-tex]')) {
        const fallback = el.textContent;
        try { window.katex.render(el.dataset.reviewTex, el, {displayMode:true,throwOnError:true,trust:false,strict:'ignore',output:'htmlAndMathml'}); }
        catch (_) { el.textContent = fallback; el.dataset.mathFallback='true'; }
      }
    } catch (_) { /* Keep readable plain formula if local runtime is unavailable. */ }
  };
  function render(root, anchor, loadMath) {
    const n = Number((anchor || '').match(/^(?:emc-|chapter-)(\d+)/)?.[1] || 1);
    const chapter = chapters.find(c=>c.n===n) || chapters[0];
    root.innerHTML='<p class="emc-review-note">按十章课件组织的复习提纲；用于掌握公式、方法与适用条件，不是公布的考试范围。每章有原创计算自测。</p><div class="emc-review-controls"><label>章节 <select id="emc-review-chapter">'+chapters.map(c=>'<option value="'+c.n+'"'+(c===chapter?' selected':'')+'>第'+c.n+'章 '+esc(c.title)+'</option>').join('')+'</select></label><label>全课程公式与考点搜索 <input id="emc-review-search" type="search" placeholder="如：插入损耗、共模、谐波"></label></div><div id="emc-review-content"></div>';
    const content=root.querySelector('#emc-review-content');
    const draw=()=>{ const q=root.querySelector('#emc-review-search').value.trim().toLowerCase();
      if(q) {const found=chapters.flatMap(c=>c.rows).filter(r=>JSON.stringify(r).toLowerCase().includes(q));content.innerHTML='<h2>搜索结果 · '+found.length+' 节</h2>'+found.map(r=>rowHTML(r)).join('');}
      else {content.innerHTML='<h2>第'+chapter.n+'章 '+esc(chapter.title)+'</h2><p class="emc-review-focus">'+esc(chapter.focus)+'</p>'+chapter.rows.map(r=>rowHTML(r)).join('')+'<section class="emc-review-example"><h3>章末自测 · 原创计算题</h3><p>'+esc(chapter.question)+'</p><details><summary>查看计算与答案</summary><p>'+esc(chapter.answer)+'</p></details></section>';}
      void enhance(content,loadMath);
    };
    root.querySelector('#emc-review-chapter').addEventListener('change',e=>{ location.hash=prefix+'exam-review/chapter-'+e.target.value; });
    root.querySelector('#emc-review-search').addEventListener('input',draw);
    draw();
    if(anchor?.startsWith('emc-')) requestAnimationFrame(()=>root.querySelector('#exam-'+CSS.escape(anchor))?.scrollIntoView({block:'start'}));
  }
  function mountLesson(body, course, selected, loadMath) {
    if(course.id!==courseId) return;
    const row=chapters.flatMap(c=>c.rows).find(r=>r.id===selected.id);
    if(!row) return;
    const block=document.createElement('aside');block.className='emc-review-inline';
    block.innerHTML=(row.extra?'<h2>课件公式补充与考试方法</h2>'+rowHTML(row,true):'')+'<p><a href="'+prefix+'exam-review/'+esc(row.id)+'">本节公式、考试重点与章末自测 →</a></p>';
    body.append(block);
    if(row.extra) void enhance(block,loadMath);
  }
  window.LNEmcExam={render,mountLesson};
})();
