'use strict';
(() => {
  const bank=window.LN_PRACTICE_BANK,questions=bank.questions,courses=window.LN_COURSES.filter(c=>!c.outlineOnly);
  const kinds={single:'单选',multi:'多选',numeric:'计算',open:'问答'};
  const skills=['建模','因果与证据','推导计算','边界与反例','迁移设计','解释表达'];
  const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const key='ln.practice.v1';let records={},persistent=true;
  try {const saved=JSON.parse(localStorage.getItem(key)||'{}');if(saved&&typeof saved==='object'&&!Array.isArray(saved))records=saved;}catch{persistent=false;}
  function save(){try{localStorage.setItem(key,JSON.stringify(records));persistent=true;}catch{persistent=false;}}
  function record(q){
    let r=records[q.id];
    const optionIds=(q.options||[]).map(o=>o.id);
    if(!r||r.version!==bank.version||!Array.isArray(r.order)||r.order.length!==optionIds.length||new Set(r.order).size!==optionIds.length||r.order.some(id=>!optionIds.includes(id))||!Array.isArray(r.selected)||typeof r.value!=='string'||typeof r.reason!=='string'||!Array.isArray(r.checks)||!Array.isArray(r.attempts)){
      const order=(q.options||[]).map(o=>o.id);
      for(let i=order.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[order[i],order[j]]=[order[j],order[i]];}
      r=records[q.id]={version:bank.version,order,selected:[],value:'',reason:'',confidence:'unsure',checks:[],attempts:[],hinted:false,revealed:false};
    }
    return r;
  }
  function evaluate(q,r){
    if(q.type==='open')return null;
    if(q.type==='numeric'){
      const raw=r.value.trim().replace(/−/g,'-');
      if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(raw))return undefined;
      const value=Number(raw);return Number.isFinite(value)?Math.abs(value-q.answer)<=q.tolerance:undefined;
    }
    if(!r.selected.length)return undefined;
    return r.selected.length===q.answer.length&&q.answer.every(x=>r.selected.includes(x));
  }
  function needsReview(q,r){return Boolean(r&&(r.hinted||r.revealed||r.attempts?.some(a=>a.correct===false)||(q.type==='open'&&r.submitted&&r.checks.length<q.rubric.length)));}
  function isMistake(r){return Boolean(r&&(r.selfMistake||r.attempts?.some(a=>a.correct===false)));}
  function button(course,section,label='练习'){
    if(course.outlineOnly||section?.kind==='outline')return '';
    return '<button type="button" class="resource-nav-button" data-open-practice data-practice-course="'+escape(course.id)+'"'+(section?' data-practice-section="'+escape(section.id)+'"':'')+' aria-haspopup="dialog" aria-controls="practice-dialog">'+escape(label)+'</button>';
  }

  // Shared learning workspace: every course reuses the same editor, navigation and feedback.
  function shell(course,section){
    return '<section class="practice-panel practice-workspace" data-practice-panel>'+
      '<header class="practice-session-head"><div class="practice-eyebrow">逐题练习 · 作答后讲解</div><div class="practice-session-title"><h2 data-p-course-title>'+escape(courses.find(c=>c.id===course)?.title||'学习练习')+'</h2><span class="practice-progress-value" data-p-progress aria-live="polite"></span></div>'+
      '<div class="practice-progress-track" aria-hidden="true"><span data-p-progress-bar></span></div><p class="practice-note" data-p-scope></p></header>'+
      '<div class="practice-workspace-tools"><label class="practice-picker">前往题目<select data-p-question aria-label="按名称选择题目"></select></label>'+
      '<details class="practice-filter-box" data-p-filter-box><summary>筛选与复习范围</summary><div class="practice-controls">'+
      '<label>课程<select data-p-course>'+courses.map(c=>'<option value="'+escape(c.id)+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('')+'</select></label>'+
      '<label>题型<select data-p-type><option value="">全部题型</option>'+Object.entries(kinds).map(([id,t])=>'<option value="'+id+'">'+t+'</option>').join('')+'</select></label>'+
      '<label>考察能力<select data-p-skill><option value="">全部能力</option>'+skills.map(s=>'<option>'+s+'</option>').join('')+'</select></label>'+
      '<label class="resource-checkbox"><input type="checkbox" data-p-review>只看待复习题</label></div></details></div>'+
      '<details class="practice-number-map" data-p-map><summary>题号导航 <span data-p-map-summary></span></summary><div data-p-grid class="practice-number-grid" aria-label="按题号跳转"></div></details>'+
      '<div class="practice-question-stage" data-p-body></div>'+
      '<div class="practice-session-foot"><p data-p-storage role="status"></p><details class="practice-evidence"><summary>作答记录与能力维度</summary><div data-p-summary></div><p>独立首答、提示后和重复作答分开记录。数值正确不代表推导正确；开放题只记录自评。</p></details></div></section>';
  }
  const answerLabel=(q,r,answer)=>r.order.filter(id=>answer.includes(id)).map(id=>String.fromCharCode(65+r.order.indexOf(id))).join('、')||'未作答';
  const formattedNumber=(n,tolerance)=>{
    const digits=Math.min(8,Math.max(2,Math.ceil(-Math.log10(Math.max(tolerance,1e-9)))+1));
    return Number(n.toFixed(digits)).toLocaleString('zh-CN',{maximumFractionDigits:digits});
  };
  function feedback(q,r){
    if(!r.submitted&&!r.revealed)return '';
    const submitted=Boolean(r.submitted),correct=r.lastCorrect;
    const partial=q.type==='multi'&&!correct&&r.selected.some(id=>q.answer.includes(id));
    const status=!submitted?'已查看参考解析':q.type==='open'?'请逐项自评论证':correct?(q.type==='numeric'?'数值吻合，过程仍需核对':'选择吻合，请继续核对理由'):partial?'部分选项吻合，仍有漏选或错选':'答案尚不吻合，检查下面的推理';
    const tone=!submitted||q.type==='open'?'review':correct?'correct':partial?'partial':'wrong';
    const answerSummary=q.options?
      '<p class="practice-answer-line"><strong>你的选择：</strong>'+escape(answerLabel(q,r,r.selected))+' <span aria-hidden="true">·</span> <strong>正确答案：</strong>'+escape(answerLabel(q,r,q.answer))+'</p>':
      q.type==='numeric'?
      '<div class="practice-numeric-compare"><div><small>你的数值</small><strong>'+escape(r.value||'未填写')+' '+escape(q.unit)+'</strong></div>'+
      '<div><small>参考答案</small><strong>'+formattedNumber(q.answer,q.tolerance)+' '+escape(q.unit)+'</strong></div></div>'+
      '<p class="practice-answer-line">容许绝对误差：±'+escape(q.tolerance)+' '+escape(q.unit)+'。只判断数值；单位、过程与条件仍需自行核查。</p>':
      '<p class="practice-answer-line">以下是参考推理与评分要点，不是对文字答案的自动判定。</p>';
    const other=q.options?r.order.filter(id=>!r.selected.includes(id)&&!q.answer.includes(id)).map(id=>{
      const o=q.options.find(x=>x.id===id);
      return '<li><strong>'+escape(o.text)+'</strong><p>'+escape(o.feedback)+'</p></li>';
    }).join(''):'';
    return '<section class="practice-feedback" aria-label="批改与解析" data-p-verdict="'+tone+'">'+
      '<header class="practice-verdict"><span class="practice-verdict-mark" aria-hidden="true">'+(tone==='correct'?'✓':tone==='wrong'?'×':tone==='partial'?'!':'i')+'</span><div><h3 role="status" tabindex="-1">'+status+'</h3><p>完整解析就在下方，原选项已直接标注。</p></div></header>'+
      answerSummary+
      (r.hinted||r.revealed?'<p class="practice-assistance-note">已使用提示或查看过答案，后续答对不会算作独立首答。</p>':'')+
      (other?'<details class="practice-other-options"><summary>其余选项为什么不选</summary><ul>'+other+'</ul></details>':'')+
      '<div class="practice-solution"><h4>完整推理与核查</h4><ol>'+q.steps.map((s,i)=>'<li>'+(q.stepsHtml?.[i]||escape(s))+'</li>').join('')+'</ol></div>'+
      (q.rubric?'<fieldset class="practice-rubric"><legend>对照自己的过程逐项自评</legend>'+q.rubric.map((s,i)=>'<label><input type="checkbox" data-p-rubric value="'+i+'"'+(r.checks.includes(i)?' checked':'')+'>'+(q.rubricHtml?.[i]||escape(s))+'</label>').join('')+'</fieldset>':'')+
      '<div class="practice-transfer"><h4>换个条件再想</h4><div>'+(q.transferHtml||escape(q.transfer))+'</div></div>'+
      '<button type="button" class="practice-subtle-button" data-p-redo>遮住解析，重新作答（保留首答）</button></section>';
  }
  function questionHtml(q){
    const r=record(q),choice=q.type==='single'||q.type==='multi',graded=r.submitted||r.revealed;
    const options=choice?'<fieldset class="practice-options"><legend>'+(q.type==='multi'?'多选 · 选择所有有依据的判断':'单选 · 选择最有依据的一项')+'</legend>'+
      r.order.map((id,index)=>{
        const o=q.options.find(x=>x.id===id),checked=r.selected.includes(id),expected=q.answer.includes(id);
        const mark=!graded?'':checked&&expected?'correct':checked&&!expected?'wrong':!checked&&expected?'missed':'neutral';
        const inline=graded&&(checked||expected)?'<span class="practice-choice-detail"><b>'+(
          checked&&expected?'已选 · 正确':checked&&!expected?'已选 · 错误':'漏选 · 应选')+'</b>'+escape(o.feedback)+'</span>':'';
        return '<label class="practice-choice" data-p-option-state="'+mark+'"><input type="'+(q.type==='multi'?'checkbox':'radio')+'" name="p-answer" value="'+escape(id)+'"'+(checked?' checked':'')+'>'+
          '<span class="practice-choice-letter" aria-hidden="true">'+String.fromCharCode(65+index)+'</span><span class="practice-choice-main"><span>'+escape(o.text)+'</span>'+inline+'</span></label>';
      }).join('')+'</fieldset>':
      q.type==='numeric'?'<label class="practice-value">计算结果 <span>('+escape(q.unit)+')</span><input type="text" inputmode="decimal" data-p-value value="'+escape(r.value)+'" autocomplete="off" placeholder="填写数值，允许科学计数法"></label>':'';
    const reason='<label class="practice-reason">'+(q.type==='open'?'写下推理过程（必填）':'推导、判断依据或草稿（选填）')+
      '<textarea data-p-reason rows="'+(q.type==='open'?7:4)+'" placeholder="写下自己的分析；本地自动保存">'+escape(r.reason)+'</textarea></label>';
    const reasoning=q.type==='open'?reason:'<details class="practice-thinking"'+((r.reason||q.type==='numeric')?' open':'')+'><summary>写下自己的推导或理由（可选）</summary>'+reason+'</details>';
    return '<article class="practice-question" data-question-id="'+escape(q.id)+'">'+
      '<div class="practice-question-meta"><span>'+kinds[q.type]+'</span><span>'+q.skills.map(escape).join(' · ')+'</span></div>'+
      '<h2 tabindex="-1" data-p-title>'+escape(q.title)+'</h2>'+
      '<div class="practice-prompt">'+(q.promptHtml||escape(q.prompt))+'</div>'+options+reasoning+
      '<div class="practice-question-tools"><label class="practice-confidence">把握度 <select data-p-confidence><option value="unsure"'+(r.confidence==='unsure'?' selected':'')+'>不确定</option><option value="sure"'+(r.confidence==='sure'?' selected':'')+'>有把握</option></select></label>'+
      '<button type="button" class="practice-subtle-button" data-p-favorite aria-pressed="'+Boolean(r.favorite)+'">'+(r.favorite?'★ 已收藏':'☆ 收藏')+'</button>'+
      '<button type="button" class="practice-subtle-button" data-p-mistake aria-pressed="'+Boolean(r.selfMistake)+'">'+(r.selfMistake?'✓ 已标记':'标记不会')+'</button></div>'+
      '<div class="practice-assist"><button type="button" class="practice-subtle-button" data-p-hint>提示一步</button>'+
      '<button type="button" class="practice-subtle-button" data-p-reveal>查看参考答案</button>'+
      '<p data-p-hint-text'+(r.hinted?'':' hidden')+'>'+(q.hintHtml||escape(q.hint))+'</p></div>'+
      '<p data-p-error role="alert"></p><div data-p-feedback>'+feedback(q,r)+'</div>'+
      '<nav class="practice-reading" aria-label="回查讲解">'+q.sections.map(id=>{const c=courses.find(c=>c.id===q.course),s=c.sections.find(s=>s.id===id);return '<a href="#course/'+c.id+'/'+id+
      (q.readingAnchor&&id===(q.readingSection||'transformer-homework')?'/'+encodeURIComponent(q.readingAnchor):'')+'">回查 · '+escape(s.title)+'</a>';}).join('')+'</nav>'+
      '<details class="practice-origin"><summary>题目来源与使用范围</summary>'+escape(q.origin)+'</details>'+
      '<div class="practice-pagination"><button type="button" class="practice-page-button" data-p-prev>上一题</button>'+
      '<button type="button" class="practice-primary-button" data-p-submit>'+(q.type==='open'?'保存并对照要点':r.submitted?'重新提交':'提交答案')+'</button>'+
      '<button type="button" class="practice-page-button" data-p-next>下一题</button></div></article>';
  }
  function mount(root,initialCourse,initialSection,collection=''){
    if(questions.some(q=>q.promptHtml)&&!document.querySelector('link[href="assets/katex/katex.min.css"]')){
      const link=document.createElement('link');link.rel='stylesheet';link.href='assets/katex/katex.min.css';document.head.append(link);
    }
    let selected='',matches=[],section=initialSection;
    const panel=root.querySelector('[data-practice-panel]'),body=panel.querySelector('[data-p-body]'),picker=panel.querySelector('[data-p-question]');
    const storage=()=>{panel.querySelector('[data-p-storage]').textContent=persistent?'记录仅保存在此浏览器 · 草稿自动保存':'当前浏览器存储不可用，作答可能无法跨页面保留';};
    function summary(){
      const course=panel.querySelector('[data-p-course]').value,items=questions.filter(q=>q.course===course);
      panel.querySelector('[data-p-summary]').innerHTML='<ul>'+skills.map(skill=>{
        const all=items.filter(q=>q.skills.includes(skill)),attempted=all.filter(q=>record(q).attempts.length),first=attempted.filter(q=>record(q).attempts[0]?.correct===true&&!record(q).attempts[0].assisted),review=all.filter(q=>needsReview(q,record(q)));
        return '<li>'+skill+'：'+all.length+'题；已提交'+attempted.length+'；独立首答吻合'+first.length+'；待回看'+review.length+'</li>';
      }).join('')+'</ul>';
    }
    const label=q=>{const r=record(q);return kinds[q.type]+' · '+q.title+(needsReview(q,r)?' · 待回看':'')+(r.attempts.some(a=>a.confidence==='sure'&&a.correct===false)?' · 自信误判':'');};
    function render(focus=false){
      const q=matches.find(q=>q.id===selected),index=matches.indexOf(q),done=matches.filter(t=>record(t).attempts.length).length;
      picker.innerHTML=matches.map(t=>'<option value="'+escape(t.id)+'"'+(t.id===selected?' selected':'')+'>'+escape(label(t))+'</option>').join('');
      picker.disabled=!matches.length;
      panel.querySelector('[data-p-course-title]').textContent=courses.find(c=>c.id===panel.querySelector('[data-p-course]').value)?.title||'课程练习';
      panel.querySelector('[data-p-progress]').textContent=q?(index+1)+' / '+matches.length:'0 / 0';
      panel.querySelector('[data-p-progress-bar]').style.width=matches.length?(done/matches.length*100)+'%':'0%';
      panel.querySelector('[data-p-map-summary]').textContent='· 已作答 '+done+' / '+matches.length;
      panel.querySelector('[data-p-grid]').innerHTML=matches.map((t,i)=>{
        const r=record(t),status=needsReview(t,r)?'review':r.attempts.length?'done':'new';
        return '<button type="button" data-p-jump="'+escape(t.id)+'" class="practice-number" data-p-number-state="'+status+'"'+(t.id===selected?' aria-current="step"':'')+' aria-label="第'+(i+1)+'题：'+escape(t.title)+'">'+(i+1)+'</button>';
      }).join('');
      body.innerHTML=q?questionHtml(q):'<p class="practice-empty">这个范围暂无题目。你可以调整筛选或查看其他课程。</p>';
      if(q){
        body.querySelector('[data-p-prev]').disabled=index===0;
        body.querySelector('[data-p-next]').disabled=index===matches.length-1;
        if(focus)body.querySelector('[data-p-title]').focus({preventScroll:true});
      }
      summary();save();storage();
    }
    function filter(){
      const course=panel.querySelector('[data-p-course]').value,type=panel.querySelector('[data-p-type]').value,skill=panel.querySelector('[data-p-skill]').value,review=panel.querySelector('[data-p-review]').checked;
      let base=questions.filter(q=>q.course===course&&(!collection||(collection==='mistakes'?isMistake(record(q)):record(q).favorite))),exact=section?base.filter(q=>q.sections.includes(section)):[];
      const fallback=Boolean(section&&!exact.length);
      if(exact.length)base=exact;
      panel.querySelector('[data-p-scope]').textContent=(section?(fallback?'本节尚无专门题目，显示课程练习':'本节关联练习'):'本课程练习')+' · '+base.length+'题；筛选和题号导航都可随时打开。';
      matches=base.filter(q=>(!type||q.type===type)&&(!skill||q.skills.includes(skill))&&(!review||needsReview(q,record(q))));
      if(!matches.some(q=>q.id===selected))selected=matches[0]?.id||'';
      render();
    }
    panel.addEventListener('change',event=>{
      if(event.target.matches('[data-p-course]')){section=null;filter();return;}
      if(event.target.matches('[data-p-type],[data-p-skill],[data-p-review]')){filter();return;}
      if(event.target===picker){selected=picker.value;render(true);return;}
      draft(event);
    });
    function draft(event){
      const q=matches.find(q=>q.id===selected);if(!q)return;
      const r=record(q),t=event.target;
      if(t.matches('[name="p-answer"]'))r.selected=Array.from(body.querySelectorAll('[name="p-answer"]:checked'),e=>e.value);
      else if(t.matches('[data-p-value]'))r.value=t.value;
      else if(t.matches('[data-p-reason]'))r.reason=t.value;
      else if(t.matches('[data-p-confidence]'))r.confidence=t.value;
      else if(t.matches('[data-p-rubric]'))r.checks=Array.from(body.querySelectorAll('[data-p-rubric]:checked'),e=>Number(e.value));
      else return;
      if(!t.matches('[data-p-rubric]')&&t.matches('[name="p-answer"],[data-p-value]')){
        r.submitted=false;r.checks=[];
        // Keep the option appearance in sync without replacing the active input or caret.
        body.querySelectorAll('[data-p-option-state]').forEach(label=>{label.dataset.pOptionState='';label.querySelector('.practice-choice-detail')?.remove();});
        body.querySelector('[data-p-feedback]').innerHTML='';
      }
      if(t.matches('[data-p-rubric]')){ /* the answer remains in review mode */ }
      body.querySelector('[data-p-error]').textContent='';
      summary();save();storage();
    }
    panel.addEventListener('input',draft);
    panel.addEventListener('click',event=>{
      const jump=event.target.closest('[data-p-jump]');
      if(jump){selected=jump.dataset.pJump;render(true);return;}
      const q=matches.find(q=>q.id===selected);if(!q)return;
      const r=record(q),target=event.target;
      if(target.closest('[data-p-submit]')){
        const value=evaluate(q,r),error=body.querySelector('[data-p-error]');
        if(q.type==='open'&&!r.reason.trim()){error.textContent='请先写下你的分析，再对照参考要点。';return;}
        if(value===undefined){error.textContent=q.type==='numeric'?'请填写有限的纯数值；单位见输入框标签。':'请先选择答案。';return;}
        r.submitted=true;r.lastCorrect=value;
        r.attempts.push({correct:value,assisted:r.hinted||r.revealed||Boolean(r.feedbackSeen),confidence:r.confidence});
        r.feedbackSeen=true;if(r.attempts.length>100)r.attempts=[r.attempts[0],...r.attempts.slice(-99)];
        render();
        body.querySelector('.practice-verdict h3')?.focus({preventScroll:true});
      }else if(target.closest('[data-p-hint]')){
        r.hinted=true;body.querySelector('[data-p-hint-text]').hidden=false;save();summary();
      }else if(target.closest('[data-p-reveal]')){
        r.revealed=true;render();body.querySelector('.practice-verdict h3')?.focus({preventScroll:true});
      }else if(target.closest('[data-p-redo]')){
        r.submitted=false;r.revealed=false;r.selected=[];r.value='';r.reason='';r.checks=[];render();
      }else if(target.closest('[data-p-favorite]')){
        r.favorite=!r.favorite;if(collection)filter();else render();
      }else if(target.closest('[data-p-mistake]')){
        r.selfMistake=!r.selfMistake;render();
      }else if(target.closest('[data-p-next],[data-p-prev]')){
        const i=matches.indexOf(q)+(target.closest('[data-p-next]')?1:-1);
        if(matches[i]){selected=matches[i].id;render(true);body.querySelector('[data-p-title]')?.scrollIntoView({block:'start'});}
      }
    });
    filter();
  }
  const extItems=()=>{if(!Array.isArray(records.externalItems))records.externalItems=[];records.externalItems=records.externalItems.filter(i=>i&&typeof i.key==='string'&&typeof i.sourceId==='string'&&typeof i.ref==='string');return records.externalItems;};
  const courseOptions=course=>courses.map(c=>'<option value="'+c.id+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('');
  const sourceLinks=s=>s.links.map(l=>'<a href="'+escape(l.url)+'" target="_blank" rel="noopener noreferrer">'+escape(l.label)+'</a>').join(' · ');
  const knowledgeLinks=s=>s.targets.map(t=>{const c=courses.find(c=>c.id===t.course),section=c.sections.find(x=>x.id===t.section);return '<a href="#course/'+c.id+'/'+section.id+'">'+escape(c.title+' · '+section.title)+'</a>';}).join(' · ');
  function sourceHtml(s,open=false){
    return '<details class="source-practice resource-entry" data-source-id="'+s.id+'"'+(open?' open':'')+'><summary><strong>'+escape(s.title)+'</strong><span class="resource-verification">'+escape(s.evidenceLevel)+'</span><span class="resource-question">'+escape(s.focus)+'</span></summary><div class="resource-entry-body"><p>'+escape(s.selection)+'</p><p>'+sourceLinks(s)+'</p><h3>为什么选它</h3><p>'+escape(s.evidence)+'</p><h3>怎样作答与核查</h3><ol>'+s.guide.map(t=>'<li>'+escape(t)+'</li>').join('')+'</ol><p><strong>解答：</strong>'+escape(s.answers)+'</p><p><strong>适用范围：</strong>'+escape(s.limit)+'</p><p>'+knowledgeLinks(s)+'</p><details><summary>访问与许可</summary><p>'+escape(s.access)+' '+escape(s.license)+'</p></details><div class="source-record"><h3>记录这一道题</h3><p>外部原站不向本站回传结果，请填具体题号或页面定位；一道题一条记录。</p><label>题号 / 定位<input data-source-ref placeholder="如：第 2 题或页面题目名"></label><label>自己的分析与错因<textarea data-source-note rows="3"></textarea></label><button class="secondary-button" data-source-save="mistake">收录错题</button> <button class="secondary-button" data-source-save="favorite">收藏再做</button><p data-source-status role="status"></p></div></div></details>';
  }
  function externalCollection(course,mode){
    const items=extItems().filter(item=>item[mode==='mistakes'?'mistake':'favorite']&&bank.sources.some(s=>s.id===item.sourceId&&s.targets.some(t=>t.course===course)));
    return '<h3>原站题目 · '+items.length+' 道</h3>'+items.map(item=>{const s=bank.sources.find(s=>s.id===item.sourceId);return '<section class="external-review" data-external-record="'+escape(item.key)+'"><h4>'+escape(s.title+' · '+item.ref)+'</h4><p>'+escape(item.note||'尚未记录分析')+'</p><p>'+sourceLinks(s)+'</p><p>'+knowledgeLinks(s)+'</p><p>状态：'+(item.reviewed?'已手动标记复习，原错题记录保留':'待复习')+'</p><button class="resource-nav-button" data-external-review>标记已复习</button><button class="resource-nav-button" data-external-favorite>'+ (item.favorite?'取消收藏':'收藏此题')+'</button></section>';}).join('');
  }

  const examRecordName='ln.practice.exam.v1';
  let examStore={};
  try{const saved=JSON.parse(localStorage.getItem(examRecordName)||'{}');if(saved&&typeof saved==='object'&&!Array.isArray(saved))examStore=saved;}catch{}
  function persistExams(){try{localStorage.setItem(examRecordName,JSON.stringify(examStore));}catch{}}
  function examScope(course,section){
    const items=questions.filter(q=>q.course===course);
    if(section){
      const exact=items.filter(q=>q.sections.includes(section));
      if(exact.length)return exact;
    }
    return items;
  }
  function mountExam(root,course,section){
    const content=root.querySelector('[data-exam-content]'),key=course+'::'+(section||'all'),eligible=examScope(course,section);
    let session=examStore[key]||null,confirming=false;
    if(session&&(!Array.isArray(session.ids)||session.ids.some(id=>!eligible.some(q=>q.id===id))||!Array.isArray(session.flagged)))session=null;
    const current=()=>session?questions.find(q=>q.id===session.ids[session.index]):null;
    const resultFor=q=>{
      const answer=session.answers[q.id]||{selected:[],value:'',reason:''};
      if(q.type==='open')return answer.reason.trim()?null:undefined;
      return evaluate(q,answer);
    };
    function getDraft(q){
      if(!session.answers[q.id])session.answers[q.id]={selected:[],value:'',reason:'',confidence:'unsure'};
      return session.answers[q.id];
    }
    function recorded(q){
      const a=getDraft(q);
      return Boolean((q.type==='single'||q.type==='multi')?a.selected.length:q.type==='numeric'?a.value.trim():a.reason.trim());
    }
    function startExam(n){
      const ids=eligible.slice(0,n).map(q=>q.id);
      session={version:1,ids,answers:{},flagged:[],index:0,finished:false,reviewId:null,createdAt:new Date().toISOString()};
      examStore[key]=session;confirming=false;persistExams();render();
    }
    const optionIndex=(q,id)=>String.fromCharCode(65+record(q).order.indexOf(id));
    const examInput=(q,a)=>{
      if(q.options)return '<fieldset class="practice-options"><legend>'+(q.type==='multi'?'多选 · 选择所有有依据的判断':'单选 · 选择最有依据的一项')+'</legend>'+
        record(q).order.map(id=>{const o=q.options.find(v=>v.id===id);
          return '<label class="practice-choice"><input type="'+(q.type==='multi'?'checkbox':'radio')+'" name="e-answer" value="'+escape(id)+'"'+(a.selected.includes(id)?' checked':'')+'>'+
          '<span class="practice-choice-letter">'+optionIndex(q,id)+'</span><span class="practice-choice-main">'+escape(o.text)+'</span></label>';
        }).join('')+'</fieldset>';
      if(q.type==='numeric')return '<label class="practice-value">计算结果（'+escape(q.unit)+'）<input type="text" inputmode="decimal" data-e-value autocomplete="off" value="'+escape(a.value)+'" placeholder="只填数值"></label>'+
        '<details class="practice-thinking"'+(a.reason?' open':'')+'><summary>记录计算过程（可选）</summary><textarea data-e-reason rows="5">'+escape(a.reason)+'</textarea></details>';
      return '<label class="practice-reason">写下推导和理由<textarea data-e-reason rows="8" placeholder="考试阶段不会展示参考答案">'+escape(a.reason)+'</textarea></label>';
    };
    function report(){
      const selected=session.ids.map(id=>questions.find(q=>q.id===id)),objective=selected.filter(q=>q.type!=='open');
      const answered=selected.filter(recorded).length,correct=objective.filter(q=>resultFor(q)===true).length;
      const pending=selected.filter(q=>q.type==='open'&&recorded(q)).length;
      const skipped=selected.filter(q=>!recorded(q)).length;
      return '<section class="practice-exam-report"><p class="practice-eyebrow">已交卷 · 已保存到本浏览器</p><h2>章节测试结果</h2>'+
        '<div class="practice-exam-metrics"><div><small>已作答</small><strong>'+answered+' / '+selected.length+'</strong></div>'+
        '<div><small>客观题吻合</small><strong>'+correct+' / '+objective.length+'</strong></div>'+
        '<div><small>问答待自评</small><strong>'+pending+'</strong></div><div><small>未作答</small><strong>'+skipped+'</strong></div></div>'+
        '<p class="practice-note">只对客观题核对答案。计算过程和开放推导需要根据解析与量规人工复核；“吻合”不等于知识掌握率。</p>'+
        '<h3>逐题核对</h3><div class="practice-exam-results">'+selected.map((q,i)=>{
          const result=resultFor(q),status=!recorded(q)?'未答':q.type==='open'?'待自评':result?'吻合':'未吻合';
          return '<button type="button" data-e-review="'+escape(q.id)+'"><span>'+String(i+1).padStart(2,'0')+' · '+escape(q.title)+'</span><small>'+status+'</small></button>';
        }).join('')+'</div><div class="practice-exam-start-actions"><button type="button" class="practice-page-button" data-e-reset>开始新一轮测试</button></div></section>';
    }
    function review(q){
      const answer=getDraft(q),r=record(q);
      const snapshot={...r,selected:answer.selected,value:answer.value,reason:answer.reason,
        checks:[],submitted:recorded(q),revealed:!recorded(q),lastCorrect:resultFor(q)};
      const originalSelected=r.selected,originalValue=r.value,originalReason=r.reason,originalSubmitted=r.submitted,originalRevealed=r.revealed,originalLast=r.lastCorrect;
      // Reuse exactly the shared answer-and-error rendering, without changing the stored attempts.
      r.selected=answer.selected;r.value=answer.value;r.reason=answer.reason;
      r.submitted=recorded(q);r.revealed=!recorded(q);r.lastCorrect=snapshot.lastCorrect;
      const markup=questionHtml(q);
      r.selected=originalSelected;r.value=originalValue;r.reason=originalReason;
      r.submitted=originalSubmitted;r.revealed=originalRevealed;r.lastCorrect=originalLast;
      return '<section class="practice-exam-review"><button type="button" class="practice-page-button" data-e-back>返回测试报告</button>'+
        '<p class="practice-eyebrow">第'+(session.ids.indexOf(q.id)+1)+'题 · 对照解析</p>'+markup+'</section>';
    }
    function render(){
      if(!eligible.length){content.innerHTML='<p class="practice-empty">本课程暂无可用于章节测试的本地题。可切换“精选来源”查看原题资源。</p>';return;}
      if(!session){
        content.innerHTML='<section class="practice-exam-welcome"><p class="practice-eyebrow">章节测试 · 交卷后统一批改</p><h2>'+escape(courses.find(c=>c.id===course)?.title||'课程')+' · 自测</h2>'+
          '<p>题目作答期间不显示标准答案，允许自由跳题、标记待检查。交卷后按原题位置逐项批改，开放题仍需人工自评。</p>'+
          '<div class="practice-exam-start-actions"><button type="button" class="practice-primary-button" data-e-start="10">10题 · 快速自测</button>'+
          '<button type="button" class="practice-page-button" data-e-start="20">20题 · 综合练习</button>'+
          '<button type="button" class="practice-page-button" data-e-start="'+eligible.length+'">全部'+eligible.length+'题</button></div>'+
          '<p class="practice-note">题目按当前课程范围顺序选取；可随时保存并离开，继续同一次未交卷测试。新一轮测试不覆盖旧首答或错题记录。</p></section>';return;
      }
      if(session.finished){
        if(session.reviewId){content.innerHTML=review(questions.find(q=>q.id===session.reviewId));content.querySelectorAll('input,textarea,select').forEach(el=>el.disabled=true);}
        else content.innerHTML=report();
        return;
      }
      const q=current(),a=getDraft(q),i=session.index,completed=session.ids.filter(id=>recorded(questions.find(q=>q.id===id))).length;
      content.innerHTML='<section class="practice-exam-working"><header class="practice-session-head"><div class="practice-eyebrow">章节测试 · 交卷前不显示答案</div>'+
        '<div class="practice-session-title"><h2>正在作答</h2><span class="practice-progress-value">'+(i+1)+' / '+session.ids.length+'</span></div>'+
        '<div class="practice-progress-track" aria-hidden="true"><span style="width:'+(completed/session.ids.length*100)+'%"></span></div>'+
        '<p class="practice-note">已答'+completed+'题 · 标记'+session.flagged.length+'题 · 当前进度自动保存在本浏览器</p></header>'+
        '<details class="practice-number-map"><summary>题号导航 · 点击跳题</summary><div class="practice-number-grid">'+session.ids.map((id,n)=>{
          const item=questions.find(x=>x.id===id);
          const state=session.flagged.includes(id)?'review':recorded(item)?'done':'new';
          return '<button type="button" class="practice-number" data-e-jump="'+n+'" data-p-number-state="'+state+'"'+(n===i?' aria-current="step"':'')+' aria-label="第'+(n+1)+'题">'+(n+1)+'</button>';
        }).join('')+'</div></details>'+
        '<article class="practice-question" data-e-question="'+escape(q.id)+'"><div class="practice-question-meta"><span>'+kinds[q.type]+'</span><span>'+q.skills.map(escape).join(' · ')+'</span></div>'+
        '<h2 tabindex="-1" data-e-title>'+escape(q.title)+'</h2><div class="practice-prompt">'+(q.promptHtml||escape(q.prompt))+'</div>'+
        examInput(q,a)+'<div class="practice-exam-tools"><button class="practice-subtle-button" data-e-flag aria-pressed="'+session.flagged.includes(q.id)+'">'+(session.flagged.includes(q.id)?'✓ 已标记待检查':'标记待检查')+'</button></div>'+
        '<div class="practice-pagination"><button class="practice-page-button" data-e-prev'+(i===0?' disabled':'')+'>上一题</button>'+
        '<button class="practice-primary-button" data-e-next'+(i===session.ids.length-1?' disabled':'')+'>下一题</button>'+
        '<button class="practice-page-button" data-e-finish>交卷</button></div>'+
        (confirming?'<div class="practice-exam-confirm" role="alertdialog" aria-label="确认交卷"><p>仍有'+(session.ids.length-completed)+'题未作答。确认交卷后会展示所有参考答案，无法回到未批改状态。</p>'+
        '<button type="button" class="practice-primary-button" data-e-confirm>确认交卷并批改</button>'+
        '<button type="button" class="practice-page-button" data-e-cancel>继续答题</button></div>':'')+
        '</article></section>';
    }
    content.addEventListener('input',event=>{
      if(!session||session.finished)return;
      const q=current(),a=getDraft(q),t=event.target;
      if(t.matches('[name="e-answer"]'))a.selected=Array.from(content.querySelectorAll('[name="e-answer"]:checked'),e=>e.value);
      else if(t.matches('[data-e-value]'))a.value=t.value;
      else if(t.matches('[data-e-reason]'))a.reason=t.value;
      else return;
      persistExams();
    });
    content.addEventListener('change',event=>{
      if(event.target.matches('[name="e-answer"],[data-e-value],[data-e-reason]')){
        const q=current(),a=getDraft(q);
        if(event.target.matches('[name="e-answer"]'))a.selected=Array.from(content.querySelectorAll('[name="e-answer"]:checked'),e=>e.value);
        persistExams();
      }
    });
    content.addEventListener('click',event=>{
      const t=event.target,action=name=>t.closest('['+name+']');
      if(action('data-e-start')){startExam(Number(action('data-e-start').dataset.eStart));return;}
      if(action('data-e-reset')){session=null;delete examStore[key];persistExams();render();return;}
      if(!session)return;
      if(session.finished){
        if(action('data-e-review'))session.reviewId=action('data-e-review').dataset.eReview;
        else if(action('data-e-back'))session.reviewId=null;
        else return;
        persistExams();render();return;
      }
      if(action('data-e-jump')){session.index=Number(action('data-e-jump').dataset.eJump);confirming=false;}
      else if(action('data-e-prev')){session.index=Math.max(0,session.index-1);confirming=false;}
      else if(action('data-e-next')){session.index=Math.min(session.ids.length-1,session.index+1);confirming=false;}
      else if(action('data-e-flag')){
        const id=current().id;session.flagged=session.flagged.includes(id)?session.flagged.filter(x=>x!==id):[...session.flagged,id];
      }else if(action('data-e-finish')){confirming=true;}
      else if(action('data-e-cancel')){confirming=false;}
      else if(action('data-e-confirm')){
        for(const id of session.ids){
          const q=questions.find(x=>x.id===id);
          if(!recorded(q))continue;
          const a=getDraft(q),r=record(q),value=resultFor(q);
          r.selected=[...a.selected];r.value=a.value;r.reason=a.reason;r.confidence=a.confidence;
          r.submitted=true;r.lastCorrect=value;
          r.attempts.push({correct:value,assisted:r.hinted||r.revealed||Boolean(r.feedbackSeen),confidence:r.confidence});
          r.feedbackSeen=true;if(r.attempts.length>100)r.attempts=[r.attempts[0],...r.attempts.slice(-99)];
        }
        save();session.finished=true;session.reviewId=null;confirming=false;
      }else return;
      persistExams();render();
      if(!session.finished&&content.querySelector('[data-e-title]'))content.querySelector('[data-e-title]').focus({preventScroll:true});
    });
    render();
  }
  function hubHtml(course){
    return '<section class="practice-hub" data-practice-hub><nav class="practice-modes" aria-label="练习与题集">'+
      '<button type="button" data-practice-mode="local" aria-pressed="true">逐题练习</button>'+
      '<button type="button" data-practice-mode="exam" aria-pressed="false">章节测试</button>'+
      '<button type="button" data-practice-mode="sources" aria-pressed="false">精选来源</button>'+
      '<button type="button" data-practice-mode="mistakes" aria-pressed="false">错题集</button>'+
      '<button type="button" data-practice-mode="favorites" aria-pressed="false">收藏集</button></nav>'+
      '<div data-practice-content></div></section>';
  }
  function mountHub(root,initialCourse,section){
    const hub=root.querySelector('[data-practice-hub]'),content=hub.querySelector('[data-practice-content]');
    let course=courses.some(c=>c.id===initialCourse)?initialCourse:courses[0].id;
    let mode=questions.some(q=>q.course===course)?'local':'sources';
    function render(){
      hub.querySelectorAll('[data-practice-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.practiceMode===mode)));
      if(mode==='local'){
        content.innerHTML=shell(course,section);mount(content,course,section);return;
      }
      if(mode==='exam'){
        content.innerHTML='<div data-exam-content></div>';
        mountExam(content,course,section);return;
      }
      let html='<label class="practice-picker">当前课程<select data-source-course>'+courseOptions(course)+'</select></label>';
      if(mode==='sources'){
        const all=bank.sources.filter(s=>s.targets.some(t=>t.course===course)),exact=all.filter(s=>s.targets.some(t=>t.course===course&&t.section===section)),selected=exact.length?exact:all;
        html+='<p class="practice-note">这些资源有原题或公开解答的出处；外部成绩不会回传本站，也不会改变你已做题的记录。</p>';
        if(section&&!exact.length)html+='<p>本节暂无直接对应选题，以下为本课程相关来源。</p>';
        const ready=selected.filter(s=>s.ready),pending=selected.filter(s=>!s.ready);
        html+=ready.length?ready.map((s,i)=>sourceHtml(s,i===0)).join(''):'<p>此范围没有已核足访问与解答的公开来源。</p>';
        if(pending.length)html+='<details class="practice-candidates"><summary>候选来源 '+pending.length+'项 · 尚待核验</summary>'+pending.map(s=>sourceHtml(s)).join('')+'</details>';
      }else{
        const native=questions.filter(q=>q.course===course&&(mode==='mistakes'?isMistake(record(q)):record(q).favorite));
        html+='<p class="practice-note">错题记录和收藏独立保留；重做不会覆盖独立首答。所有数据仅在当前浏览器。</p>'+
          externalCollection(course,mode)+'<h3>站内练习 · '+native.length+'题</h3>'+(native.length?shell(course):'<p>暂无对应的站内题。</p>');
      }
      content.innerHTML=html;
      if(mode!=='sources'&&content.querySelector('[data-practice-panel]')){
        mount(content,course,null,mode);
        content.querySelector('[data-p-course]').closest('label').hidden=true;
      }
      save();
    }
    hub.addEventListener('change',event=>{
      if(event.target.matches('[data-source-course]')){course=event.target.value;section=null;render();}
      else if(event.target.matches('[data-p-course]'))course=event.target.value;
    });
    hub.addEventListener('click',event=>{
      const tab=event.target.closest('[data-practice-mode]');
      if(tab){mode=tab.dataset.practiceMode;render();return;}
      const saveButton=event.target.closest('[data-source-save]');
      if(saveButton){
        const entry=saveButton.closest('[data-source-id]'),ref=entry.querySelector('[data-source-ref]').value.trim(),status=entry.querySelector('[data-source-status]');
        if(!ref){status.textContent='先填写具体题号或定位，避免把整套来源当一道题。';return;}
        const id=entry.dataset.sourceId,key=id+'::'+ref;let item=extItems().find(i=>i.key===key);
        if(!item){item={key,sourceId:id,ref,favorite:false,mistake:false,reviewed:false};extItems().push(item);}
        item.note=entry.querySelector('[data-source-note]').value;item[saveButton.dataset.sourceSave]=true;
        if(saveButton.dataset.sourceSave==='mistake')item.reviewed=false;
        save();status.textContent=persistent?'已保存，可在错题集或收藏集按课程再做。':'当前浏览器无法持久保存这条记录。';return;
      }
      const external=event.target.closest('[data-external-record]');
      if(external){
        const item=extItems().find(i=>i.key===external.dataset.externalRecord);
        if(event.target.closest('[data-external-review]')){item.reviewed=true;save();render();}
        else if(event.target.closest('[data-external-favorite]')){item.favorite=!item.favorite;save();render();}
      }
    });
    render();
  }
  const dialog=document.querySelector('#practice-dialog');let origin=null;
  document.addEventListener('click',event=>{
    const trigger=event.target.closest('[data-open-practice]');if(!trigger)return;
    const directory=document.querySelector('#reader-directory');
    origin={element:directory.contains(trigger)?document.querySelector('[data-reader-directory]'):trigger,x:scrollX,y:scrollY};
    if(directory.open)directory.close();
    const course=trigger.dataset.practiceCourse,section=trigger.dataset.practiceSection;
    document.querySelector('#practice-dialog-content').innerHTML=hubHtml(course);mountHub(dialog,course,section);
    document.body.classList.add('practice-open');dialog.showModal();
    const questionId=trigger.dataset.practiceQuestion;
    if(questionId&&questions.some(q=>q.id===questionId&&q.course===course)){
      dialog.querySelector('[data-practice-mode="local"]').click();
      const picker=dialog.querySelector('[data-p-question]');
      if([...picker.options].some(option=>option.value===questionId)){picker.value=questionId;picker.dispatchEvent(new Event('change',{bubbles:true}));}
    }
  });
  dialog.addEventListener('click',event=>{
    if(event.target.closest('[data-close-practice]')){dialog.close();return;}
    const readingLink=event.target.closest('.practice-reading a');
    if(!readingLink||event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||readingLink.hash!==location.hash)return;
    event.preventDefault();origin=null;dialog.close();
    const body=document.querySelector('#lesson-body'),anchor=decodeURIComponent(readingLink.hash.split('/').slice(3).join('/'));
    if(body)window.LNPublication.settle(body,anchor);
  });
  dialog.addEventListener('close',()=>{document.body.classList.remove('practice-open');if(origin?.element?.isConnected){scrollTo({left:origin.x,top:origin.y,behavior:'instant'});origin.element.focus({preventScroll:true});}origin=null;});
  window.LNPractice={noteReferenceUse: id=>{const q=questions.find(q=>q.id===id);if(q){const r=record(q);r.revealed=true;r.feedbackSeen=true;save();}},button,pageHtml:course=>'<h1>练习</h1>'+hubHtml(course),mount:mountHub,onRoute:()=>{origin=null;if(dialog.open)dialog.close();}};
})();
