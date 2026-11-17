(function(root) {
  'use strict';
  // Normalized spatial fundamental for teaching; not a measured machine model.
  const k = 2.2;
  const F = (theta,q) => Math.sin(theta) + q*Math.cos(theta);
  const B = (theta,q,sat) => sat ? Math.tanh(k*F(theta,q))/Math.tanh(k) : F(theta,q);
  const integrate = f => {
    const n=600, h=Math.PI/n; let s=f(0)+f(Math.PI);
    for(let i=1;i<n;i++) s+=(i%2?4:2)*f(h*i);
    return s*h/3;
  };
  function calculate(q, saturated) {
    q=Number(q); if(!Number.isFinite(q)||q<0||q>0.8) throw new RangeError('q must be in [0, 0.8]');
    const sat=Boolean(saturated);
    return {q, saturated:sat, neutralShiftDeg:-Math.atan(q)*180/Math.PI,
      relativeFlux:integrate(t=>B(t,q,sat))/integrate(t=>B(t,0,sat))};
  }
  function graph(q,sat) {
    const x=t=>78+(t+Math.PI)*327/Math.PI;
    function curve(fn,y0) {
      let d='';
      for(let i=0;i<=240;i++){
        const t=-Math.PI+2*Math.PI*i/240, y=y0-53*Math.max(-1.5,Math.min(1.5,fn(t)));
        d+=(i?'L':'M')+x(t).toFixed(1)+' '+y.toFixed(1)+' ';
      }
      return d;
    }
    const main='<path d="'+curve(t=>Math.sin(t),148)+'" stroke="currentColor" stroke-width="2.7"/>';
    const arm='<path d="'+curve(t=>q*Math.cos(t),148)+'" stroke="var(--accent,currentColor)" stroke-dasharray="8 5" stroke-width="2.7"/>';
    const sum='<path d="'+curve(t=>F(t,q),148)+'" stroke="currentColor" stroke-dasharray="2 5" stroke-width="2.7"/>';
    const neutral=x(-Math.atan(q));
    return '<svg viewBox="0 0 810 445" role="img" aria-label="上下两幅共用空间坐标：上图主极、电枢和合成磁动势，下图空载与负载气隙磁密；竖虚线表示负载磁中性线。">'+
      '<g fill="none" stroke-linecap="round">'+
      '<path d="M78 148H732 M78 348H732 M405 58V424" stroke="currentColor" opacity=".35"/>'+
      main+arm+sum+
      '<path d="'+curve(t=>B(t,0,sat),348)+'" stroke="currentColor" stroke-dasharray="8 5" stroke-width="3"/>'+
      '<path d="'+curve(t=>B(t,q,sat),348)+'" stroke="var(--accent,currentColor)" stroke-width="3"/>'+
      '<path d="M'+neutral.toFixed(1)+' 252V428" stroke="var(--accent,currentColor)" stroke-width="2" stroke-dasharray="3 5"/>'+
      '</g><g fill="currentColor" font-family="system-ui,sans-serif" font-size="16">'+
      '<text x="80" y="32">空间磁动势（无量纲）</text><text x="80" y="247">气隙磁密（归一化）</text>'+
      '<text x="'+x(-Math.PI/2)+'" y="44" text-anchor="middle">S 极轴</text>'+
      '<text x="'+x(Math.PI/2)+'" y="44" text-anchor="middle">N 极轴</text>'+
      '<text x="'+x(0)+'" y="443" text-anchor="middle">0：几何中性线</text>'+
      '<text x="'+x(-Math.PI/2)+'" y="443" text-anchor="middle">−π/2</text>'+
      '<text x="'+x(Math.PI/2)+'" y="443" text-anchor="middle">π/2</text>'+
      '</g></svg>';
  }
  function mount(body) {
    body.querySelectorAll('[data-dc-reaction-lab]').forEach(el=>{
      if(el.dataset.ready) return; el.dataset.ready='1';
      el.innerHTML='<div class="dc-reaction-controls"><label>交轴电枢磁动势／主磁动势 <output data-q-value>0.35</output>'+
        '<input data-q type="range" min="0" max="0.8" step="0.05" value="0.35"></label>'+
        '<label><input data-sat type="checkbox" checked>考虑非线性磁化</label></div>'+
        '<div class="dc-reaction-plot" data-plot></div><p class="dc-reaction-result" data-result role="status" aria-live="polite"></p>';
      const input=el.querySelector('[data-q]'), check=el.querySelector('[data-sat]');
      function update() {
        const q=Number(input.value), sat=check.checked, r=calculate(q,sat);
        el.querySelector('[data-q-value]').textContent=q.toFixed(2);
        el.querySelector('[data-plot]').innerHTML=graph(q,sat);
        el.querySelector('[data-result]').textContent=
          '本示意坐标下磁中性线偏移 '+r.neutralShiftDeg.toFixed(1)+'°；每极净磁通相对空载 '+
          (100*r.relativeFlux).toFixed(1)+'%。'+
          (sat?' 增磁侧受饱和限制，净磁通可能减少。':' 理想线性情形下交轴分量每极积分为零。');
      }
      input.addEventListener('input',update); check.addEventListener('change',update); update();
    });
  }
  const api={calculate, F, B, mount}; root.LN_DCReactionLab=api;
  if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof window==='undefined'?globalThis:window);
