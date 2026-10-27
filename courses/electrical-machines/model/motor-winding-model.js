/* MotorWindingModel 1.0 — SI electrical quantities, geometry in millimetres.
 * Standalone classic script (also CommonJS) so downloaded pages need no server. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MotorWindingModel = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const TAU = 2 * Math.PI;
  const mod = (x, n) => ((x % n) + n) % n;
  const wrap = a => mod(a + Math.PI, TAU) - Math.PI;
  const defaults = Object.freeze({
    poles: 4, slots: 16, turns: 12, winding: 'simplex-progressive-lap',
    rotorDiameter: 100, coreLength: 100, shaftDiameter: 20, slotDepth: 8,
    slotOpeningRatio: .38, airGap: 1, poleThickness: 14,
    commutatorDiameter: 52, commutatorLength: 24, commutatorGap: 30,
    endHeight: 18, brushWidth: .65, micaRatio: .08,
    wireArea: .4, temperature: 75, supplyVoltage: 22, rpm: 1200, fluxDensity: .6,
    provenance: '示例参数；未对应已测量的实机'
  });
  function validate(input) {
    const p = { ...defaults, ...input }, errors = [], warnings = [];
    for (const [key, value] of Object.entries(defaults)) {
      if (typeof value === 'number' && !Number.isFinite(p[key])) errors.push(`${key} 必须为有限数值。`);
    }
    if (errors.length) return { valid: false, errors, warnings, parameters: p };
    if (!Number.isInteger(p.poles) || p.poles < 2 || p.poles > 8 || p.poles % 2) errors.push('总极数 P 须为2—8之间的偶数。');
    if (!Number.isInteger(p.slots) || p.slots < 8 || p.slots > 64 || p.slots % p.poles) errors.push('槽数 Q 须为8—64的整数，并能被总极数整除。');
    if (p.slots / p.poles < 2) errors.push('本模型每极至少需要2槽。');
    if (!Number.isInteger(p.turns) || p.turns < 1 || p.turns > 200) errors.push('每线圈匝数须为1—200的整数。');
    if (p.winding !== defaults.winding) errors.push('当前生成器仅实现双层、全距、单叠叠进绕组；其他形式不可套用此接线。');
    if (typeof p.provenance !== 'string' || p.provenance.length > 200) errors.push('参数来源须为不超过200字的文本。');
    const ranges = { rotorDiameter: [30, 1000], coreLength: [20, 2000], shaftDiameter: [2, 500], slotDepth: [1, 100], airGap: [.1, 20], poleThickness: [2, 200], commutatorDiameter: [10, 800], commutatorLength: [5, 300], commutatorGap: [5, 500], endHeight: [3, 300], brushWidth: [.2, 1.4], micaRatio: [.02, .2], slotOpeningRatio: [.15, .6], wireArea: [.05, 100], temperature: [-20, 180], supplyVoltage: [0, 1000], rpm: [-6000, 6000], fluxDensity: [.01, 1.8] };
    for (const [key, [lo, hi]] of Object.entries(ranges)) if (p[key] < lo || p[key] > hi) errors.push(`${key} 超出本参考模型范围 ${lo}—${hi}。`);
    if (p.shaftDiameter / 2 + p.slotDepth >= p.rotorDiameter / 2) errors.push('槽底必须位于轴孔以外，并留有铁心轭部。');
    if (p.commutatorDiameter <= p.shaftDiameter + 4) errors.push('换向器外径须大于轴径，并留有绝缘与基体空间。');
    if (p.commutatorDiameter >= p.rotorDiameter) errors.push('本结构要求换向器外径小于转子外径。');
    if (p.commutatorGap <= p.endHeight + 3) errors.push('前端绕组与换向器的轴向示例空间不足；增大轴向间距。');
    if (p.brushWidth <= p.micaRatio) errors.push('刷宽必须大于云母缝宽，否则可能完全失去接触。');
    if (p.brushWidth + 1 - p.micaRatio >= p.slots / p.poles) errors.push('刷宽过大：某些转角可能让异极电刷接触同一片，造成母线短接。');
    const radius = p.rotorDiameter / 2;
    const slotArea = .5 * (radius ** 2 - (radius - p.slotDepth) ** 2) * TAU / p.slots * p.slotOpeningRatio;
    const fill = 2 * p.turns * p.wireArea / slotArea;
    if (fill >= 1) errors.push('裸铜面积已达到或超过槽截面积，几何上不可容纳。');
    else if (fill > .5) warnings.push('示例毛槽满率超过50%；尚未扣除漆膜、槽衬、层间绝缘和槽楔，须单独校核。');
    warnings.push('端部曲线为有尺寸的层级路由示意；未进行绝缘、弯曲半径、三维碰撞或制造工艺校核。');
    return { valid: !errors.length, errors, warnings, parameters: p, slotArea, grossFill: fill };
  }
  const point = (x, a, r) => ({ x, a, r });
  const cartesian = q => [q.x, q.r * Math.cos(q.a), q.r * Math.sin(q.a)];
  function length(points) {
    let sum = 0;
    for (let i = 1; i < points.length; i++) {
      const a = cartesian(points[i - 1]), b = cartesian(points[i]);
      sum += Math.hypot(...a.map((v, k) => v - b[k]));
    }
    return sum;
  }
  function createModel(input = {}) {
    const validation = validate(input);
    if (!validation.valid) { const e = new RangeError(validation.errors.join('\n')); e.validation = validation; throw e; }
    const p = validation.parameters, Q = p.slots, pitch = TAU / Q, span = Q / p.poles;
    const r = p.rotorDiameter / 2, topR = r - .3 * p.slotDepth, lowerR = r - .75 * p.slotDepth;
    const xFront = p.coreLength / 2, xComm = xFront + p.commutatorGap, cr = p.commutatorDiameter / 2;
    const coils = Array.from({ length: Q }, (_, i) => {
      const a = i * pitch, b = (i + span) * pitch;
      const leadIn = [point(xComm, (i - .5) * pitch, cr), point(xFront + p.endHeight + 2, a - .015, topR), point(xFront, a, topR)];
      const top = [point(xFront, a, topR), point(-xFront, a, topR)];
      const rear = [], front = [];
      for (let j = 0; j <= 16; j++) {
        const t = j / 16;
        rear.push(point(-xFront - p.endHeight * Math.sin(Math.PI * t), a + (b - a) * t, topR + (lowerR - topR) * t));
        front.push(point(xFront + p.endHeight * Math.sin(Math.PI * t), b + (a - b) * t, lowerR + (topR - .8 - lowerR) * t));
      }
      const bottom = [point(-xFront, b, lowerR), point(xFront, b, lowerR)];
      const leadOut = [point(xFront, a, topR - .8), point(xFront + p.endHeight + 4, a + .015, topR - .8), point(xComm, (i + .5) * pitch, cr)];
      const turnLengthMM = length(top) + length(rear) + length(bottom) + length(front);
      const copperLengthM = (p.turns * turnLengthMM + length(leadIn) + length(leadOut)) / 1000;
      const resistance = .017241 * (1 + .00393 * (p.temperature - 20)) * copperLengthM / p.wireArea;
      return { id: i + 1, index: i, upperSlot: i + 1, lowerSlot: mod(i + span, Q) + 1,
        upperSide: 2 * i + 1, lowerSide: 2 * mod(i + span, Q) + 2,
        startBar: i + 1, endBar: mod(i + 1, Q) + 1,
        segments: [leadIn, top, rear, bottom, front, leadOut],
        turnLengthMM, copperLengthM, resistance, topR, lowerR };
    });
    const slots = Array.from({ length: Q }, (_, i) => ({ id: i + 1, upperCoil: i + 1, lowerCoil: mod(i - span, Q) + 1 }));
    return { schema: 'motor-winding-model/v1', parameters: p, validation, coils, slots,
      pitch, span, poles: p.poles, barOffset: -pitch / 2,
      pitches: { coilSlots: span, backSidePositions: 2 * span + 1, frontDirectedSidePositions: 1 - 2 * span, resultantSidePositions: 2, commutatorBars: 1 },
      equalPotentialGroups: Array.from({ length: 2 * span }, (_, i) => Array.from({ length: p.poles / 2 }, (_, j) => i + 2 * span * j + 1)) };
  }
  function electricalState(model, angleDeg = 0, brushShiftDeg = 0) {
    const p = model.parameters, Q = p.slots, alpha = angleDeg * Math.PI / 180, shift = brushShiftDeg * Math.PI / 180;
    if (!Number.isFinite(alpha) || !Number.isFinite(shift)) throw new RangeError('转角与刷架角须为有限数值。');
    const omega = p.rpm * TAU / 60, period = TAU / p.poles;
    const brushes = Array.from({ length: p.poles }, (_, j) => {
      const angle = j * period + shift;
      const bars = Array.from({ length: Q }, (_, k) => k).filter(k => Math.abs(wrap(alpha + (k - .5) * model.pitch - angle)) < (p.brushWidth + 1 - p.micaRatio) * model.pitch / 2 - 1e-10);
      return { id: j + 1, polarity: j % 2 === 0 ? 1 : -1, angle, bars };
    });
    const contact = new Map(), errors = [];
    for (const b of brushes) {
      if (!b.bars.length) errors.push(`电刷${b.id}未接触任何换向片。`);
      for (const k of b.bars) {
        if (contact.has(k) && contact.get(k).id !== b.id) errors.push(`换向片${k + 1}被多只电刷同时接触。`);
        contact.set(k, b);
      }
    }
    const B = (radius, theta) => fieldAt(model, radius, theta).radial;
    const states = model.coils.map(c => {
      const theta = alpha + c.index * model.pitch;
      const torquePerAmp = -p.turns * p.coreLength / 1000 * (c.topR / 1000 * B(c.topR,theta) - c.lowerR / 1000 * B(c.lowerR,theta + model.span * model.pitch));
      const from = contact.get(c.index), to = contact.get(mod(c.index + 1, Q));
      return { id: c.id, emf: -omega * torquePerAmp, torquePerAmp,
        commutating: !!from && !!to && from.id === to.id, brushId: from?.id === to?.id ? from?.id : null,
        branchId: null, direction: 0, current: null };
    });
    const branches = [], visited = new Set();
    for (const brush of brushes) for (const start of brush.bars) for (const step of [1, -1]) {
      const firstCoil = mod(start + (step === 1 ? 0 : -1), Q);
      if (states[firstCoil].commutating || visited.has(firstCoil)) continue;
      let node = start; const path = [];
      for (let guard = 0; guard <= Q; guard++) {
        const index = mod(node + (step === 1 ? 0 : -1), Q);
        if (visited.has(index)) break;
        path.push({ coil: index, direction: step }); visited.add(index); node = mod(node + step, Q);
        const endBrush = contact.get(node);
        if (endBrush) {
          if (endBrush.id === brush.id || endBrush.polarity === brush.polarity) errors.push('某主支路未连接相反极性的电刷。');
          const forward = brush.polarity === 1;
          const oriented = forward ? path : path.slice().reverse().map(e => ({ coil: e.coil, direction: -e.direction }));
          branches.push({ id: 0, fromBrush: forward ? brush.id : endBrush.id, toBrush: forward ? endBrush.id : brush.id,
            sector: Math.min(brush.id, endBrush.id) === 1 && Math.max(brush.id, endBrush.id) === p.poles ? p.poles - 1 : Math.min(brush.id, endBrush.id) - 1,
            path: oriented });
          break;
        }
      }
    }
    branches.sort((a, b) => a.sector - b.sector);
    for (let i = 0; i < branches.length; i++) {
      const b = branches[i]; b.id = i + 1;
      b.resistance = b.path.reduce((s, e) => s + model.coils[e.coil].resistance, 0);
      b.backEmf = -b.path.reduce((s, e) => s + e.direction * states[e.coil].emf, 0);
      b.current = errors.length || b.resistance <= 0 ? null : (p.supplyVoltage - b.backEmf) / b.resistance;
      for (const e of b.path) Object.assign(states[e.coil], { branchId: b.id, direction: e.direction, current: b.current === null ? null : e.direction * b.current });
    }
    if (branches.length !== p.poles) errors.push(`当前接触图产生${branches.length}条主支路，预期${p.poles}条。`);
    const unassigned = states.filter(c => !c.commutating && c.branchId === null);
    if (unassigned.length) errors.push('存在未分配到主支路的非换向线圈。');
    const current = branches.reduce((s, b) => s + (b.current ?? 0), 0);
    const copperLoss = branches.reduce((s, b) => s + (b.current ?? 0) ** 2 * b.resistance, 0);
    const conversionPower = branches.reduce((s, b) => s + b.backEmf * (b.current ?? 0), 0);
    const torque = states.reduce((s, c) => s + c.torquePerAmp * (c.current ?? 0), 0);
    return { angleDeg, brushShiftDeg, valid: !errors.length, errors, brushes: brushes.map(b => ({ ...b, bars: b.bars.map(k => k + 1) })),
      coils: states, branches, commutatingCoils: states.filter(c => c.commutating).map(c => c.id),
      estimate: { current, copperLoss, conversionPower, torque, inputPower: p.supplyVoltage * current,
        powerResidual: p.supplyVoltage * current - copperLoss - conversionPower,
        torquePowerResidual: torque * omega - conversionPower,
        scope: '仅非换向主支路的瞬时电阻近似；不包含换向线圈的电流、转矩和损耗。' } };
  }
  function fieldAt(model, radiusMM, theta) {
    // A_x=(Bm R/p)(r/R)^p cos(p theta): a source-free analytic multipole in
    // a homogeneous reference region. It is not a solved slotted iron field.
    const p=model.parameters.poles/2, ratio=radiusMM/(model.parameters.rotorDiameter/2);
    const amplitude=model.parameters.fluxDensity*ratio**(p-1);
    return { radial: -amplitude*Math.sin(p*theta), tangential: -amplitude*Math.cos(p*theta) };
  }
  function exportData(model, state) {
    return { schema: model.schema, createdAt: new Date().toISOString(), units: { geometry: 'mm', voltage: 'V', current: 'A', resistance: 'ohm', torque: 'N m' },
      parameters: model.parameters, conventions: { numbering: '1-based external labels; 0-based branch.path.coil', winding: 'T_i → B_(i+q) ; bar_i → bar_(i+1)', stator: 'fixed; rotor positive about +x by right hand', barOffsetDegrees: model.barOffset * 180 / Math.PI },
      pitches: model.pitches, validation: model.validation, connections: model.coils.map(({ segments, ...c }) => c), slots: model.slots,
      geometry: { coordinates: 'x / mm, a / rad, r / mm; undeformed rotor coordinates', coilPaths: model.coils.map(c => ({ coil: c.id, segments: c.segments })) },
      field: { type:'analytic-multipole-reference', referenceRadiusMM:model.parameters.rotorDiameter/2, potential:'A_x=(Bm*R/p)*(r/R)^p*cos(p*theta)', limits:'A harmonic field in a homogeneous reference region; not a solved field in slotted iron. Air-gap input changes geometry, not prescribed Bm.' },
      equalPotentialGroups: model.equalPotentialGroups, operatingState: state,
      limits: ['示例尺寸与工况，非经实机标定的性能预测。', '正弦径向磁场已给定；不求磁路饱和、电枢反应和换向极。', '无电感和接触电阻模型；短路线圈电流未解。', '无公差、绝缘、端部碰撞、温升和机械强度认证。'] };
  }
  function connectionsCSV(model) {
    return '\ufeffcoil,upper_slot,lower_slot,start_bar,end_bar,turns,resistance_ohm\r\n' + model.coils.map(c => [c.id, c.upperSlot, c.lowerSlot, c.startBar, c.endBar, model.parameters.turns, c.resistance.toFixed(8)].join(',')).join('\r\n');
  }
  return Object.freeze({ defaults, validate, createModel, electricalState, fieldAt, exportData, connectionsCSV, cartesian, mod, wrap, TAU });
});
