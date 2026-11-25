'use strict';
(() => {
  const data=window.LN_CROSS_KNOWLEDGE_DATA;
  const courses=window.LN_COURSES;
  const byCourse=new Map(courses.map(c=>[c.id,c]));
  const byId=new Map(data.nodes.map(n=>[n.id,n]));
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const route=n=>'#course/'+n.course+'/'+n.section+'/cross-'+n.id;
  const label=n=>byCourse.get(n.course).title+' · '+n.title;
  const hasCourse=id=>data.nodes.some(n=>n.course===id);
  const related=id=>data.links.filter(e=>e.from===id||e.to===id).map(e=>({edge:e,other:byId.get(e.from===id?e.to:e.from)}));
  const linksFor=course=>data.links.filter(e=>!course||byId.get(e.from).course===course||byId.get(e.to).course===course);
  const link=(n,reader=false)=>'<a '+(reader?'class="paper-reference" id="cross-link-'+esc(n.id)+'" ':'')+'href="'+esc(route(n))+'">'+esc(label(n))+'</a>';
  function mountLesson(body,course,section) {
    const local=data.nodes.filter(n=>n.course===course.id&&n.section===section.id);
    if(!local.length)return;
    // The inserted asides contain no p/h/li/td elements, preserving glossary passage indices.
    const paragraphs=[...body.querySelectorAll('p')];
    for(const n of local){
      if(body.querySelector('#cross-'+n.id))continue;
      const matches=paragraphs.filter(p=>p.textContent.includes(n.match));
      if(matches.length!==1)continue;
      const aside=document.createElement('aside');
      aside.className='cross-knowledge-inline'; aside.id='cross-'+n.id;
      aside.setAttribute('aria-label','相关课程知识');
      const relevant=related(n.id);
      // ID includes both endpoints; one destination can occur more than once on a lesson.
      aside.innerHTML='<strong>知识联系</strong>'+relevant.map(({edge,other})=>'<div class="cross-knowledge-item"><a class="paper-reference" id="cross-link-'+esc(n.id)+'-'+esc(other.id)+'" href="'+esc(route(other))+'">'+esc(label(other))+'</a><span>'+esc(edge.description)+'</span></div>').join('');
      matches[0].after(aside);
    }
  }
  function coursePanel(course) {
    if(!hasCourse(course.id))return '';
    const edges=linksFor(course.id);
    return '<details class="cross-course-panel"><summary>跨课程知识联系 <span>'+edges.length+' 条</span></summary><div><a class="secondary-button" href="#knowledge/'+esc(course.id)+'">打开跨课程图谱</a><div class="cross-course-list">'+edges.map(e=>'<div><strong>'+link(byId.get(e.from))+' ↔ '+link(byId.get(e.to))+'</strong><span>'+esc(e.description)+'</span></div>').join('')+'</div></div></details>';
  }
  function graphCourse(filter) {
    const links=linksFor(filter), ids=new Set(links.flatMap(e=>[e.from,e.to]));
    const nodes=data.nodes.filter(n=>ids.has(n.id));
    const topics=new Map(data.topics.map(t=>[t.id,t]));
    return {id:'cross-knowledge-'+(filter||'all'),title:'跨课程知识网络',crossKnowledge:true,
      sections:nodes.map(n=>({id:n.id,title:label(n),group:topics.get(n.topic).title,href:route(n)})),
      knowledgeMap:{chapters:data.topics.filter(t=>nodes.some(n=>n.topic===t.id)).map(t=>({group:t.title,description:t.description})),nodes:nodes.map(n=>({section:n.id,title:n.title,note:byCourse.get(n.course).title+' · '+n.note,keywords:[byCourse.get(n.course).title]})),links}};
  }
  function render(root,requested) {
    const filter=hasCourse(requested)?requested:'';
    const graph=graphCourse(filter);
    const choices=courses.filter(c=>hasCourse(c.id));
    const pending=data.pending.map(t=>'<div><strong>'+esc(t.title)+'</strong><span>'+esc(t.description)+'</span>'+(t.nodes.length?'<div class="cross-pending-links">'+t.nodes.map(id=>link(byId.get(id))).join(' · ')+'</div>':'')+'</div>').join('');
    root.classList.add('course-main','map-main');
    root.innerHTML='<a class="back-link" href="'+(filter?'#course/'+esc(filter)+'/map':'#overview')+'">'+(filter?'返回本课程图谱':'全部课程')+'</a><section class="course-heading"><div><h1>跨课程知识网络</h1><p class="page-meta">按共享原理组织 · 仅连接已核对的正文</p></div></section><div class="cross-filter"><label for="cross-course-filter">课程筛选</label><select id="cross-course-filter"><option value="">全部关联课程</option>'+choices.map(c=>'<option value="'+esc(c.id)+'"'+(filter===c.id?' selected':'')+'>'+esc(c.title)+'</option>').join('')+'</select></div><ln-knowledge-map></ln-knowledge-map><details class="cross-course-panel"><summary>待接入的理论与课程</summary><div class="cross-course-list">'+pending+'</div></details>';
    root.querySelector('#cross-course-filter').addEventListener('change',e=>{location.hash='knowledge'+(e.target.value?'/'+e.target.value:'');});
    root.querySelector('ln-knowledge-map').course=graph;
  }
  window.LNCrossKnowledge={hasCourse,mountLesson,coursePanel,render,graphCourse};
})();
