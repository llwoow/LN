'use strict';
(() => {
  const key='ln.physics001.notes.v1';
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const ratings=['未自评','需要重学','大致理解','能独立解释'];
  let cleanup=()=>{},cachedNotes=null;
  function valid(v){return v&&Number.isInteger(v.rating)&&v.rating>=0&&v.rating<=3&&typeof v.note==='string'&&v.note.length<=50000&&typeof v.updatedAt==='string'&&Number.isFinite(Date.parse(v.updatedAt));}
  function read(){if(cachedNotes)return cachedNotes;try{const data=JSON.parse(localStorage.getItem(key)||'{}');return cachedNotes=Object.fromEntries(Object.entries(data).filter(([id,v])=>/^([1-9]|1[0-8])$/.test(id)&&valid(v)));}catch{return cachedNotes={};}}
  function mount(body,payload){
    cleanup();const abort=new AbortController(),signal=abort.signal;const videos=[...body.querySelectorAll('video')];
    const on=(node,event,fn)=>node?.addEventListener(event,fn,{signal});
    // Reading a visible worked solution is reference use, never an independent first attempt.
    if(payload.physics001)window.LNPractice.noteReferenceUse('hs-physics001-'+String(payload.physics001).padStart(2,'0'));
    for(const video of videos)on(video,'play',()=>videos.forEach(other=>{if(other!==video)other.pause();}));
    const stopGif=d=>{d.querySelector('img').removeAttribute('src');};
    body.querySelectorAll('[data-gif]').forEach(d=>{
      on(d,'toggle',()=>{if(d.open)d.querySelector('img').src=d.dataset.gif;else stopGif(d);});
      on(d.querySelector('[data-stop-gif]'),'click',()=>{stopGif(d);d.open=false;});
    });
    const notes=read();
    function save(status){try{localStorage.setItem(key,JSON.stringify(notes));status.textContent='已保存在当前浏览器。';}catch{status.textContent='浏览器存储不可用，请导出后保存。';}}
    const note=body.querySelector('[data-physics-note]');
    if(note){const id=note.dataset.physicsNote,r=notes[id]||{rating:0,note:''};
      note.innerHTML='<label>自己对本题的判断<select data-note-rating>'+ratings.map((t,i)=>'<option value="'+i+'"'+(r.rating===i?' selected':'')+'>'+t+'</option>').join('')+'</select></label><label>具体卡在哪一步<textarea rows="3" maxlength="50000" data-note-text>'+esc(r.note)+'</textarea></label><p data-note-status role="status">自评不是成绩；只保存在当前浏览器。</p>';
      const update=()=>{notes[id]={rating:Number(note.querySelector('select').value),note:note.querySelector('textarea').value,updatedAt:new Date().toISOString()};save(note.querySelector('[data-note-status]'));};
      on(note.querySelector('select'),'change',update);on(note.querySelector('textarea'),'input',update);
    }
    const notebook=body.querySelector('[data-physics-notebook]');
    if(notebook){notebook.innerHTML='<label>导入旧笔记 JSON<input type="file" accept="application/json,.json" data-notes-import></label><button class="secondary-button" data-notes-export>导出笔记</button><p data-notes-status role="status"></p><div data-notes-list></div>';
      const status=notebook.querySelector('[data-notes-status]');
      const list=()=>{notebook.querySelector('[data-notes-list]').innerHTML=Object.entries(notes).sort((a,b)=>Number(a[0])-Number(b[0])).map(([id,v])=>'<article><p><a href="#course/hs-physics/physics-001-q'+id.padStart(2,'0')+'">第'+id+'题</a> · '+ratings[v.rating]+'</p><p class="physics-note-content">'+esc(v.note||'未填写具体卡点。')+'</p></article>').join('')||'<p>尚无笔记，不能据此判断已掌握或没有薄弱点。</p>';};list();
      on(notebook.querySelector('[data-notes-import]'),'change',async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>2e6)throw Error('文件大于2 MB');const data=JSON.parse(await file.text());if(signal.aborted)return;if(data.assessment!=='physics-001'||!data.records||Array.isArray(data.records)||typeof data.records!=='object')throw Error('不是试卷001的笔记文件');let count=0,skipped=0;for(const [id,v] of Object.entries(data.records)){if(!/^([1-9]|1[0-8])$/.test(id)||!valid(v)){skipped++;continue;}if(!notes[id]||Date.parse(v.updatedAt)>Date.parse(notes[id].updatedAt)){notes[id]={rating:v.rating,note:v.note,updatedAt:v.updatedAt};count++;}}save(status);list();status.textContent='合并 '+count+' 题笔记，跳过 '+skipped+' 条无效记录。'+status.textContent;}catch(e){status.textContent='导入失败：'+e.message;}e.target.value='';});
      on(notebook.querySelector('[data-notes-export]'),'click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({assessment:'physics-001',contentVersion:'1.2-LN',recordType:'self-evaluation-not-exam-score',exportedAt:new Date().toISOString(),records:notes},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='physics001-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
    }
    body.querySelectorAll('[data-physics-lab]').forEach(lab=>{
      const id=Number(lab.dataset.physicsLab),config=window.PhysicsModels.controls[id];const values=Object.fromEntries(config.sliders.map(s=>[s[0],s[5]]));
      lab.innerHTML='<h3>'+esc(config.title)+'</h3><p>'+esc(config.hint)+'</p>'+config.sliders.map(s=>'<label>'+esc(s[1])+' <output data-lab-output="'+s[0]+'">'+s[5]+'</output> '+esc(s[6])+'<input type="range" data-lab-input="'+s[0]+'" min="'+s[2]+'" max="'+s[3]+'" step="'+s[4]+'" value="'+s[5]+'"></label>').join('')+'<div class="physics-lab-diagram"></div><p data-lab-phase aria-live="polite"></p><dl class="physics-metrics"></dl><p data-lab-caption></p>';
      function draw(){const z=window.PhysicsModels.model(id,values);lab.querySelector('.physics-lab-diagram').innerHTML=z.svg;lab.querySelector('[data-lab-phase]').textContent=z.phase;lab.querySelector('[data-lab-caption]').textContent=z.caption;lab.querySelector('dl').innerHTML=z.metrics.map(([k,v])=>'<div><dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd></div>').join('');}
      on(lab,'input',e=>{const input=e.target.closest('[data-lab-input]');if(!input)return;values[input.dataset.labInput]=Number(input.value);lab.querySelector('[data-lab-output="'+input.dataset.labInput+'"]').value=input.value;draw();});draw();
    });
    cleanup=()=>{abort.abort();videos.forEach(v=>{v.pause();v.removeAttribute('src');v.querySelectorAll('source').forEach(s=>s.removeAttribute('src'));v.load();});body.querySelectorAll('[data-gif]').forEach(stopGif);};
  }
  window.LNPhysics001={mount,onRoute:()=>{cleanup();cleanup=()=>{};}};
})();
