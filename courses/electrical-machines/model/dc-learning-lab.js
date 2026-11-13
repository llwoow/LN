(function (root) {
  'use strict';

  // Teaching model: symmetric simplex winding; not a geometrical wave-winding solver.
  function calculate(input) {
    const poles = Number(input.poles);
    const conductors = Number(input.conductors ?? 480);
    const armatureCurrent = Number(input.armatureCurrent);
    const flux = Number(input.flux ?? 0.025);
    const rpm = Number(input.rpm ?? 1200);
    const winding = input.winding;
    if (![2, 4, 6, 8].includes(poles) || !['lap', 'wave'].includes(winding) ||
        !Number.isFinite(conductors) || conductors <= 0 ||
        !Number.isFinite(armatureCurrent) || armatureCurrent < 0 ||
        !Number.isFinite(flux) || flux <= 0 || !Number.isFinite(rpm) || rpm < 0) {
      throw new RangeError('Invalid teaching-model parameters');
    }
    const branches = winding === 'lap' ? poles : 2; // A=2a
    const pairs = branches / 2;
    const seriesConductors = conductors / branches;
    const branchCurrent = armatureCurrent / branches;
    const ce = poles * conductors / (60 * branches);
    const ct = poles * conductors / (2 * Math.PI * branches);
    const emf = ce * flux * rpm;
    const torque = ct * flux * armatureCurrent;
    const power = emf * armatureCurrent;
    return { poles, winding, conductors, armatureCurrent, flux, rpm, branches,
      pairs, seriesConductors, branchCurrent, ce, ct, emf, torque, power };
  }

  const questions = Object.freeze({
    wave6: { answer: 'b', explanation: '正常单波绕组 A=2，与六极无关；每支路电流为 36/2=18 A。' },
    lap4: { answer: 'c', explanation: '四极单叠 A=P=4。每支路串联有效导体数 Z/A=480/4=120，不是线圈数。' },
    generator: { answer: 'a', explanation: '82 kW 是发电机额定端口输出：I=82000/230≈356.52 A。并励绕组从端口取电，所以 Ia=I+If。' },
    brushes: { answer: 'b', explanation: '若题目说的是电刷总压降 2 V，发电机电势 E=U+IaRa+2 V，不能再乘以 2。' },
    compare: { answer: 'c', explanation: '四极单叠 A=4、单波 A=2。相同 Z、Φ、n 时单波电势为两倍；若每根导体允许电流不变，单波允许总电流减半，不能无成本地增加容量。' }
  });

  function check(questionId, choice) {
    const q = questions[questionId];
    if (!q) throw new RangeError('Unknown question');
    return { correct: choice === q.answer, explanation: q.explanation };
  }

  function diagram(state) {
    const width = 760, left = 85, usable = 590, top = 42, bottom = 222;
    const paths = Array.from({ length: state.branches }, (_, i) => {
      const x = left + (i + 0.5) * usable / state.branches;
      return '<g><path d="M' + x + ' ' + top + ' V102 M' + x + ' 162 V' + bottom +
        '" stroke="currentColor" stroke-width="2"/>' +
        '<rect x="' + (x - 22) + '" y="102" width="44" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/>' +
        '<text x="' + x + '" y="137" text-anchor="middle" font-size="19" fill="currentColor">' + (i + 1) + '</text>' +
        '<text x="' + x + '" y="88" text-anchor="middle" font-size="16" fill="currentColor">' + state.branchCurrent.toFixed(1) + ' A</text></g>';
    }).join('');
    return '<svg viewBox="0 0 ' + width + ' 260" role="img" aria-label="' + state.branches +
      ' 条并联支路的等效图，每支路电流 ' + state.branchCurrent.toFixed(2) + ' 安培" focusable="false">' +
      '<path d="M' + left + ' ' + top + ' H' + (left + usable) + ' M' + left + ' ' + bottom + ' H' + (left + usable) +
      '" stroke="var(--accent)" stroke-width="3"/>' + paths +
      '<text x="18" y="47" font-size="18" fill="currentColor">+</text>' +
      '<text x="18" y="228" font-size="18" fill="currentColor">−</text>' +
      '<text x="380" y="250" text-anchor="middle" font-size="15" fill="currentColor">同一对电刷端之间的并联电路（拓扑示意）</text></svg>';
  }

  function mount(body) {
    if (!body) return;
    body.querySelectorAll('[data-dc-winding-lab]').forEach((host) => {
      if (host.dataset.mounted) return;
      host.dataset.mounted = 'true';
      host.innerHTML = '<div class="dc-lab-controls">' +
        '<label>磁极总数 P<select data-dc-poles><option value="2">2 极</option><option value="4" selected>4 极</option><option value="6">6 极</option><option value="8">8 极</option></select></label>' +
        '<label>绕组类型<select data-dc-winding><option value="lap">单叠绕组</option><option value="wave">正常单波绕组</option></select></label>' +
        '<label class="dc-lab-current">电枢总电流 Ia <input data-dc-current type="range" min="10" max="120" step="10" value="40"><output data-dc-current-value>40 A</output></label></div>' +
        '<div class="dc-lab-diagram" data-dc-diagram></div>' +
        '<div class="dc-lab-values" aria-live="polite">' +
        '<span>并联支路数 A<strong data-dc-value="branches">4</strong></span>' +
        '<span>支路对数 a<strong data-dc-value="pairs">2</strong></span>' +
        '<span>每支路电流<strong data-dc-value="branchCurrent">10 A</strong></span>' +
        '<span>每支路串联导体数<strong data-dc-value="seriesConductors">120</strong></span>' +
        '<span>感应电动势 E<strong data-dc-value="emf">240 V</strong></span>' +
        '<span>电磁功率 EIₐ<strong data-dc-value="power">9600 W</strong></span></div>';
      const poles = host.querySelector('[data-dc-poles]');
      const winding = host.querySelector('[data-dc-winding]');
      const current = host.querySelector('[data-dc-current]');
      function update() {
        const state = calculate({ poles: poles.value, winding: winding.value, armatureCurrent: current.value });
        host.querySelector('[data-dc-diagram]').innerHTML = diagram(state);
        host.querySelector('[data-dc-current-value]').textContent = state.armatureCurrent + ' A';
        for (const [field, value] of Object.entries({
          branches: state.branches, pairs: state.pairs,
          branchCurrent: state.branchCurrent.toFixed(2) + ' A',
          seriesConductors: state.seriesConductors.toFixed(0),
          emf: state.emf.toFixed(1) + ' V',
          power: state.power.toFixed(1) + ' W'
        })) host.querySelector('[data-dc-value="' + field + '"]').textContent = value;
      }
      [poles, winding, current].forEach((input) => input.addEventListener('input', update));
      update();
    });
    body.querySelectorAll('[data-dc-question]').forEach((card) => {
      if (card.dataset.mounted) return;
      card.dataset.mounted = 'true';
      const button = card.querySelector('[data-dc-check]');
      const feedback = card.querySelector('[data-dc-feedback]');
      if (!button || !feedback) return;
      button.addEventListener('click', () => {
        const selected = card.querySelector('input[type="radio"]:checked');
        if (!selected) {
          feedback.textContent = '先选择一个答案，再检查。';
          return;
        }
        const result = check(card.dataset.dcQuestion, selected.value);
        feedback.textContent = (result.correct ? '正确。' : '不正确。') + result.explanation;
        feedback.dataset.correct = String(result.correct);
      });
    });
  }

  const api = { calculate, check, mount };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.LN_DCMachinesLabs = api;
})(typeof window === 'undefined' ? null : window);
