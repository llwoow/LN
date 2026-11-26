'use strict';
(() => {
  const bank=window.LN_PRACTICE_BANK,questions=bank.questions,courses=window.LN_COURSES.filter(c=>!c.outlineOnly);
  const kinds={single:'单选',multi:'多选',numeric:'计算',fill:'填空',open:'问答'};
  const skills=['建模','因果与证据','推导计算','边界与反例','迁移设计','解释表达'];
  const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const key='ln.practice.v1';let records={},persistent=true;
  const normalize=v=>String(v??'').trim().replace(/[’‘]/g,"'").replace(/\s+/g,' ').toLowerCase();
  function stopMedia(root){root?.querySelectorAll('audio').forEach(a=>{a.pause();a.removeAttribute('src');a.load();});}
  function readStored(key) {
    const value=JSON.parse(localStorage.getItem(key)||'{}');
    return value && typeof value==='object' && !Array.isArray(value) ? value : {};
  }
  try {records=readStored(key);}catch{persistent=false;}
  window.addEventListener('storage',event=>{
    if(event.key!==key)return;
    try {records=readStored(key);}catch{persistent=false;}
  });
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
    if(q.type==='fill')return r.value.trim()?q.answer.some(a=>normalize(a)===normalize(r.value)):undefined;
    if(q.type==='numeric'){
      const raw=r.value.trim().replace(/−/g,'-');
      if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(raw))return undefined;
      const value=Number(raw);return Number.isFinite(value)?Math.abs(value-q.answer)<=q.tolerance:undefined;
    }
    if(!r.selected.length)return undefined;
    return r.selected.length===q.answer.length&&q.answer.every(x=>r.selected.includes(x));
  }
  function attemptFor(r,correct,confidence,q,draft=r) {
    const attempt={correct,assisted:Boolean(r.hinted || r.revealed || r.feedbackSeen || r.attempts.length),confidence};
    if(q?.collection==='english-2027'){
      attempt.answer=q.type==='open'?draft.reason:q.type==='numeric'||q.type==='fill'?draft.value:[...draft.selected];
      attempt.time=new Date().toISOString();
    }
    return attempt;
  }
  function appendAttempt(r,attempt) {
    r.attempts.push(attempt);
    if(attempt.time)r.updatedAt=attempt.time;
    r.feedbackSeen=true;
    if(r.attempts.length>100)r.attempts=[r.attempts[0],...r.attempts.slice(-99)];
  }
  function needsReview(q,r){return Boolean(r&&(r.hinted||r.revealed||(!r.attempts.length&&r.feedbackSeen)||r.attempts.some(a=>a.correct===false)||(q.type==='open'&&r.submitted&&r.checks.length<q.rubric.length)));}
  function isMistake(r){return Boolean(r&&(r.selfMistake||r.attempts?.some(a=>a.correct===false)));}
  function practiceHref(course,section,question){
    return '#practice/'+course+(section||question?'/'+(section||''):'')+(question?'/'+encodeURIComponent(question):'');
  }
  function button(course,section,label='练习'){
    if(course.outlineOnly||section?.kind==='outline')return '';
    return '<a class="resource-nav-button" data-open-practice href="'+escape(practiceHref(course.id,section?.id))+'">'+escape(label)+'</a>';
  }
  function prepareLesson(body){
    // Previously published lesson content embeds exercise buttons with course, section and question IDs.
    for(const trigger of body.querySelectorAll('button[data-open-practice]')){
      const {practiceCourse,practiceSection,practiceQuestion}=trigger.dataset;
      const link=document.createElement('a');
      for(const {name,value} of trigger.attributes){
        if(!['type','aria-haspopup','aria-controls'].includes(name))link.setAttribute(name,value);
      }
      link.href=practiceHref(practiceCourse,practiceSection,practiceQuestion);
      link.append(...trigger.childNodes);
      trigger.replaceWith(link);
    }
  }

  // Shared learning workspace: every course reuses the same editor, navigation and feedback.
  function shell(course,section){
    return '<section class="practice-panel practice-workspace" data-practice-panel>'+
      '<header class="practice-session-head"><div class="practice-session-title"><h2 data-p-course-title>'+escape(courses.find(c=>c.id===course)?.title||'学习练习')+'</h2><span class="practice-progress-value" data-p-progress aria-live="polite"></span></div>'+
      '<div class="practice-progress-track" aria-hidden="true"><span data-p-progress-bar></span></div><p class="practice-note" data-p-scope></p></header>'+
      '<div class="practice-workspace-tools"><label class="practice-picker"><select data-p-question aria-label="按名称选择题目"></select></label>'+
      '<details class="practice-number-map" data-p-map><summary>题号</summary><div class="practice-tool-panel"><p data-p-map-summary></p><div data-p-grid class="practice-number-grid" aria-label="按题号跳转"></div></div></details>'+
      '<details class="practice-filter-box" data-p-filter-box><summary>筛选</summary><div class="practice-controls practice-tool-panel">'+
      '<label>课程<select data-p-course>'+courses.map(c=>'<option value="'+escape(c.id)+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('')+'</select></label>'+
      '<label>题型<select data-p-type><option value="">全部题型</option>'+Object.entries(kinds).map(([id,t])=>'<option value="'+id+'">'+t+'</option>').join('')+'</select></label>'+
      '<label>考察能力<select data-p-skill><option value="">全部能力</option>'+skills.map(s=>'<option>'+s+'</option>').join('')+'</select></label>'+
      '<label class="resource-checkbox"><input type="checkbox" data-p-review>只看待复习题</label></div></details></div>'+
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
    const status=!submitted?'已查看参考解析':q.type==='open'?'请逐项自评论证':correct?(q.type==='fill'?'答案吻合':q.type==='numeric'?'数值吻合，过程仍需核对':'选择吻合，请继续核对理由'):partial?'部分选项吻合，仍有漏选或错选':'答案尚不吻合，检查下面的推理';
    const tone=!submitted||q.type==='open'?'review':correct?'correct':partial?'partial':'wrong';
    const answerSummary=q.options?
      '<p class="practice-answer-line"><strong>你的选择：</strong>'+escape(answerLabel(q,r,r.selected))+' <span aria-hidden="true">·</span> <strong>正确答案：</strong>'+escape(answerLabel(q,r,q.answer))+'</p>':
      q.type==='numeric'?
      '<div class="practice-numeric-compare"><div><small>你的数值</small><strong>'+escape(r.value||'未填写')+' '+escape(q.unit)+'</strong></div>'+
      '<div><small>参考答案</small><strong>'+formattedNumber(q.answer,q.tolerance)+' '+escape(q.unit)+'</strong></div></div>'+
      '<p class="practice-answer-line">容许绝对误差：±'+escape(q.tolerance)+' '+escape(q.unit)+'。只判断数值；单位、过程与条件仍需自行核查。</p>':
      q.type==='fill'?'<p class="practice-answer-line"><strong>你的答案：</strong>'+escape(r.value||'未填写')+' · <strong>可接受形式：</strong>'+escape(q.answer.join(' / '))+'</p>':
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
  function promptHtml(q,answerFor=id=>records[id]){
    let markup=q.promptHtml||escape(q.prompt);
    if(q.collection==='english-2027'&&q.passage==='S')for(const other of questions.filter(x=>x.collection===q.collection&&x.passage==='S')){
      const chosen=answerFor(other.id)?.selected?.[0],option=other.options?.find(o=>o.id===chosen);
      if(option)markup=markup.replaceAll('['+other.sourceQuestion+']','【'+other.sourceQuestion+' '+escape(option.text)+'】');
    }
    return markup;
  }
  function noteTranscript(q){
    if(!q||q.collection!=='english-2027'||!q.passage)return;
    for(const other of questions.filter(x=>x.collection===q.collection&&x.passage===q.passage))record(other).feedbackSeen=true;
    save();
  }
  function questionHtml(q,r=record(q)){
    const choice=q.type==='single'||q.type==='multi',graded=r.submitted||r.revealed;
    const options=choice?'<fieldset class="practice-options"><legend>'+(q.type==='multi'?'多选 · 选择所有有依据的判断':'单选 · 选择最有依据的一项')+'</legend>'+
      r.order.map((id,index)=>{
        const o=q.options.find(x=>x.id===id),checked=r.selected.includes(id),expected=q.answer.includes(id);
        const mark=!graded?'':checked&&expected?'correct':checked&&!expected?'wrong':!checked&&expected?'missed':'neutral';
        const inline=graded&&(checked||expected)?'<span class="practice-choice-detail"><b>'+(
          checked&&expected?'已选 · 正确':checked&&!expected?'已选 · 错误':'漏选 · 应选')+'</b>'+escape(o.feedback)+'</span>':'';
        return '<label class="practice-choice" data-p-option-state="'+mark+'"><input type="'+(q.type==='multi'?'checkbox':'radio')+'" name="p-answer" value="'+escape(id)+'"'+(checked?' checked':'')+'>'+
          '<span class="practice-choice-letter" aria-hidden="true">'+String.fromCharCode(65+index)+'</span><span class="practice-choice-main"><span>'+escape(o.text)+'</span>'+inline+'</span></label>';
      }).join('')+'</fieldset>':
      q.type==='fill'?'<label class="practice-value">填空答案<input type="text" data-p-value value="'+escape(r.value)+'" autocomplete="off"></label>':
      q.type==='numeric'?'<label class="practice-value">计算结果 <span>('+escape(q.unit)+')</span><input type="text" inputmode="decimal" data-p-value value="'+escape(r.value)+'" autocomplete="off" placeholder="填写数值，允许科学计数法"></label>':'';
    const reason='<label class="practice-reason">'+(q.type==='open'?'写下推理过程（必填）':'推导、判断依据或草稿（选填）')+
      '<textarea data-p-reason rows="'+(q.type==='open'?7:4)+'" placeholder="写下自己的分析；本地自动保存">'+escape(r.reason)+'</textarea></label>';
    const reasoning=q.type==='open'?reason:'<details class="practice-thinking"'+((r.reason||q.type==='numeric')?' open':'')+'><summary>写下自己的推导或理由（可选）</summary>'+reason+'</details>';
    const briefTone=!graded||!r.submitted?'review':q.type==='open'?'review':r.lastCorrect?'correct':'wrong';
    const briefStatus=!r.submitted?'已查看参考答案':q.type==='open'?'推理过程待自行对照':r.lastCorrect?'已吻合':'需要修正';
    const briefAnswer=q.options?'你的选择 '+answerLabel(q,r,r.selected)+' · 正确答案 '+answerLabel(q,r,q.answer):
      q.type==='numeric'?'参考数值 '+formattedNumber(q.answer,q.tolerance)+' '+q.unit:
      q.type==='fill'?'可接受形式 '+q.answer.join(' / '):'参考推导与评分要点在题目下方';
    const overview=graded?'<div class="practice-result-overview" data-p-overview data-p-overview-tone="'+briefTone+'" tabindex="-1" role="status">'+
      '<strong>'+briefStatus+'</strong><span>'+escape(briefAnswer)+'</span></div>':'';
    return '<article class="practice-question" data-question-id="'+escape(q.id)+'">'+
      '<div class="practice-question-meta"><span>'+kinds[q.type]+'</span><span>'+q.skills.map(escape).join(' · ')+'</span></div>'+
      '<h2 tabindex="-1" data-p-title>'+escape(q.title)+'</h2>'+
      '<div class="practice-prompt">'+promptHtml(q)+'</div>'+overview+options+reasoning+
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
  function mount(root,initialCourse,initialSection,collection='',initialQuestion=''){
    if(questions.some(q=>q.promptHtml)&&!document.querySelector('link[href="assets/katex/katex.min.css"]')){
      const link=document.createElement('link');link.rel='stylesheet';link.href='assets/katex/katex.min.css';document.head.append(link);
    }
    let selected=initialQuestion,matches=[],section=initialSection;
    const panel=root.querySelector('[data-practice-panel]'),body=panel.querySelector('[data-p-body]'),picker=panel.querySelector('[data-p-question]');
    const tools=panel.querySelector('.practice-workspace-tools');
    const disclosures=[...tools.querySelectorAll('details')];
    tools.addEventListener('toggle',event=>{
      if(event.target.open)disclosures.forEach(item=>{if(item!==event.target)item.open=false;});
    },true);
    tools.addEventListener('keydown',event=>{
      const open=disclosures.find(item=>item.open);
      if(event.key!=='Escape'||!open)return;
      event.preventDefault();
      open.open=false;
      open.querySelector('summary').focus();
    });
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
      panel.querySelector('[data-p-map-summary]').textContent='已作答 '+done+' / '+matches.length;
      panel.querySelector('[data-p-grid]').innerHTML=matches.map((t,i)=>{
        const r=record(t),status=needsReview(t,r)?'review':r.attempts.length?'done':'new';
        return '<button type="button" data-p-jump="'+escape(t.id)+'" class="practice-number" data-p-number-state="'+status+'"'+(t.id===selected?' aria-current="step"':'')+' aria-label="第'+(i+1)+'题：'+escape(t.title)+'">'+(i+1)+'</button>';
      }).join('');
      stopMedia(body);body.innerHTML=q?questionHtml(q):'<p class="practice-empty">这个范围暂无题目。你可以调整筛选或查看其他课程。</p>';
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
      panel.querySelector('[data-p-scope]').textContent=(section?(fallback?'本节暂无题，显示全课':'本节关联练习'):'全课')+' · '+base.length+'题';
      matches=base.filter(q=>(!type||q.type===type)&&(!skill||q.skills.includes(skill))&&(!review||needsReview(q,record(q))));
      if(!matches.some(q=>q.id===selected))selected=matches[0]?.id||'';
      render();
    }
    panel.addEventListener('change',event=>{
      if(event.target.matches('[data-p-course]')){section=null;filter();return;}
      if(event.target.matches('[data-p-type],[data-p-skill],[data-p-review]')){filter();return;}
      if(event.target===picker){
        disclosures.forEach(item=>{item.open=false;});
        selected=picker.value;render(true);return;
      }
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
      if(!t.matches('[data-p-rubric]')&&t.matches('[name="p-answer"],[data-p-value],[data-p-reason]')){
        r.submitted=false;r.checks=[];
        // Keep the option appearance in sync without replacing the active input or caret.
        body.querySelectorAll('[data-p-option-state]').forEach(label=>{label.dataset.pOptionState='';label.querySelector('.practice-choice-detail')?.remove();});
        body.querySelector('[data-p-feedback]').innerHTML='';
        body.querySelector('[data-p-overview]')?.remove();
      }
      if(t.matches('[data-p-rubric]')){ /* the answer remains in review mode */ }
      body.querySelector('[data-p-error]').textContent='';
      if(q.collection==='english-2027'){r.updatedAt=new Date().toISOString();if(t.matches('[name="p-answer"]')&&q.passage==='S')body.querySelector('.practice-prompt').innerHTML=promptHtml(q);}
      summary();save();storage();
    }
    panel.addEventListener('toggle',event=>{if(event.target.matches('[data-practice-transcript]')&&event.target.open)noteTranscript(matches.find(q=>q.id===selected));},true);
    panel.addEventListener('input',draft);
    panel.addEventListener('click',event=>{
      const jump=event.target.closest('[data-p-jump]');
      if(jump){
        panel.querySelector('[data-p-map]').open=false;
        selected=jump.dataset.pJump;render(true);return;
      }
      if(!tools.contains(event.target))disclosures.forEach(item=>{item.open=false;});
      const q=matches.find(q=>q.id===selected);if(!q)return;
      const r=record(q),target=event.target;
      if(target.closest('[data-p-submit]')){
        const value=evaluate(q,r),error=body.querySelector('[data-p-error]');
        if(q.type==='open'&&!r.reason.trim()){error.textContent='请先写下你的分析，再对照参考要点。';return;}
        if(value===undefined){error.textContent=q.type==='numeric'?'请填写有限的纯数值；单位见输入框标签。':q.type==='fill'?'请先填写答案。':'请先选择答案。';return;}
        r.submitted=true;r.lastCorrect=value;
        appendAttempt(r,attemptFor(r,value,r.confidence,q));
        render();
        const resultAnchor=body.querySelector(q.type==='open'?'.practice-verdict':'[data-p-overview]');
        resultAnchor?.scrollIntoView({block:'start',behavior:'instant'});
        resultAnchor?.focus({preventScroll:true});
      }else if(target.closest('[data-p-hint]')){
        r.hinted=true;body.querySelector('[data-p-hint-text]').hidden=false;save();summary();
      }else if(target.closest('[data-p-reveal]')){
        r.revealed=true;r.feedbackSeen=true;render();
        const revealAnchor=body.querySelector(q.type==='open'?'.practice-verdict':'[data-p-overview]');
        revealAnchor?.scrollIntoView({block:'start',behavior:'instant'});
        revealAnchor?.focus({preventScroll:true});
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
  function examScope(course,section){
    const items=questions.filter(q=>q.course===course);
    const exact=section ? items.filter(q=>q.sections.includes(section)) : [];
    return exact.length ? exact : items;
  }
  function mountExam(root,course,section){
    const content=root.querySelector('[data-exam-content]');
    const scopeKey=course+'::'+(section||'all');
    const eligible=examScope(course,section);
    const byId=new Map(eligible.map(q=>[q.id,q]));
    const filterLabels={all:'全部',wrong:'错题',skipped:'未答',pending:'待自评'};
    const blankAnswer={selected:[],value:'',reason:'',confidence:'unsure'};
    let session, storageOK=true, reportFilter='all';

    try {session=readStored(examRecordName)[scopeKey];}catch{storageOK=false;}
    if(!session?.ids?.length || !Array.isArray(session.ids) ||
       session.ids.some(id=>!byId.has(id)) || !session.answers || !Array.isArray(session.flagged)) {
      session=null;
    } else {
      session.index=Math.max(0,Math.min(session.ids.length-1,Math.floor(Number(session.index)||0)));
      if(!session.ids.includes(session.reviewId))session.reviewId=null;
    }

    const roundOf=value=>value?.roundId || value?.createdAt;
    function persistSession(replace=false) {
      try {
        const stored=readStored(examRecordName);
        const saved=stored[scopeKey];
        if(!replace && saved && (roundOf(saved)!==roundOf(session) || saved.finished&&!session?.finished)){
          storageOK=false;
          return false;
        }
        if(session)stored[scopeKey]=session;
        else delete stored[scopeKey];
        localStorage.setItem(examRecordName,JSON.stringify(stored));
        storageOK=true;
      } catch {
        storageOK=false;
      }
      return storageOK;
    }

    const current=()=>byId.get(session.ids[session.index]);
    function draftFor(q){
      const answer=session.answers[q.id] ||= {...blankAnswer,selected:[]};
      // Freeze the displayed option order with the test so it survives a reload.
      answer.order ||= [...record(q).order];
      return answer;
    }
    function resultFor(q){
      if(session.submission)return session.submission.results[q.id]?.correct;
      const answer=session.answers[q.id] || blankAnswer;
      return q.type==='open' ? (answer.reason.trim() ? null : undefined) : evaluate(q,answer);
    }
    const recorded=q=>resultFor(q)!==undefined;
    const countAnswered=()=>session.ids.filter(id=>recorded(byId.get(id))).length;
    function startExam(n){
      session={
        version:1,ids:eligible.slice(0,n).map(q=>q.id),answers:{},flagged:[],
        index:0,finished:false,reviewId:null,createdAt:new Date().toISOString(),
        roundId:globalThis.crypto.getRandomValues(new Uint32Array(4)).join('-')
      };
      session.ids.forEach(id=>draftFor(byId.get(id)));
      reportFilter='all';
      persistSession(true);
      render();
      focusHeading('[data-e-title]');
    }

    function syncHistory(){
      const submission=session.submission;
      if(!submission || submission.historySynced)return true;
      try {records=readStored(key);}catch{return false;}
      for(const [id,result] of Object.entries(submission.results)){
        const r=record(byId.get(id));
        if(!r.attempts.some(a=>a.examId===submission.id))appendAttempt(r,{...result,examId:submission.id});
      }
      save();
      if(!persistent)return false;
      submission.historySynced=true;
      persistSession();
      return true;
    }

    function submitExam(){
      // A previously saved submission wins if the same test was open in another tab.
      try {
        const saved=readStored(examRecordName)[scopeKey];
        if(saved && roundOf(saved)!==roundOf(session))return false;
        if(saved?.finished){
          session=saved;
          return true;
        }
        records=readStored(key);
      }catch{return false;}

      const results={};
      for(const id of session.ids){
        const q=byId.get(id),correct=resultFor(q);
        if(correct!==undefined)results[id]=attemptFor(record(q),correct,draftFor(q).confidence,q,draftFor(q));
      }
      session.submission={
        id:session.roundId || globalThis.crypto.getRandomValues(new Uint32Array(4)).join('-'),
        results
      };
      session.finished=true;
      if(persistSession())return true;

      session.finished=false;
      delete session.submission;
      return false;
    }

    function examInput(q,a){
      if(q.options){
        const options=a.order.map((id,index)=>{
          const option=q.options.find(value=>value.id===id);
          return '<label class="practice-choice"><input type="'+(q.type==='multi'?'checkbox':'radio')+'" name="e-answer" value="'+escape(id)+'"'+(a.selected.includes(id)?' checked':'')+'>'+
            '<span class="practice-choice-letter">'+String.fromCharCode(65+index)+'</span><span class="practice-choice-main">'+escape(option.text)+'</span></label>';
        }).join('');
        return '<fieldset class="practice-options"><legend>'+(q.type==='multi'?'多选 · 选择所有有依据的判断':'单选 · 选择最有依据的一项')+'</legend>'+options+'</fieldset>';
      }
      if(q.type==='fill')return '<label class="practice-value">填空答案<input type="text" data-e-value autocomplete="off" value="'+escape(a.value)+'"></label>';
      if(q.type==='numeric')return '<label class="practice-value">计算结果（'+escape(q.unit)+'）<input type="text" inputmode="decimal" data-e-value autocomplete="off" value="'+escape(a.value)+'" placeholder="只填数值"></label>'+
        '<p class="practice-exam-input-note" data-e-invalid aria-live="polite"></p>'+
        '<details class="practice-thinking"'+(a.reason?' open':'')+'><summary>记录计算过程（可选）</summary><textarea data-e-reason rows="5">'+escape(a.reason)+'</textarea></details>';
      return '<label class="practice-reason">写下推导和理由<textarea data-e-reason rows="8">'+escape(a.reason)+'</textarea></label>';
    }

    function reportStatus(q){
      if(!recorded(q))return ['skipped','未答'];
      if(q.type==='open'){
        const complete=(session.selfChecks?.[q.id]?.length||0)===q.rubric.length;
        return complete ? ['reviewed','已自评'] : ['pending','待自评'];
      }
      return resultFor(q) ? ['correct','吻合'] : ['wrong','未吻合'];
    }
    function updateReportFilter(){
      content.querySelectorAll('[data-e-filter]').forEach(button=>{
        button.setAttribute('aria-pressed',String(button.dataset.eFilter===reportFilter));
      });
      const rows=[...content.querySelectorAll('[data-e-result]')];
      rows.forEach(row=>{row.hidden=reportFilter!=='all' && row.dataset.eResult!==reportFilter;});
      content.querySelector('[data-e-filter-status]').textContent=rows.every(row=>row.hidden) ? '这组暂无题目' : '';
    }

    function report(){
      const selected=session.ids.map(id=>byId.get(id));
      const counts={all:selected.length,wrong:0,skipped:0,pending:0,correct:0};
      const rows=selected.map((q,index)=>{
        const [status,label]=reportStatus(q);
        if(status in counts)counts[status]++;
        return '<button type="button" data-e-review="'+escape(q.id)+'" data-e-result="'+status+'"><span>'+
          String(index+1).padStart(2,'0')+' · '+escape(q.title)+'</span><small>'+label+'</small></button>';
      }).join('');
      const objective=selected.filter(q=>q.type!=='open').length;
      return '<section class="practice-exam-report"><h2 data-e-report-title tabindex="-1">章节测试结果</h2>'+
        '<div class="practice-exam-metrics"><div><small>已作答</small><strong>'+(selected.length-counts.skipped)+' / '+selected.length+'</strong></div>'+
        '<div><small>客观题吻合</small><strong>'+counts.correct+' / '+objective+'</strong></div>'+
        '<div><small>待自评</small><strong>'+counts.pending+'</strong></div><div><small>未作答</small><strong>'+counts.skipped+'</strong></div></div>'+
        '<p class="practice-note">计算过程和问答可在解析中自行核对。</p>'+
        '<h3>逐题核对</h3><div class="practice-exam-filters" role="group" aria-label="筛选测试结果">'+
        Object.entries(filterLabels).map(([id,label])=>'<button type="button" class="practice-page-button" data-e-filter="'+id+'">'+label+' '+counts[id]+'</button>').join('')+
        '</div><p class="practice-note" role="status" data-e-filter-status></p>'+
        '<div class="practice-exam-results">'+rows+'</div>'+
        '<div class="practice-exam-start-actions"><button type="button" class="practice-page-button" data-e-reset>开始新一轮测试</button></div></section>';
    }

    function review(q){
      const answer=draftFor(q),r=record(q),answered=recorded(q);
      if(!r.feedbackSeen || !persistent){r.feedbackSeen=true;save();}
      const snapshot={
        ...r,...answer,checks:session.selfChecks?.[q.id]||[],
        submitted:answered,revealed:!answered,lastCorrect:resultFor(q)
      };
      return '<section class="practice-exam-review"><button type="button" class="practice-page-button" data-e-back>返回测试报告</button>'+
        '<p class="practice-eyebrow">第'+(session.ids.indexOf(q.id)+1)+'题 · 对照解析</p><p class="practice-note" role="status" data-e-review-storage>'+
        (persistent?'':'解析查看记录暂未保存')+'</p>'+questionHtml(q,snapshot)+'</section>';
    }

    function updateProgress(){
      const answered=countAnswered();
      const status=content.querySelector('[data-e-progress]');
      const message='已答 '+answered+' / '+session.ids.length+' · 标记 '+session.flagged.length;
      if(status.textContent!==message)status.textContent=message;
      content.querySelector('[data-e-progress-bar]').style.width=answered/session.ids.length*100+'%';
      content.querySelector('[data-e-storage]').textContent=storageOK?'草稿自动保存于本浏览器':'草稿暂未保存';
      content.querySelectorAll('[data-e-jump]').forEach(button=>{
        const id=session.ids[Number(button.dataset.eJump)];
        const state=session.flagged.includes(id)?'review':recorded(byId.get(id))?'done':'new';
        button.dataset.pNumberState=state;
        button.setAttribute('aria-label','第'+(Number(button.dataset.eJump)+1)+'题 · '+({review:'待检查',done:'已答',new:'未答'}[state]));
      });
      const invalid=content.querySelector('[data-e-invalid]');
      const q=current();
      if(invalid){
        const message=draftFor(q).value.trim()&&!recorded(q)?'请输入有效数值，单位已标在输入框旁。':'';
        if(invalid.textContent!==message)invalid.textContent=message;
      }
    }
    function focusHeading(selector){
      const heading=content.querySelector(selector);
      heading?.scrollIntoView({block:'start'});
      heading?.focus({preventScroll:true});
    }
    function render(){
      stopMedia(content);
      if(!eligible.length){content.innerHTML='<p class="practice-empty">本课程暂无章节测试。可在精选来源查看原题。</p>';return;}
      if(!session){
        const sizes=[10,20].filter(n=>n<eligible.length);
        sizes.push(eligible.length);
        const buttons=sizes.map((n,index)=>'<button type="button" class="'+(index===0?'practice-primary-button':'practice-page-button')+
          '" data-e-start="'+n+'">'+(n===eligible.length?'全部 '+n+' 题':n+' 题')+'</button>').join('');
        content.innerHTML='<section class="practice-exam-welcome"><h2 data-e-welcome-title tabindex="-1">'+escape(courses.find(c=>c.id===course)?.title||'课程')+' · 章节测试</h2>'+
          '<p>可跳题或标记待检查，交卷后查看解析。草稿保存在此浏览器。</p>'+
          '<div class="practice-exam-start-actions">'+buttons+'</div></section>';
        return;
      }
      if(session.finished){
        const synced=syncHistory();
        if(session.reviewId){
          const q=byId.get(session.reviewId);
          content.innerHTML=review(q);
          content.querySelectorAll('input,textarea,select').forEach(el=>{
            el.disabled=!(q.type==='open' && recorded(q) && el.matches('[data-p-rubric]'));
          });
        } else {
          content.innerHTML=report();
          updateReportFilter();
        }
        if(!synced)content.insertAdjacentHTML('afterbegin','<p class="practice-note" role="status">测试已保存，练习记录待同步。重新打开测试可重试。</p>');
        return;
      }

      const q=current(),a=draftFor(q),i=session.index;
      content.innerHTML='<section class="practice-exam-working"><header class="practice-session-head">'+
        '<div class="practice-session-title"><h2>章节测试</h2><span class="practice-progress-value">'+(i+1)+' / '+session.ids.length+'</span></div>'+
        '<div class="practice-progress-track" aria-hidden="true"><span data-e-progress-bar></span></div>'+
        '<div class="practice-exam-progress"><p class="practice-note" data-e-progress role="status"></p><small data-e-storage></small>'+
        '<details class="practice-number-map"><summary>题号</summary><div class="practice-number-grid">'+session.ids.map((id,n)=>
          '<button type="button" class="practice-number" data-e-jump="'+n+'"'+(n===i?' aria-current="step"':'')+'>'+(n+1)+'</button>'
        ).join('')+'</div></details></div></header>'+
        '<article class="practice-question" data-e-question="'+escape(q.id)+'"><div class="practice-question-meta"><span>'+kinds[q.type]+'</span><span>'+q.skills.map(escape).join(' · ')+'</span></div>'+
        '<h2 tabindex="-1" data-e-title>'+escape(q.title)+'</h2><div class="practice-prompt">'+promptHtml(q,id=>session.answers[id])+'</div>'+
        examInput(q,a)+'<div class="practice-exam-tools"><button type="button" class="practice-subtle-button" data-e-flag aria-pressed="'+session.flagged.includes(q.id)+'">'+(session.flagged.includes(q.id)?'✓ 已标记待检查':'标记待检查')+'</button></div>'+
        '<div class="practice-pagination"><button type="button" class="practice-page-button" data-e-prev'+(i===0?' disabled':'')+'>上一题</button>'+
        '<button type="button" class="practice-primary-button" data-e-next'+(i===session.ids.length-1?' disabled':'')+'>下一题</button>'+
        '<button type="button" class="practice-page-button" data-e-finish>交卷</button></div>'+
        '<dialog class="practice-exam-confirm" aria-label="确认交卷"><h3>确认交卷</h3><p data-e-confirm-message></p><p data-e-submit-error role="alert"></p>'+
        '<div class="practice-exam-confirm-actions"><button type="button" class="practice-page-button" data-e-cancel autofocus>继续答题</button>'+
        '<button type="button" class="practice-primary-button" data-e-confirm>确认交卷</button></div></dialog>'+
        '</article></section>';
      updateProgress();
    }

    content.addEventListener('toggle',event=>{if(session&&!session.finished&&event.target.matches('[data-practice-transcript]')&&event.target.open)noteTranscript(current());},true);
    content.addEventListener('input',event=>{
      if(!session)return;
      const target=event.target;
      if(session.finished){
        if(!session.reviewId || !target.matches('[data-p-rubric]'))return;
        session.selfChecks ||= {};
        session.selfChecks[session.reviewId]=[...content.querySelectorAll('[data-p-rubric]:checked')].map(input=>Number(input.value));
        content.querySelector('[data-e-review-storage]').textContent=persistSession()?'':'自评暂未保存';
        return;
      }
      const a=draftFor(current());
      if(target.matches('[name="e-answer"]'))a.selected=[...content.querySelectorAll('[name="e-answer"]:checked')].map(input=>input.value);
      else if(target.matches('[data-e-value]'))a.value=target.value;
      else if(target.matches('[data-e-reason]'))a.reason=target.value;
      else return;
      if(target.matches('[name="e-answer"]')&&current().collection==='english-2027'&&current().passage==='S')content.querySelector('.practice-prompt').innerHTML=promptHtml(current(),id=>session.answers[id]);
      persistSession();
      updateProgress();
    });

    content.addEventListener('click',event=>{
      const target=event.target.closest('button');
      if(!target)return;
      const data=target.dataset;
      if(data.eStart){startExam(Number(data.eStart));return;}
      if(!session)return;

      if(session.finished){
        if(data.eFilter){reportFilter=data.eFilter;updateReportFilter();}
        else if('eReset' in data){session=null;persistSession(true);render();focusHeading('[data-e-welcome-title]');}
        else if(data.eReview){
          session.reviewId=data.eReview;
          persistSession();
          render();
          focusHeading('[data-p-title]');
        } else if('eBack' in data){
          const id=session.reviewId;
          session.reviewId=null;
          persistSession();
          render();
          const row=content.querySelector('[data-e-review="'+CSS.escape(id)+'"]:not([hidden])');
          if(row){row.scrollIntoView({block:'nearest'});row.focus({preventScroll:true});}
          else focusHeading('[data-e-report-title]');
        }
        return;
      }

      const confirmation=content.querySelector('.practice-exam-confirm');
      if('eFinish' in data){
        const skipped=session.ids.length-countAnswered();
        confirmation.querySelector('[data-e-confirm-message]').textContent=
          (skipped?'还有 '+skipped+' 题未作答。':'所有题目均已作答。')+'交卷后可以查看解析。';
        confirmation.querySelector('[data-e-submit-error]').textContent='';
        confirmation.showModal();
        return;
      }
      if('eCancel' in data){confirmation.close();return;}
      if('eConfirm' in data){
        if(!submitExam()){
          confirmation.querySelector('[data-e-submit-error]').textContent='暂时无法保存，请重试。';
          return;
        }
        confirmation.close();
        render();
        focusHeading('[data-e-report-title]');
        return;
      }
      if('eJump' in data)session.index=Number(data.eJump);
      else if('ePrev' in data)session.index=Math.max(0,session.index-1);
      else if('eNext' in data)session.index=Math.min(session.ids.length-1,session.index+1);
      else if('eFlag' in data){
        const id=current().id;
        session.flagged=session.flagged.includes(id)?session.flagged.filter(item=>item!==id):[...session.flagged,id];
        const marked=session.flagged.includes(id);
        target.setAttribute('aria-pressed',String(marked));
        target.textContent=marked?'✓ 已标记待检查':'标记待检查';
        persistSession();
        updateProgress();
        return;
      }else return;
      persistSession();
      render();
      focusHeading('[data-e-title]');
    });
    render();
  }
  function hubHtml(){
    return '<section class="practice-hub" data-practice-hub><nav class="practice-modes" aria-label="练习与题集">'+
      '<button type="button" data-practice-mode="local" aria-pressed="true">逐题练习</button>'+
      '<button type="button" data-practice-mode="exam" aria-pressed="false">章节测试</button>'+
      '<button type="button" data-practice-mode="sources" aria-pressed="false">精选来源</button>'+
      '<button type="button" data-practice-mode="mistakes" aria-pressed="false">错题集</button>'+
      '<button type="button" data-practice-mode="favorites" aria-pressed="false">收藏集</button></nav>'+
      '<div data-practice-content></div></section>';
  }
  function mountHub(root,initialCourse,section,initialQuestion){
    const hub=root.querySelector('[data-practice-hub]'),content=hub.querySelector('[data-practice-content]');
    let course=courses.some(c=>c.id===initialCourse)?initialCourse:courses[0].id;
    let mode=questions.some(q=>q.course===course)?'local':'sources';
    function render(){
      stopMedia(content);
      hub.querySelectorAll('[data-practice-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.practiceMode===mode)));
      if(mode==='local'){
        content.innerHTML=shell(course,section);mount(content,course,section,'',initialQuestion);initialQuestion='';return;
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
      else if(event.target.matches('[data-p-course]')){course=event.target.value;section=null;}
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
  document.addEventListener('play',event=>{if(event.target.tagName==='AUDIO')document.querySelectorAll('audio').forEach(a=>{if(a!==event.target)a.pause();});},true);
  function exportEnglishRecords(){
    const subset={};
    for(const q of questions.filter(q=>q.collection==='english-2027')){
      const r=records[q.id];if(r&&(r.attempts?.length||r.reason||r.value||r.selected?.length||r.favorite||r.selfMistake||r.feedbackSeen||r.revealed))subset[q.sourceQuestion]=r;
    }
    return {assessment:'hainan-english-2027-v1',format:'ln-practice-v1',recordType:'local-learning-not-official-score',exportedAt:new Date().toISOString(),records:subset};
  }
  function importEnglishRecords(data){
    if(data?.assessment!=='hainan-english-2027-v1'||!data.records||typeof data.records!=='object'||Array.isArray(data.records))throw Error('不是本套英语记录');
    let count=0;
    for(const q of questions.filter(q=>q.collection==='english-2027')){
      const x=data.records[q.sourceQuestion]||data.records[q.id];
      if(!x||typeof x.reason!=='string'||x.reason.length>50000||typeof x.value!=='string'||x.value.length>5000||!Array.isArray(x.attempts))continue;
      const r=record(q),hasLocal=Boolean(r.attempts.length||r.reason||r.value||r.selected.length);
      if(!hasLocal){r.reason=x.reason;r.value=x.value;const selected=Array.isArray(x.selected)?x.selected:[x.selected];r.selected=selected.filter(id=>q.options?.some(o=>o.id===id));}
      r.favorite=Boolean(r.favorite||x.favorite);r.selfMistake=Boolean(r.selfMistake||x.selfMistake||x.mistake);
      for(const a of x.attempts.slice(0,100)){
        if(!a||(!Array.isArray(a.answer)&&typeof a.answer!=='string')||JSON.stringify(a.answer).length>50000)continue;
        const selected=Array.isArray(a.answer)?a.answer:[a.answer];
        const draft={value:typeof a.answer==='string'?a.answer:'',selected};
        const correct=evaluate(q,draft);
        const time=typeof a.time==='string'&&Number.isFinite(Date.parse(a.time))?a.time:null;
        if(r.attempts.some(old=>old.time===time&&JSON.stringify(old.answer)===JSON.stringify(a.answer)))continue;
        r.attempts.push({answer:a.answer,correct:correct===undefined?null:correct,assisted:true,confidence:'unsure',time,imported:true});
      }
      if(r.attempts.length>100)r.attempts=[r.attempts[0],...r.attempts.slice(-99)];
      // Imported conditions cannot establish an independent first response.
      r.feedbackSeen=true;r.updatedAt=new Date().toISOString();count++;
    }
    save();return {count,persistent};
  }
  window.LNPractice={exportEnglishRecords,importEnglishRecords,onRoute:()=>stopMedia(document.querySelector('[data-practice-hub]')),noteReferenceUse: id=>{const q=questions.find(q=>q.id===id);if(q){const r=record(q);r.revealed=true;r.feedbackSeen=true;save();}},button,prepareLesson,pageHtml:()=>'<h1 class="practice-page-title">练习</h1>'+hubHtml(),mount:mountHub};
})();
