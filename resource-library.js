'use strict';
(() => {
  const data=window.LN_RESOURCE_CATALOG;
  const resources=data.resources, courses=window.LN_COURSES.filter(c=>!c.outlineOnly);
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const courseById=id=>courses.find(c=>c.id===id);
  const applies=(resource,course,section)=>resource.targets.some(t=>t.course===course&&(!section||t.section===section));
  const external=entry=>'<a href="'+escape(entry.url)+'" target="_blank" rel="noopener noreferrer">'+escape(entry.label)+'</a>';
  const downloads=resource=>resource.downloads.map(d=>'<a href="'+escape(d.path)+'"'+(d.view?' target="_blank" rel="noopener"':' download')+'>'+escape(d.label)+'</a>').join(' · ');
  const targetLink=target=>{
    const course=courseById(target.course),section=course.sections.find(s=>s.id===target.section);
    return '<a href="#course/'+course.id+'/'+section.id+'">'+escape(course.title+' · '+section.title)+'</a>';
  };
  function entryHtml(resource,open=false) {
    const verification=resource.verification;
    const siteOnly=resource.localLesson&&!resource.links.length;
    const status=siteOnly?'站内算例':verification.executed?'已复算部分任务':'已读资料，未运行';
    const externalLinks=resource.links.length?'<div class="resource-links-inline">'+resource.links.map(external).join(' · ')+'</div>':'';
    const localLesson=resource.localLesson?'<p><a href="'+escape(resource.localLesson)+'">'+(siteOnly?'打开站内作图算例 →':'打开本站规格对照实验 →')+'</a></p>':'';
    return '<details class="resource-entry" data-resource-id="'+resource.id+'"'+(open?' open':'')+'><summary><strong>'+escape(resource.title)+'</strong><span class="resource-verification">'+status+'</span><span class="resource-question">'+escape(resource.question)+'</span></summary><div class="resource-entry-body"><p class="resource-kind">'+escape(resource.kind)+'</p>'+externalLinks+localLesson+'<h3>怎样使用</h3><ol>'+resource.steps.map(s=>'<li>'+escape(s)+'</li>').join('')+'</ol>'+(resource.output?'<p><strong>产出：</strong>'+escape(resource.output)+'</p>':'')+'<p><strong>门槛：</strong>'+escape(resource.requirements)+'</p><h3>核验范围与局限</h3><p>'+escape(verification.scope)+(verification.environment?'<br>复算环境：'+escape(verification.environment):'')+'</p><ul>'+resource.limits.map(l=>'<li>'+escape(l)+'</li>').join('')+'</ul>'+(resource.downloads.length?'<p class="resource-downloads">'+downloads(resource)+'</p>':'')+'<details class="resource-evidence"><summary>来源、许可与对应章节</summary><p>核查日期：'+escape(resource.checked)+'。'+escape(resource.license)+'</p>'+(resource.sourceCommit?'<p>所读源码提交：'+escape(resource.sourceCommit)+'</p>':'')+'<p>'+escape(verification.read)+'</p><ul>'+resource.evidence.map(e=>'<li><a href="'+escape(e.url)+'" target="_blank" rel="noopener noreferrer">'+escape(e.summary||'具体来源')+'</a>'+(e.blobSha?' · 文件 '+escape(e.blobSha.slice(0,10)):'')+'</li>').join('')+'</ul><div class="resource-targets">'+resource.targets.map(targetLink).join(' · ')+'</div></details></div></details>';
  }
  function scoped(course,section) {
    const exact=resources.filter(r=>applies(r,course,section));
    return exact.length?exact:resources.filter(r=>applies(r,course));
  }
  function button(course,section,label='实作资源') {
    if(course.outlineOnly||section?.kind==='outline'||!resources.some(r=>applies(r,course.id)))return '';
    return '<button type="button" class="resource-nav-button" aria-haspopup="dialog" aria-controls="resource-dialog" data-open-resources data-resource-course="'+escape(course.id)+'"'+(section?' data-resource-section="'+escape(section.id)+'"':'')+'><svg class="icon" aria-hidden="true"><use href="#i-file"/></svg>'+label+'</button>';
  }

  const dialog=document.querySelector('#resource-dialog');
  let origin=null;
  function openResources(course,section,trigger) {
    const directory=document.querySelector('#reader-directory');
    origin={element:directory.contains(trigger)?document.querySelector('[data-reader-directory]'):trigger,x:scrollX,y:scrollY};
    if(directory.open)directory.close();
    const selected=scoped(course,section);
    document.querySelector('#resource-dialog-title').textContent=(courseById(course)?.title||'课程')+' · 实作与资料';
    document.querySelector('#resource-dialog-content').innerHTML='<p class="resource-scope-note">'+(section&&selected.some(r=>applies(r,course,section))?'本节对应资源':'本课程资源')+' · '+selected.length+' 项。核验范围按条目分别说明。</p>'+selected.map(r=>entryHtml(r,true)).join('')+'<p><a href="#resources/'+escape(course)+'">浏览本课程全部资源 →</a></p>';
    document.body.classList.add('resource-open');dialog.showModal();
  }
  dialog.addEventListener('close',()=>{
    document.body.classList.remove('resource-open');
    if(origin?.element?.isConnected){scrollTo({left:origin.x,top:origin.y,behavior:'instant'});origin.element.focus({preventScroll:true});}
    origin=null;
  });
  dialog.addEventListener('click',event=>{
    if(event.target.closest('[data-close-resources]'))dialog.close();
    if(event.target===dialog){const box=dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)dialog.close();}
  });
  document.addEventListener('click',event=>{
    const trigger=event.target.closest('[data-open-resources]');
    if(trigger){event.preventDefault();openResources(trigger.dataset.resourceCourse,trigger.dataset.resourceSection,trigger);}
  });

  function pageHtml(course) {
    return '<section class="resource-library" aria-labelledby="resource-page-title"><div class="page-heading"><h1 id="resource-page-title">实作与资料</h1><p class="page-meta">'+resources.length+' 项 · 核查 '+escape(data.checked)+'</p></div><div class="resource-controls"><label>课程<select data-resource-course-filter><option value="">全部课程</option>'+courses.map(c=>'<option value="'+c.id+'"'+(c.id===course?' selected':'')+'>'+escape(c.title)+'</option>').join('')+'</select></label><label>查找<input type="search" data-resource-query placeholder="问题、工具或数据…"></label><label class="resource-checkbox"><input type="checkbox" data-resource-code-only>含 GitHub 源码</label><label class="resource-checkbox"><input type="checkbox" data-resource-run-only>已复算部分任务</label></div><p data-resource-count role="status"></p><div data-resource-results></div></section>';
  }
  function bindPage(root,initialCourse,section) {
    const controls=root.querySelector('.resource-controls'),results=root.querySelector('[data-resource-results]');
    let signature=null;
    function update(){
      const course=controls.querySelector('[data-resource-course-filter]').value;
      const query=controls.querySelector('[data-resource-query]').value.trim().toLowerCase();
      const code=controls.querySelector('[data-resource-code-only]').checked,run=controls.querySelector('[data-resource-run-only]').checked;
      const nextSignature=JSON.stringify([course,query,code,run]);
      if(nextSignature===signature)return;
      signature=nextSignature;
      let matches=resources.filter(r=>(!course||applies(r,course))&&(!code||r.repository)&&(!run||r.verification.executed)&&[r.title,r.question,r.kind,...r.steps,...r.targets.map(t=>courseById(t.course).title)].join(' ').toLowerCase().includes(query));
      if(section&&course===initialCourse)matches.sort((a,b)=>Number(applies(b,course,section))-Number(applies(a,course,section)));
      root.querySelector('[data-resource-count]').textContent=matches.length+' 项；计算复现、资料核读与硬件实测分别说明。';
      results.innerHTML=matches.length?matches.map((r,i)=>entryHtml(r,Boolean(course)&&i===0)).join(''):'<p>没有匹配资源。</p>';
    }
    controls.addEventListener('input',update);controls.addEventListener('change',update);update();
  }

  // These are candidate equations on the positive-speed branch, not a digital twin.
  function motorSteady(load,alpha=1,resistanceFactor=1,fit=false) {
    const s=data.motorSpecification,k=s.torque_constant_Nm_per_A,w0=s.no_load_rpm*2*Math.PI/60;
    const tau0=k*s.no_load_current_A,R=s.terminal_resistance_ohm*resistanceFactor;
    const constant=alpha*tau0,b=(1-alpha)*tau0/w0;
    const offset=fit?s.voltage_V-R*s.no_load_current_A-k*w0:0;
    const w=(s.voltage_V-offset-R*(load+constant)/k)/(k+R*b/k);
    return {rpm:w*60/(2*Math.PI),current:(load+constant+b*w)/k,offset,b,constant};
  }
  function plot(values,points) {
    const W=640,H=300,left=76,right=18,top=24,bottom=58;
    const all=[...values.map(v=>v.rpm),...points.map(v=>v.rpm)];
    const min=Math.floor((Math.min(...all)-200)/500)*500,max=Math.ceil((Math.max(...all)+200)/500)*500;
    const x=t=>left+t/.03*(W-left-right),y=n=>top+(max-n)/(max-min)*(H-top-bottom);
    let svg='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="候选模型速度曲线与两个厂商公开规格点对照"><path d="M'+left+' '+top+'V'+(H-bottom)+'H'+(W-right)+'" fill="none" stroke="currentColor" stroke-width="2"/>';
    for(let i=0;i<=3;i++){const t=i*.01;svg+='<text x="'+x(t)+'" y="'+(H-bottom+29)+'" text-anchor="middle">'+i*10+'</text>';}
    for(let i=0;i<=3;i++){const n=min+(max-min)*i/3;svg+='<text x="'+(left-10)+'" y="'+(y(n)+6)+'" text-anchor="end">'+Math.round(n)+'</text>';}
    svg+='<text x="'+((W+left)/2)+'" y="'+(H-5)+'" text-anchor="middle">负载转矩 / mN·m</text><text x="6" y="16">r/min</text><path d="'+values.map((v,i)=>(i?'L':'M')+x(v.torque).toFixed(2)+' '+y(v.rpm).toFixed(2)).join(' ')+'" fill="none" stroke="var(--accent)" stroke-width="3"/>';
    points.forEach(p=>{const a=x(p.torque),b=y(p.rpm);svg+='<path d="M'+(a-6)+' '+(b-6)+'l12 12m-12 0 12-12" stroke="currentColor" stroke-width="3"/>';});
    return svg+'</svg>';
  }
  function mountLesson(body) {
    const lab=body.querySelector('[data-dc-specs-lab]');if(!lab)return;
    const s=data.motorSpecification;
    lab.querySelector('[data-dc-controls]').innerHTML='<label>恒定损耗占比 α <output data-dc-alpha-value>100%</output><input type="range" data-dc-alpha min="0" max="1" step="0.1" value="1"></label><label>等效电阻倍率 <output data-dc-r-value>1.00</output><input type="range" data-dc-r min="1" max="1.8" step="0.05" value="1"></label><label class="resource-checkbox"><input type="checkbox" data-dc-fit>用空载点校准等效压降（不算独立验证）</label><button type="button" class="secondary-button" data-dc-reset>恢复初始假设</button>';
    function update(){
      const alpha=Number(lab.querySelector('[data-dc-alpha]').value),factor=Number(lab.querySelector('[data-dc-r]').value),fit=lab.querySelector('[data-dc-fit]').checked;
      lab.querySelector('[data-dc-alpha-value]').value=Math.round(100*alpha)+'%';lab.querySelector('[data-dc-r-value]').value=factor.toFixed(2);
      const v=motorSteady(s.nominal_torque_Nm,alpha,factor,fit),error=100*(v.rpm/s.nominal_rpm-1);
      lab.querySelector('[data-dc-results]').textContent='额定负载下：模型 '+v.rpm.toFixed(1)+' r/min、'+v.current.toFixed(3)+' A；厂商规格 '+s.nominal_rpm+' r/min、'+s.nominal_current_A+' A。转速偏差 '+(error>=0?'+':'')+error.toFixed(2)+'%。等效压降 '+v.offset.toFixed(3)+' V。';
      const values=Array.from({length:61},(_,i)=>({torque:i*.0005,...motorSteady(i*.0005,alpha,factor,fit)}));
      lab.querySelector('[data-dc-plot]').innerHTML=plot(values,[{torque:0,rpm:s.no_load_rpm},{torque:s.nominal_torque_Nm,rpm:s.nominal_rpm}]);
    }
    lab.querySelector('[data-dc-controls]').addEventListener('input',update);
    lab.querySelector('[data-dc-reset]').addEventListener('click',()=>{lab.querySelector('[data-dc-alpha]').value='1';lab.querySelector('[data-dc-r]').value='1';lab.querySelector('[data-dc-fit]').checked=false;update();});
    lab.querySelector('[data-dc-downloads]').innerHTML=downloads(resources.find(r=>r.id==='motor-catalogue-check'));update();
  }
  window.LNResources={button,pageHtml,bindPage,mountLesson,motorSteady,onRoute:()=>{origin=null;if(dialog.open)dialog.close();}};
})();
