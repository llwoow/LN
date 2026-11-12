'use strict';
// Original numerical teaching visualization for LN automatic control, chapter 4.
// All roots are solved from s^4+5s^3+8s^2+6s+K=0; no pre-rendered fake trajectories.
(function(){
const KD=4.331570416;
const BR=-2.28858434682;
const Z=(re,im=0)=>({re,im}),add=(a,b)=>Z(a.re+b.re,a.im+b.im),sub=(a,b)=>Z(a.re-b.re,a.im-b.im);
const mul=(a,b)=>Z(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
const div=(a,b)=>{const d=b.re*b.re+b.im*b.im;return Z((a.re*b.re+a.im*b.im)/d,(a.im*b.re-a.re*b.im)/d);};
const abs=a=>Math.hypot(a.re,a.im),scale=(a,n)=>Z(a.re*n,a.im*n);
function polynomial(s,k){let z=add(s,Z(5));z=add(mul(z,s),Z(8));z=add(mul(z,s),Z(6));return add(mul(z,s),Z(k));}
function solve(k){
  if(k===0) return [Z(-3),Z(0),Z(-1,1),Z(-1,-1)];
  if(Math.abs(k-KD)<2e-7){
    const a=5+2*BR,b=8+10*BR+3*BR*BR,omega=Math.sqrt(b-a*a/4);
    return [Z(BR),Z(BR),Z(-a/2,omega),Z(-a/2,-omega)];
  }
  // Durand-Kerner: simultaneous complex roots, with independent residual checks.
  let roots=[Z(4,0.7),Z(-4,1.2),Z(0.3,-4),Z(-0.8,4.1)];
  for(let iteration=0;iteration<240;iteration++){
    let largest=0;
    const prev=roots.slice();
    roots=prev.map((x,i)=>{
      let den=Z(1);
      for(let j=0;j<4;j++)if(j!==i)den=mul(den,sub(x,prev[j]));
      if(abs(den)<1e-26)return x;
      const delta=div(polynomial(x,k),den);
      largest=Math.max(largest,abs(delta));
      return sub(x,delta);
    });
    if(largest<2e-13)break;
  }
  return roots.map(x=>Z(Math.abs(x.re)<1e-12?0:x.re,Math.abs(x.im)<1e-10?0:x.im));
}
function groups(k){
  const r=solve(k);
  if(k<=KD+2e-7){
    const real=r.filter(z=>Math.abs(z.im)<1e-6).sort((a,b)=>a.re-b.re);
    const complex=r.filter(z=>Math.abs(z.im)>=1e-6);
    if(real.length===2 && complex.length===2) return {leftReal:real[0],rightReal:real[1],rightUpper:complex.find(z=>z.im>0),rightLower:complex.find(z=>z.im<0)};
    const a=r.slice().sort((a,b)=>a.re-b.re);
    return {leftReal:a[0],rightReal:a[1],rightUpper:a[2].im>0?a[2]:a[3],rightLower:a[2].im<0?a[2]:a[3]};
  }
  const sorted=r.slice().sort((a,b)=>a.re-b.re);
  const left=sorted.slice(0,2),right=sorted.slice(2,4);
  return {leftUpper:left.find(z=>z.im>=0),leftLower:left.find(z=>z.im<0),rightUpper:right.find(z=>z.im>=0),rightLower:right.find(z=>z.im<0)};
}
function originFamily(k,z){
  const g=groups(k),realOrigin=[g.leftReal,g.rightReal,g.leftUpper,g.leftLower].filter(Boolean);
  const complexOrigin=[g.rightUpper,g.rightLower];
  const nearest=points=>Math.min(...points.map(p=>abs(sub(z,p))));
  return nearest(realOrigin)<=nearest(complexOrigin)?'real':'complex';
}
const XP=350,YP=260,S=55;
const xy=z=>[XP+S*z.re,YP-S*z.im];
const fmt=z=>z.re.toFixed(6)+(z.im<0?' − j':' + j')+Math.abs(z.im).toFixed(6);
const P=z=>{const p=xy(z);return p[0].toFixed(2)+','+p[1].toFixed(2);};
const ns='http://www.w3.org/2000/svg';
function svg(tag,attrs,parent){let e=document.createElementNS(ns,tag);for(let [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(parent)parent.appendChild(e);return e;}
function path(points,colour,dashes,parent){
  if(points.length<2)return;
  const d=points.map((p,i)=>(i?'L':'M')+P(p)).join(' ');
  return svg('path',{d,fill:'none',stroke:colour,'stroke-width':2.6,'stroke-dasharray':dashes||'','vector-effect':'non-scaling-stroke'},parent);
}
const Cblue='#1676b5',Corange='#d16c20';
function drawBackground(root){
  const grid=root.querySelector('[data-ac-root-grid]'), asym=root.querySelector('[data-ac-root-asymptotes]'), curves=root.querySelector('[data-ac-root-curves]'), poles=root.querySelector('[data-ac-root-poles]');
  for(let n=-6;n<=7;n++){
    const x=XP+S*n;
    svg('line',{x1:x,y1:10,x2:x,y2:510,stroke:'currentColor','stroke-opacity':n===0?0.6:0.13,'stroke-width':n===0?1.6:1},grid);
    if(n>=-5&&n<=6)svg('text',{x:x+3,y:YP+17,'font-size':11,fill:'currentColor'},grid).textContent=n;
  }
  for(let n=-4;n<=4;n++){
    const y=YP-S*n;
    svg('line',{x1:10,y1:y,x2:750,y2:y,stroke:'currentColor','stroke-opacity':n===0?0.6:0.13,'stroke-width':n===0?1.6:1},grid);
    if(n!==0)svg('text',{x:XP+6,y:y-5,'font-size':11,fill:'currentColor'},grid).textContent=n+'j';
  }
  svg('text',{x:699,y:YP-8,'font-size':14,fill:'currentColor'},grid).textContent='Re(s)';
  svg('text',{x:XP+8,y:18,'font-size':14,fill:'currentColor'},grid).textContent='Im(s)';
  const center=Z(-1.25);
  for(const ang of [45,135,225,315]){
    const rad=ang*Math.PI/180;
    const end=Z(center.re+13*Math.cos(rad),13*Math.sin(rad));
    path([center,end],'#88909d','7 6',asym);
  }
  const phases=[[],[],[],[],[],[]];
  const split1=110,split2=240;
  for(let i=0;i<=split1;i++){
    const k=KD*i/split1,g=groups(k);
    phases[0].push(g.leftReal);phases[1].push(g.rightReal);
    phases[2].push(g.rightUpper);phases[3].push(g.rightLower);
  }
  for(let i=1;i<=split2;i++){
    const k=KD+(80-KD)*i/split2,g=groups(k);
    phases[4].push(g.leftUpper);phases[5].push(g.leftLower);
    phases[2].push(g.rightUpper);phases[3].push(g.rightLower);
  }
  phases[4].unshift(Z(BR));phases[5].unshift(Z(BR));
  for(const index of [0,1,4,5])path(phases[index],Cblue,'',curves);
  for(const index of [2,3])path(phases[index],Corange,'',curves);
  for(const z of [Z(-3),Z(0),Z(-1,1),Z(-1,-1)]){
    const [x,y]=xy(z);
    svg('path',{d:`M${x-6},${y-6}L${x+6},${y+6}M${x-6},${y+6}L${x+6},${y-6}`,stroke:'currentColor','stroke-width':2.5,fill:'none'},poles);
  }
  const [bx,by]=xy(Z(BR));
  svg('circle',{cx:bx,cy:by,r:4.5,fill:Cblue},poles);
  const wrong=root.querySelector('[data-ac-root-wrong]');
  const wrongPath=[
    // Deliberately invalid, conceptual branch-connection sketch: not a computed locus.
    `M${bx},${by} C${bx+100},${by-80} ${bx+220},${by-110} ${bx+310},${by-210}`,
    `M${bx},${by} C${bx+100},${by+80} ${bx+220},${by+110} ${bx+310},${by+210}`,
    `M${P(Z(-1,1))} C${bx+30},${by-110} ${bx-60},${by-160} ${bx-125},${by-215}`,
    `M${P(Z(-1,-1))} C${bx+30},${by+110} ${bx-60},${by+160} ${bx-125},${by+215}`
  ];
  for(const d of wrongPath)svg('path',{d,stroke:'#c23c42','stroke-width':2.5,'stroke-dasharray':'8 5',fill:'none','vector-effect':'non-scaling-stroke'},wrong);
  wrong.style.display='none';
}
function mount(root){
  const box=root.querySelector('[data-ac-root-locus]');
  if(!box || box.dataset.mounted)return;
  box.dataset.mounted='true';
  const input=box.querySelector('[data-ac-root-k]'),plot=box.querySelector('[data-ac-root-svg]'),status=box.querySelector('[data-ac-root-status]'),labels=box.querySelector('[data-ac-root-values]'),markers=box.querySelector('[data-ac-root-moving]');
  drawBackground(box);
  function render(){
    const k=Number(input.value);const roots=solve(k);
    const maxResidual=Math.max(...roots.map(z=>abs(polynomial(z,k))));
    const stable=k>0&&k<8.16;
    box.querySelector('[data-ac-root-label]').textContent=k.toFixed(6);
    status.textContent=(k===0?'K=0：有零极点，不渐近稳定。':Math.abs(k-8.16)<1e-8?'K=8.16：纯虚根，临界稳定。':stable?'全部闭环极点在左半平面：渐近稳定。':'存在右半平面极点：不稳定。')+' 当前最大特征多项式残差 ≈ '+maxResidual.toExponential(2);
    labels.replaceChildren();markers.replaceChildren();
    roots.sort((a,b)=>a.re-b.re||a.im-b.im);
    roots.forEach((z,i)=>{
      const li=document.createElement('li');li.textContent='s'+(i+1)+' = '+fmt(z);labels.append(li);
      const [x,y]=xy(z);
      svg('circle',{cx:x,cy:y,r:6,fill:originFamily(k,z)==='real'?Cblue:Corange,stroke:'#fff','stroke-width':1.4},markers);
    });
    const angleOn=box.querySelector('[data-ac-root-tangent]').getAttribute('aria-pressed')==='true';
    if(angleOn){
      for(const sign of [-1,1]){
        const start=Z(-1,sign),theta=-sign*71.565*Math.PI/180,end=Z(start.re+0.74*Math.cos(theta),start.im+0.74*Math.sin(theta));
        const [x1,y1]=xy(start),[x2,y2]=xy(end);
        svg('line',{x1,y1,x2,y2,stroke:'#b1268c','stroke-width':3,'stroke-linecap':'round'},markers);
        svg('circle',{cx:x2,cy:y2,r:4,fill:'#b1268c'},markers);
      }
    }
  }
  input.addEventListener('input',render);
  box.querySelectorAll('[data-ac-set-k]').forEach(btn=>btn.addEventListener('click',()=>{
    input.value=btn.dataset.acSetK;render();input.focus();
  }));
  const tangent=box.querySelector('[data-ac-root-tangent]');
  tangent.addEventListener('click',()=>{tangent.setAttribute('aria-pressed',tangent.getAttribute('aria-pressed')!=='true');render();});
  const wrong=box.querySelector('[data-ac-root-wrong]'),toggle=box.querySelector('[data-ac-root-wrong-toggle]');
  toggle.addEventListener('click',()=>{
    const next=toggle.getAttribute('aria-pressed')!=='true';toggle.setAttribute('aria-pressed',String(next));
    wrong.style.display=next?'':'none';
    box.querySelector('[data-ac-root-test]').textContent=next?'红虚线是错误方案示意，不是特征方程的数值根；点击图中任意位置验证其 K(s) 是否为非负实数。':'点选图内任意位置，可由 K(s)=−D(s) 验证它是否落在正增益根轨迹上。';
  });
  function probe(x,y){
    const s=Z((x-XP)/S,(YP-y)/S),k=scale(polynomial(s,0),-1);
    const normalized=Math.abs(k.im)/Math.max(1,abs(k));
    box.querySelector('[data-ac-root-test]').textContent=
      '所选 s = '+fmt(s)+'；K(s)= '+fmt(k)+'；相对虚部分量 '+normalized.toExponential(2)+
      '。'+(normalized<1e-3&&k.re>=0?'接近正增益根轨迹（需考虑点击精度）。':'该点不满足非负实增益条件。');
  }
  plot.addEventListener('click',event=>{
    const rect=plot.getBoundingClientRect();
    const x=(event.clientX-rect.left)/rect.width*760;
    const y=(event.clientY-rect.top)/rect.height*520;
    probe(x,y);
  });
  render();
}
window.LN_ROOT_LOCUS={solve,polynomial,group:groups,originFamily,KD};
window.LN_MOUNT_ROOT_LOCUS=mount;
})();