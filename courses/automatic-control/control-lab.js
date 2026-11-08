'use strict';
// Original interactive computations for LN automatic-control chapter 3.
// The lesson DOM is re-created on navigation; listeners are attached only to
// the active lesson root, with no global timers or persistent event handlers.
window.LN_MOUNT_CONTROL_LABS = function mountControlLabs(root) {
  const routh = root.querySelector('[data-ac-routh]');
  if (routh) {
    const slider = routh.querySelector('[data-ac-k-input]');
    const show = (name, value) => { const node = routh.querySelector('[data-ac-' + name + ']'); node.textContent = value.toFixed(4); node.classList.toggle('ac-negative', value < 0); };
    const render = () => {
      const k = Number(slider.value);
      const b = (10-k)/3;
      const c = (20-10*k-k*k)/(10-k);
      show('b',b); show('c',c); show('d',2*k);
      routh.querySelector('[data-ac-k]').textContent=k.toFixed(2);
      const stable = k > 0 && b > 0 && c > 0;
      const status = routh.querySelector('[data-ac-routh-status]');
      status.textContent = stable ? '第一列全正，闭环渐近稳定。' : '首列不全为严格正数，不能判为渐近稳定。';
      status.classList.toggle('ac-negative',!stable);
    };
    slider.addEventListener('input',render);
    render();
  }
  const damping = root.querySelector('[data-ac-damping]');
  if (damping) {
    const slider = damping.querySelector('[data-ac-z-input]');
    const wn=3;
    const response = (z,t) => {
      if (Math.abs(z-1)<1e-9) return 1-(1+wn*t)*Math.exp(-wn*t);
      if(z<1) {
        const q=Math.sqrt(1-z*z),w=wn*q;
        return 1-Math.exp(-z*wn*t)*(Math.cos(w*t)+z/q*Math.sin(w*t));
      }
      const q=Math.sqrt(z*z-1),a=-wn*(z-q),b=-wn*(z+q);
      return 1-(b*Math.exp(a*t)-a*Math.exp(b*t))/(b-a);
    };
    const render=()=>{
      const z=Number(slider.value);
      damping.querySelector('[data-ac-z]').textContent=z.toFixed(2);
      const points=[];
      for(let n=0;n<=240;n++){
        const t=n*5/240, y=response(z,t);
        const px=46+589*n/240,py=215-117.65*y;
        points.push((n?'L':'M')+px.toFixed(2)+','+py.toFixed(2));
      }
      damping.querySelector('[data-ac-damping-path]').setAttribute('d',points.join(' '));
      const text=z<1?('欠阻尼；峰值时间 ≈ '+(Math.PI/(wn*Math.sqrt(1-z*z))).toFixed(2)+' s，超调量 ≈ '+(100*Math.exp(-Math.PI*z/Math.sqrt(1-z*z))).toFixed(2)+'%。'):z===1?'临界阻尼；阶跃响应单调且无超调。':'过阻尼；两个负实极点，阶跃响应无超调。';
      damping.querySelector('[data-ac-z-status]').textContent=text;
    };
    slider.addEventListener('input',render);
    render();
  }
  const error = root.querySelector('[data-ac-error]');
  if (error) {
    const select=error.querySelector('[data-ac-type]');
    const render=()=>{
      const type=select.value, ref=[],out=[];
      const a=(-10+Math.sqrt(60))/2,b=(-10-Math.sqrt(60))/2;
      for(let i=0;i<=240;i++){
        const t=i*6/240, r=2*t;
        let e=0;
        if(type==='0') e=(2/21)*t+(40/441)*(1-Math.exp(-21*t));
        else if(type==='1') e=(1/5)*(1-Math.exp(-10*t));
        else e=2*(Math.exp(a*t)-Math.exp(b*t))/(a-b);
        const x=48+587*i/240;
        const y1=220-204*r/12.5, y2=220-204*(r-e)/12.5;
        ref.push((i?'L':'M')+x.toFixed(2)+','+y1.toFixed(2));
        out.push((i?'L':'M')+x.toFixed(2)+','+y2.toFixed(2));
      }
      error.querySelector('[data-ac-ref-path]').setAttribute('d',ref.join(' '));
      error.querySelector('[data-ac-output-path]').setAttribute('d',out.join(' '));
      error.querySelector('[data-ac-error-status]').textContent=type==='0'?
        '0型：误差 e(t)=(2/21)t+(40/441)(1−e^(−21t))，长期线性增大。':
        type==='1'?'I型：误差 e(t)=0.2(1−e^(−10t))，最终趋于0.2。':
        'II型：误差 e(t)=2(e^(a t)−e^(b t))/(a−b)，a≈−1.127、b≈−8.873，最终趋于0。';
    };
    select.addEventListener('change',render);
    render();
  }
};
