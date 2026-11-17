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
  function shell(course,section){
    return '<section class="practice-panel practice-v2" data-practice-panel>'
      +'<div class="practice-topline"><div><span class="practice-eyebrow">LN · 智能练习</span><h2>专注作答，逐步理解</h2></div><span class="practice-local-note">进度仅保存在本浏览器</span></div>'
      +'<div class="practice-session-modes" aria-label="作答模式"><button type="button" data-p-session="practice" aria-pressed="true">逐题练习 <small>立即批改</small></button><button type="button" data-p-session="exam" aria-pressed="false">模拟测试 <small>交卷后看答案</small></button></div>'
      +'<div class="practice-overview"><div class="practice-overview-row"><strong data-p-position>第 1 题</strong><span data-p-count></span></div><div class="practice-progress-track"><span data-p-progress-fill></span></div></div>'
      +'<details class="practice-filter-drawer"><summary>筛选题目与知识点</summary><div class="practice-controls"><label>课程<select data-p-course>'+courses.map(c=>'<option value="'+c.id+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('')+'</select></label><label>题型<select data-p-type><option value="">全部题型</option>'+Object.entries(kinds).map(([id,t])=>'<option value="'+id+'">'+t+'</option>').join('')+'</select></label><label>考察<select data-p-skill><option value="">全部能力</option>'+skills.map(s=>'<option>'+s+'</option>').join('')+'</select></label><label class="resource-checkbox"><input type="checkbox" data-p-review>待回看</label></div></details>'
      +'<p data-p-scope></p><div class="practice-jumpbar"><label class="practice-picker">选择题目<select data-p-question></select></label><details class="practice-number-drawer"><summary>题号导航</summary><nav data-p-grid aria-label="按题号跳转"></nav></details></div>'
      +'<div data-p-exam-report hidden></div><div data-p-body></div>'
      +'<div class="practice-session-footer" data-p-exam-footer hidden><p>模拟测试中答案暂不显示，交卷后再统一批改。</p><button type="button" class="secondary-button" data-p-finish-exam>交卷并查看报告</button><button type="button" class="resource-nav-button" data-p-restart-exam hidden>重新开始本套测试</button></div>'
      +'<p data-p-storage role="status"></p><details class="practice-evidence"><summary>查看作答证据与复习统计</summary><div data-p-summary></div><p>首答与提示后作答分开记录。数值吻合不代表推导正确；开放问答只进行手动自评。</p></details></section>';
  }
  function feedback(q,r){
    if(!r.submitted&&!r.revealed)return '';
    const status=r.revealed&&!r.submitted?'已查看参考分析':q.type==='open'?'请逐项自评论证':r.lastCorrect?(q.type==='numeric'?'数值吻合，过程仍需核对':'选择吻合，请继续核对理由'):'答案尚不吻合，检查下面的关键步骤';
    const comparison=q.options?'<div class="practice-answer-compare"><span>我的选择：<strong>'+escape(r.selected.length?r.order.filter(id=>r.selected.includes(id)).map(id=>String(r.order.indexOf(id)+1)).join('、')+'（当前显示序号）':'未选择')+'</strong></span><span>正确选项：<strong>'+escape(r.order.filter(id=>q.answer.includes(id)).map(id=>String(r.order.indexOf(id)+1)).join('、')+'（当前显示序号）')+'</strong></span></div>'
      :q.type==='numeric'?'<div class="practice-answer-compare"><span>你的数值：<strong>'+escape(r.value||'未填写')+' '+escape(q.unit)+'</strong></span><span>参考值：<strong>'+escape(Number(q.answer.toPrecision(8)))+' '+escape(q.unit)+'</strong></span><span>容差：±'+escape(q.tolerance)+' '+escape(q.unit)+'</span></div>':'';
    let missed='';
    if(q.type==='multi'){
      const extra=r.selected.filter(id=>!q.answer.includes(id));
      const lacking=q.answer.filter(id=>!r.selected.includes(id));
      if(extra.length||lacking.length)missed='<p class="practice-multi-difference">'+(extra.length?'错选：'+escape(extra.map(id=>String(r.order.indexOf(id)+1)).join('、'))+'　':'')+(lacking.length?'漏选：'+escape(lacking.map(id=>String(r.order.indexOf(id)+1)).join('、')):'')+'</p>';
    }
    return '<section class="practice-feedback" aria-label="反馈"><div class="practice-feedback-heading"><span class="practice-feedback-symbol" aria-hidden="true">'+(r.revealed&&!r.submitted?'i':r.lastCorrect===true?'✓':q.type==='open'?'✎':'!')+'</span><h3 role="status">'+status+'</h3></div>'
      +comparison+missed+(r.hinted||r.revealed?'<p class="practice-assistance-note">已使用提示或参考分析；这次作答不会被算作独立首答。</p>':'')
      +(q.type==='numeric'?'<p class="practice-assistance-note">这里只核对指定单位下的数值；无法从数值自动判断推导是否正确。</p>':'')
      +'<h4>逐步推导与核查</h4><ol class="practice-solution-steps">'+q.steps.map((s,i)=>'<li><span class="practice-step-index">'+(i+1)+'</span><div>'+(q.stepsHtml?.[i]||escape(s))+'</div></li>').join('')+'</ol>'
      +(q.rubric?'<fieldset class="practice-rubric"><legend>对照自己的过程逐项自评</legend>'+q.rubric.map((s,i)=>'<label><input type="checkbox" data-p-rubric value="'+i+'"'+(r.checks.includes(i)?' checked':'')+'>'+(q.rubricHtml?.[i]||escape(s))+'</label>').join('')+'</fieldset>':'')
      +'<h4>改变条件再试一次</h4><div class="practice-transfer">'+(q.transferHtml||escape(q.transfer))+'</div>'
      +'<button type="button" class="secondary-button" data-p-redo>遮住解析重新作答（保留首答）</button></section>';
  }
  function questionHtml(q,answer,examPending=false){
    const r=answer||record(q),choice=q.type==='single'||q.type==='multi';
    const show=!examPending&&(r.submitted||r.revealed);
    const options=choice?'<fieldset class="practice-options"><legend>'+(q.type==='multi'?'多选 · 选择全部有依据的判断':'单选 · 选择最有依据的一项')+'</legend>'+r.order.map((id,i)=>{
      const o=q.options.find(x=>x.id===id),picked=r.selected.includes(id),correct=q.answer.includes(id);
      const state=show?(correct?' practice-option-correct':picked?' practice-option-wrong':' practice-option-muted'):'';
      return '<label class="practice-option'+state+'"><input type="'+(q.type==='multi'?'checkbox':'radio')+'" name="p-answer" value="'+id+'"'+(picked?' checked':'')+'><span class="practice-option-letter" aria-hidden="true">'+(i+1)+'</span><span class="practice-option-detail"><span class="practice-option-text">'+escape(o.text)+'</span>'+(show?'<span class="practice-option-reason"><strong>'+ (correct?'正确选项':picked?'错误选项':'不选')+'</strong> · '+escape(o.feedback)+'</span>':'')+'</span></label>';
    }).join('')+'</fieldset>':q.type==='numeric'?'<label class="practice-value">计算结果 · '+escape(q.unit)+'<input type="text" inputmode="decimal" data-p-value value="'+escape(r.value)+'" autocomplete="off" placeholder="填写数值（可用科学计数法）"></label>':'';
    const reason='<div class="practice-working"><label class="practice-reason">'+(q.type==='open'?'写下你的分析和推导':'我的推导与理由（可选）')+'<textarea data-p-reason rows="'+(q.type==='open'?6:3)+'" placeholder="记录关键方程、条件和检查步骤">'+escape(r.reason)+'</textarea></label></div>';
    return '<article class="practice-question" data-question-id="'+escape(q.id)+'">'
      +'<div class="practice-question-heading"><p class="page-meta">'+kinds[q.type]+' · '+escape(q.skills.join(' / '))+'</p><div class="practice-bookmark"><button type="button" class="resource-nav-button" data-p-favorite aria-pressed="'+Boolean(r.favorite)+'">'+(r.favorite?'★ 已收藏':'☆ 收藏')+'</button><button type="button" class="resource-nav-button" data-p-mistake aria-pressed="'+Boolean(r.selfMistake)+'">'+(r.selfMistake?'已标记待复习':'标记不会')+'</button></div></div>'
      +'<h2 tabindex="-1" data-p-title>'+escape(q.title)+'</h2><div class="practice-prompt">'+(q.promptHtml||escape(q.prompt))+'</div>'+options
      +reason+'<div class="practice-confidence-row"><label class="practice-confidence">答题把握<select data-p-confidence><option value="unsure"'+(r.confidence==='unsure'?' selected':'')+'>还不确定</option><option value="sure"'+(r.confidence==='sure'?' selected':'')+'>有把握并能解释</option></select></label><div class="practice-aids"><button type="button" class="resource-nav-button" data-p-hint'+(examPending?' hidden':'')+'>提示一步</button><button type="button" class="resource-nav-button" data-p-reveal'+(examPending?' hidden':'')+'>查看参考分析</button></div></div>'
      +'<div class="practice-actions"><button type="button" class="secondary-button" data-p-submit>'+(examPending?'保存本题并下一题':q.type==='open'?'保存并对照要点':'提交并查看解析')+'</button></div><p data-p-error role="alert"></p>'
      +'<div class="practice-hint" data-p-hint-text'+(r.hinted?'':' hidden')+'>'+(q.hintHtml||escape(q.hint))+'</div><div data-p-feedback>'+(!examPending?feedback(q,r):'')+'</div>'
      +'<details class="practice-related"><summary>关联讲解与题目出处</summary><nav class="practice-reading" aria-label="回查讲解">'+q.sections.map(id=>{const c=courses.find(c=>c.id===q.course),s=c.sections.find(s=>s.id===id);return s?'<a href="#course/'+c.id+'/'+id+(q.readingAnchor&&id===(q.readingSection||'transformer-homework')?'/'+encodeURIComponent(q.readingAnchor):'')+'">回查：'+escape(s.title)+'</a>':'';}).join('')+'</nav><p class="practice-origin">'+escape(q.origin)+'</p></details>'
      +'<nav class="practice-pagination" aria-label="题目切换"><button type="button" class="secondary-button" data-p-prev>上一题</button><button type="button" class="secondary-button" data-p-next>下一题</button></nav></article>';
  }
  function mount(root,initialCourse,initialSection,collection=''){
    if(questions.some(q=>q.promptHtml)&&!document.querySelector('link[href="assets/katex/katex.min.css"]')){const link=document.createElement('link');link.rel='stylesheet';link.href='assets/katex/katex.min.css';document.head.append(link);}
    let selected='',matches=[],section=initialSection,sessionMode='practice';
    const panel=root.querySelector('[data-practice-panel]'),body=panel.querySelector('[data-p-body]'),picker=panel.querySelector('[data-p-question]');
    const storage=()=>{panel.querySelector('[data-p-storage]').textContent=persistent?'草稿、错题和首答记录已保存于当前浏览器。':'浏览器存储不可用，本次记录仅保留到页面关闭。';};
    const examId=()=>[panel.querySelector('[data-p-course]').value,section||'all',collection||'local'].join('::');
    function exam(){
      if(!records.practiceExams||typeof records.practiceExams!=='object'||Array.isArray(records.practiceExams))records.practiceExams={};
      const id=examId();
      if(!records.practiceExams[id])records.practiceExams[id]={createdAt:Date.now(),submitted:false,answers:{}};
      return records.practiceExams[id];
    }
    function examAnswer(q){
      const s=exam(),r=record(q);
      if(!s.answers[q.id])s.answers[q.id]={order:[...r.order],selected:[],value:'',reason:'',confidence:'unsure',checks:[],hinted:false,revealed:false,submitted:false,attempts:[],favorite:!!r.favorite,selfMistake:!!r.selfMistake};
      return s.answers[q.id];
    }
    function activeRecord(q){return sessionMode==='exam'?examAnswer(q):record(q);}
    const isAnswered=(q,r)=>q.type==='open'?Boolean(r.reason.trim()):q.type==='numeric'?r.value.trim()!=='' : r.selected.length>0;
    function summary(){
      const course=panel.querySelector('[data-p-course]').value,items=questions.filter(q=>q.course===course);
      panel.querySelector('[data-p-summary]').innerHTML='<ul>'+skills.map(skill=>{
        const all=items.filter(q=>q.skills.includes(skill)),attempted=all.filter(q=>record(q).attempts.length),first=attempted.filter(q=>record(q).attempts[0]?.correct===true&&!record(q).attempts[0].assisted),review=all.filter(q=>needsReview(q,record(q)));
        return '<li>'+skill+'：'+all.length+' 题；已提交 '+attempted.length+'；独立首答吻合 '+first.length+'；待回看 '+review.length+'</li>';
      }).join('')+'</ul><p>问答只记录作答与自评，不计入“首答吻合”。提示或查看参考答案后的结果不会算作独立首答。</p>';
    }
    const label=q=>{const r=record(q);return kinds[q.type]+' · '+q.title+(needsReview(q,r)?' · 待回看':'')+(r.attempts.some(a=>a.confidence==='sure'&&a.correct===false)?' · 自信误判':'');};
    function render(focus=false){
      const q=matches.find(q=>q.id===selected),ex=sessionMode==='exam'?exam():null;
      picker.innerHTML=matches.map(q=>'<option value="'+escape(q.id)+'"'+(q.id===selected?' selected':'')+'>'+escape(label(q))+'</option>').join('');
      picker.disabled=!matches.length;
      const current=q?activeRecord(q):null,at=q?matches.indexOf(q):-1,answered=matches.filter(item=>sessionMode==='exam'?isAnswered(item,examAnswer(item)):record(item).attempts.length>0).length;
      panel.querySelector('[data-p-position]').textContent=q?'第 '+(at+1)+' / '+matches.length+' 题':'当前没有题目';
      panel.querySelector('[data-p-count]').textContent='已作答 '+answered+' / '+matches.length;
      panel.querySelector('[data-p-progress-fill]').style.width=matches.length?((answered/matches.length)*100)+'%':'0%';
      panel.querySelector('[data-p-grid]').innerHTML=matches.map((item,i)=>{
        const recordNow=sessionMode==='exam'?examAnswer(item):record(item),done=sessionMode==='exam'?isAnswered(item,recordNow):recordNow.attempts.length>0;
        return '<button type="button" data-p-jump="'+escape(item.id)+'"'+(item.id===selected?' aria-current="step"':'')+' class="'+(done?'practice-jump-done':'')+'" aria-label="第'+(i+1)+'题'+(done?'已作答':'未作答')+'">'+(i+1)+'</button>';
      }).join('');
      panel.querySelectorAll('[data-p-session]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.pSession===sessionMode)));
      const footer=panel.querySelector('[data-p-exam-footer]'),report=panel.querySelector('[data-p-exam-report]');
      footer.hidden=sessionMode!=='exam';report.hidden=!(ex?.submitted);
      footer.querySelector('[data-p-finish-exam]').hidden=!!ex?.submitted;
      footer.querySelector('[data-p-restart-exam]').hidden=!ex?.submitted;
      if(ex?.submitted){
        const all=matches.filter(item=>item.type!=='open');
        const graded=all.filter(item=>isAnswered(item,examAnswer(item)));
        const right=graded.filter(item=>evaluate(item,examAnswer(item))===true);
        const open=matches.filter(item=>item.type==='open');
        report.innerHTML='<div class="practice-exam-result"><h3 role="status">本次测试已交卷</h3><p>客观题：已提交 '+graded.length+' 道，其中答案吻合 '+right.length+' 道。另有 '+(all.length-graded.length)+' 道客观题未作答。</p><p>开放问答 '+open.length+' 道需逐项自评；计算题只核对数值，不代表推导正确。</p><p>可点击题号逐题检查自己提交的答案、正确选项与详细解析。后续重测不会覆盖原始首答。</p></div>';
      }else report.innerHTML='';
      body.innerHTML=q?questionHtml(q,current,sessionMode==='exam'&&!ex.submitted):'<p>这个范围没有匹配题目，可调整筛选。</p>';
      if(q){
        body.querySelector('[data-p-prev]').disabled=at===0;
        body.querySelector('[data-p-next]').disabled=at===matches.length-1;
        if(sessionMode==='exam'&&ex.submitted){
          body.querySelectorAll('[name="p-answer"],[data-p-value],[data-p-reason],[data-p-confidence]').forEach(el=>el.disabled=true);
          body.querySelector('[data-p-submit]').hidden=true;
          body.querySelectorAll('[data-p-hint],[data-p-reveal]').forEach(el=>el.hidden=true);
        }
        if(focus)body.querySelector('[data-p-title]').focus({preventScroll:true});
      }
      summary();save();storage();
    }
    function filter(){
      const course=panel.querySelector('[data-p-course]').value,type=panel.querySelector('[data-p-type]').value,skill=panel.querySelector('[data-p-skill]').value,review=panel.querySelector('[data-p-review]').checked;
      let base=questions.filter(q=>q.course===course&&(!collection||(collection==='mistakes'?isMistake(record(q)):record(q).favorite))),exact=section?base.filter(q=>q.sections.includes(section)):[];
      const fallback=Boolean(section&&!exact.length);if(exact.length)base=exact;
      panel.querySelector('[data-p-scope]').textContent=(section?(fallback?'本节暂未编配专属习题，显示本课程题目':'本节关联练习'):'本课程练习')+' · '+base.length+' 题。';
      matches=base.filter(q=>(!type||q.type===type)&&(!skill||q.skills.includes(skill))&&(!review||needsReview(q,record(q))));
      if(!matches.some(q=>q.id===selected))selected=matches[0]?.id||'';
      render();
    }
    function draft(event){
      const q=matches.find(q=>q.id===selected);if(!q)return;
      if(sessionMode==='exam'&&exam().submitted)return;
      const r=activeRecord(q),t=event.target;
      if(t.matches('[name="p-answer"]'))r.selected=Array.from(body.querySelectorAll('[name="p-answer"]:checked'),el=>el.value);
      else if(t.matches('[data-p-value]'))r.value=t.value;
      else if(t.matches('[data-p-reason]'))r.reason=t.value;
      else if(t.matches('[data-p-confidence]'))r.confidence=t.value;
      else if(t.matches('[data-p-rubric]'))r.checks=Array.from(body.querySelectorAll('[data-p-rubric]:checked'),el=>Number(el.value));
      else return;
      if(!t.matches('[data-p-rubric]')&&sessionMode==='practice'){
        r.submitted=false;r.checks=[];body.querySelector('[data-p-feedback]').innerHTML='';
        body.querySelectorAll('.practice-option-correct,.practice-option-wrong,.practice-option-muted').forEach(el=>{
          el.classList.remove('practice-option-correct','practice-option-wrong','practice-option-muted');
          el.querySelector('.practice-option-reason')?.remove();
        });
      }
      save();storage();
    }
    panel.addEventListener('change',event=>{
      const t=event.target;
      if(t.matches('[data-p-course]')){section=null;selected='';filter();return;}
      if(t.matches('[data-p-type],[data-p-skill],[data-p-review]')){selected='';filter();return;}
      if(t===picker){selected=picker.value;render(true);return;}
      draft(event);
    });
    panel.addEventListener('input',draft);
    panel.addEventListener('click',event=>{
      const target=event.target,session=target.closest('[data-p-session]');
      if(session){sessionMode=session.dataset.pSession;selected='';render();return;}
      const jump=target.closest('[data-p-jump]');
      if(jump){selected=jump.dataset.pJump;render(true);return;}
      if(target.closest('[data-p-restart-exam]')){
        delete records.practiceExams[examId()];selected='';filter();return;
      }
      if(target.closest('[data-p-finish-exam]')){
        if(sessionMode!=='exam')return;
        const ex=exam();if(ex.submitted)return;
        ex.submitted=true;ex.submittedAt=Date.now();
        // Answer collection is a separate draft; historical practice answers are never overwritten.
        for(const item of matches){
          const draft=examAnswer(item);
          if(!isAnswered(item,draft)){draft.submitted=false;continue;}
          const result=evaluate(item,draft);
          draft.submitted=true;draft.lastCorrect=result;
          const original=record(item);
          const assisted=original.attempts.length>0||original.hinted||original.revealed||Boolean(original.feedbackSeen);
          original.attempts.push({correct:result,assisted,confidence:draft.confidence,mode:'exam'});
          original.feedbackSeen=true;
          if(original.attempts.length>100)original.attempts=[original.attempts[0],...original.attempts.slice(-99)];
        }
        render();panel.querySelector('[data-p-exam-report]')?.scrollIntoView({block:'nearest'});return;
      }
      const q=matches.find(q=>q.id===selected);if(!q)return;
      const r=activeRecord(q);
      if(target.closest('[data-p-submit]')){
        const error=body.querySelector('[data-p-error]');
        if(sessionMode==='exam'){
          if(exam().submitted)return;
          if(!isAnswered(q,r)){error.textContent='请先作答；也可以直接点击“下一题”跳过。';return;}
          const index=matches.indexOf(q);
          if(index<matches.length-1){selected=matches[index+1].id;render(true);}
          else {error.textContent='已保存最后一题。请点击下方“交卷并查看报告”统一批改。';save();}
          return;
        }
        const value=evaluate(q,r);
        if(q.type==='open'&&!r.reason.trim()){error.textContent='先写下你的分析，再对照参考要点。';return;}
        if(value===undefined){error.textContent=q.type==='numeric'?'请填写有限的纯数值；单位见输入框标签。':'请先选择答案。';return;}
        r.submitted=true;r.lastCorrect=value;
        r.attempts.push({correct:value,assisted:r.hinted||r.revealed||Boolean(r.feedbackSeen),confidence:r.confidence});
        r.feedbackSeen=true;
        if(r.attempts.length>100)r.attempts=[r.attempts[0],...r.attempts.slice(-99)];
        render();
      }else if(target.closest('[data-p-hint]')){if(sessionMode==='exam')return;r.hinted=true;body.querySelector('[data-p-hint-text]').hidden=false;save();summary();}
      else if(target.closest('[data-p-reveal]')){if(sessionMode==='exam')return;r.revealed=true;render();}
      else if(target.closest('[data-p-redo]')){if(sessionMode==='exam')return;r.submitted=false;r.revealed=false;r.selected=[];r.value='';r.reason='';r.checks=[];render();}
      else if(target.closest('[data-p-favorite]')){
        const original=record(q);original.favorite=!original.favorite;r.favorite=original.favorite;
        if(collection)filter();else render();
      }else if(target.closest('[data-p-mistake]')){
        const original=record(q);original.selfMistake=!original.selfMistake;r.selfMistake=original.selfMistake;render();
      }else if(target.closest('[data-p-next],[data-p-prev]')){
        const index=matches.indexOf(q)+(target.closest('[data-p-next]')?1:-1);
        if(matches[index]){selected=matches[index].id;render(true);body.scrollIntoView({block:'start',behavior:'instant'});}
      }
    });
    // The full exercise collection uses the same entry for every LN course.
    panel.querySelector('.practice-session-modes').hidden=!!collection;
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
  function hubHtml(course){return '<section data-practice-hub><nav class="practice-modes" aria-label="练习与题集"><button type="button" data-practice-mode="local" aria-pressed="true">开始练习</button><button type="button" data-practice-mode="mistakes" aria-pressed="false">错题复习</button><button type="button" data-practice-mode="favorites" aria-pressed="false">我的收藏</button><button type="button" data-practice-mode="sources" aria-pressed="false">精选来源</button></nav><div data-practice-content></div></section>';}
  function mountHub(root,initialCourse,section){
    const hub=root.querySelector('[data-practice-hub]'),content=hub.querySelector('[data-practice-content]');
    let course=courses.some(c=>c.id===initialCourse)?initialCourse:courses[0].id;
    let mode='local';
    function render(){
      hub.querySelectorAll('[data-practice-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.practiceMode===mode)));
      if(mode==='local'){content.innerHTML=shell(course,section);mount(content,course,section);return;}
      let html='<label class="practice-picker">课程<select data-source-course>'+courseOptions(course)+'</select></label>';
      if(mode==='sources'){
        const all=bank.sources.filter(s=>s.targets.some(t=>t.course===course)),exact=all.filter(s=>s.targets.some(t=>t.course===course&&t.section===section)),selected=exact.length?exact:all;
        html+='<p class="practice-note">先用有出处的题。研究验证、教材审校、实际教学与官方样题分别标注；它们不是同一种质量证据。</p>';
        if(section&&!exact.length)html+='<p>本节暂无直接对应选题，以下为本课程相关来源。</p>';
        const ready=selected.filter(s=>s.ready),pending=selected.filter(s=>!s.ready);
        html+=ready.length?ready.map((s,i)=>sourceHtml(s,i===0)).join(''):'<p>此范围的逐题解析或访问尚未核足，先保留下面的候选说明。</p>';
        if(pending.length)html+='<details class="practice-candidates"><summary>候选来源 '+pending.length+' 项 · 详解或访问尚待补足</summary>'+pending.map(s=>sourceHtml(s)).join('')+'</details>';
      }else{
        const native=questions.filter(q=>q.course===course&&(mode==='mistakes'?isMistake(record(q)):record(q).favorite));
        html+='<p class="practice-note">本站客观题答错后自动保留；问答与外部题可手动收录。重做不覆盖首答，收藏独立保存。记录限当前浏览器。</p>'+externalCollection(course,mode)+'<h3>站内练习 · '+native.length+' 道</h3>'+(native.length?shell(course):'<p>暂无本站题目。</p>');
      }
      content.innerHTML=html;if(mode!=='sources'&&content.querySelector('[data-practice-panel]')){mount(content,course,null,mode);content.querySelector('[data-p-course]').closest('label').hidden=true;}save();
    }
    hub.addEventListener('change',event=>{if(event.target.matches('[data-source-course]')){course=event.target.value;section=null;render();}else if(event.target.matches('[data-p-course]'))course=event.target.value;});
    hub.addEventListener('click',event=>{
      const tab=event.target.closest('[data-practice-mode]');if(tab){mode=tab.dataset.practiceMode;render();return;}
      const saveButton=event.target.closest('[data-source-save]');
      if(saveButton){
        const entry=saveButton.closest('[data-source-id]'),ref=entry.querySelector('[data-source-ref]').value.trim(),status=entry.querySelector('[data-source-status]');
        if(!ref){status.textContent='先填写具体题号或定位，避免把整套来源当一道题。';return;}
        const id=entry.dataset.sourceId,key=id+'::'+ref;let item=extItems().find(i=>i.key===key);
        if(!item){item={key,sourceId:id,ref,favorite:false,mistake:false,reviewed:false};extItems().push(item);}
        item.note=entry.querySelector('[data-source-note]').value;item[saveButton.dataset.sourceSave]=true;if(saveButton.dataset.sourceSave==='mistake')item.reviewed=false;save();status.textContent=persistent?'已保存，可在错题集或收藏集按课程再做。':'浏览器存储不可用，本次记录仅保留到页面关闭。';return;
      }
      const external=event.target.closest('[data-external-record]');if(external){const item=extItems().find(i=>i.key===external.dataset.externalRecord);if(event.target.closest('[data-external-review]')){item.reviewed=true;save();render();}else if(event.target.closest('[data-external-favorite]')){item.favorite=!item.favorite;save();render();}}
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
      if(dialog.querySelector('[data-practice-mode="local"]').getAttribute('aria-pressed')!=='true')dialog.querySelector('[data-practice-mode="local"]').click();
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
