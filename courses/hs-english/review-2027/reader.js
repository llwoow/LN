'use strict';
(()=>{
  let cleanup=()=>{};
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function mount(body,payload){
    cleanup();const abort=new AbortController(),signal=abort.signal;
    const on=(node,type,fn)=>node?.addEventListener(type,fn,{signal});
    for(const id of payload.referenceQuestions||[])window.LNPractice.noteReferenceUse(id);
    for(const lab of body.querySelectorAll('[data-english-lab]')){
      const id=lab.dataset.englishLab;let items;
      if(['K06','K09'].includes(id))items=[
        ['后置修饰','The book [written] by a young teacher became popular.','主句谓语是became；written by...修饰book，book承受write动作。'],
        ['完整谓语','The book [was written] by a young teacher last year.','本句需要完整谓语；过去、被动与book单数共同要求was written。'],
        ['并列谓语','The teacher [wrote] the book and [sent] it to a publisher.','and连接两个动作，wrote与sent可以共享主语，并不是有了wrote后sent就必须非谓语。']];
      else if(id==='T02')items=[
        ['符合证据','Some volunteers [reported] feeling calmer.','只说明部分志愿者报告感受，不自动说明所有人的成绩或因果。'],
        ['扩大范围','[All] volunteers felt calmer.','some变成all，范围超出给定证据。'],
        ['添加因果','The room [caused higher marks for everyone].','原文既没给成绩，也没排除其他原因，还增加everyone。']];
      else if(id==='T03')items=[
        ['建立连接','Students record every unknown word. [This interrupts their reading.] As a result, they lose the argument.','This回指逐词记录；后句解释这种打断的结果，前后构成因果链。'],
        ['只有同主题','Students record every unknown word. [Dictionaries have many pages.] As a result, they lose the argument.','词典与词汇主题有关，但没有解释为何失去论证主线；同主题不足以填空。']];
      else items=[
        ['原文约束','A model boat is [broken], and an exhibition opens in [one hour].','已有条件是损坏、时间有限与伙伴愿意负责。后续不能凭空把展览改成一周后。'],
        ['第一段推进','They [match the pieces] and [change the poster] while the glue dries.','动作解决损坏，也给等待时间安排合理任务，为访客到场做准备。'],
        ['第二段回扣','They [show the repaired side] and explain what they learned.','展示回扣事故和责任，不依赖无关奖项或突然成功。']];
      lab.innerHTML='<h3>改变条件，对照理解</h3><div class="english-lab-buttons">'+items.map((x,i)=>'<button class="secondary-button" data-state="'+i+'" aria-pressed="'+(!i)+'">'+x[0]+'</button>').join('')+'</div><div data-english-scene></div><p data-english-explain aria-live="polite"></p>';
      const draw=i=>{lab.querySelector('[data-english-scene]').innerHTML=esc(items[i][1]).replace(/\[([^\]]+)\]/g,'<mark>$1</mark>');lab.querySelector('[data-english-explain]').textContent=items[i][2];lab.querySelectorAll('[data-state]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.state)===i)));};
      on(lab,'click',e=>{const b=e.target.closest('[data-state]');if(b)draw(Number(b.dataset.state));});draw(0);
    }
    const notebook=body.querySelector('[data-english-records]');
    if(notebook){
      notebook.innerHTML='<p>英语练习使用LN原有错题与收藏。可导入此前独立网页的记录；已有首答保留，导入的作答标记为使用过参考。</p><div class="english-record-actions"><button class="secondary-button" data-english-export>导出英语记录</button><label>导入记录<input data-english-import type="file" accept="application/json,.json"></label><button class="secondary-button" data-english-local-import>读取此浏览器的旧英语记录</button></div><p data-english-status role="status"></p>';
      const status=notebook.querySelector('[data-english-status]');
      const merge=data=>{const result=window.LNPractice.importEnglishRecords(data);status.textContent='已合并 '+result.count+' 题；保留LN已有首答。'+(result.persistent?'':'浏览器存储不可用，请立即导出。');};
      on(notebook.querySelector('[data-english-import]'),'change',async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>2e6)throw Error('文件大于2 MB');const data=JSON.parse(await f.text());if(signal.aborted)return;merge(data);}catch(err){status.textContent='导入失败：'+err.message;}e.target.value='';});
      on(notebook.querySelector('[data-english-local-import]'),'click',()=>{try{const saved=localStorage.getItem('hainan.english2027.records.v1');if(!saved){status.textContent='此浏览器同一站点下没有旧记录，可选择此前导出的JSON文件。';return;}merge({assessment:'hainan-english-2027-v1',records:JSON.parse(saved)});}catch(err){status.textContent='读取失败：'+err.message;}});
      on(notebook.querySelector('[data-english-export]'),'click',()=>{const data=window.LNPractice.exportEnglishRecords(),url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='hainan-english2027-records.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
    }
    cleanup=()=>{abort.abort();body.querySelectorAll('audio').forEach(a=>{a.pause();a.removeAttribute('src');a.load();});};
  }
  window.LNEnglish2027={mount,onRoute:()=>{cleanup();cleanup=()=>{};}};
})();
