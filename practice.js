'use strict';
(() => {
  const bank=window.LN_PRACTICE_BANK,questions=bank.questions,courses=window.LN_COURSES;
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
    return '<button type="button" class="resource-nav-button" data-open-practice data-practice-course="'+escape(course.id)+'"'+(section?' data-practice-section="'+escape(section.id)+'"':'')+' aria-haspopup="dialog" aria-controls="practice-dialog">'+escape(label)+'</button>';
  }
  function shell(course,section){
    return '<section class="practice-panel" data-practice-panel><p class="practice-note">原创练习 · 选择题为主，配合计算与问答。答题记录仅保存在当前浏览器。</p><div class="practice-controls"><label>课程<select data-p-course>'+courses.map(c=>'<option value="'+c.id+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('')+'</select></label><label>题型<select data-p-type><option value="">全部题型</option>'+Object.entries(kinds).map(([id,t])=>'<option value="'+id+'">'+t+'</option>').join('')+'</select></label><label>考察<select data-p-skill><option value="">全部能力</option>'+skills.map(s=>'<option>'+s+'</option>').join('')+'</select></label><label class="resource-checkbox"><input type="checkbox" data-p-review>待回看</label></div><p data-p-scope></p><label class="practice-picker">选题<select data-p-question></select></label><div data-p-body></div><p data-p-storage role="status"></p><details class="practice-evidence"><summary>作答证据与待回看</summary><div data-p-summary></div><p>首答、提示后与看答案后的结果分开记录。数值吻合不代表推导正确；自评不是自动批改，也不据此宣布掌握整门课。</p></details></section>';
  }
  function feedback(q,r){
    if(!r.submitted&&!r.revealed)return '';
    const result=r.lastCorrect;
    const status=r.revealed&&!r.submitted?'已查看参考分析':q.type==='open'?'请逐项自评论证':result?(q.type==='numeric'?'数值吻合，过程仍需核对':'选择吻合，请继续核对理由'):'答案尚不吻合，检查下面的推理';
    return '<section class="practice-feedback" aria-label="反馈"><h3 role="status">'+status+'</h3>'+(r.hinted||r.revealed?'<p>本题已使用提示或参考分析，后续答对不作独立首答证据。</p>':'')+(q.options?'<ul class="practice-option-feedback">'+r.order.map(id=>{const o=q.options.find(x=>x.id===id);return '<li><strong>'+(q.answer.includes(id)?'应选':'不选')+'：'+escape(o.text)+'</strong><p>'+escape(o.feedback)+'</p></li>';}).join('')+'</ul>':'')+'<h4>推理与核查</h4><ol>'+q.steps.map(s=>'<li>'+escape(s)+'</li>').join('')+'</ol>'+(q.rubric?'<fieldset class="practice-rubric"><legend>对照自己的过程逐项自评</legend>'+q.rubric.map((s,i)=>'<label><input type="checkbox" data-p-rubric value="'+i+'"'+(r.checks.includes(i)?' checked':'')+'>'+escape(s)+'</label>').join('')+'</fieldset>':'')+'<button class="secondary-button" data-p-redo>遮住解析再做（保留首答）</button><h4>换个条件再想</h4><p>'+escape(q.transfer)+'</p></section>';
  }
  function questionHtml(q){
    const r=record(q),choice=q.type==='single'||q.type==='multi';
    const input=choice?'<fieldset class="practice-options"><legend>'+(q.type==='multi'?'选择全部有依据的判断':'选择最有依据的一项')+'</legend>'+r.order.map(id=>{const o=q.options.find(x=>x.id===id);return '<label><input type="'+(q.type==='multi'?'checkbox':'radio')+'" name="p-answer" value="'+id+'"'+(r.selected.includes(id)?' checked':'')+'><span>'+escape(o.text)+'</span></label>';}).join('')+'</fieldset>':q.type==='numeric'?'<label class="practice-value">计算结果 / '+escape(q.unit)+'<input type="text" inputmode="decimal" data-p-value value="'+escape(r.value)+'" autocomplete="off" placeholder="只填数值，可用科学计数法"></label>':'';
    return '<article class="practice-question" data-question-id="'+q.id+'"><p class="page-meta">'+kinds[q.type]+' · '+q.skills.join(' / ')+'</p><h2 tabindex="-1" data-p-title>'+escape(q.title)+'</h2><p class="practice-prompt">'+escape(q.prompt)+'</p>'+input+'<label class="practice-reason">'+(q.type==='open'?'写下你的分析':'理由、推导或核查（建议填写）')+'<textarea data-p-reason rows="'+(q.type==='open'?5:3)+'">'+escape(r.reason)+'</textarea></label><label class="practice-confidence">作答把握<select data-p-confidence><option value="unsure"'+(r.confidence==='unsure'?' selected':'')+'>还不确定</option><option value="sure"'+(r.confidence==='sure'?' selected':'')+'>有把握并能解释</option></select></label><div class="practice-actions"><button class="resource-nav-button" data-p-favorite aria-pressed="'+Boolean(r.favorite)+'">'+(r.favorite?'已收藏':'收藏本题')+'</button><button class="resource-nav-button" data-p-mistake aria-pressed="'+Boolean(r.selfMistake)+'">'+(r.selfMistake?'已标记待复习':'标记不会')+'</button><button class="secondary-button" data-p-submit>'+(q.type==='open'?'保存并对照要点':'提交作答')+'</button><button class="resource-nav-button" data-p-hint>提示一步</button><button class="resource-nav-button" data-p-reveal>查看参考分析</button></div><p data-p-error role="alert"></p><p data-p-hint-text'+(r.hinted?'':' hidden')+'>'+escape(q.hint)+'</p><div data-p-feedback>'+feedback(q,r)+'</div><nav class="practice-reading" aria-label="回查讲解">'+q.sections.map(id=>{const c=courses.find(c=>c.id===q.course),s=c.sections.find(s=>s.id===id);return '<a href="#course/'+c.id+'/'+id+'">回查：'+escape(s.title)+'</a>';}).join('')+'</nav><p class="practice-origin">'+escape(q.origin)+'</p><div class="practice-pagination"><button class="secondary-button" data-p-prev>上一题</button><button class="secondary-button" data-p-next>下一题</button></div></article>';
  }
  function mount(root,initialCourse,initialSection,collection=''){
    let selected='',matches=[],section=initialSection;
    const panel=root.querySelector('[data-practice-panel]'),body=panel.querySelector('[data-p-body]'),picker=panel.querySelector('[data-p-question]');
    const storage=()=>{panel.querySelector('[data-p-storage]').textContent=persistent?'草稿与记录保存于当前浏览器，可随时离开后继续。':'浏览器存储不可用，本次记录仅保留到页面关闭。';};
    function summary(){
      const course=panel.querySelector('[data-p-course]').value,items=questions.filter(q=>q.course===course);
      panel.querySelector('[data-p-summary]').innerHTML='<ul>'+skills.map(skill=>{
        const all=items.filter(q=>q.skills.includes(skill)),attempted=all.filter(q=>record(q).attempts.length),first=attempted.filter(q=>record(q).attempts[0]?.correct===true&&!record(q).attempts[0].assisted),review=all.filter(q=>needsReview(q,record(q)));
        return '<li>'+skill+'：'+all.length+' 题；已提交 '+attempted.length+'；独立首答吻合 '+first.length+'；待回看 '+review.length+'</li>';
      }).join('')+'</ul><p>问答只记录作答与要点自评，不计入“首答吻合”。有把握却答错的题会在选题中标注。</p>';
    }
    const label=q=>{const r=record(q);return kinds[q.type]+' · '+q.title+(needsReview(q,r)?' · 待回看':'')+(r.attempts.some(a=>a.confidence==='sure'&&a.correct===false)?' · 自信误判':'');};
    function render(focus=false){
      const q=matches.find(q=>q.id===selected);picker.innerHTML=matches.map(q=>'<option value="'+q.id+'"'+(q.id===selected?' selected':'')+'>'+escape(label(q))+'</option>').join('');
      picker.disabled=!matches.length;body.innerHTML=q?questionHtml(q):'<p>这个范围没有匹配题目，可调整筛选。</p>';
      if(q){const i=matches.indexOf(q);body.querySelector('[data-p-prev]').disabled=i===0;body.querySelector('[data-p-next]').disabled=i===matches.length-1;if(focus)body.querySelector('[data-p-title]').focus({preventScroll:true});}
      summary();save();storage();
    }
    function filter(){
      const course=panel.querySelector('[data-p-course]').value,type=panel.querySelector('[data-p-type]').value,skill=panel.querySelector('[data-p-skill]').value,review=panel.querySelector('[data-p-review]').checked;
      let base=questions.filter(q=>q.course===course&&(!collection||(collection==='mistakes'?isMistake(record(q)):record(q).favorite))),exact=section?base.filter(q=>q.sections.includes(section)):[];
      const fallback=Boolean(section&&!exact.length);if(exact.length)base=exact;
      panel.querySelector('[data-p-scope]').textContent=(section?(fallback?'本节尚无专门编配题目，显示本课程练习':'本节关联练习'):'本课程练习')+' · '+base.length+' 题。当前题库不代表全章、全科覆盖。';
      matches=base.filter(q=>(!type||q.type===type)&&(!skill||q.skills.includes(skill))&&(!review||needsReview(q,record(q))));
      if(!matches.some(q=>q.id===selected))selected=matches[0]?.id||'';render();
    }
    panel.addEventListener('change',event=>{
      if(event.target.matches('[data-p-course]')){section=null;filter();return;}
      if(event.target.matches('[data-p-type],[data-p-skill],[data-p-review]')){filter();return;}
      if(event.target===picker){selected=picker.value;render(true);return;}
      draft(event);
    });
    function draft(event){
      const q=matches.find(q=>q.id===selected);if(!q)return;const r=record(q),t=event.target;
      if(t.matches('[name="p-answer"]'))r.selected=Array.from(body.querySelectorAll('[name="p-answer"]:checked'),e=>e.value);
      else if(t.matches('[data-p-value]'))r.value=t.value;
      else if(t.matches('[data-p-reason]'))r.reason=t.value;
      else if(t.matches('[data-p-confidence]'))r.confidence=t.value;
      else if(t.matches('[data-p-rubric]'))r.checks=Array.from(body.querySelectorAll('[data-p-rubric]:checked'),e=>Number(e.value));
      else return;
      if(!t.matches('[data-p-rubric]')){r.submitted=false;r.checks=[];body.querySelector('[data-p-feedback]').innerHTML=feedback(q,r);}
      summary();save();storage();
    }
    panel.addEventListener('input',draft);
    panel.addEventListener('click',event=>{
      const q=matches.find(q=>q.id===selected);if(!q)return;const r=record(q),target=event.target;
      if(target.closest('[data-p-submit]')){
        const value=evaluate(q,r),error=body.querySelector('[data-p-error]');
        if(q.type==='open'&&!r.reason.trim()){error.textContent='先写下你的分析，再对照参考要点。';return;}
        if(value===undefined){error.textContent=q.type==='numeric'?'请填写有限的纯数值；单位见输入框标签。':'请先选择答案。';return;}
        r.submitted=true;r.lastCorrect=value;r.attempts.push({correct:value,assisted:r.hinted||r.revealed||Boolean(r.feedbackSeen),confidence:r.confidence});r.feedbackSeen=true;if(r.attempts.length>100)r.attempts=[r.attempts[0],...r.attempts.slice(-99)];render();
      }else if(target.closest('[data-p-hint]')){r.hinted=true;const hint=body.querySelector('[data-p-hint-text]');hint.hidden=false;save();summary();}
      else if(target.closest('[data-p-reveal]')){r.revealed=true;render();}
      else if(target.closest('[data-p-redo]')){r.submitted=false;r.revealed=false;r.selected=[];r.value='';r.reason='';r.checks=[];render();}
      else if(target.closest('[data-p-favorite]')){r.favorite=!r.favorite;if(collection)filter();else render();}
      else if(target.closest('[data-p-mistake]')){r.selfMistake=!r.selfMistake;render();}
      else if(target.closest('[data-p-next],[data-p-prev]')){
        const index=matches.indexOf(q)+(target.closest('[data-p-next]')?1:-1);if(matches[index]){selected=matches[index].id;render(true);body.scrollIntoView({block:'start',behavior:'instant'});}
      }
    });
    filter();
  }
  const extItems=()=>{if(!Array.isArray(records.externalItems))records.externalItems=[];records.externalItems=records.externalItems.filter(i=>i&&typeof i.key==='string'&&typeof i.sourceId==='string'&&typeof i.ref==='string');return records.externalItems;};
  const courseOptions=course=>courses.map(c=>'<option value="'+c.id+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('');
  const sourceLinks=s=>s.links.map(l=>'<a href="'+escape(l.url)+'" target="_blank" rel="noopener noreferrer">'+escape(l.label)+'</a>').join(' · ');
  const knowledgeLinks=s=>s.targets.map(t=>{const c=courses.find(c=>c.id===t.course),section=c.sections.find(x=>x.id===t.section);return '<a href="#course/'+c.id+'/'+section.id+'">'+escape(c.title+' · '+section.title)+'</a>';}).join(' · ');
  function sourceHtml(s,open=false){
    return '<details class="source-practice resource-entry" data-source-id="'+s.id+'"'+(open?' open':'')+'><summary><strong>'+escape(s.title)+'</strong><span class="resource-verification">'+escape(s.evidenceLevel)+'</span><span class="resource-question">'+escape(s.focus)+'</span></summary><div class="resource-entry-body"><p>'+escape(s.selection)+'</p><p>'+sourceLinks(s)+'</p><h3>为什么选它</h3><p>'+escape(s.evidence)+'</p><h3>怎样作答与核查</h3><ol>'+s.guide.map(t=>'<li>'+escape(t)+'</li>').join('')+'</ol><p><strong>解答：</strong>'+escape(s.answers)+'</p><p><strong>适用范围：</strong>'+escape(s.limit)+'</p><p>'+knowledgeLinks(s)+'</p><details><summary>访问、许可与核查范围</summary><p>'+escape(s.access)+' '+escape(s.license)+'</p><p>核查 '+escape(s.checked)+'：'+escape(s.readScope)+'</p><p>'+s.evidenceLinks.map(l=>'<a href="'+escape(l.url)+'" target="_blank" rel="noopener noreferrer">'+escape(l.label)+'</a>').join(' · ')+'</p></details><div class="source-record"><h3>记录这一道题</h3><p>外部原站不向本站回传结果，请填具体题号或页面定位；一道题一条记录。</p><label>题号 / 定位<input data-source-ref placeholder="如：第 2 题或页面题目名"></label><label>自己的分析与错因<textarea data-source-note rows="3"></textarea></label><button class="secondary-button" data-source-save="mistake">收录错题</button> <button class="secondary-button" data-source-save="favorite">收藏再做</button><p data-source-status role="status"></p></div></div></details>';
  }
  function externalCollection(course,mode){
    const items=extItems().filter(item=>item[mode==='mistakes'?'mistake':'favorite']&&bank.sources.some(s=>s.id===item.sourceId&&s.targets.some(t=>t.course===course)));
    return '<h3>原站题目 · '+items.length+' 道</h3>'+items.map(item=>{const s=bank.sources.find(s=>s.id===item.sourceId);return '<section class="external-review" data-external-record="'+escape(item.key)+'"><h4>'+escape(s.title+' · '+item.ref)+'</h4><p>'+escape(item.note||'尚未记录分析')+'</p><p>'+sourceLinks(s)+'</p><p>'+knowledgeLinks(s)+'</p><p>状态：'+(item.reviewed?'已手动标记复习，原错题记录保留':'待复习')+'</p><button class="resource-nav-button" data-external-review>标记已复习</button><button class="resource-nav-button" data-external-favorite>'+ (item.favorite?'取消收藏':'收藏此题')+'</button></section>';}).join('');
  }
  function hubHtml(course){return '<section data-practice-hub><nav class="practice-modes" aria-label="练习与题集"><button data-practice-mode="sources" aria-pressed="true">精选来源</button><button data-practice-mode="local" aria-pressed="false">本站补充</button><button data-practice-mode="mistakes" aria-pressed="false">错题集</button><button data-practice-mode="favorites" aria-pressed="false">收藏集</button></nav><div data-practice-content></div></section>';}
  function mountHub(root,initialCourse,section){
    const hub=root.querySelector('[data-practice-hub]'),content=hub.querySelector('[data-practice-content]');let course=courses.some(c=>c.id===initialCourse)?initialCourse:courses[0].id,mode='sources';
    function render(){
      hub.querySelectorAll('[data-practice-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.practiceMode===mode)));
      if(mode==='local'){content.innerHTML='<p class="practice-note">本站原创补充，尚未经过学习者试测或测量学验证。已发表的来源题优先在“精选来源”练习。</p>'+shell(course,section);mount(content,course,section);return;}
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
        html+='<p class="practice-note">本站客观题答错后自动保留；问答与外部题可手动收录。重做不覆盖首答，收藏独立保存。记录限当前浏览器。</p>'+externalCollection(course,mode)+'<h3>本站补充 · '+native.length+' 道</h3>'+(native.length?shell(course):'<p>暂无本站题目。</p>');
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
  });
  dialog.addEventListener('click',event=>{if(event.target.closest('[data-close-practice]'))dialog.close();});
  dialog.addEventListener('close',()=>{document.body.classList.remove('practice-open');if(origin?.element?.isConnected){scrollTo({left:origin.x,top:origin.y,behavior:'instant'});origin.element.focus({preventScroll:true});}origin=null;});
  window.LNPractice={button,pageHtml:course=>'<h1>练习</h1>'+hubHtml(course),mount:mountHub,onRoute:()=>{origin=null;if(dialog.open)dialog.close();}};
})();
