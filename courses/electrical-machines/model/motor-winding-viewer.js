(function (root) {
  'use strict';
  const M = root.MotorWindingModel;
  if (!M) throw new Error('请先加载 motor-winding-model.js。');
  const scriptBase = typeof document !== 'undefined' && document.currentScript ? new URL('.', document.currentScript.src).href : './';
  const COLORS = ['#236d9c', '#087f83', '#7859ac', '#cb5263', '#ad7932', '#8c7333', '#486d52', '#865e56'];
  const fmt = (v, n = 2) => Number.isFinite(v) ? v.toFixed(n) : '未求解';
  const rad = v => v * Math.PI / 180, deg = v => v * 180 / Math.PI;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const escapeHTML = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const parameterFields = [
    ['poles', '总极数 P', 1], ['slots', '槽／线圈／片数 Q', 1], ['turns', '每线圈匝数 w', 1],
    ['rotorDiameter', '转子外径 / mm', 1], ['coreLength', '铁心有效长度 / mm', 1], ['shaftDiameter', '轴径 / mm', 1],
    ['slotDepth', '槽深 / mm', .1], ['slotOpeningRatio', '槽角宽／槽距', .01], ['airGap', '径向气隙 / mm', .1],
    ['commutatorDiameter', '换向器外径 / mm', 1], ['commutatorLength', '换向器长度 / mm', 1], ['commutatorGap', '铁心端至换向器 / mm', 1],
    ['endHeight', '端部弧高 / mm', 1], ['wireArea', '单根裸铜面积 / mm²', .05], ['temperature', '绕组温度 / °C', 1],
    ['supplyVoltage', '端电压 U / V', .1], ['rpm', '转速 n / r·min⁻¹', 1], ['fluxDensity', '参考半径处场峰值 Bm / T', .01]
  ];
  class MotorWindingViewer {
    constructor(host, options = {}) {
      if (!(host instanceof HTMLElement)) throw new TypeError('host 必须是一个 HTMLElement。');
      if (host.shadowRoot?.childNodes.length) throw new Error('容器已存在其他内容；每个实例请使用独立容器。');
      this.host = host; this.root = host.shadowRoot || host.attachShadow({ mode: 'open' }); this.destroyed = false;
      this.model = M.createModel(options.parameters || {});
      this.state = { mode: 'assembly', angle: 0, brushShift: 0, zoom: 1, yaw: .83, pitch: .45, panX: 0, panY: 0, explode: 0, unroll: 1, coil: 1, branch: 0,
        playing: false, parts: { coil: true, rotor: true, poles: true, commutator: true, brushes: true, shaft: true, numbers: false, currents: false }, ...options.state };
      this.state.parts = { coil:true,rotor:true,poles:true,commutator:true,brushes:true,shaft:true,numbers:false,currents:false,...options.state?.parts };
      this.abort = new AbortController(); this.pointers = new Map(); this.frame = 0; this.animation = 0;
      const css = new URL('motor-winding-viewer.css', options.assetBase || scriptBase).href;
      this.root.innerHTML = `<link rel="stylesheet" href="${escapeHTML(css)}"><section class="module" aria-label="直流电机单叠绕组交互组件">
        <header class="module-head"><div><h2 data-ui="title">四极直流电机 · 双层单叠绕组</h2><p>同一接线图驱动四种视图 · 视角与转子角独立 · 尺寸单位 mm</p></div><span class="badge">工程原理参考模型 v1.0</span></header>
        <div class="workspace"><div class="stage-area"><div class="tabs" role="tablist" aria-label="观察方式">
        ${[['assembly','立体装配'],['unroll','圆柱展开'],['flat','槽层展开'],['circuit','支路电路']].map(([key, text]) => `<button role="tab" id="mode-${key}" aria-controls="scene-panel" data-mode="${key}" aria-selected="${key === 'assembly'}">${text}</button>`).join('')}</div>
        <div class="stage" role="tabpanel" id="scene-panel" aria-labelledby="mode-assembly"><canvas tabindex="0" aria-label="直流电机模型。方向键旋转或平移，正负键缩放；精确接线及状态见下方表格。"></canvas><div class="hud"><span data-ui="mode-label"></span><span data-ui="pose"></span><span data-ui="shorts"></span></div><div class="zoom-tools"><button data-action="zoom-in" aria-label="放大">＋</button><button data-action="zoom-out" aria-label="缩小">−</button><button data-action="expand" aria-label="展开画布">⛶</button></div></div>
        <div class="stage-note" data-ui="gesture">左键／单指旋转视角；右键或Shift拖动平移；滚轮／双指缩放。点击铜线可选择线圈。</div>
        <div class="camera"><button data-action="front">轴端视角</button><button data-action="side">侧视</button><button data-action="reset">重置视角</button><button data-action="png">导出PNG</button><label>缩放 <input data-control="zoom" type="range" min="35" max="500" value="100" aria-label="画面缩放"><output data-ui="zoom">100%</output></label></div><div class="legend" data-ui="legend"></div></div>
        <aside class="sidebar"><section class="group"><h3>转子与电刷</h3><div class="control"><label>转子机械角 θ <output data-ui="angle"></output></label><input data-control="angle" type="range" min="0" max="360" step=".1" value="0" aria-label="转子机械角"></div><div class="row"><button data-action="play" aria-pressed="false">缓慢转动</button><button data-action="step">转过一片距</button></div><div class="control"><label>刷架位移 δ <output data-ui="brushShift"></output></label><input data-control="brushShift" type="range" min="-20" max="20" step=".1" value="0" aria-label="刷架位移"></div><div class="control"><label>刷宽／片距 <output data-ui="brushWidth"></output></label><input data-control="brushWidth" type="range" min=".2" max="1.4" step=".01" value=".65" aria-label="刷宽与片距之比"></div><p class="hint">缓慢转动是观察速度；电势计算采用参数表中的转速。橙色线圈被刷子短接，电流未求解。</p></section>
        <section class="group"><h3>逐段追踪</h3><div class="control"><label>选择线圈</label><select data-control="coil" aria-label="选择线圈"></select></div><div class="row"><button data-action="prev-coil">上一只</button><button data-action="next-coil">下一只</button><button data-action="clear">全部</button></div><div class="control"><label>筛选当前主支路</label><select data-control="branch" aria-label="筛选主支路"></select></div><div class="key" data-ui="selection" aria-live="polite"></div></section>
        <section class="group"><h3>结构与显示</h3><div class="checks">${[['coil','绕组路径'],['rotor','开槽铁心'],['poles','主磁极'],['commutator','换向片'],['brushes','电刷'],['shaft','转轴'],['numbers','槽／片编号'],['currents','主支路电流箭头']].map(([k,v])=>`<label><input data-part="${k}" type="checkbox" ${this.state.parts[k]?'checked':''}>${v}</label>`).join('')}</div><div class="control" data-ui="explode-wrap"><label>结构拆解 <output data-ui="explode">0%</output></label><input data-control="explode" type="range" min="0" max="100" value="0" aria-label="结构拆解"></div><div class="control" data-ui="unroll-wrap" hidden><label>展开程度 <output data-ui="unroll">100%</output></label><input data-control="unroll" type="range" min="0" max="100" value="100" aria-label="圆柱展开程度"></div><p class="hint">拆解与展开只改变显示。每条线代表一只多匝线圈的路径束；交叉处未标节点即不连接。</p></section></aside></div>
        <div class="facts"><div class="summary-grid"><div class="metric"><b data-ui="count"></b><span>总极数／槽数／线圈数／片数</span></div><div class="metric"><b data-ui="path-count"></b><span>当前主支路数</span></div><div class="metric"><b data-ui="short-count"></b><span>正在换向的短路线圈</span></div><div class="metric"><b data-ui="fill"></b><span>示例毛槽满率，仅计裸铜</span></div></div><p class="live-description" data-ui="live"></p>
        <details open><summary>刷片接触与当前支路</summary><div class="table-wrap"><table><caption class="sr-only">当前刷片接触表</caption><thead><tr><th>电刷</th><th>极性</th><th>实际接触换向片</th><th>短路线圈</th></tr></thead><tbody data-ui="contacts"></tbody></table></div><div class="table-wrap"><table><caption class="sr-only">非换向主支路，路径均按正母线到负母线排列</caption><thead><tr><th>支路</th><th>刷端：正→负</th><th>线圈路径／遍历方向</th><th>E<sub>b</sub> / V</th><th>R<sub>b</sub> / Ω</th><th>I<sub>b</sub> / A</th></tr></thead><tbody data-ui="branches"></tbody></table></div><p class="data-note">→表示线圈沿首片到末片遍历，←表示反向。负电流表示实际电流与正母线→负母线约定相反；换向线圈不能视作电流为零。</p></details>
        <details><summary>完整槽层接线表与节距约定</summary><p class="data-note" data-ui="pitch"></p><div class="table-wrap"><table><thead><tr><th>线圈</th><th>上层槽</th><th>下层槽</th><th>首片→末片</th><th>当前归属</th><th>定位</th></tr></thead><tbody data-ui="connections"></tbody></table></div><p class="data-note" data-ui="equalizers"></p></details>
        <details><summary>尺寸、工况与参数校验</summary><p class="data-note">这些初值是示例，不是某台电机的额定参数。仅生成全距、双层、单叠叠进绕组；改变槽数或极数会重建接线，不能通过缩放替代。</p><form data-ui="parameters"><div class="parameter-grid">${parameterFields.map(([key,label,step])=>`<label>${label}<input name="${key}" type="number" step="${step}" required></label>`).join('')}<label class="wide">参数来源／型号<input name="provenance" type="text" maxlength="200"></label></div><div class="row"><button class="primary" type="submit">校验并重建模型</button><button type="button" data-action="defaults">恢复示例参数</button><button type="button" data-action="json">导出模型JSON</button><button type="button" data-action="csv">导出接线CSV</button><label>导入JSON <input type="file" data-ui="import" accept="application/json,.json" style="max-width:180px;font-size:12px"></label></div></form><p class="error" data-ui="error" role="alert"></p><div class="warnings" data-ui="warnings"></div><p class="data-note" data-ui="dimensions"></p></details>
        <details><summary>计算链与适用条件</summary><div class="formula" data-ui="formulas"></div><p class="data-note">Bᵣ 为向外的径向磁密；rₜ、r<sub>b</sub>分别为上下层有效半径，ℓ为有效长度；轴向 +x 指向换向器，θ 按 +x 右手正向。上层沿前→后、下层沿后→前。只对铁心有效长度内的导体积分；端部电势忽略。主支路按瞬时电阻关系估算，未求电感、互感、接触压降、电枢反应和换向暂态。</p><div class="table-wrap"><table><thead><tr><th>仅非换向主支路的估计</th><th>当前值</th></tr></thead><tbody data-ui="estimates"></tbody></table></div><p class="warnings">以上转矩、铜耗和功率仅计未被短接的主支路线圈。短路线圈的电流、转矩与损耗未知，因此这里不显示整机效率，也不预测火花、温升、寿命或允许转速。</p><p class="data-note">无量纲显示层别位移不参与计算。下层／上层有效半径来自参数化槽深，磁场采用预设解析谐波参考场，不是含槽铁心的有限元或实测场。</p></details></div></section>`;
      this.canvas = this.root.querySelector('canvas'); this.ctx = this.canvas.getContext('2d', { alpha: false });
      if (!this.ctx) throw new Error('当前浏览器不支持 Canvas 2D。接线模型仍可由 MotorWindingModel 独立使用。');
      this.bind(); this.resizeObserver = new ResizeObserver(() => this.resize()); this.resizeObserver.observe(this.canvas);
      this.refreshModelUI(); this.updateElectrical(); this.syncUI(); this.resize();
    }
    ui(key) { return this.root.querySelector(`[data-ui="${key}"]`); }
    control(key) { return this.root.querySelector(`[data-control="${key}"]`); }
    on(target, type, callback, opts = {}) { target.addEventListener(type, callback, { ...opts, signal: this.abort.signal }); }
    emit(type, detail) { this.host.dispatchEvent(new CustomEvent(type, { detail, bubbles: true, composed: true })); }
    getState() { return JSON.parse(JSON.stringify(this.state)); }
    getModel() { return JSON.parse(JSON.stringify(M.exportData(this.model, this.electrical))); }
    setParameters(patch) {
      const next = M.createModel({ ...this.model.parameters, ...patch });
      this.model = next; this.state.coil = Math.min(this.state.coil, next.coils.length); this.state.branch = 0;
      this.refreshModelUI(); this.updateElectrical(); this.syncUI(); this.invalidate();
      this.emit('modelchange', this.getModel()); return this;
    }
    setState(patch) {
      const allowed = ['angle','brushShift','zoom','yaw','pitch','panX','panY','explode','unroll'];
      for (const key of allowed) if (key in patch && !Number.isFinite(patch[key])) throw new RangeError(`${key} 须为有限数值。`);
      if (patch.mode) this.setMode(patch.mode);
      for (const key of allowed) if (key in patch) this.state[key] = patch[key];
      this.state.angle = M.mod(this.state.angle, 360); this.state.brushShift = clamp(this.state.brushShift, -20, 20);
      this.state.zoom = clamp(this.state.zoom,.35,5); this.state.pitch = clamp(this.state.pitch,-1.5,1.5);
      this.state.explode = clamp(this.state.explode,0,1); this.state.unroll = clamp(this.state.unroll,0,1);
      if (patch.parts) Object.assign(this.state.parts, patch.parts);
      if ('coil' in patch) this.selectCoil(patch.coil);
      if ('branch' in patch) this.selectBranch(patch.branch);
      if ('angle' in patch || 'brushShift' in patch) this.updateElectrical();
      this.syncUI(); this.invalidate(); this.emit('statechange', this.getState()); return this;
    }
    setMode(mode) {
      if (!['assembly','unroll','flat','circuit'].includes(mode)) throw new RangeError('未知视图。');
      this.state.mode = mode; this.resetCamera(); this.syncUI(); this.invalidate(); return this;
    }
    selectCoil(id) {
      if (!Number.isInteger(id) || id < 0 || id > this.model.coils.length) throw new RangeError('线圈编号超出范围。');
      this.state.coil = id; this.state.branch = 0; this.syncUI(); this.invalidate();
      this.emit('selectionchange', { coil: id, branch: 0 }); return this;
    }
    selectBranch(id) {
      if (!Number.isInteger(id) || id < 0 || id > this.model.poles) throw new RangeError('支路编号超出范围。');
      this.state.branch = id; this.state.coil = 0; this.syncUI(); this.invalidate();
      this.emit('selectionchange', { coil: 0, branch: id }); return this;
    }
    resetCamera() {
      Object.assign(this.state,{zoom:1,panX:0,panY:0,yaw:this.state.mode==='unroll'?.04:.83,pitch:this.state.mode==='unroll'?.04:.45});
      this.syncUI(); this.invalidate(); return this;
    }
    exportPNG() { this.draw(); return this.canvas.toDataURL('image/png'); }
    exportConnections(format = 'json') {
      if (format === 'csv') return M.connectionsCSV(this.model);
      if (format !== 'json') throw new RangeError('format 须为 json 或 csv。');
      return JSON.stringify(this.getModel(), null, 2);
    }
    download(content, name, type) {
      const url = URL.createObjectURL(new Blob([content], { type })); const a = document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }
    destroy() {
      if (this.destroyed) return; this.destroyed = true; this.abort.abort(); this.resizeObserver.disconnect();
      cancelAnimationFrame(this.frame); cancelAnimationFrame(this.animation); this.root.replaceChildren(); this.pointers.clear();
    }
    refreshModelUI() {
      const p = this.model.parameters;
      this.ui('title').textContent = `${p.poles}极直流电机 · ${p.slots}槽双层单叠绕组`;
      this.control('coil').innerHTML = '<option value="0">全部线圈</option>' + this.model.coils.map(c=>`<option value="${c.id}">C${c.id} · 上${c.upperSlot}→下${c.lowerSlot} · 片${c.startBar}→${c.endBar}</option>`).join('');
      this.control('branch').innerHTML = '<option value="0">全部主支路</option>' + Array.from({length:p.poles},(_,i)=>`<option value="${i+1}">支路 ${i+1}</option>`).join('');
      this.ui('legend').innerHTML = Array.from({length:p.poles},(_,i)=>`<span><i style="background:${COLORS[i]}"></i>支路${i+1}</span>`).join('')+'<span><i style="background:#e88c22"></i>换向短路／电流未知</span>';
      for (const [key] of parameterFields) this.ui('parameters').elements[key].value = p[key];
      this.ui('parameters').elements.provenance.value = p.provenance;
      const pp = this.model.pitches;
      this.ui('pitch').textContent = `对外编号从1开始。q=${pp.coilSlots}槽；后节距 Yb=+${pp.backSidePositions}、有向前节距 Yf=${pp.frontDirectedSidePositions}，单位均为“元件边位置”（上层2i−1，下层2i）。合成+2位置，换向片距 yc=+1片。Z=2Qw=${2*p.slots*p.turns}根有效导体；元件边位置不是多匝中的每一根导体。`;
      this.ui('equalizers').textContent = '理想等电位候选组：'+this.model.equalPotentialGroups.map(g=>g.join('↔')).join('；')+'。实际多极叠绕的均压线须另行设计；本图未添加这些连接，不可把候选表当成制造布线。';
      this.ui('warnings').textContent = this.model.validation.warnings.join('\n');
      this.ui('dimensions').textContent = `参数来源：${p.provenance}。参考槽面积 ${fmt(this.model.validation.slotArea)} mm²；铜电阻以ρ20=0.017241 Ω·mm²/m及α20=0.00393/°C估算，长度由示例端部路径与匝数估计。未计绝缘和实际槽型，非出厂电阻。气隙参数只改变几何；给定Bm不会由气隙自动重算，励磁磁路尚未求解。`;
      this.ui('formulas').innerHTML = '单位：电磁积分中r、R、ℓ用m；Ω=2πn/60，单位rad/s。<br>连接：片 i → 上层 i → 下层 (i+q) → 片 (i+1)，编号循环。<br>槽角：ψᵢ=θ+2π(i−1)/Q；片中心：θ+2π(i−3/2)/Q。<br>参考场：Aₓ=(BₘR/p)(r/R)ᵖ cos(pψ)，p=P/2，R为转子外半径。<br>Bᵣ=−Bₘ(r/R)ᵖ⁻¹ sin(pψ)；Bθ=−Bₘ(r/R)ᵖ⁻¹ cos(pψ)。<br>线圈有向电势：εᵢ=wΩℓ[rₜBᵣ(rₜ,ψᵢ)−r<sub>b</sub>Bᵣ(r<sub>b</sub>,ψᵢ+2πq/Q)]。<br>铜电阻：Rᵢ=ρ<sub>20</sub>[1+α<sub>20</sub>(T−20)](wℓ<sub>turn</sub>+ℓ<sub>lead</sub>)/S<sub>Cu</sub>；此处长度用m、S<sub>Cu</sub>用mm²、ρ<sub>20</sub>用Ω·mm²/m。<br>路径反电势：E<sub>b</sub>=−Σsᵢεᵢ；R<sub>b</sub>=ΣRᵢ；I<sub>b</sub>=(U−E<sub>b</sub>)/R<sub>b</sub>，sᵢ=±1；线圈有向电流Iᵢ=sᵢI<sub>b</sub>。<br>单线圈转矩：τᵢ=−wℓ[rₜBᵣ(rₜ,ψᵢ)−r<sub>b</sub>Bᵣ(r<sub>b</sub>,ψᵢ+2πq/Q)]Iᵢ。<br>校核：UΣI<sub>b</sub>=ΣI<sub>b</sub>²R<sub>b</sub>+ΣE<sub>b</sub>I<sub>b</sub>；ΩΣτᵢ=ΣE<sub>b</sub>I<sub>b</sub>。<br>短接几何持续时间（常转速）：t꜀=(b−g)(2π/Q)/|Ω|，b为刷宽比、g为缝宽比；Ω=0时不定义持续时间。';
      this.ui('error').textContent = '';
    }
    updateElectrical() {
      this.electrical = M.electricalState(this.model, this.state.angle, this.state.brushShift);
      const e=this.electrical,p=this.model.parameters;
      this.ui('contacts').innerHTML=e.brushes.map(b=>`<tr><td>B${b.id}</td><td>${b.polarity>0?'＋':'−'}</td><td>${b.bars.join('、')}</td><td>${e.coils.filter(c=>c.commutating&&c.brushId===b.id).map(c=>'C'+c.id).join('、')||'无'}</td></tr>`).join('');
      this.ui('branches').innerHTML=e.branches.map(b=>`<tr><td>${b.id}</td><td>B${b.fromBrush}→B${b.toBrush}</td><td>${b.path.map(c=>(c.direction>0?'→':'←')+'C'+(c.coil+1)).join(' ')}</td><td>${fmt(b.backEmf)}</td><td>${fmt(b.resistance,4)}</td><td>${fmt(b.current)}</td></tr>`).join('');
      this.ui('connections').innerHTML=this.model.coils.map(c=>{const s=e.coils[c.index];return `<tr data-coil-row="${c.id}"><td>C${c.id}</td><td>${c.upperSlot}</td><td>${c.lowerSlot}</td><td>${c.startBar}→${c.endBar}</td><td>${s.commutating?'换向短路':'支路'+s.branchId}</td><td><button data-select-coil="${c.id}">追踪</button></td></tr>`}).join('');
      this.ui('count').textContent=`${p.poles} / ${p.slots} / ${p.slots} / ${p.slots}`;
      this.ui('path-count').textContent=e.branches.length;this.ui('short-count').textContent=e.commutatingCoils.length;
      this.ui('fill').textContent=fmt(this.model.validation.grossFill*100,1)+'%';
      this.ui('live').textContent=`转子角 ${fmt(this.state.angle,1)}°；刷架 ${fmt(this.state.brushShift,1)}°。${e.commutatingCoils.length?'正在换向：'+e.commutatingCoils.map(i=>'C'+i).join('、')+'。':'当前没有线圈被电刷跨片短接。'}主支路线圈数 ${e.branches.map(b=>b.path.length).join(' / ')}；合计加上换向线圈恰为${p.slots}只。`;
      const v=e.estimate;
      const items=[['正母线电流 ΣI<sub>b</sub> / A',fmt(v.current)],['主支路铜耗 ΣI<sub>b</sub>²R<sub>b</sub> / W',fmt(v.copperLoss)],['主支路电磁转换功率 ΣE<sub>b</sub>I<sub>b</sub> / W',fmt(v.conversionPower)],['主支路转矩贡献 / N·m',fmt(v.torque,4)],['内部功率等式残差 / W',v.powerResidual.toExponential(2)],['转矩×角速度校核残差 / W',v.torquePowerResidual.toExponential(2)]];
      this.ui('estimates').innerHTML=items.map(([k,val])=>`<tr><td>${k}</td><td>${val}</td></tr>`).join('');
      this.syncSelection();
    }
    syncSelection() {
      if (!this.electrical) return;
      const id=this.state.coil,branch=this.state.branch;
      if(id){const c=this.model.coils[id-1],s=this.electrical.coils[id-1];this.ui('selection').innerHTML=`<strong>C${id}：上${c.upperSlot} → 下${c.lowerSlot}</strong><p>首片${c.startBar} → 末片${c.endBar}；跨${this.model.span}槽。${s.commutating?'<span class="unknown">正在被B'+s.brushId+'短接，电流未求解。</span>':'当前在支路'+s.branchId+'，有向电流 '+fmt(s.current)+' A。'}</p>`;}
      else if(branch){const b=this.electrical.branches[branch-1];this.ui('selection').innerHTML=`<strong>当前支路${branch}：B${b.fromBrush}＋ → B${b.toBrush}−</strong><p>${b.path.map(e=>(e.direction>0?'→':'←')+'C'+(e.coil+1)).join(' ')}。I<sub>b</sub>≈${fmt(b.current)} A。</p>`;}
      else this.ui('selection').innerHTML='<strong>全部连接</strong><p>颜色随电刷接触图重新分配，不永久绑定线圈编号；橙色表示换向短路。</p>';
      for(const row of this.root.querySelectorAll('[data-coil-row]'))row.classList.toggle('selected-row',+row.dataset.coilRow===id);
    }
    syncUI() {
      const s=this.state;
      for(const key of ['angle','brushShift','zoom','explode','unroll']){
        const value=['zoom','explode','unroll'].includes(key)?s[key]*100:s[key];this.control(key).value=value;
        this.ui(key).textContent=fmt(value,key==='angle'||key==='brushShift'?1:0)+(['angle','brushShift'].includes(key)?'°':'%');
      }
      this.control('brushWidth').value=this.model.parameters.brushWidth;this.ui('brushWidth').textContent=fmt(this.model.parameters.brushWidth);
      this.control('coil').value=s.coil;this.control('branch').value=s.branch;
      for(const b of this.root.querySelectorAll('[data-mode]')){b.setAttribute('aria-selected',String(b.dataset.mode===s.mode));b.tabIndex=b.dataset.mode===s.mode?0:-1;}
      this.root.querySelector('[role="tabpanel"]').setAttribute('aria-labelledby','mode-'+s.mode);
      for(const box of this.root.querySelectorAll('[data-part]'))box.checked=!!s.parts[box.dataset.part];
      this.ui('explode-wrap').hidden=s.mode!=='assembly';this.ui('unroll-wrap').hidden=s.mode!=='unroll';
      this.ui('mode-label').textContent={assembly:'正交投影 · 装配与尺寸参考',unroll:'参考半径弧长展开 · 左右切口相接',flat:'槽层展开 · 上层实线 / 下层虚线',circuit:'接触图生成的电路 · 正母线→负母线'}[s.mode];
      this.ui('pose').textContent=`转子 ${fmt(s.angle,1)}° · 视角 ${fmt(deg(s.yaw),0)}° / ${fmt(deg(s.pitch),0)}° · ${fmt(s.zoom*100,0)}%`;
      this.ui('shorts').textContent=`${this.electrical?.branches.length||this.model.poles}条主支路 · ${this.electrical?.commutatingCoils.length||0}只换向短路线圈`;
      this.ui('gesture').textContent=['flat','circuit'].includes(s.mode)?'单指／左键拖动平移，双指／滚轮缩放；左右切口表示同一圆周位置。':'左键／单指旋转视角；右键或Shift拖动平移；滚轮／双指缩放。点击铜线可选择线圈。';
      this.syncSelection();
    }
    bind() {
      this.on(this.root,'click',e=>{
        const mode=e.target.closest('[data-mode]');if(mode)this.setMode(mode.dataset.mode);
        const select=e.target.closest('[data-select-coil]');if(select)this.selectCoil(+select.dataset.selectCoil);
        const btn=e.target.closest('[data-action]');if(!btn)return;
        const a=btn.dataset.action;
        if(a==='zoom-in'||a==='zoom-out')this.setState({zoom:this.state.zoom*(a==='zoom-in'?1.25:.8)});
        if(a==='reset')this.resetCamera();
        if(a==='front')this.setState({yaw:Math.PI/2,pitch:0,panX:0,panY:0});
        if(a==='side')this.setState({yaw:0,pitch:0,panX:0,panY:0});
        if(a==='expand'){this.uiModule().classList.toggle('expanded');setTimeout(()=>this.resize(),50);}
        if(a==='play')this.togglePlay();
        if(a==='step')this.setState({angle:this.state.angle+360/this.model.parameters.slots});
        if(a==='prev-coil')this.selectCoil(M.mod((this.state.coil||1)-2,this.model.coils.length)+1);
        if(a==='next-coil')this.selectCoil((this.state.coil%this.model.coils.length)+1);
        if(a==='clear')this.selectCoil(0);
        if(a==='defaults'){this.setParameters(M.defaults);this.setState({angle:0,brushShift:0});}
        if(a==='json'||a==='csv')this.download(this.exportConnections(a),`motor-winding.${a}`,a==='json'?'application/json':'text/csv;charset=utf-8');
        if(a==='png'){const link=document.createElement('a');link.href=this.exportPNG();link.download='motor-winding-'+this.state.mode+'.png';link.click();}
      });
      this.on(this.root,'input',e=>{
        const key=e.target.dataset.control;if(!key)return;
        if(['angle','brushShift','zoom','explode','unroll'].includes(key))this.setState({[key]:+e.target.value/(['zoom','explode','unroll'].includes(key)?100:1)});
        if(key==='brushWidth')try{this.setParameters({brushWidth:+e.target.value});}catch(error){this.ui('error').textContent=error.message;this.syncUI();}
      });
      this.on(this.root,'change',e=>{if(e.target.dataset.part)this.setState({parts:{[e.target.dataset.part]:e.target.checked}});if(e.target.dataset.control==='coil')this.selectCoil(+e.target.value);if(e.target.dataset.control==='branch')this.selectBranch(+e.target.value);});
      this.on(this.ui('parameters'),'submit',e=>{e.preventDefault();const p={};for(const [key] of parameterFields)p[key]=+e.target.elements[key].value;p.provenance=e.target.elements.provenance.value;try{this.setParameters(p);}catch(error){this.ui('error').textContent=error.message;}});
      this.on(this.ui('import'),'change',async e=>{const input=e.target;try{const file=input.files[0];if(!file)return;if(file.size>1024*1024)throw new Error('参数JSON应小于1 MiB。');const data=JSON.parse(await file.text());this.setParameters(data.parameters||data);if(data.operatingState)this.setState({angle:data.operatingState.angleDeg,brushShift:data.operatingState.brushShiftDeg});}catch(error){this.ui('error').textContent=error.message;}finally{input.value='';}});
      this.on(this.root,'keydown',e=>{
        if(e.key==='Escape'){this.uiModule().classList.remove('expanded');this.resize();}
        if(e.target.matches('[data-mode]')&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const tabs=[...this.root.querySelectorAll('[data-mode]')],i=tabs.indexOf(e.target),next=e.key==='Home'?0:e.key==='End'?tabs.length-1:M.mod(i+(e.key==='ArrowRight'?1:-1),tabs.length);this.setMode(tabs[next].dataset.mode);tabs[next].focus();}
      });
      this.bindPointers();
    }
    uiModule(){return this.root.querySelector('.module');}
    togglePlay() {
      this.state.playing=!this.state.playing;const btn=this.root.querySelector('[data-action="play"]');btn.textContent=this.state.playing?'暂停转动':'缓慢转动';btn.setAttribute('aria-pressed',String(this.state.playing));
      cancelAnimationFrame(this.animation);let previous=0;
      const tick=t=>{if(!this.state.playing||this.destroyed)return;if(previous&&t-previous<200)this.setState({angle:this.state.angle+(t-previous)*.012});previous=t;this.animation=requestAnimationFrame(tick);};
      if(this.state.playing)this.animation=requestAnimationFrame(tick);
    }
    bindPointers() {
      const c=this.canvas,position=e=>{const r=c.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top,pan:e.button===2||e.shiftKey};};
      const pinch=()=>{const a=[...this.pointers.values()];return a.length>1?{x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2,d:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)||1}:null;};
      this.on(c,'pointerdown',e=>{if(e.pointerType==='mouse'&&e.button!==0&&e.button!==2)return;e.preventDefault();c.setPointerCapture(e.pointerId);const p=position(e);this.pointers.set(e.pointerId,p);this.press={x:p.x,y:p.y,moved:false};this.lastPinch=pinch();c.classList.add('dragging');});
      this.on(c,'pointermove',e=>{if(!this.pointers.has(e.pointerId))return;e.preventDefault();const old=this.pointers.get(e.pointerId),p=position(e);p.pan=old.pan;this.pointers.set(e.pointerId,p);const dx=p.x-old.x,dy=p.y-old.y;if(this.press&&Math.hypot(p.x-this.press.x,p.y-this.press.y)>5)this.press.moved=true;
        if(this.pointers.size>1){const n=pinch();if(this.lastPinch)this.setState({zoom:this.state.zoom*n.d/this.lastPinch.d,panX:this.state.panX+n.x-this.lastPinch.x,panY:this.state.panY+n.y-this.lastPinch.y});this.lastPinch=n;if(this.press)this.press.moved=true;}
        else if(p.pan||['flat','circuit'].includes(this.state.mode))this.setState({panX:this.state.panX+dx,panY:this.state.panY+dy});else this.setState({yaw:this.state.yaw+dx*.008,pitch:this.state.pitch+dy*.008});});
      const release=e=>{if(!this.pointers.has(e.pointerId))return;const p=position(e);if(e.type==='pointerup'&&this.pointers.size===1&&this.press&&!this.press.moved)this.pick(p.x,p.y);this.pointers.delete(e.pointerId);this.lastPinch=pinch();if(!this.pointers.size)c.classList.remove('dragging');};
      for(const type of ['pointerup','pointercancel','lostpointercapture'])this.on(c,type,release);
      this.on(c,'contextmenu',e=>e.preventDefault());this.on(c,'wheel',e=>{e.preventDefault();this.setState({zoom:this.state.zoom*Math.exp(-clamp(e.deltaY,-350,350)*.0015)});},{passive:false});
      this.on(c,'keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();const dx=e.key==='ArrowLeft'?-1:e.key==='ArrowRight'?1:0,dy=e.key==='ArrowUp'?-1:e.key==='ArrowDown'?1:0;if(e.shiftKey||['flat','circuit'].includes(this.state.mode))this.setState({panX:this.state.panX+dx*15,panY:this.state.panY+dy*15});else this.setState({yaw:this.state.yaw+dx*.1,pitch:this.state.pitch+dy*.1});}if(e.key==='+'||e.key==='=')this.setState({zoom:this.state.zoom*1.2});if(e.key==='-')this.setState({zoom:this.state.zoom/1.2});});
    }
    resize() {const r=this.canvas.getBoundingClientRect();if(r.width<2||r.height<2)return;this.W=r.width;this.H=r.height;this.dpr=Math.min(2,devicePixelRatio||1);this.canvas.width=Math.round(this.W*this.dpr);this.canvas.height=Math.round(this.H*this.dpr);this.invalidate();}
    invalidate() {if(this.frame||this.destroyed)return;this.frame=requestAnimationFrame(()=>{this.frame=0;this.draw();});}
    /* Geometry and four renderers follow. Only drawing code reads camera state. */
    coilStyle(index) {const c=this.electrical.coils[index],selected=this.state.coil===index+1,filter=this.state.branch;const active=!filter||c.branchId===filter;return{color:c.commutating?'#e88c22':COLORS[(c.branchId||1)-1],alpha:active?(this.state.coil && !selected ? .16 : 1):.06,width:selected?4.5:2.5};}
    label(x,y,text,color='#173442',size=12,bg=true) {if(x<0||x>this.W||y<0||y>this.H)return;const c=this.ctx;c.save();c.font=`600 ${size}px system-ui,sans-serif`;c.textAlign='center';c.textBaseline='middle';if(bg){const w=c.measureText(text).width+8;c.fillStyle=this.theme.surface;c.fillRect(x-w/2,y-size*.7,w,size*1.4);}c.fillStyle=color==='#173442'||color==='#53616a'?this.theme.text:color;c.fillText(text,x,y);c.restore();}
    line2(points,color,width=2,alpha=1,dash=false,coil=null) {const c=this.ctx;if(points.length<2)return;c.save();c.strokeStyle=color;c.lineWidth=width;c.globalAlpha=alpha;c.lineJoin='round';c.lineCap='round';c.setLineDash(dash?[5,4]:[]);c.beginPath();c.moveTo(...points[0]);for(const q of points.slice(1))c.lineTo(...q);c.stroke();c.restore();if(coil!==null&&alpha>.3)for(let i=1;i<points.length;i++)this.pickLines.push({a:points[i-1],b:points[i],coil});}
    arrow2(a,b,color='#173442') {const c=this.ctx,t=Math.atan2(b[1]-a[1],b[0]-a[0]),x=(a[0]+b[0])/2,y=(a[1]+b[1])/2;c.save();c.fillStyle=color;c.beginPath();c.moveTo(x+7*Math.cos(t),y+7*Math.sin(t));c.lineTo(x-5*Math.cos(t)+4*Math.sin(t),y-5*Math.sin(t)-4*Math.cos(t));c.lineTo(x-5*Math.cos(t)-4*Math.sin(t),y-5*Math.sin(t)+4*Math.cos(t));c.closePath();c.fill();c.restore();}
    pick(x,y) {let best=9,id=0;for(const l of this.pickLines||[]){const dx=l.b[0]-l.a[0],dy=l.b[1]-l.a[1],d=dx*dx+dy*dy,t=d?clamp(((x-l.a[0])*dx+(y-l.a[1])*dy)/d,0,1):0,dist=Math.hypot(x-l.a[0]-t*dx,y-l.a[1]-t*dy);if(dist<best){best=dist;id=l.coil;}}if(id)this.selectCoil(id);}
    draw() {if(!this.W||this.destroyed)return;const style=getComputedStyle(this.host);this.theme={background:style.getPropertyValue('--subtle').trim()||'#fafafa',surface:style.getPropertyValue('--surface').trim()||'#fff',text:style.getPropertyValue('--text').trim()||'#242424'};this.pickLines=[];const c=this.ctx;c.setTransform(this.dpr,0,0,this.dpr,0,0);c.fillStyle=this.theme.background;c.fillRect(0,0,this.W,this.H);if(this.state.mode==='flat')this.drawFlat();else if(this.state.mode==='circuit')this.drawCircuit();else this.drawSpatial();this.label(this.W/2,this.H-13,'尺寸与工况为示例 · '+(this.state.mode==='flat'?'同一编号对应同一线圈':'换向短路线圈电流未求解'),'#53616a',10,true);}
  }
  // Renderers use the topology's own paths. No view maintains a second winding.
  function periodicPairs(points, pitch) {
    const result=[],lo=-pitch/2,hi=M.TAU-pitch/2;
    for(const offset of [-M.TAU,0,M.TAU])for(let i=1;i<points.length;i++){
      const a={...points[i-1],a:points[i-1].a+offset},b={...points[i],a:points[i].a+offset},da=b.a-a.a;
      let t0=0,t1=1;
      if(Math.abs(da)<1e-10){if(a.a<lo-1e-9||a.a>hi+1e-9)continue;}
      else{const ts=[(lo-a.a)/da,(hi-a.a)/da].sort((x,y)=>x-y);t0=Math.max(0,ts[0]);t1=Math.min(1,ts[1]);if(t0>t1)continue;}
      const at=t=>({x:a.x+(b.x-a.x)*t,a:a.a+da*t,r:a.r+(b.r-a.r)*t});result.push([at(t0),at(t1)]);
    }
    return result;
  }
  MotorWindingViewer.prototype.drawSpatial=function(){
    const p=this.model.parameters,s=this.state,c=this.ctx,r=p.rotorDiameter/2,front=p.coreLength/2,commX=front+p.commutatorGap,
      commMove=s.mode==='assembly'?s.explode*r*.8:0,coilMove=s.mode==='assembly'?s.explode*p.slotDepth*1.3:0,shapes=[],alpha=rad(s.angle);
    const isUnroll=s.mode==='unroll',centerX=(commX+p.commutatorLength-front)/2;
    const totalLength=p.coreLength+p.commutatorGap+p.commutatorLength+2*p.endHeight+35;
    const scale=Math.min(this.W/(isUnroll?M.TAU*r*1.13:totalLength*1.15),this.H/(isUnroll?totalLength*1.15:(r+p.airGap+p.poleThickness+30)*2.35))*s.zoom;
    const project=xyz=>{const x=xyz[0]-(isUnroll?0:centerX),y=xyz[1],z=xyz[2];const h=x*Math.cos(s.yaw)+y*Math.sin(s.yaw),d=-x*Math.sin(s.yaw)+y*Math.cos(s.yaw);return[this.W/2+s.panX+h*scale,this.H/2+s.panY-(z*Math.cos(s.pitch)-d*Math.sin(s.pitch))*scale,d*Math.cos(s.pitch)+z*Math.sin(s.pitch)];};
    const coord=(x,a,rr)=>[x,rr*Math.cos(a),rr*Math.sin(a)];
    const face=(vertices,color,opacity)=>shapes.push({vertices,color,opacity,face:true});
    const wire=(vertices,color,width,opacity,coil=null,arrow=false)=>shapes.push({vertices,color,width,opacity,coil,arrow});
    const sector=(x1,x2,ri,ro,a0,a1,color,opacity,steps=8)=>{
      for(let j=0;j<steps;j++){
        const a=a0+(a1-a0)*j/steps,b=a0+(a1-a0)*(j+1)/steps;
        for(const rr of [ri,ro])face([coord(x1,a,rr),coord(x2,a,rr),coord(x2,b,rr),coord(x1,b,rr)],color,opacity);
        for(const x of [x1,x2])face([coord(x,a,ri),coord(x,a,ro),coord(x,b,ro),coord(x,b,ri)],color,opacity);
      }
      for(const a of [a0,a1])face([coord(x1,a,ri),coord(x1,a,ro),coord(x2,a,ro),coord(x2,a,ri)],color,opacity);
    };
    if(!isUnroll){
      if(s.parts.shaft)sector(-front-p.endHeight-15,commX+p.commutatorLength+commMove+24,0,p.shaftDiameter/2,0,M.TAU,'#7b8e9b',.7,32);
      if(s.parts.rotor){
        sector(-front,front,p.shaftDiameter/2,r-p.slotDepth,0,M.TAU,'#78929f',.2,40);
        for(let i=0;i<p.slots;i++){const a=alpha+(i+p.slotOpeningRatio/2)*this.model.pitch,b=alpha+(i+1-p.slotOpeningRatio/2)*this.model.pitch;sector(-front,front,r-p.slotDepth,r,a,b,'#75919e',.3,2);}
        for(let i=0;i<p.slots;i++)wire([coord(-front,alpha+i*this.model.pitch,r-p.slotDepth),coord(front,alpha+i*this.model.pitch,r-p.slotDepth)],'#8aa2ad',.8,.4);
      }
      if(s.parts.poles){const ri=r+p.airGap+s.explode*r*.8,ro=ri+p.poleThickness;
        for(let i=0;i<p.poles;i++){const a=(i+.5)*M.TAU/p.poles;sector(-front*.96,front*.96,ri,ro,a-.34*M.TAU/p.poles,a+.34*M.TAU/p.poles,i%2?'#668dbc':'#c7777e',.35,8);}
      }
      if(s.parts.commutator)for(let i=0;i<p.slots;i++){const a=alpha+(i-.5)*this.model.pitch,w=(1-p.micaRatio)*this.model.pitch/2;sector(commX+commMove,commX+p.commutatorLength+commMove,p.shaftDiameter/2+2,p.commutatorDiameter/2,a-w,a+w,'#b87943',.87,2);}
      if(s.parts.brushes)for(const b of this.electrical.brushes){const rr=p.commutatorDiameter/2,w=p.brushWidth*this.model.pitch/2;sector(commX+commMove+3,commX+commMove+p.commutatorLength-3,rr,rr+12,b.angle-w,b.angle+w,b.polarity>0?'#b64b58':'#447fa9',.95,4);}
    }
    const unroll=q=>{
      const k=1-s.unroll,t=q.a-(Math.PI-this.model.pitch/2),base=r;
      const y=k<1e-5?q.r-base:(base/k+q.r-base)*Math.cos(k*t)-base/k;
      const z=k<1e-5?base*t:(base/k+q.r-base)*Math.sin(k*t);
      return[z,y+base*(1-s.unroll),centerX-q.x];
    };
    if(isUnroll && s.parts.rotor){
      for(let i=0;i<p.slots;i++){
        const a=alpha+i*this.model.pitch;
        for(const pair of periodicPairs([{x:-front,a,r},{x:front,a,r}],this.model.pitch))wire(pair.map(unroll),'#9bb0ba',1,.6);
      }
    }
    if(s.parts.coil)for(const coil of this.model.coils){
      const style=this.coilStyle(coil.index),es=this.electrical.coils[coil.index];
      coil.segments.forEach((segment,j)=>{
        const pts=segment.map((q,k)=>{const onComm=(j===0&&k===0)||(j===5&&k===segment.length-1);return{x:q.x+(onComm?commMove:0),a:q.a+alpha,r:q.r+(onComm?0:coilMove)};});
        if(isUnroll){for(const pair of periodicPairs(pts,this.model.pitch))wire(pair.map(unroll),style.color,style.width,style.alpha,coil.id);}
        else for(let k=1;k<pts.length;k++)wire([M.cartesian(pts[k-1]),M.cartesian(pts[k])],style.color,style.width,style.alpha,coil.id,s.parts.currents&&j===1&&es.current!==null&&Math.abs(es.current)>1e-6);
      });
    }
    for(const item of shapes){item.screen=item.vertices.map(project);item.depth=item.screen.reduce((v,q)=>v+q[2],0)/item.screen.length;}
    shapes.sort((a,b)=>a.depth-b.depth);
    for(const item of shapes){
      const ps=item.screen.map(q=>q.slice(0,2));
      if(item.face){c.save();c.globalAlpha=item.opacity;c.fillStyle=item.color;c.beginPath();c.moveTo(...ps[0]);for(const q of ps.slice(1))c.lineTo(...q);c.closePath();c.fill();c.restore();}
      else{if(item.opacity>.3)this.line2(ps,'#ffffff',item.width+1.5,item.opacity*.65);this.line2(ps,item.color,item.width,item.opacity,false,item.coil);if(item.arrow&&item.opacity>.3){const es=this.electrical.coils[item.coil-1],dir=Math.sign(es.current);this.arrow2(...(dir>0?ps:ps.slice().reverse()),item.color);}}
    }
    if(!isUnroll){
      if(s.parts.poles)for(let i=0;i<p.poles;i++){const a=(i+.5)*M.TAU/p.poles,screen=project(coord(0,a,r+p.airGap+p.poleThickness+8+s.explode*r*.8));this.label(screen[0],screen[1],i%2?'S':'N',i%2?'#346388':'#a43d48',14);}
      if(s.parts.brushes)for(const b of this.electrical.brushes){const q=project(coord(commX+p.commutatorLength/2+commMove,b.angle,p.commutatorDiameter/2+21));this.label(q[0],q[1],`B${b.id}${b.polarity>0?'＋':'−'}`,b.polarity>0?'#a43d48':'#346388',11);}
      if(s.parts.numbers)for(let i=0;i<p.slots;i++){const q=project(coord(-front-6,alpha+i*this.model.pitch,r+2));this.label(q[0],q[1],String(i+1),'#345464',10);const bar=project(coord(commX+p.commutatorLength+commMove+3,alpha+(i-.5)*this.model.pitch,p.commutatorDiameter/2+2));this.label(bar[0],bar[1],String(i+1),'#805329',9);}
      const a=project([-front,0,-r-15]),b=project([front,0,-r-15]);this.line2([a.slice(0,2),b.slice(0,2)],'#69818e',1);this.label((a[0]+b[0])/2,(a[1]+b[1])/2+12,`有效长度 ${p.coreLength} mm`,'#53616a',10);
    }else if(s.parts.numbers)for(let i=0;i<p.slots;i++){
      const aa=M.mod(alpha+i*this.model.pitch+this.model.pitch/2,M.TAU)-this.model.pitch/2;
      const q=project(unroll({x:-front-5,a:aa,r}));this.label(q[0],q[1],String(i+1),'#345464',10);
    }
  };
  MotorWindingViewer.prototype.drawFlat=function(){
    const p=this.model.parameters,s=this.state,c=this.ctx,r=p.rotorDiameter/2,front=p.coreLength/2,commX=front+p.commutatorGap,alpha=rad(s.angle);
    const lo=-this.model.pitch/2,hi=M.TAU-this.model.pitch/2,width=M.TAU*r,total=p.coreLength+p.commutatorGap+p.commutatorLength+2*p.endHeight+35;
    const scale=Math.min((this.W-35)/(width+25),(this.H-65)/total)*s.zoom;
    const P=(angle,x)=>[this.W/2+s.panX+(angle-(lo+hi)/2)*r*scale,this.H/2+s.panY+((commX+p.commutatorLength-front)/2-x)*scale];
    const left=P(lo,0)[0],right=P(hi,0)[0],top=P(0,commX+p.commutatorLength+15)[1],bottom=P(0,-front-p.endHeight-15)[1];
    c.save();c.beginPath();c.rect(left,top,right-left,bottom-top);c.clip();
    if(s.parts.poles)for(let j=0;j<p.poles;j++)for(const t of [-M.TAU,0,M.TAU]){const a=(j+.16)*M.TAU/p.poles-alpha+t,b=(j+.84)*M.TAU/p.poles-alpha+t;if(b<lo||a>hi)continue;const q=P(a,front),v=P(b,-front);c.fillStyle=j%2?'#3f78ad0f':'#b74b580f';c.fillRect(q[0],q[1],v[0]-q[0],v[1]-q[1]);this.label((q[0]+v[0])/2,(q[1]+v[1])/2,j%2?'S':'N',j%2?'#6c8ba5':'#bc7e85',16,false);}
    for(let i=0;i<p.slots;i++){
      const a=i*this.model.pitch;
      if(s.parts.rotor){const q=P(a-p.slotOpeningRatio*this.model.pitch/2,front),b=P(a+p.slotOpeningRatio*this.model.pitch/2,-front);c.fillStyle='#d4e0e74f';c.fillRect(q[0],q[1],b[0]-q[0],b[1]-q[1]);}
      if(s.parts.numbers){const q=P(a,-front-10);this.label(q[0],q[1],String(i+1),'#36596b',11);}
    }
    if(s.parts.commutator)for(let i=0;i<p.slots;i++)for(const t of [-M.TAU,0,M.TAU]){const a=(i-.5)*this.model.pitch+t,w=(1-p.micaRatio)*this.model.pitch/2;if(a+w<lo||a-w>hi)continue;const q=P(a-w,commX+p.commutatorLength),b=P(a+w,commX);c.fillStyle='#d2a174';c.fillRect(q[0],q[1],b[0]-q[0],b[1]-q[1]);const lab=P(a,commX+p.commutatorLength/2);this.label(lab[0],lab[1],String(i+1),'#603f25',10,false);}
    if(s.parts.brushes)for(const brush of this.electrical.brushes)for(const t of [-M.TAU,0,M.TAU]){const a=brush.angle-alpha+t,w=p.brushWidth*this.model.pitch/2;if(a+w<lo||a-w>hi)continue;const q=P(a-w,commX+p.commutatorLength+8),b=P(a+w,commX+p.commutatorLength-2);c.fillStyle=brush.polarity>0?'#b74b58':'#3f78ad';c.fillRect(q[0],q[1],b[0]-q[0],b[1]-q[1]);const lab=P(a,commX+p.commutatorLength+17);this.label(lab[0],lab[1],`B${brush.id}${brush.polarity>0?'＋':'−'}`,brush.polarity>0?'#a43d48':'#346388',10);}
    if(s.parts.coil)for(const coil of this.model.coils){
      const st=this.coilStyle(coil.index),es=this.electrical.coils[coil.index];
      coil.segments.forEach((segment,j)=>{
        const offset=j===1?-p.slotOpeningRatio*this.model.pitch*.15:j===3?p.slotOpeningRatio*this.model.pitch*.15:0;
        for(const pair of periodicPairs(segment.map(q=>({...q,a:q.a+offset})),this.model.pitch)){
          const points=pair.map(q=>P(q.a,q.x));this.line2(points,st.color,st.width,st.alpha,j===3,coil.id);
          if(s.parts.currents&&(j===1||j===3)&&Math.abs(pair[0].x-pair[1].x)>p.coreLength*.7&&es.current!==null&&Math.abs(es.current)>1e-6&&st.alpha>.3)this.arrow2(...(es.current>0?points:points.slice().reverse()),st.color);
        }
      });
    }
    c.restore();this.line2([[left,top],[left,bottom]],'#7e98a6',1,.8,true);this.line2([[right,top],[right,bottom]],'#7e98a6',1,.8,true);
    this.label(this.W/2+s.panX,bottom+12,'左右同一切口 · 换向片1可在切口两边显示 · 层别作少量横向偏置','#53616a',10);
  };
  MotorWindingViewer.prototype.drawCircuit=function(){
    const e=this.electrical,s=this.state,c=this.ctx,maxRows=Math.max(...e.branches.map(b=>b.path.length)),width=Math.max(620,e.branches.length*145+70),height=180+maxRows*43;
    const scale=Math.min((this.W-30)/width,(this.H-60)/height)*s.zoom,P=(x,y)=>[this.W/2+s.panX+(x-width/2)*scale,this.H/2+s.panY+(y-height/2)*scale];
    const line=(a,b,color,w=3,opacity=1)=>this.line2([P(...a),P(...b)],color,w,opacity);
    line([30,40],[width-30,40],'#ad4655',3);line([30,height-40],[width-30,height-40],'#3578a4',3);
    let q=P(width/2,15);this.label(q[0],q[1],`＋母线  U=${fmt(this.model.parameters.supplyVoltage,1)} V`,'#a43d48',12);
    q=P(width/2,height-14);this.label(q[0],q[1],'−母线；两端点均来自当前刷片接触图','#346388',11);
    e.branches.forEach((b,i)=>{
      if(!s.parts.coil)return;
      const x=70+(width-140)*(i+.5)/e.branches.length,color=COLORS[i],active=!s.branch||s.branch===b.id;
      c.save();c.globalAlpha=active?1:.14;line([x,40],[x,height-40],color,3,active?1:.14);
      q=P(x,64);this.label(q[0],q[1],`支路${b.id} · B${b.fromBrush}→B${b.toBrush}`,color,11);
      b.path.forEach((edge,j)=>{
        const y=92+j*43,a=P(x-43,y-13),bb=P(x+43,y+14),selected=s.coil===edge.coil+1;
        c.fillStyle=selected?'#173442':'#ffffff';c.strokeStyle=color;c.lineWidth=selected?3:1.5;c.fillRect(a[0],a[1],bb[0]-a[0],bb[1]-a[1]);c.strokeRect(a[0],a[1],bb[0]-a[0],bb[1]-a[1]);
        this.label((a[0]+bb[0])/2,(a[1]+bb[1])/2,`${edge.direction>0?'→':'←'} C${edge.coil+1}`,selected?'#ffffff':color,Math.max(9,Math.min(12,13*scale)),false);
        this.pickLines.push({a:[a[0],(a[1]+bb[1])/2],b:[bb[0],(a[1]+bb[1])/2],coil:edge.coil+1});
      });
      q=P(x,height-64);this.label(q[0],q[1],`${fmt(b.current)} A`,color,11);c.restore();
    });
    this.label(this.W/2,this.H-33,'短路中的 '+(e.commutatingCoils.map(i=>'C'+i).join('、')||'无')+' 单独列于接触表，不计入普通串联路径。','#9c4d12',10);
  };
  root.MotorWindingViewer = MotorWindingViewer;
  if (root.customElements && !customElements.get('motor-winding-viewer')) customElements.define('motor-winding-viewer', class extends HTMLElement {
    connectedCallback(){if(!this.viewer||this.viewer.destroyed)this.viewer=new MotorWindingViewer(this);}
    disconnectedCallback(){queueMicrotask(()=>{if(!this.isConnected&&this.viewer)this.viewer.destroy();});}
  });
})(typeof globalThis !== 'undefined' ? globalThis : this);
