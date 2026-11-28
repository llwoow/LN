(function(){
"use strict";
const prefix="#course/electromagnetic-compatibility/",esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const key=version=>"ln.emc.chapter1."+version+".v1";
const fresh=()=>({answers:{},marks:{},submitted:false});
const grade=(q,a)=>{
 if(q.kind==="single"||q.kind==="tf")return a===q.answer?q.points:0;
 if(q.kind==="multi"){const v=Array.isArray(a)?[...new Set(a)]:[];return v.some(x=>!q.answer.includes(x))?0:q.points*v.length/q.answer.length;}
 if(q.kind==="calc")return q.fields.reduce((s,f,i)=>{const v=String(a?.[i]??"").trim();return s+(v!==""&&Number.isFinite(Number(v))&&Math.abs(Number(v)-f.value)<=.05?q.points/q.fields.length:0);},0);
 return 0;
};
const bounded=(v,max)=>Math.min(max,Math.max(0,Number(v)||0));
function totals(qs,state){let auto=0,manual=0,autoMax=0;for(const q of qs){if(q.kind==="essay"||q.kind==="advanced"){const rub=q.sub||q.rubric;rub.forEach((r,i)=>manual+=bounded(state.marks[q.id+"-"+i],r.points));}else{autoMax+=q.points;auto+=grade(q,state.answers[q.id]);}}return {auto,manual,autoMax,total:auto+manual};}
const answered=(q,a)=>q.kind==="advanced"?q.sub.every((_,i)=>String(a?.[i]??"").trim()):q.kind==="calc"?q.fields.every((_,i)=>String(a?.[i]??"").trim()):q.kind==="multi"?Array.isArray(a)&&a.length>0:q.kind==="essay"?!!String(a??"").trim():Number.isInteger(a);

const roundId=()=>globalThis.crypto?.randomUUID?.()||Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
const getState=(version,onlyId)=>{try{const s=JSON.parse(localStorage.getItem(key(version)+(onlyId?'.redo.'+onlyId:''))||'null');return s&&s.answers&&s.marks?s:null;}catch{return null;}};
const hasAnswer=(q,a)=>q.kind==='multi'?Array.isArray(a)&&a.length>0:q.kind==='calc'||q.kind==='advanced'?Array.isArray(a)&&a.some(v=>String(v??'').trim()):q.kind==='essay'?!!String(a??'').trim():Number.isInteger(a);
function resultRows(qs,s,redo=false){
 return qs.filter(q=>hasAnswer(q,s.answers[q.id])).map(q=>{
  const rub=q.sub||q.rubric,marks=Object.fromEntries((rub||[]).map((_,i)=>[i,s.marks[q.id+'-'+i]]).filter(([,v])=>v!==undefined));
  const assessed=rub&&rub.every((_,i)=>Object.hasOwn(marks,i)&&Number.isFinite(Number(marks[i]))&&marks[i]!==null&&marks[i]!=="");
  return {id:q.id,answer:s.answers[q.id],draft:s.answers[q.id+'-draft']||'',marks,max:q.points,score:rub?(assessed?rub.reduce((v,r,i)=>v+bounded(marks[i],r.points),0):null):grade(q,s.answers[q.id]),evidence:rub?(assessed?'self':'pending'):'auto',redo,incomplete:!answered(q,s.answers[q.id])};
 });
}
function sync(version,qs,s,onlyId){
 if(!s.submitted)return true;
 if(!s.round)s.round=onlyId?'legacy-redo-'+version+'-'+onlyId:'legacy-'+version;
 return window.LNPractice?.importPaperRound(version,s.round,resultRows(qs,s,!!onlyId))??false;
}
function syncAll(){for(const version of ['A','B2']){const s=getState(version);if(s?.submitted)sync(version,window.LN_EMC_TESTS[version],s);}}
function answerText(q,a){
 if(q.options)return [].concat(a??[]).filter(i=>q.options[i]!==undefined).map(i=>String.fromCharCode(65+i)+'. '+q.options[i]).join('；')||'未答';
 if(q.fields)return q.fields.map((f,i)=>f.label+'：'+(a?.[i]??'未答')+' '+f.unit).join('；');
 if(q.sub)return q.sub.map((_,i)=>'第'+(i+1)+'问：'+(a?.[i]||'未答')).join('\n');
 return String(a||'未答');
}
function printQuestion(q,version,mode,attempt){
 const show=mode!=='exam';let s='<section class="ln-print-question"><h3>'+esc(version+' · '+q.id+' '+(q.title||''))+' <small>('+q.points+' 分)</small></h3><div>'+q.stem+'</div>'+(q.diagram||'');
 if(q.options)s+='<ol type="A">'+q.options.map(o=>'<li>'+o+'</li>').join('')+'</ol>';
 if(q.fields)s+=q.fields.map(f=>'<p>'+esc(f.label)+'：________ '+esc(f.unit)+'</p>').join('');
 if(q.sub)s+=q.sub.map(p=>'<p>'+esc(p.prompt)+'</p>'+(show?'':'<div class="ln-answer-space"></div>')).join('');
 if(!show&&!q.options&&!q.sub)s+='<div class="ln-answer-space"></div>';
 if(show){
   if(mode==='graded')s+='<h4>个人作答</h4><div class="ln-print-personal">'+esc(answerText(q,attempt?.answer))+'</div>'+(attempt?.draft?'<p class="ln-print-personal">'+esc(attempt.draft)+'</p>':'')+'<p>'+esc(attempt?.evidence==='pending'?'待自评':attempt?.score!=null?attempt.score+'/'+q.points+(attempt.evidence==='self'?'（自评）':'（自动核对）'):'未评分')+'</p>';
   s+='<h4>参考答案与评分</h4>';
   if(q.options)s+='<p>'+esc(answerText(q,q.answer))+'</p>';
   if(q.fields)s+='<p>'+esc(q.fields.map(f=>f.value.toFixed(2)+' '+f.unit).join('；'))+'</p>';
   if(q.explanation)s+='<p>'+q.explanation+'</p>';if(q.reference)s+='<p>'+q.reference+'</p>';
   if(q.sub||q.rubric)s+='<ol>'+(q.sub||q.rubric).map((r,i)=>'<li>'+ (q.sub?esc(r.answer):r.text)+'（'+r.points+' 分）'+(mode==='graded'&&attempt?.marks?.[i]!==undefined?' · 自评 '+esc(attempt.marks[i])+' 分':'')+'</li>').join('')+'</ol>';
 }
 return s+'</section>';
}
function printPaper(version,mode,onlyId){
 const qs=window.LN_EMC_TESTS[version].filter(q=>!onlyId||q.id===onlyId),s=getState(version,onlyId);
 if(mode==='graded'&&!s?.submitted)throw Error('请先交卷，再导出个人答卷与评分。');
 const label='第一章 · '+version+'卷',header='<h1>'+label+'</h1><p>'+qs.length+' 题 · '+qs.reduce((n,q)=>n+q.points,0)+' 分'+(onlyId?'':' · 建议 '+(version==='A'?60:120)+' 分钟')+'</p>';
 const attempts=mode==='graded'?resultRows(qs,s,!!onlyId):[];
 const list=m=>qs.map(q=>printQuestion(q,version,m,attempts.find(a=>a.id===q.id))).join('');
 return header+(mode==='combined'?'<h2>试题</h2>'+list('exam')+'<h2 class="ln-print-new-page">参考答案与评分细则</h2>'+list('answer'):list(mode));
}

function mount(root,version,onlyId){
 const qs=window.LN_EMC_TESTS[version].filter(q=>!onlyId||q.id===onlyId), advanced=version==="B2",max=qs.reduce((n,q)=>n+q.points,0),storeKey=key(version)+(onlyId?'.redo.'+onlyId:'');if(!qs.length){root.textContent='此题不存在。';return;}let state=fresh();let storage=true;
 try{const v=JSON.parse(localStorage.getItem(storeKey)||"null");if(v&&v.answers&&v.marks&&typeof v.submitted==="boolean")state=v;}catch(_){storage=false;}
 const save=()=>{try{localStorage.setItem(storeKey,JSON.stringify(state));}catch(_){storage=false;}};
 if(state.submitted){sync(version,qs,state,onlyId);save();}
 const persistRound=()=>{const ok=sync(version,qs,state,onlyId);save();if(!ok)storage=false;};
 const pct=v=>Number(v.toFixed(2)).toString();
 const status=q=>{if(!state.submitted)return answered(q,state.answers[q.id])?"已答":"未答";if(q.kind==="essay"||q.kind==="advanced"){const rub=q.sub||q.rubric;if(!rub.every((_,i)=>Object.hasOwn(state.marks,q.id+"-"+i)))return "待自评";return rub.reduce((s,r,i)=>s+bounded(state.marks[q.id+"-"+i],r.points),0)===q.points?"自评满分":"待复习";}return grade(q,state.answers[q.id])===q.points?"正确":"待复习";};
 const input=(q,i,v,kind="text")=>'<input aria-label="'+q.id+' 第'+(i+1)+'项" type="'+kind+'" data-q="'+q.id+'" data-i="'+i+'" value="'+esc(v)+'" '+(state.submitted?"disabled":"")+' >';
 const textarea=(q,i,v)=>'<textarea aria-label="'+q.id+' 第'+(i+1)+'问作答" data-q="'+q.id+'" data-i="'+i+'" rows="5" '+(state.submitted?"disabled":"")+'>'+esc(v)+'</textarea>';
 const feedback=q=>{if(!state.submitted)return "";let out='<div class="emc-test-feedback"><h4>答案与评分</h4>';
 if(q.kind==="advanced"||q.kind==="essay"){
  if(q.reference)out+='<p>'+q.reference+'</p>';
  (q.sub||q.rubric).forEach((r,i)=>out+='<div class="emc-test-rubric"><p>'+(q.sub?esc(r.answer):r.text)+' </p><label>本项自评（满分 '+r.points+'） <input type="number" min="0" max="'+r.points+'" step="0.25" data-mark="'+q.id+"-"+i+'" value="'+(Object.hasOwn(state.marks,q.id+"-"+i)?bounded(state.marks[q.id+"-"+i],r.points):"")+'"></label></div>');
 }else{
  const a=q.kind==="calc"?q.fields.map(f=>f.value.toFixed(2)+" "+f.unit).join(" / "):[].concat(q.answer).map(i=>String.fromCharCode(65+i)+" "+q.options[i]).join("；");
  out+='<p>得分 '+pct(grade(q,state.answers[q.id]))+' / '+q.points+'；正确答案：'+esc(a)+'</p><p>'+q.explanation+'</p>';
  if(q.kind==="calc")out+='<p>自动评分只核对数值（绝对容差0.05），不判定推导步骤分；原卷步骤分需人工核对。</p>';
 }
 return out+'<p><button type="button" data-paper-mark="mistake" data-paper-q="'+q.id+'">标记错题</button> <button type="button" data-paper-mark="favorite" data-paper-q="'+q.id+'">切换收藏</button> <span data-paper-notice="'+q.id+'"></span></p><p><a href="'+prefix+q.lesson+'">回查对应知识点</a> · <a href="'+prefix+'exam-review/chapter-1">第一章重点难点</a></p></div>';};
 const renderQ=q=>{let a=state.answers[q.id],s='<section class="emc-test-question" id="emc-test-'+q.id+'"><h3>'+q.id+(q.title?" "+esc(q.title):"")+' <small>'+q.points+' 分</small></h3><div>'+q.stem+'</div>'+(q.diagram||"");
 if(q.options)s+=q.options.map((o,i)=>'<label class="emc-test-option"><input type="'+(q.kind==="multi"?"checkbox":"radio")+'" name="'+q.id+'" data-q="'+q.id+'" data-choice="'+i+'" '+((q.kind==="multi"?Array.isArray(a)&&a.includes(i):a===i)?"checked":"")+' '+(state.submitted?"disabled":"")+'><span>'+String.fromCharCode(65+i)+'. '+o+'</span></label>').join("");
 else if(q.kind==="calc")s+=q.fields.map((f,i)=>'<label class="emc-test-field">'+esc(f.label)+' '+input(q,i,a?.[i]??"")+' '+esc(f.unit)+'</label>').join("")+'<label>推导草稿（不参与自动评分）'+textarea(q,99,state.answers[q.id+"-draft"]||"")+'</label>';
 else if(q.kind==="advanced")s+=q.sub.map((p,i)=>'<p>'+esc(p.prompt)+'</p>'+textarea(q,i,a?.[i]??"")).join("");
 else s+=textarea(q,0,a||"");
 return s+feedback(q)+'</section>';};
 const progress=()=>{const t=totals(qs,state),n=qs.filter(q=>answered(q,state.answers[q.id])).length;
 root.querySelector("[data-test-status]").textContent=state.submitted?"自动核对 "+pct(t.auto)+"/"+t.autoMax+"；主观自评 "+pct(t.manual)+"/"+(max-t.autoMax)+"；合计 "+pct(t.total)+"/"+max+"（非教师评分）"+(storage?"":"；本地记录或同步未确认，请勿清空原答卷"):"已答 "+n+" / "+qs.length+" 题"+(storage?"":"；浏览器存储不可用");
 for(const b of root.querySelectorAll("[data-jump]"))b.textContent=b.dataset.jump.slice(1)+" "+status(qs.find(q=>q.id===b.dataset.jump));
 const next=root.querySelector('[data-action="review"]');if(next)next.disabled=!qs.some(q=>status(q)==="待复习"||status(q)==="待自评");
 };
 const draw=()=>{root.innerHTML='<h2>第一章 · '+(onlyId?'单题重做 · '+onlyId+' · ':'')+(advanced?'B2 进阶闭卷测试':'A卷基础全面测试')+'</h2><p><a href="'+prefix+'exam-review/chapter-1">返回第一章复习</a> · <a href="'+prefix+'exam-review/test-'+(advanced?'a':'b2')+'">切换'+(advanced?'A卷':'B2卷')+'</a> · <a href="#practice/electromagnetic-compatibility/mistakes">统一错题集</a></p><p>'+max+'分 · '+qs.length+'题 · '+(onlyId?'保留原题评分，重做不覆盖首答。':'建议 '+(advanced?120:60)+' 分钟。')+''+(advanced?'闭卷，可使用普通计算器。无需查教材或PPT；写出推导、单位及判断依据。lg以10为底。':'单选每题2分；多选每题4分，无错选按正确选项比例给分，错选0分；判断每题2分；计算每小问2分；简答按评分点。')+'</p><p>作答只保存在本浏览器。答案交卷后显示；本地闭卷模式不等于防作弊考试。'+(advanced?'所有题目由本人按原细则自评。':'客观题自动核对，主观题自评。')+'</p><div class="emc-test-toolbar"><strong data-test-status aria-live="polite"></strong><div class="emc-test-nav">'+qs.map(q=>'<button type="button" data-jump="'+q.id+'">'+q.id+'</button>').join("")+'</div><button type="button" data-action="submit" '+(state.submitted?'hidden':'')+'>交卷并查看答案</button> <button type="button" data-action="reset">清空本卷重做</button> '+(state.submitted?'<button type="button" data-action="review">定位待复习题</button>':'')+'</div>'+qs.map(renderQ).join("")+(state.submitted?'<p>参考：第一章历史A卷及B2原创训练；《电磁兼容原理及应用》及课程PPT。<a href="https://github.com/llwoow/LN/blob/main/courses/electromagnetic-compatibility/CHAPTER1-TEST-AUDIT.md" target="_blank" rel="noopener noreferrer">B2命题依据与覆盖审查</a></p>':'');progress();};
 root.addEventListener("input",e=>{const t=e.target;if(t.dataset.mark&&state.submitted){const [id,i]=t.dataset.mark.split("-"),q=qs.find(q=>q.id===id);if(t.value.trim()==='')delete state.marks[t.dataset.mark];else state.marks[t.dataset.mark]=bounded(t.value,(q.sub||q.rubric)[i].points);persistRound();progress();return;}if(state.submitted||!t.dataset.q||t.dataset.choice!==undefined)return;const q=qs.find(q=>q.id===t.dataset.q),i=Number(t.dataset.i);if(i===99)state.answers[q.id+"-draft"]=t.value;else if(q.kind==="essay")state.answers[q.id]=t.value;else{const a=Array.isArray(state.answers[q.id])?state.answers[q.id]:[];a[i]=t.value;state.answers[q.id]=a;}save();progress();});
 root.addEventListener("change",e=>{const t=e.target;if(state.submitted||t.dataset.choice===undefined)return;const q=qs.find(q=>q.id===t.dataset.q),i=+t.dataset.choice;if(q.kind==="multi"){const v=new Set(state.answers[q.id]||[]);t.checked?v.add(i):v.delete(i);state.answers[q.id]=[...v];}else state.answers[q.id]=i;save();progress();});
 root.addEventListener("click",e=>{const t=e.target.closest("button");if(!t)return;if(t.dataset.paperMark){const ok=window.LNPractice?.markPaper(version,t.dataset.paperQ,t.dataset.paperMark);const notice=root.querySelector('[data-paper-notice="'+t.dataset.paperQ+'"]');if(notice)notice.textContent=ok?'已更新统一题库':'保存失败';return;}if(t.dataset.jump){root.querySelector("#emc-test-"+t.dataset.jump)?.scrollIntoView({block:"start"});return;}if(t.dataset.action==="review"&&state.submitted){const q=qs.find(q=>status(q)==="待复习"||status(q)==="待自评");if(q)root.querySelector("#emc-test-"+q.id)?.scrollIntoView({block:"start"});return;}if(t.dataset.action==="submit"&&!state.submitted){const n=qs.filter(q=>!answered(q,state.answers[q.id])).length;if(!confirm((n?"尚有 "+n+" 题未完整作答。":"")+"交卷后不能修改本次答案，确认交卷？"))return;state.submitted=true;state.round=roundId();persistRound();draw();root.scrollIntoView({block:"start"});}if(t.dataset.action==="reset"&&confirm("清除本卷作答与评分，确定重做？")){if(state.submitted){persistRound();if(!storage){alert("统一记录尚未确认保存，已保留原答卷。");return;}}state=fresh();save();draw();root.scrollIntoView({block:"start"});}});
 draw();
}
window.LNEmcChapterTest={mount,grade,totals,answered,answerText,printPaper,printQuestion,syncAll,resultRows};
})();