'use strict';
(() => {
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (url, label) => '<a href="'+escape(url)+'" target="_blank" rel="noopener">'+escape(label)+'</a>';
  const table = (headers, rows) => '<div class="table-scroll"><table><thead><tr>'+headers.map(h=>'<th scope="col">'+escape(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(cell=>'<td>'+cell+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
  function resourcesHtml() {
    const data = window.LN_HIGH_SCHOOL_INDEX;
    const courses = window.LN_COURSES.filter(c=>c.level==='highschool');
    const sources = data['来源目录'];
    const sourceLink = id => { const s=sources.find(s=>s['来源编号']===id);return s ? link(s['网址'],s['标题']) : escape(id); };
    const versionRows = data['版本差异'].map(r=>[escape(r['学科']),escape(r['比较对象']),escape(r['差异或风险']),escape(r['使用方式'])]);
    const bookRows = subject => data['教材册次与知识'].filter(r=>r['学科']===subject).map(r=>[escape(r['索引层级']),escape(r['版本']),escape(r['册次']),escape(r['知识点分布']),escape(r['海南使用状态'])]);
    const online = [
      ['https://basic.smartedu.cn/tchMaterial','国家中小学智慧教育平台','按学段、学科及教材版本查教材与课程；部分资源需登录。'],
      ['https://jc.pep.com.cn/','人教教材电子版','用于核对实际教材；入口可能有登录或访问限制。'],
      ['https://stkw.pep.com.cn/jfts/tbjxycp/gz/','人教同步解析与测评','新版九科同步教辅目录；对应册次，不是整套正文转载。'],
      ['https://resource.unischool.cn/jc/nse_shr_old/','外研高中修订版资源','与人教主题、单元顺序分别查找，不混用旧版 Module 体系。'],
      ['https://www.ictr.edu.cn/download_center/fangan.html','课标与课程方案','2020底本保留历史标签；2025日常修订的存在不等于已完成逐条差分。']
    ];
    return '<a class="back-link" href="#highschool">← 高中</a><section class="highschool-resources publication-body"><h1>教材与来源</h1><p class="page-meta">海南 · 2027届 · 本次整理 '+escape(data.checked)+'</p>'+
      '<p>高中目录按所附核验报告的九科、50册主索引与235个知识节点组织。选科和课程类别沿用原报告。</p>'+
      '<p>海南采用六科自主选三的3＋3框架。'+link('https://www.eol.cn/kaoshi/gaokao/gkzc/202610/t20261026_2786604.shtml','2027报名通知转载')+'支持选科规则，不据此预测卷型、题量或新增考点。非统编六科的个人实际版本、教材印次和学校进度仍需与实书核对。</p>'+
      '<div class="source-downloads">'+link('courses/highschool/assets/hainan-2027-report.pdf','原核验报告 PDF')+link('courses/highschool/assets/hainan-2027-index.xlsx','原知识与交叉核验表 XLSX')+'</div>'+
      '<h2>九科与册次</h2>'+table(['学科','主索引册数','范围与版本'],courses.map(c=>['<a href="#course/'+escape(c.id)+'">'+escape(c.title)+'</a>',String(new Set(c.sections.filter(s=>!s.supplement).map(s=>s.group)).size),escape(c.versionNote)]))+
      '<details class="study-sources"><summary>版本差异</summary>'+table(['学科','版本','差异','对应方法'],versionRows)+'</details>'+
      '<details class="study-sources"><summary>外研英语 · 七册42个单元</summary><p>保留原报告核验的修订版单元导航；与人教主题索引按内容查找，不把两版单元号视为相同。</p>'+table(['册次','单元'],data['外研七册单元'].map(r=>[escape(r['册次']),escape(r['单元名'])]))+'</details>'+
      '<h2>教材、教辅与公开课程</h2><ul class="resource-links">'+online.map(([url,title,note])=>'<li>'+link(url,title)+'<p>'+escape(note)+'</p></li>').join('')+'</ul>'+
      '<h2>逐科教材索引</h2>'+courses.map(c=>'<details class="study-sources"><summary>'+escape(c.title)+' · 主索引与候选版本</summary>'+table(['层级','版本','册次','知识模块','海南核验范围'],bookRows(c.title))+'</details>').join('')+
      '<details class="study-sources"><summary>交叉核验与待确认事项</summary>'+table(['结论','核验结果','适用限制'],data['交叉验证台账'].map(r=>[escape(r['结论']),escape(r['状态']),escape(r['适用限制'])]))+table(['待确认','影响','目前处理'],data['待核事项'].map(r=>[escape(r['事项']),escape(r['影响']),escape(r['当前处理'])]))+'</details>'+
      '<details class="study-sources"><summary>原报告来源目录 · 28项</summary><ul class="resource-links">'+sources.map(s=>'<li>'+sourceLink(s['来源编号'])+'<p>'+escape(s['证据类型'])+' · '+escape(s['支持的结论'])+'</p><p>'+escape(s['不能推出的结论'])+'</p></li>').join('')+'</ul></details></section>';
  }
  window.LNHighSchool = {resourcesHtml};
})();
