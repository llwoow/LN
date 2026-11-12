/* Original LN educational projections and kinematic profiles. No hardware IO. */
(function(root){
  'use strict';
  function projection(current,deg){
    if(!Number.isFinite(current)||!Number.isFinite(deg))throw new TypeError('finite inputs');
    const t=deg*Math.PI/180;
    return {alpha:current,beta:0,d:current*Math.cos(t),q:-current*Math.sin(t)};
  }
  function plan(distance,vmax,amax){
    if(![distance,vmax,amax].every(Number.isFinite)||vmax<=0||amax<=0)throw new RangeError('invalid profile');
    const s=Math.sign(distance)||1,D=Math.abs(distance),v=Math.min(vmax,Math.sqrt(D*amax)),ta=v/amax,tc=v ? Math.max(0,(D-v*v/amax)/v):0;
    return {distance,v,amax,ta,tc,total:2*ta+tc,s,kind:tc>1e-10?'梯形':'三角形'};
  }
  function sample(p,t){
    t=Math.max(0,Math.min(t,p.total));let x,v,a;
    if(t<p.ta){a=p.amax;v=a*t;x=.5*a*t*t;}
    else if(t<p.ta+p.tc){a=0;v=p.v;x=.5*p.v*p.ta+p.v*(t-p.ta);}
    else {const left=p.total-t;a=t>=p.total?0:-p.amax;v=p.amax*left;x=Math.abs(p.distance)-.5*p.amax*left*left;}
    return {x:p.s*x,v:p.s*v,a:p.s*a};
  }
  function mount(scope){
    scope.querySelectorAll('[data-rd-lab]:not([data-mounted])').forEach(el=>{
      el.dataset.mounted='true';const type=el.dataset.rdLab;
      const fields=type==='projection'?[['i','α轴电流 / A',0,5,.1,2],['theta','转子电角 / °',-180,180,1,30]]:[['distance','目标位移 / rad',-2,2,.05,1],['v','速度上限 / rad·s⁻¹',.1,2,.05,1],['a','加速度上限 / rad·s⁻²',.2,4,.1,2]];
      const ui=document.createElement('div');ui.className='rd-lab-ui';
      fields.forEach(([key,label,min,max,step,value])=>{const row=document.createElement('label');row.textContent=label;const val=document.createElement('output');const input=document.createElement('input');input.type='range';Object.assign(input,{min,max,step,value});input.dataset.key=key;row.append(val,input);ui.append(row);});
      const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 640 300');svg.setAttribute('role','img');
      const result=document.createElement('p');result.className='rd-lab-result';result.setAttribute('role','status');result.setAttribute('aria-live','polite');
      const plot=document.createElement('div');plot.className='rd-lab-plot';plot.tabIndex=0;plot.setAttribute('role','region');plot.setAttribute('aria-label',type==='projection'?'dq投影图，可横向阅读':'速度轨迹图，可横向阅读');plot.append(svg);ui.append(plot,result);el.replaceChildren(ui);
      function draw(){
        const values={};ui.querySelectorAll('input').forEach(i=>{values[i.dataset.key]=Number(i.value);i.previousElementSibling.textContent=i.value;});
        if(type==='projection'){
          const r=projection(values.i,values.theta),t=values.theta*Math.PI/180,S=32,cx=270,cy=150;
          const dx=Math.cos(t),dy=-Math.sin(t),qx=-Math.sin(t),qy=-Math.cos(t);
          const point=(x,y)=>`${cx+S*x},${cy-S*y}`;
          // q unit vector is (-sin θ, cos θ) in physical coordinates.
          const px=r.d*Math.cos(t),py=r.d*Math.sin(t);
          svg.innerHTML=`<title>静止α轴电流在旋转dq坐标中的有向投影</title><g fill="none" stroke="currentColor" stroke-width="2"><path d="M50 150H490M270 30V270" opacity=".4"/><path d="M${cx-110*dx} ${cy-110*dy}L${cx+110*dx} ${cy+110*dy}M${cx-110*qx} ${cy-110*qy}L${cx+110*qx} ${cy+110*qy}" stroke-dasharray="5 4"/><path d="M${cx} ${cy}L${point(values.i,0)}" stroke-width="5"/><path d="M${point(values.i,0)}L${point(px,py)}" stroke-dasharray="3 3"/><circle cx="${cx+S*px}" cy="${cy-S*py}" r="5"/></g><g fill="currentColor" font-family="sans-serif" font-size="17"><text x="500" y="155">α / A</text><text x="280" y="25">β / A</text><text x="${cx+120*dx}" y="${cy+120*dy}">d</text><text x="${cx+120*qx}" y="${cy+120*qy}">q</text><text x="20" y="290">每格尺度：32 px/A；粗线为原电流，虚线为旋转坐标</text></g>`;
          result.textContent=`iα=${r.alpha.toFixed(2)} A，iβ=0 A；id=${r.d.toFixed(3)} A，iq=${r.q.toFixed(3)} A。平方和=${(r.d*r.d+r.q*r.q).toFixed(3)} A²。转坐标没有改变原矢量。`;
        }else{
          const p=plan(values.distance,values.v,values.a),scaleT=Math.max(p.total,.001),sx=t=>60+520*t/scaleT,sy=v=>160-90*v/values.v;
          const points=Array.from({length:201},(_,i)=>{const t=p.total*i/200;return `${sx(t)},${sy(sample(p,t).v)}`;}).join(' ');
          svg.innerHTML=`<title>从静止到静止的限速限加速度速度曲线</title><g fill="none" stroke="currentColor" stroke-width="2"><path d="M60 30V260M60 160H600" opacity=".5"/><polyline points="${points}" stroke-width="4"/></g><g fill="currentColor" font-family="sans-serif" font-size="18"><text x="65" y="25">速度 / rad·s⁻¹</text><text x="15" y="75">${values.v.toFixed(1)}</text><text x="15" y="255">${(-values.v).toFixed(1)}</text><text x="58" y="285">0</text><text x="480" y="285">${p.total.toFixed(3)} s</text></g>`;
          result.textContent=`${p.kind}轨迹；峰值速度 ${p.v.toFixed(3)} rad/s；加速 ${p.ta.toFixed(3)} s，巡航 ${p.tc.toFixed(3)} s；总时长 ${p.total.toFixed(3)} s。速度曲线的有向面积为 ${p.distance.toFixed(3)} rad。这是运动学规划，未模拟负载、电流或跟踪延迟。`;
        }
      }
      ui.addEventListener('input',draw);draw();
    });
  }
  root.LNDriveModels={projection,plan,sample};root.LN_MOUNT_DRIVE_LABS=mount;
  if(typeof module!=='undefined')module.exports={projection,plan,sample};
})(typeof window==='undefined'?globalThis:window);
