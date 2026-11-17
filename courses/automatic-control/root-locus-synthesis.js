'use strict';
// LN lesson 4.3.1 — original cubic closed-loop numerical visualization.
(function () {
  const Q = (s) => document.querySelector(s);
  const NS = 'http://www.w3.org/2000/svg';
  const roots = (k) => {
    // s=t−2/3 gives t^3+(2/3)t+(k−20/27)=0.
    // The discriminant is strictly positive: one real + two conjugate roots.
    const q = k - 20 / 27;
    const discriminant = q * q / 4 + 8 / 729;
    const a = Math.cbrt(-q / 2 + Math.sqrt(discriminant));
    const b = Math.cbrt(-q / 2 - Math.sqrt(discriminant));
    const re = -(a + b) / 2 - 2 / 3;
    const im = Math.sqrt(3) * (a - b) / 2;
    return [
      { re: a + b - 2 / 3, im: 0 },
      { re, im: Math.abs(im) },
      { re, im: -Math.abs(im) }
    ];
  };
  const polynomial = (z, k) => {
    const square = {re:z.re * z.re - z.im * z.im, im:2 * z.re * z.im};
    const cube = {re:square.re*z.re-square.im*z.im, im:square.re*z.im+square.im*z.re};
    return {re:cube.re+2*square.re+2*z.re+k,im:cube.im+2*square.im+2*z.im};
  };
  const formatRoot = (z) => Math.abs(z.im) < 1e-9
    ? z.re.toFixed(5)
    : z.re.toFixed(5) + (z.im >= 0 ? '+' : '−') + 'j' + Math.abs(z.im).toFixed(5);
  const fmt = n => Number(n.toFixed(4)).toString();
  function mount(host) {
    const lab = host.querySelector('[data-ac-synthesis]');
    if (!lab || lab.dataset.mounted === 'true') return;
    lab.dataset.mounted = 'true';
    const svg = lab.querySelector('[data-ac-syn-svg]');
    const range = lab.querySelector('[data-ac-syn-k]');
    const output = lab.querySelector('[data-ac-syn-k-value]');
    const status = lab.querySelector('[data-ac-syn-status]');
    const values = lab.querySelector('[data-ac-syn-values]');
    const X0=-4.5, X1=3.4, Y0=-3.4, Y1=3.4, W=680, H=360;
    const X = re => (re-X0)/(X1-X0)*W, Y=im=>(Y1-im)/(Y1-Y0)*H;
    const esc = v => String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const segment = (a,b) => '<line x1="'+X(a.re).toFixed(2)+'" y1="'+Y(a.im).toFixed(2)+'" x2="'+X(b.re).toFixed(2)+'" y2="'+Y(b.im).toFixed(2)+'"/>';
    function draw(k) {
      const rs = roots(k);
      const maxError = Math.max(...rs.map(z=>{const e=polynomial(z,k);return Math.hypot(e.re,e.im);}));
      let html = '<g class="ac-syn-grid">';
      for (let x=-4;x<=3;x++) html+=segment({re:x,im:Y0},{re:x,im:Y1});
      for (let y=-3;y<=3;y++) html+=segment({re:X0,im:y},{re:X1,im:y});
      html += '</g><g class="ac-syn-axis">' + segment({re:X0,im:0},{re:X1,im:0}) +
        segment({re:0,im:Y0},{re:0,im:Y1}) + '</g>';
      html += '<g class="ac-syn-ticks">';
      for(let x=-4;x<=3;x++) html += '<text x="'+(X(x)+4)+'" y="'+(Y(0)+17)+'">'+x+'</text>';
      for(let y=-3;y<=3;y++) if(y!==0)html += '<text x="'+(X(0)+6)+'" y="'+(Y(y)-3)+'">'+y+'j</text>';
      html += '<text x="646" y="'+(Y(0)-7)+'">Re</text><text x="'+(X(0)+8)+'" y="13">jω</text></g>';
      const from={re:-2/3,im:0};
      html+='<g class="ac-syn-asym">';
      for (const angle of [Math.PI/3,Math.PI,5*Math.PI/3]) {
        const length=8;
        html+=segment(from,{re:from.re+length*Math.cos(angle),im:from.im+length*Math.sin(angle)});
      }
      html+='</g><g class="ac-syn-zeta">';
      // ζ=0.5, tan β=√3: the two fixed-angle rays meet the cubic locus at K=1.
      html+=segment({re:0,im:0},{re:-1.8,im:Math.sqrt(3)*1.8});
      html+=segment({re:0,im:0},{re:-1.8,im:-Math.sqrt(3)*1.8});
      html+='</g><g class="ac-syn-curves">';
      for(let part=0;part<3;part++){
        let d='';
        for(let i=0;i<=240;i++){
          const z=roots(20*i/240)[part];
          d+=(i?'L':'M')+X(z.re).toFixed(2)+','+Y(z.im).toFixed(2);
        }
        html+='<path d="'+d+'"/>';
      }
      html+='</g><g class="ac-syn-poles">';
      for(const p of [{re:0,im:0},{re:-1,im:1},{re:-1,im:-1}]){
        const x=X(p.re),y=Y(p.im);
        html+='<path d="M'+(x-6)+','+(y-6)+'l12,12m0,-12l-12,12"/>';
      }
      html+='</g><g class="ac-syn-current">';
      for(const z of rs)html+='<circle cx="'+X(z.re)+'" cy="'+Y(z.im)+'" r="5.5"/>';
      html+='</g><text class="ac-syn-plot-note" x="15" y="23">蓝色实线：根轨迹　橙虚线：渐近线　紫点线：ζ=0.5</text>';
      svg.innerHTML=html;
      output.textContent=k.toFixed(1);
      const stable=k>0+1e-8 && k<4-1e-8;
      const borderline=k<1e-8?'K=0：原点存在极点，不渐近稳定':
        Math.abs(k-4)<1e-8?'K=4：一对纯虚根，临界稳定，不是渐近稳定':
        stable?'0<K<4：三根实部均为负，渐近稳定':'K>4：右半平面存在共轭根，闭环不稳定';
      status.textContent=borderline+'。数值特征方程最大残差 '+maxError.toExponential(2)+'。';
      const pair=rs[1],omega=Math.hypot(pair.re,pair.im),zeta=omega>0?-pair.re/omega:NaN;
      values.textContent='实根 '+formatRoot(rs[0])+'；共轭根 '+formatRoot(rs[1])+'、'+formatRoot(rs[2])+'。该共轭根对：ωn='+fmt(omega)+' rad/s，ωd='+fmt(pair.im)+' rad/s，ζ='+fmt(zeta)+'（ζ<0 表示右半平面增长模态）。';
    }
    range.addEventListener('input',()=>draw(Number(range.value)));
    lab.querySelectorAll('[data-ac-syn-preset]').forEach(button=>button.addEventListener('click',()=>{
      range.value=button.dataset.acSynPreset;
      draw(Number(range.value));
    }));
    host.querySelectorAll('[data-ac-syn-question]').forEach(fieldset=>{
      fieldset.querySelectorAll('[data-ac-syn-choice]').forEach(button=>button.addEventListener('click',()=>{
        const correct=Number(fieldset.dataset.correct),chosen=Number(button.dataset.acSynChoice);
        fieldset.querySelectorAll('button').forEach(b=>{
          const right=Number(b.dataset.acSynChoice)===correct;
          b.classList.toggle('ac-syn-correct',right);
          b.classList.toggle('ac-syn-incorrect',b===button&&!right);
          b.setAttribute('aria-pressed',String(b===button));
        });
        const output=fieldset.querySelector('[data-ac-syn-feedback]');
        output.textContent=(chosen===correct?'正确。':'需要纠正。')+' '+fieldset.dataset.explain;
        output.classList.toggle('ac-syn-error',chosen!==correct);
      }));
    });
    draw(Number(range.value));
  }
  window.LN_AC_SYNTHESIS={roots,polynomial};
  window.LN_MOUNT_AC_SYNTHESIS=mount;
})();