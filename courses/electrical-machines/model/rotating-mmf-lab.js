/* Three-phase rotating MMF: two-pole idealized teaching model. */
(function (root) {
  'use strict';
  const PI = Math.PI, TAU = 2 * PI;
  const offsets = [0, 2 * PI / 3, 4 * PI / 3];
  const colors = ['#329fe4', '#c68c3c', '#36a77f'];
  const gold = '#d49b27';
  const stageInfo = [
    ['① 单相脉振', '单独看 A 相：空间轴线固定，但电流会变号，瞬时磁动势正负反转。仅靠一相不能形成幅值恒定的旋转基波。', 'fA1 = Fφ1 cosθ · cosωt'],
    ['② 三相叠加', 'A、B、C 相绕组在空间相差 120°，电流在时间上相差 120°。蓝、棕、绿波形逐点叠加，黄色曲线就是合成基波。', 'fΣ = fA1 + fB1 + fC1 = 1.5 Fφ1 cos(θ−ωt)'],
    ['③ 恒幅旋转', '注意黄色波峰在水平方向移动，而峰高始终为单相峰值的 1.5 倍。固定一点仍会观察到磁动势随时间正弦变化。', 'θ峰值 = ωt (mod 360°)，FΣ = 1.5 Fφ1'],
    ['④ 正反向分解', '单相脉振波可分为等幅正向波和反向波。三相正向波同相叠加、反向波因相位对称而抵消，最终只剩恒幅正向旋转波。', 'cosθ cosωt = ½cos(θ−ωt) + ½cos(θ+ωt)']
  ];
  function calculate(phase, theta) {
    const currents = offsets.map(shift => Math.cos(phase - shift));
    const perPhase = offsets.map((shift, i) => currents[i] * Math.cos(theta - shift));
    const total = perPhase.reduce((a, b) => a + b, 0);
    const forward = 1.5 * Math.cos(theta - phase);
    const backward = 0.5 * offsets.reduce((s, shift) => s + Math.cos(theta + phase - 2 * shift), 0);
    return { currents, perPhase, total, forward, backward };
  }
  function mount(body) {
    body.querySelectorAll('[data-mmf-lab]').forEach(host => {
      if (host.dataset.mmfMounted === 'true') return;
      host.dataset.mmfMounted = 'true';
      host.innerHTML = '<div class="mmf-stages" role="group" aria-label="讲解阶段">' +
        stageInfo.map((s, i) => '<button type="button" data-stage="' + i + '" aria-pressed="' + (i === 1) + '">' + s[0] + '</button>').join('') + '</div>' +
        '<div class="mmf-grid">' +
        '<div class="mmf-panel mmf-rotor"><div class="mmf-heading">定子横截面：磁动势轴线</div>' +
        '<svg viewBox="0 0 230 242" role="img" aria-label="二极定子磁动势轴线旋转示意">' +
        '<defs><marker id="mmf-arrow-47" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="' + gold + '"/></marker></defs>' +
        '<circle cx="115" cy="112" r="89" fill="none" stroke="var(--muted)" stroke-opacity=".5" stroke-width="2"/>' +
        '<circle cx="115" cy="112" r="76" fill="none" stroke="var(--muted)" stroke-opacity=".25"/>' +
        '<g data-axes stroke="var(--muted)" stroke-dasharray="4 4" stroke-opacity=".45"></g>' +
        '<g fill="currentColor" font-size="12" text-anchor="middle"><text x="115" y="13">A+</text><text x="210" y="174">B+</text><text x="20" y="174">C+</text></g>' +
        '<g data-vectors></g>' +
        '<line data-opposite x1="115" y1="112" x2="115" y2="185" stroke="#db7777" stroke-width="3" stroke-linecap="round"/>' +
        '<line data-result x1="115" y1="112" x2="115" y2="34" stroke="' + gold + '" stroke-width="5" stroke-linecap="round" marker-end="url(#mmf-arrow-47)"/>' +
        '<circle cx="115" cy="112" r="3.5" fill="currentColor"/>' +
        '<text data-rotor-label x="115" y="237" text-anchor="middle" font-size="12" fill="currentColor">波峰：0° 电角度</text>' +
        '</svg><p class="mmf-small">图中顺时针为 θ 正方向；箭头表示磁动势轴线，非磁感线或转子运动。</p></div>' +
        '<div class="mmf-panel"><div class="mmf-phase"><strong class="mmf-heading">时间相位 ωt</strong><output data-phase>0°</output></div>' +
        '<input data-slider class="mmf-slider" type="range" min="0" max="360" step="1" value="0" aria-label="拖动时间电角度 0 到 360 度"/>' +
        '<div class="mmf-tools"><button type="button" data-play aria-label="播放或暂停动画">▶ 播放</button>' +
        '<button type="button" data-step>单步 +60°</button><button type="button" data-reset>重置</button>' +
        '<label>速度 <select data-speed aria-label="动画速度"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label></div>' +
        '<div class="mmf-heading">三相瞬时电流（按峰值归一化）</div>' +
        ['A','B','C'].map((c, i) => '<div class="mmf-current"><strong style="color:' + colors[i] + '">' + c + '</strong><div class="mmf-track"><span class="mmf-bar" data-bar="' + i + '" style="background:' + colors[i] + '"></span></div><output data-value="' + i + '">0.00</output></div>').join('') +
        '<p class="mmf-small">各相电流改变其对应磁动势的瞬时方向与大小。</p></div></div>' +
        '<div class="mmf-panel" style="margin-top:.75rem"><div class="mmf-axis-select"><strong class="mmf-heading">沿定子圆周展开：空间磁动势</strong>' +
        '<label class="mmf-small">横轴范围 <select data-range aria-label="空间电角度显示范围"><option value="360">0°～360°</option><option value="720">−180°～540°</option><option value="1080" selected>−360°～720°</option></select></label></div>' +
        '<div class="mmf-scroll" tabindex="0" role="region" aria-label="空间磁动势波形，可横向滚动">' +
        '<svg viewBox="0 0 920 259" role="img" aria-label="单相及三相合成磁动势的空间曲线">' +
        '<g data-grid></g><g data-curves></g><g data-peaks></g>' +
        '<text x="12" y="15" font-size="12" fill="var(--muted)">f / Fφ1</text>' +
        '<text x="906" y="254" font-size="12" text-anchor="end" fill="var(--muted)">空间电角度 θ (°)</text></svg></div>' +
        '<div data-legend class="mmf-legend"></div>' +
        '<p class="mmf-legend-label">黄色虚线跟踪每个周期的正峰值。−360°～720° 是基波延拓，不是三个实际磁极周期。</p></div>' +
        '<div class="mmf-note" aria-live="polite"><strong data-title>② 三相叠加</strong><p data-explain></p><p data-equation class="mmf-eq-inline"></p></div>';
      const $ = s => host.querySelector(s);
      let stage = 1, range = 1080, phase = 0, speed = 1;
      let playing = false, last = 0;
      const rad = d => d * PI / 180;
      const point = (deg, radius) => [115 + radius * Math.sin(rad(deg)), 112 - radius * Math.cos(rad(deg))];
      const axes = offsets.map(shift => {
        const p = point(shift * 180 / PI, 85), q = point(shift * 180 / PI + 180, 85);
        return '<line x1="' + p[0] + '" y1="' + p[1] + '" x2="' + q[0] + '" y2="' + q[1] + '"/>';
      }).join('');
      $('[data-axes]').innerHTML = axes;
      const X0 = 53, XWidth = 849, Y0 = 125, YScale = 64;
      function domain() { return range === 360 ? [0, 360] : (range === 720 ? [-180, 540] : [-360, 720]); }
      function xOf(deg) { const d = domain(); return X0 + (deg - d[0]) * XWidth / (d[1] - d[0]); }
      function yOf(val) { return Y0 - YScale * val; }
      function linePath(fn) {
        const d = domain(); let out = '';
        for (let i = 0; i <= 360; i++) {
          const th = rad(d[0] + (d[1] - d[0]) * i / 360);
          out += (i ? 'L' : 'M') + xOf(th * 180 / PI).toFixed(2) + ',' + yOf(fn(th)).toFixed(2);
        }
        return out;
      }
      function curve(fn, color, width, opacity, dash) {
        return '<path d="' + linePath(fn) + '" stroke="' + color + '" fill="none" stroke-width="' + width + '"' +
          ' opacity="' + opacity + '"' + (dash ? ' stroke-dasharray="' + dash + '"' : '') +
          ' stroke-linejoin="round" stroke-linecap="round"/>';
      }
      function legend(color, name) { return '<span class="mmf-key"><i class="mmf-swatch" style="background:' + color + '"></i>' + name + '</span>'; }
      function drawGrid() {
        const d = domain(), step = range === 360 ? 90 : 180;
        let html = '';
        [-1.5,-1,0,1,1.5].forEach(v => {
          const y = yOf(v);
          html += '<line x1="53" y1="' + y + '" x2="902" y2="' + y + '" stroke="var(--muted)" stroke-opacity="' + (v === 0 ? '.55' : '.23') + '"/>';
          html += '<text x="44" y="' + (y + 4) + '" text-anchor="end" fill="var(--muted)" font-size="12">' + v + '</text>';
        });
        for (let deg = d[0]; deg <= d[1]; deg += step) {
          const x = xOf(deg);
          html += '<line x1="' + x + '" y1="22" x2="' + x + '" y2="223" stroke="var(--muted)" stroke-opacity="' + (deg === 0 ? '.6' : '.25') + '" stroke-dasharray="3 5"/>';
          html += '<text x="' + x + '" y="241" fill="var(--muted)" font-size="12" text-anchor="middle">' + deg + '°</text>';
        }
        $('[data-grid]').innerHTML = html;
      }
      function draw() {
        const deg = phase * 180 / PI;
        $('[data-phase]').textContent = Math.round(deg) + '° / 360°';
        $('[data-slider]').value = Math.round(deg);
        const c = calculate(phase, 0).currents;
        c.forEach((val, i) => {
          const bar = $('[data-bar="' + i + '"]');
          bar.style.left = (val >= 0 ? 50 : 50 + 50 * val) + '%';
          bar.style.width = 50 * Math.abs(val) + '%';
          $('[data-value="' + i + '"]').textContent = (val >= 0 ? '+' : '') + val.toFixed(2);
        });
        const showCount = stage === 0 ? 1 : 3;
        let vectors = '';
        for (let i = 0; i < showCount; i++) {
          const p = point(offsets[i] * 180 / PI, 72 * c[i]);
          vectors += '<line x1="115" y1="112" x2="' + p[0] + '" y2="' + p[1] + '" stroke="' + colors[i] +
            '" stroke-width="3" stroke-linecap="round" opacity="' + (stage === 2 ? '.45' : '1') + '"/>' +
            '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="3" fill="' + colors[i] + '"/>';
        }
        $('[data-vectors]').innerHTML = vectors;
        const single = stage === 0;
        const angle = single ? (c[0] >= 0 ? 0 : 180) : deg;
        const peak = point(angle, 78), opposite = point(angle + 180, 70);
        $('[data-result]').style.display = single ? 'none' : '';
        $('[data-opposite]').style.display = single ? 'none' : '';
        $('[data-result]').setAttribute('x2', peak[0]); $('[data-result]').setAttribute('y2', peak[1]);
        $('[data-opposite]').setAttribute('x2', opposite[0]); $('[data-opposite]').setAttribute('y2', opposite[1]);
        $('[data-rotor-label]').textContent = single ? 'A 相固定轴线（脉振）' : '合成波正峰值：' + Math.round(deg) + '°';
        const f = (i, th) => c[i] * Math.cos(th - offsets[i]);
        let lines = '', labels = '';
        if (stage === 0) {
          lines = curve(th => f(0, th), colors[0], 3, 1);
          labels = legend(colors[0], 'A 相脉振');
        } else if (stage === 1) {
          for (let i = 0; i < 3; i++) lines += curve(th => f(i, th), colors[i], 2.1, .8);
          lines += curve(th => 1.5 * Math.cos(th - phase), gold, 3.7, 1);
          labels = legend(colors[0], 'A 相') + legend(colors[1], 'B 相') + legend(colors[2], 'C 相') + legend(gold, '合成');
        } else if (stage === 2) {
          for (let i = 0; i < 3; i++) lines += curve(th => f(i, th), colors[i], 1.6, .23);
          lines += curve(th => 1.5 * Math.cos(th - phase), gold, 4, 1);
          labels = legend(gold, '恒幅旋转波') + legend(colors[0], '单相贡献（淡色）');
        } else {
          lines += curve(th => .5 * Math.cos(th - phase), '#d58542', 2.4, 1, '6 4');
          lines += curve(th => .5 * Math.cos(th + phase), '#c476b3', 2.4, 1, '6 4');
          lines += curve(th => f(0, th), colors[0], 2.3, .88);
          lines += curve(th => 1.5 * Math.cos(th - phase), gold, 3.7, 1);
          labels = legend('#d58542', 'A 相正向波') + legend('#c476b3', 'A 相反向波') +
            legend(colors[0], 'A 相脉振') + legend(gold, '三相合成');
        }
        $('[data-curves]').innerHTML = lines;
        $('[data-legend]').innerHTML = labels;
        let peaks = '';
        if (!single) {
          const d = domain();
          for (let k = -5; k <= 5; k++) {
            const at = deg + 360 * k;
            if (at < d[0] - .0001 || at > d[1] + .0001) continue;
            const x = xOf(at);
            peaks += '<line x1="' + x + '" y1="22" x2="' + x + '" y2="223" stroke="' + gold +
              '" stroke-opacity=".6" stroke-dasharray="5 5"/><circle cx="' + x + '" cy="' + yOf(1.5) + '" r="4" fill="' + gold + '"/>';
          }
        }
        $('[data-peaks]').innerHTML = peaks;
        $('[data-title]').textContent = stageInfo[stage][0];
        $('[data-explain]').textContent = stageInfo[stage][1];
        $('[data-equation]').textContent = stageInfo[stage][2];
      }
      function setPlaying(flag) { playing = flag; $('[data-play]').textContent = playing ? 'Ⅱ 暂停' : '▶ 播放'; }
      host.querySelectorAll('[data-stage]').forEach(button => {
        button.addEventListener('click', () => {
          stage = Number(button.dataset.stage);
          host.querySelectorAll('[data-stage]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
          draw();
        });
      });
      $('[data-play]').addEventListener('click', () => setPlaying(!playing));
      $('[data-step]').addEventListener('click', () => {
        setPlaying(false);
        phase = ((Math.floor(phase / (PI / 3) + 1e-7) + 1) % 6) * PI / 3;
        draw();
      });
      $('[data-reset]').addEventListener('click', () => { setPlaying(false); phase = 0; draw(); });
      $('[data-slider]').addEventListener('input', event => { setPlaying(false); phase = Number(event.target.value) * PI / 180; draw(); });
      $('[data-speed]').addEventListener('change', event => { speed = Number(event.target.value); });
      $('[data-range]').addEventListener('change', event => {
        range = Number(event.target.value); drawGrid(); draw();
      });
      drawGrid(); setPlaying(playing); draw();
      function frame(now) {
        if (!host.isConnected) return; // Navigation destroys the host; do not retain an animation loop.
        if (last && playing && !document.hidden && now - last > 30) {
          phase = (phase + Math.min(now - last, 100) * speed * TAU / 10000) % TAU;
          draw();
        }
        if (now - last > 30) last = now;
        requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    });
  }
  const api = { calculate, mount };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.LN_RotatingMMFLab = api;
})(typeof window !== 'undefined' ? window : null);
