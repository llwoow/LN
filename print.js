(function(){
'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const site=new URL('.',location.href).href,courseList=window.LN_COURSES.filter(c=>!c.outlineOnly),paperRe=/^test-(a|b2)(?:-(Q\d{2}))?$/;
let serial=0,active=null;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function route(){const [view,id,section,anchor]=location.hash.slice(1).split('/');return {view,id,section,anchor};}
function readable(c){return c.sections.filter(s=>s.src&&s.kind!=='outline');}
function styles(doc){return [...doc.querySelectorAll('link[rel="stylesheet"]')].map(n=>n.href).filter(x=>x.startsWith(site));}
function cloneContent(source,{figures=true}={}){
 const copy=source.cloneNode(true),prefix='lnp'+(++serial)+'-',ids=new Map();
 const oldCanvases=[...source.querySelectorAll('canvas')],newCanvases=[...copy.querySelectorAll('canvas')];
 newCanvases.forEach((c,i)=>{const note=copy.ownerDocument.createElement('p');note.textContent='交互画布未能取得静态图，请回原网页查看。';try{const src=oldCanvases[i];if(!src.width||!src.height)throw Error();const img=copy.ownerDocument.createElement('img');img.src=src.toDataURL('image/png');img.alt='模型当前画面（静态快照）';c.replaceWith(img);}catch{c.replaceWith(note);}});
 copy.querySelectorAll('details').forEach(d=>d.open=true);
 const sourceInputs=[...source.querySelectorAll('input,textarea,select')],clonedInputs=[...copy.querySelectorAll('input,textarea,select')];
 // Canvas replacements may not change control order. Only show parameters in scientific labs, never arbitrary drafts in a lecture.
 clonedInputs.forEach((el,i)=>{
   const actual=sourceInputs[i],lab=el.closest('[data-emc-lab],[data-rd-lab],[data-dc-winding-lab],[data-dc-reaction-lab],[data-mmf-lab],[data-induction-lab],.emc-lab-ui,.control-lab,.lab-controls');
   if(lab&&actual){const t=copy.ownerDocument.createElement('span');t.className='ln-print-param';t.textContent=actual.tagName==='SELECT'?(actual.selectedOptions[0]?.textContent||actual.value):actual.type==='checkbox'||actual.type==='radio'?(actual.checked?'是':'否'):actual.value;el.replaceWith(t);}
   else el.remove();
 });
 copy.querySelectorAll('button,script,iframe,audio,video,dialog,.lesson-tools,.lesson-pagination,.reference-return,.definition-popover,.definition-formula-tool,.practice-controls,.practice-actions,.practice-navigation,.emc-test-toolbar,[data-open-practice],.resource-dialog,.lesson-source-tool,.bookmark-button').forEach(n=>{if(n.matches('button.definition-symbol')){n.replaceWith(...n.childNodes);}else if(n.matches('video,iframe')){const p=copy.ownerDocument.createElement('p');p.textContent='动态媒体：请回原网页观看。';n.replaceWith(p);}else n.remove();});
 copy.querySelectorAll('img').forEach(img=>{img.loading='eager';if(img.getAttribute('src'))img.src=new URL(img.getAttribute('src'),source.ownerDocument.baseURI).href;});
 if(!figures)copy.querySelectorAll('figure,svg,canvas,img').forEach(n=>{if(!n.closest('.katex'))n.remove();});
 // Isolate figure/marker/equation identifiers across independently authored sections.
 copy.querySelectorAll('[id]').forEach(n=>{const id=n.id;ids.set(id,prefix+id);n.id=prefix+id;});
 copy.querySelectorAll('*').forEach(n=>{for(const a of [...n.attributes]){
   let v=a.value;
   if(['href','xlink:href'].includes(a.name)&&v.startsWith('#')&&ids.has(v.slice(1)))v='#'+ids.get(v.slice(1));
   else if(n.tagName.toLowerCase()==='a'&&a.name==='href'&&!v.startsWith('#lnp')){try{v=new URL(v,source.ownerDocument.URL).href;}catch{}}
   v=v.replace(/url\(#([^)]+)\)/g,(m,id)=>ids.has(id)?'url(#'+ids.get(id)+')':m);
   if(['aria-labelledby','aria-describedby','for'].includes(a.name))v=v.split(/\s+/).map(id=>ids.get(id)||id).join(' ');
   if(a.name.startsWith('on'))n.removeAttribute(a.name);else if(v!==a.value)n.setAttribute(a.name,v);
 }});
 return copy.outerHTML;
}
async function awaitReady(frame,section,token){
 const expected=section.course+'/'+section.id;
 for(let i=0;i<400;i++){
   if(token.cancelled)throw Error('已取消');
   const doc=frame.contentDocument,body=doc?.querySelector('#lesson-body');
   if(body?.dataset.lessonKey===expected&&body.dataset.printReady==='yes'){
     await Promise.race([doc.fonts?.ready||Promise.resolve(),sleep(2500)]);await sleep(180);return body;
   }
   if(body?.dataset.lessonKey===expected&&body.querySelector('[data-retry-lesson]'))throw Error('章节加载失败：'+section.title);
   await sleep(75);
 }
 throw Error('章节加载超时：'+section.title);
}
async function build(settings,token,status){
 const css=new Set([...styles(document),site+'assets/katex/katex.min.css',site+'courses/electromagnetic-compatibility/chapter1-tests.css',site+'print.css']);
 let title='',body='';
 if(settings.type==='paper'){
   title='电磁兼容 · '+settings.version+'卷';
   body=window.LNEmcChapterTest.printPaper(settings.version,settings.mode,settings.onlyId);
 }else if(settings.type==='nativeExam'){
   title='章节测试';
   const gen=document.querySelector('[data-exam-content]')?.lnPrintExam;if(!gen)throw Error('当前测试未加载。');
   body=gen(settings.mode);
 }else if(settings.type==='mistakes'){
   title='LN 错题集';body='<h1>'+title+'</h1>'+window.LNPractice.printMistakes(settings.course,settings.mode!=='exam');
 }else if(settings.type==='current'){
   title=document.title.replace(/ · LN$/,'');
   const source=document.querySelector('#lesson-body,#emc-review-content')||document.querySelector('main');
   if(!source||source.getAttribute('aria-busy')==='true'||source.querySelector('[data-retry-lesson]'))throw Error('正文未加载完成。');
   if(source.querySelector('[data-exam-content],.practice-exam-working,.emc-test-question'))throw Error('请使用试卷导出模式。');
   body='<h1>'+esc(title)+'</h1>'+cloneContent(source,settings);
 }else{
   const c=courseList.find(c=>c.id===settings.course),selected=readable(c).filter(s=>settings.sections.includes(s.id));
   if(!selected.length)throw Error('请选择至少一个有正文的小节。');
   title=c.title+(selected.length===1?' · '+selected[0].title:' · 课程讲义');
   body='<h1>'+esc(title)+'</h1>';
   if(settings.toc)body+='<nav class="ln-print-toc"><h2>目录</h2><ol>'+selected.map((s,i)=>'<li><a href="#ln-print-section-'+i+'">'+esc(s.title)+'</a></li>').join('')+'</ol></nav>';
   const frame=document.createElement('iframe');frame.name='LN_PRINT_SOURCE';frame.className='ln-print-source';frame.setAttribute('aria-hidden','true');frame.tabIndex=-1;
   document.body.append(frame);token.source=frame;
   try{
     for(const [i,s] of selected.entries()){
       status('加载 '+(i+1)+' / '+selected.length+'：'+s.title);
       const url=site+'#course/'+c.id+'/'+s.id;
       if(i===0)frame.src=url;else frame.contentWindow.location.hash='#course/'+c.id+'/'+s.id;
       const source=await awaitReady(frame,{...s,course:c.id},token);
       styles(source.ownerDocument).forEach(x=>css.add(x));
       body+='<section id="ln-print-section-'+i+'" class="ln-print-unit"><h2>'+esc(s.title)+'</h2>'+cloneContent(source,settings)+'</section>';
     }
   }finally{frame.remove();token.source=null;}
 }
 if(token.cancelled)throw Error('已取消');
 return {title,body,css:[...css],paper:settings.paper};
}
async function writePreview(frame,doc){
 const d=frame.contentDocument;
 d.open();d.write('<!doctype html><html lang="zh-CN" data-theme="light" data-palette="default"><head><meta charset="utf-8"><base href="'+esc(site)+'"><title>'+esc(doc.title)+'</title>'+doc.css.map(x=>'<link rel="stylesheet" href="'+esc(x)+'">').join('')+'<style>@page{size:'+ (doc.paper==='A5'?'A5':'A4')+';margin:16mm 14mm 18mm} </style></head><body class="ln-print-document"><main class="ln-print-main lesson publication-body">'+doc.body+'</main></body></html>');d.close();
 await Promise.race([Promise.all([...d.querySelectorAll('link[rel=stylesheet]')].map(l=>l.sheet?Promise.resolve():new Promise(r=>{l.onload=r;l.onerror=r;}))),sleep(5000)]);
 await Promise.race([d.fonts?.ready||Promise.resolve(),sleep(3000)]);
 await Promise.race([Promise.all([...d.images].map(img=>img.decode?.().catch(()=>{})||Promise.resolve())),sleep(5000)]);
 const failed=[...d.images].filter(img=>!img.complete||!img.naturalWidth).length;
 return failed;
}
function open(){
 if(active)return;
 const r=route(),course=courseList.find(c=>c.id===r.id),paper=r.view==='course'&&r.section==='exam-review'?paperRe.exec(r.anchor||''):null,native=!!document.querySelector('[data-exam-content]');
 const dlg=document.createElement('dialog');dlg.className='ln-print-dialog';dlg.setAttribute('aria-label','打印与 PDF 导出');
 dlg.innerHTML='<div class="ln-print-head"><h2>打印与 PDF 导出</h2><button type="button" data-close>关闭</button></div><div class="ln-print-options"><label>内容<select data-type><option value="current">当前阅读页（静态快照）</option><option value="sections">自选课程章节</option><option value="paper">A / B2 标准试卷</option>'+(native?'<option value="nativeExam">当前章节测试（完整试卷）</option>':'')+'<option value="mistakes">统一错题集</option></select></label><label data-course-wrap>课程<select data-course>'+courseList.map(c=>'<option value="'+esc(c.id)+'" '+(c===course?'selected':'')+'>'+esc(c.title)+'</option>').join('')+'</select></label><label data-scope-wrap>范围<select data-scope><option value="group">当前章 / 首章</option><option value="custom">自选小节</option><option value="all">全课程正文</option></select></label><div data-sections></div><label data-version-wrap>试卷<select data-version><option>A</option><option>B2</option></select></label><label data-mode-wrap>版本<select data-mode><option value="exam">试题版（无答案）</option><option value="answer">答案详解版</option><option value="combined">试题与答案合订</option><option value="graded">个人答卷及批改</option></select></label><label>纸张<select data-paper><option>A4</option><option>A5</option></select></label><label><input type="checkbox" data-fig checked>保留图表</label><label><input type="checkbox" data-toc checked>目录</label></div><div class="ln-print-head"><button type="button" data-build>生成预览</button><button type="button" data-print disabled>打印 / 另存为 PDF</button><span data-status role="status"></span></div><iframe title="PDF 排版预览" data-preview></iframe>';
 document.body.append(dlg);active=dlg;dlg.showModal();
 const $=s=>dlg.querySelector(s),type=$('[data-type]'),cs=$('[data-course]'),scope=$('[data-scope]'),list=$('[data-sections]'),version=$('[data-version]'),mode=$('[data-mode]'),frame=$('[data-preview]');
 let token=null,ready=false;
 type.value=paper?'paper':native?'nativeExam':r.view==='practice'&&document.querySelector('[data-practice-mode="mistakes"][aria-pressed="true"]')?'mistakes':course&&r.section&&course.sections.some(s=>s.id===r.section)?'sections':'current';
 if(paper)version.value=paper[1]==='a'?'A':'B2';
 function updateList(){
   const c=courseList.find(c=>c.id===cs.value);if(!c)return;
   const ss=readable(c),group=(c===course&&c.sections.find(s=>s.id===r.section)?.group)||ss[0]?.group;
   list.innerHTML=ss.map(s=>'<label><input type="checkbox" value="'+esc(s.id)+'" '+((scope.value==='all'||s.group===group)?'checked':'')+' '+(scope.value==='custom'?'':'disabled')+'>'+esc(s.title)+'</label>').join('');
   list.hidden=type.value!=='sections';
 }
 function update(){
   const t=type.value;$('[data-fig]').disabled=['paper','nativeExam','mistakes'].includes(t);if($('[data-fig]').disabled)$('[data-fig]').checked=true;$('[data-course-wrap]').hidden=t!=='sections'&&t!=='mistakes';$('[data-scope-wrap]').hidden=t!=='sections';$('[data-version-wrap]').hidden=t!=='paper';$('[data-mode-wrap]').hidden=!['paper','nativeExam','mistakes'].includes(t);
   mode.innerHTML=t==='mistakes'?'<option value="exam">错题重做版（无答案）</option><option value="graded">错题与个人记录、解析</option>':'<option value="exam">试题版（无答案）</option><option value="answer">答案详解版</option><option value="combined">试题与答案合订</option><option value="graded">个人答卷及批改</option>';
   let all=cs.querySelector('option[value=""]');if(t==='mistakes'&&!all){all=document.createElement('option');all.value='';all.textContent='全部课程';cs.prepend(all);cs.value='';}else if(t!=='mistakes'&&all){all.remove();if(!cs.value)cs.value=course?.id||courseList[0].id;}
   updateList();
 }
 const status=s=>$('[data-status]').textContent=s;
 function cancel(){if(token){token.cancelled=true;token.source?.remove();}}
 dlg.addEventListener('close',()=>{cancel();dlg.remove();active=null;});$('[data-close]').onclick=()=>dlg.close();
 dlg.addEventListener('change',()=>{ready=false;$('[data-print]').disabled=true;});
 type.onchange=update;cs.onchange=updateList;scope.onchange=updateList;update();
 $('[data-build]').onclick=async()=>{
   cancel();const t=token={cancelled:false};ready=false;$('[data-print]').disabled=true;$('[data-build]').disabled=true;
   try{
     const settings={type:type.value,course:cs.value,sections:[...list.querySelectorAll('input:checked')].map(i=>i.value),version:version.value,onlyId:paper&&version.value===(paper[1]==='a'?'A':'B2')?paper[2]:undefined,mode:mode.value,paper:$('[data-paper]').value,figures:$('[data-fig]').checked,toc:$('[data-toc]').checked};
     status('生成中…');const out=await build(settings,t,status);if(t.cancelled)return;
     const failed=await writePreview(frame,out);if(t.cancelled)return;
     ready=true;$('[data-print]').disabled=false;status(failed?'预览已生成；'+failed+' 张图未加载，请检查后再打印。':'预览已生成。请检查分页后打印。');
   }catch(e){if(!t.cancelled)status(e.message||'生成失败');}finally{if(!t.cancelled)$('[data-build]').disabled=false;}
 };
 $('[data-print]').onclick=()=>{if(ready){frame.contentWindow.focus();frame.contentWindow.print();}};
}
document.getElementById('ln-print-open')?.addEventListener('click',open);
window.LNPrint={open,build,writePreview,cloneContent};
})();