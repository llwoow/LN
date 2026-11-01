'use strict';
window.LN_MOUNT_TRANSFORMER_MODELS=function(){

(()=>{
'use strict';const root=document.getElementById('t3d-widget');if(!root||root.dataset.ready)return;
const canvas=root.querySelector('#t3d-canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
const nameEl=root.querySelector('#t3d-part-name'),desc=root.querySelector('#t3d-part-desc'),msg=root.querySelector('#t3d-viewport-msg');
const info={core:['三相铁心','三根心柱和上下铁轭构成共同磁路；铁心中存在磁滞及涡流损耗。'],coilA:['A 相绕组（内低压、外高压）','A 相绕组套在 A 相心柱上，采用同心圆筒式教学示意：低压绕组靠近铁心，高压绕组位于外侧，中间留有绝缘与油道空间。'],coilB:['B 相绕组（内低压、外高压）','B 相与 A、C 相相同：每柱一相，同柱同轴布置高低压绕组。可在“绕组拆解”视图中观察内外层分离。'],coilC:['C 相绕组（内低压、外高压）','C 相绕组与铁心共同构成电磁系统。绕组中电流产生铜耗，负荷升高时热点温度通常先出现在绕组区域。'],tank:['主油箱 / 顶盖 / 绝缘油','主油箱包围铁心和绕组，顶盖上布置套管、压力释放等附件；绝缘油兼具绝缘与传热作用。箱壁和顶盖只是外部表面，不能把它们当成绕组热点位置。'],bushing:['高低压套管组','工程化示意为：顶部前侧 3 只较高的高压套管，后侧另有较矮的低压套管组（含中性点简化示意）。它们把绕组引线可靠引出油箱外。'],conservator:['储油柜','储油柜为油体热胀冷缩提供缓冲容积，通常高置于主油箱上方，通过联管与主油箱连通。'],relay:['气体继电器','位于主油箱到储油柜的联通管上，对故障产气及异常油流等作出响应，用于保护。'],breather:['吸湿器','对储油柜呼吸气路中的空气进行除湿；不同储油柜有不同的油气隔离设计。'],radiator:['片式散热器组','片式散热器通过上下集油管与主油箱连接，增大换热面积；自然油循环时热油上升流入散热器，冷却后再回流主油箱。'],relief:['压力释放装置','当内部故障导致油箱压力异常升高时，压力释放装置会迅速动作泄压。'],oilflow:['油流路径','热油上升、进入散热器后冷却下降、再流回油箱；这里只显示定性运动方向。']};
const state={yaw:.68,pitch:.27,dist:15.1,target:[.1,.65,0],mode:'cut',flow:false,labels:true,sel:'core'};
const shapes=[];const C={iron:'#688096',steel:'#8498a7',dark:'#496678',gold:'#e6ab63',copper:'#b87945',blue:'#4a9cba',ivory:'#e9dcc3',tank:'#5097b0',top:'#92b7c7',pipe:'#7399ac',oil:'#89d5e2',hot:'#d98c3c',cold:'#399db5'};
const add=(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]],sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]],scale=(a,k)=>a.map(x=>x*k),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2],norm=a=>scale(a,1/(Math.hypot(...a)||1));
function poly(v,color,group,part,opacity=1){shapes.push({v,color,group,part,opacity});}
function line(a,b,color,group,part,width=.04,opacity=1){shapes.push({v:[a,b],color,group,part,width,opacity,line:true});}
function cube(g,p,c,s,col,op=1){let [x,y,z]=c,[a,b,d]=s.map(v=>v/2);let v=[[x-a,y-b,z-d],[x+a,y-b,z-d],[x+a,y+b,z-d],[x-a,y+b,z-d],[x-a,y-b,z+d],[x+a,y-b,z+d],[x+a,y+b,z+d],[x-a,y+b,z+d]];for(const q of [[0,1,2,3],[4,7,6,5],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2]])poly(q.map(i=>v[i]),col,g,p,op);}
function cyl(g,p,a,b,r,c,op=1,n=15){let d=norm(sub(b,a)),u=norm(cross(Math.abs(d[1])<.9?[0,1,0]:[1,0,0],d)),v=cross(d,u);const ring=(center,t)=>add(center,scale(add(scale(u,Math.cos(t)),scale(v,Math.sin(t))),r));for(let j=0;j<n;j++){let t=j/n*2*Math.PI,s=(j+1)/n*2*Math.PI;poly([ring(a,t),ring(a,s),ring(b,s),ring(b,t)],c,g,p,op);}poly(Array.from({length:n},(_,i)=>ring(a,i/n*2*Math.PI)),c,g,p,op);poly(Array.from({length:n},(_,i)=>ring(b,i/n*2*Math.PI)),c,g,p,op);}
function path(points,g,p,c,w=.05){for(let i=0;i<points.length-1;i++)line(points[i],points[i+1],c,g,p,w);}
function helix(g,p,x,z,y,h,r,turns,c,w=.06){let prev=null,N=Math.round(turns*18);for(let i=0;i<=N;i++){let t=i/N,a=t*2*Math.PI*turns-.5*Math.PI,pt=[x+r*Math.cos(a),y+(t-.5)*h,z+r*Math.sin(a)];if(prev)line(prev,pt,c,g,p,w);prev=pt;}}
function ring(g,p,x,y,z,r,c,w=.05){let pathv=[];for(let j=0;j<=44;j++){let a=j*2*Math.PI/44;pathv.push([x+r*Math.cos(a),y,z+r*Math.sin(a)]);}path(pathv,g,p,c,w)}
function annulus(g,p,x,y,z,r1,r2,h,c,op=1){let n=22;for(let i=0;i<n;i++){let a=i*2*Math.PI/n,b=(i+1)*2*Math.PI/n;const point=(r,y,theta)=>[x+r*Math.cos(theta),y,z+r*Math.sin(theta)];poly([point(r2,y-h/2,a),point(r2,y-h/2,b),point(r2,y+h/2,b),point(r2,y+h/2,a)],c,g,p,op);poly([point(r1,y-h/2,a),point(r1,y+h/2,a),point(r1,y+h/2,b),point(r1,y-h/2,b)],c,g,p,op);poly([point(r1,y+h/2,a),point(r2,y+h/2,a),point(r2,y+h/2,b),point(r1,y+h/2,b)],c,g,p,op);}}
// Real, transformable 3D primitives; projected with perspective on canvas (software pipeline).
cube('core','core',[0,1.12,0],[5.5,.4,.58],C.iron);cube('core','core',[0,-1.12,0],[5.5,.4,.58],C.iron);
for(let x of [-2,0,2])cube('core','core',[x,0,0],[.46,2.5,.46],C.dark);
const phaseLeadColors=['#d28a40','#4da17b','#be5e56'];
for(const [i,x] of [-2,0,2].entries()){
 let g=['coilA','coilB','coilC'][i],inner=g+'Inner',outer=g+'Outer',lead=phaseLeadColors[i];
 // 正确的教学关系：每根心柱上一套高低压同心绕组，内低压、外高压。
 annulus(inner,g,x,.00,0,.36,.49,1.70,'#6ec5d6',.98);   // 低压绕组（内）
 annulus(outer,g,x,.00,0,.58,.74,1.74,'#d89452',.95);   // 高压绕组（外）
 // 绕线纹理与端部压圈
 helix(inner,g,x,0,.00,1.67,.495,11.5,'#7fd4e0',.040);
 helix(outer,g,x,0,.00,1.70,.745,12,'#c27b41',.061);
 ring(inner,g,x,.88,0,.42,'#9be0eb',.045); ring(inner,g,x,-.88,0,.42,'#9be0eb',.045);
 ring(outer,g,x,.88,0,.66,'#f0c27a',.055); ring(outer,g,x,-.88,0,.66,'#f0c27a',.055);
 // 仅示意高压引线经上部引出至套管；低压侧未在此视角全部展开。
 path([[x+.66,.86,.10],[x+.66,1.16,.34],[x+.28,1.39,.56],[x,1.72,.83]],outer,g,lead,.060);
 path([[x-.43,.85,-.04],[x-.45,1.12,-.20]],inner,g,'#72cfdf',.042);
}
// tank faces and exterior: closer to practical oil-immersed transformer proportions.
cube('tankframe','tank',[0,-1.84,0],[7.45,.15,3.92],C.dark);
for(let side of [[0,-.03,-1.93,7.42,3.52,.08],[0,-.03,1.93,7.42,3.52,.08],[-3.71,-.03,0,.08,3.52,3.86],[3.71,-.03,0,.08,3.52,3.86]])cube('tankwall','tank',side.slice(0,3),side.slice(3),C.tank,.14);
cube('tankcover','tank',[0,1.76,0],[7.36,.14,3.84],C.top,.98); // 实际顶盖；剖视时隐藏
for(let z of [-1.90,1.90])path([[-3.63,1.78,z],[3.63,1.78,z]],'tankframe','tank',C.dark,.055);
for(let x of [-3.63,3.63])path([[x,1.78,-1.90],[x,1.78,1.90]],'tankframe','tank',C.dark,.055);
// cover bolts along long sides
for(let x of [-3.0,-2.2,-1.4,-.6,.2,1.0,1.8,2.6,3.2]){cyl('tankframe','tank',[x,1.82,1.74],[x,1.92,1.74],.035,C.dark);cyl('tankframe','tank',[x,1.82,-1.74],[x,1.92,-1.74],.035,C.dark);}
// lifting lugs
for(let x of [-2.9,2.9]){path([[x,1.88,1.30],[x,2.18,1.30],[x+.24,2.18,1.30],[x+.24,1.88,1.30]],'tankframe','tank',C.dark,.05);path([[x,1.88,-1.30],[x,2.18,-1.30],[x+.24,2.18,-1.30],[x+.24,1.88,-1.30]],'tankframe','tank',C.dark,.05);}
// front reinforcing ribs
for(let x of [-2.7,-1.35,0,1.35,2.7])cube('tankframe','tank',[x,-.05,1.89],[.10,2.85,.08],C.dark,.96);
for(let x of [-2.55,2.55])cube('tankframe','tank',[x,-2.02,0],[.76,.30,2.48],C.dark);
// High-voltage bushings: taller porcelain on front side.
for(let x of [-2,0,2]){cyl('bushing','bushing',[x,1.79,.88],[x,3.12,.88],.100,C.dark);for(let k=0;k<7;k++){let y=2.00+k*.132;cyl('bushing','bushing',[x,y-.034,.88],[x,y+.034,.88],.29-(k*.01),C.ivory,1,14)}cyl('bushing','bushing',[x,3.05,.88],[x,3.26,.88],.060,C.gold);path([[x,1.70,.79],[x,1.45,.52],[x+.18,1.22,.20]],'bushing','bushing',C.gold,.05);}
// Low-voltage bushings: shorter set on rear side, include neutral as simplified engineering cue.
for(let x of [-2.55,-.85,.85,2.55]){cyl('bushing','bushing',[x,1.80,-.70],[x,2.46,-.70],.090,C.dark);for(let k=0;k<4;k++){let y=1.98+k*.120;cyl('bushing','bushing',[x,y-.028,-.70],[x,y+.028,-.70],.23-(k*.008),C.ivory,1,12)}cyl('bushing','bushing',[x,2.42,-.70],[x,2.58,-.70],.05,C.gold);}
// conservator and protection equipment.
cyl('conservator','conservator',[-3.72,3.66,-2.18],[-1.14,3.66,-2.18],.46,C.top,1,26);
for(let x of [-3.66,-1.20])cyl('conservator','conservator',[x,3.66,-2.18],[x+.08,3.66,-2.18],.47,C.dark,1,26);
for(let x of [-3.02,-1.76])path([[x,3.20,-2.12],[x,1.82,-1.46]],'conservator','conservator',C.pipe,.082);
path([[-2.02,1.80,-1.48],[-2.02,2.46,-1.58],[-1.74,2.75,-1.78],[-1.74,3.48,-2.12]],'relay','relay',C.pipe,.10);
cube('relay','relay',[-2.01,2.45,-1.58],[.55,.38,.40],C.gold);
path([[-3.72,3.66,-2.18],[-4.18,3.66,-2.18],[-4.18,2.28,-2.18]],'breather','breather',C.pipe,.07);
cyl('breather','breather',[-4.18,1.62,-2.18],[-4.18,2.28,-2.18],.20,C.ivory,1,17);cyl('breather','breather',[-4.18,1.56,-2.18],[-4.18,1.68,-2.18],.24,C.gold);
// pressure relief and small thermometer pocket on cover
cyl('relief','relief',[2.78,1.80,-.98],[2.78,2.21,-.98],.14,C.pipe);cyl('relief','relief',[2.78,2.18,-.98],[2.78,2.30,-.98],.36,C.gold);
path([[1.72,1.82,1.20],[1.72,2.28,1.20]],'tankframe','tank',C.pipe,.05);
// radiator bank with headers and many thin plates.
for(let i=0;i<12;i++){let z=-1.66+i*.30;cube('radiator','radiator',[4.52,-.13,z],[.74,2.86,.09],C.top);cube('radiator','radiator',[4.55,-.13,z],[.56,2.52,.022],'#b9d8e3',.72);}
cyl('radiator','radiator',[3.70,1.18,-.05],[4.88,1.18,-.05],.17,C.pipe,1,22);
cyl('radiator','radiator',[3.70,-1.48,-.05],[4.88,-1.48,-.05],.17,C.pipe,1,22);
for(let z of [-1.55,-.35,.85])path([[3.67,1.18,z],[4.18,1.18,z]],'radiator','radiator',C.dark,.07);
const anchor={core:[0,1.13,0],coilA:[-2,.25,.8],coilB:[0,.25,.8],coilC:[2,.25,.8],tank:[-3.25,-.75,1.80],bushing:[0,3.00,.90],conservator:[-2.48,3.66,-2.18],relay:[-2.01,2.45,-1.58],breather:[-4.18,1.9,-2.18],radiator:[4.55,0,0],relief:[2.78,2.2,-.98]};
function shift(group){if(state.mode==='explode'){
 if(['tankwall','tankframe'].includes(group))return [-2.2,-.3,0];if(group==='radiator')return [1.6,0,0];if(['relay','conservator','breather'].includes(group))return [-1.1,.5,-.4];if(['bushing','relief'].includes(group))return [0,.8,0];if(group.startsWith('coil'))return [0,0,1.6];}
 if(state.mode==='winding'){if(group.endsWith('Inner'))return [.42,0,3.75];if(group.endsWith('Outer'))return [-.32,0,1.65];if(group.startsWith('coil'))return [0,0,2.3];if(group==='core')return [0,0,-.9];}return [0,0,0]}
function visible(s){if(s.group==='tankcover'&&state.mode!=='outer')return false;if(state.mode==='winding')return s.group==='core'||s.group.startsWith('coil');if(state.mode==='outer'&&(s.group==='core'||s.group.startsWith('coil')))return false;return true;}
const labelWrap=root.querySelector('.t3d-label-layer'), labels={};for(let key of Object.keys(anchor)){const b=document.createElement('button');b.type='button';b.className='t3d-float-label';b.textContent=info[key][0].replace('高低压绕组','相绕组');b.onclick=()=>select(key);labelWrap.appendChild(b);labels[key]=b;}
function select(key){state.sel=key;nameEl.textContent=info[key][0];desc.textContent=info[key][1];root.querySelectorAll('[data-part]').forEach(b=>b.classList.toggle('is-selected',b.dataset.part===key));Object.keys(labels).forEach(k=>labels[k].classList.toggle('is-selected',k===key));}
function mode(m){state.mode=m;root.querySelectorAll('[data-t3d-mode]').forEach(b=>{let on=b.dataset.t3dMode===m;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)});if(m==='explode'){state.dist=17;state.target=[-.3,.5,0]}else if(m==='winding'){state.dist=14.6;state.target=[0,.5,0];state.yaw=.42;state.pitch=.21}else{state.dist=Math.min(17,state.dist);state.target=[.1,.65,0]}}
root.querySelectorAll('[data-t3d-mode]').forEach(b=>b.onclick=()=>mode(b.dataset.t3dMode));root.querySelectorAll('[data-part]').forEach(b=>b.onclick=()=>select(b.dataset.part));
const f=root.querySelector('#t3d-flow'),l=root.querySelector('#t3d-labels');f.onchange=()=>state.flow=f.checked;l.onchange=()=>state.labels=l.checked;
root.querySelector('#t3d-zoom-in').onclick=()=>state.dist=Math.max(7,state.dist*.82);root.querySelector('#t3d-zoom-out').onclick=()=>state.dist=Math.min(30,state.dist*1.21);
root.querySelector('#t3d-reset').onclick=()=>{state.yaw=.68;state.pitch=.27;state.dist=15.1;state.target=[.1,.65,0];mode('cut');state.flow=f.checked=false;state.labels=l.checked=true;select('core')};
let project,sceneVisible=true;
let sceneObserver;if('IntersectionObserver' in window){sceneObserver=new IntersectionObserver(e=>{sceneVisible=e[0].isIntersecting},{rootMargin:'150px'});sceneObserver.observe(root);}
function render(t){if(!root.isConnected){sceneObserver?.disconnect();return;}if(!sceneVisible||document.hidden){setTimeout(()=>requestAnimationFrame(render),450);return;}let rect=canvas.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);let W=Math.max(1,Math.round(rect.width*dpr)),H=Math.max(1,Math.round(rect.height*dpr));if(canvas.width!==W||canvas.height!==H){canvas.width=W;canvas.height=H;}ctx.clearRect(0,0,W,H);
 const v=norm([Math.sin(state.yaw)*Math.cos(state.pitch),Math.sin(state.pitch),Math.cos(state.yaw)*Math.cos(state.pitch)]),right=norm(cross([0,1,0],v)),up=norm(cross(v,right));const eye=add(state.target,scale(v,state.dist)),focal=H*.5/Math.tan(47*Math.PI/360);
 root.dataset.projDebug=JSON.stringify({v,right,up,eye,focal,W,H});project=point=>{let d=sub(point,eye),depth=-dot(d,v);if(depth<.12)return null;return [W/2+dot(d,right)*focal/depth,H/2-dot(d,up)*focal/depth,depth];};
 let faces=[];for(let s of shapes){if(!visible(s))continue;let pts=s.v.map(x=>project(add(x,shift(s.group))));if(pts.some(x=>!x))continue;let depth=pts.reduce((a,b)=>a+b[2],0)/pts.length;faces.push({pts,depth,s});}
 faces.sort((a,b)=>b.depth-a.depth);for(let o of faces){let {s,pts}=o;ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);if(s.line){let width=(s.width||.04)*focal/o.depth;ctx.lineWidth=Math.max(.65,Math.min(8,width*2));ctx.lineCap='round';ctx.lineJoin='round';ctx.strokeStyle=s.part===state.sel?'#f4c95e':s.color;ctx.globalAlpha=s.opacity;ctx.stroke();}
 else{ctx.closePath();ctx.fillStyle=s.part===state.sel?(s.group==='tankwall'?'#8eb5c2':'#e0a851'):s.color;ctx.globalAlpha=s.group==='tankwall'?(state.mode==='outer'?.95:state.mode==='cut'?.082:.055):s.opacity;ctx.fill();ctx.lineWidth=.55*dpr;ctx.strokeStyle='#294f67';ctx.globalAlpha=Math.min(.3,s.opacity*.3);ctx.stroke();}}
 ctx.globalAlpha=1;
 if(state.flow&&state.mode==='cut'){
  let loops=[{a:[-2.75,-1.2,1.22],b:[-2.75,1.22,1.22],c:C.hot},{a:[2.75,-1.2,1.22],b:[2.75,1.22,1.22],c:C.hot},{a:[4.54,1.14,-1.5],b:[4.54,-1.4,-1.5],c:C.cold}];loops.forEach((line,i)=>{for(let j=0;j<5;j++){let u=((t/4700+j/5+i*.11)%1),v1=add(line.a,scale(sub(line.b,line.a),u)),p=project(v1);if(!p)continue;ctx.beginPath();ctx.arc(p[0],p[1],Math.max(2,7*dpr/p[2]),0,2*Math.PI);ctx.fillStyle=line.c;ctx.fill();}});
 }
 Object.keys(labels).forEach(k=>{let b=labels[k];let hidden=!state.labels||(state.mode==='winding'&&!['core','coilA','coilB','coilC'].includes(k))||(state.mode==='outer'&&['core','coilA','coilB','coilC'].includes(k))||(k==='tank'&&state.mode==='cut');let group=k.startsWith('coil')?(state.mode==='winding'?k+'Outer':k):k==='tank'?'tankwall':k;let p=project(add(anchor[k],shift(group)));if(hidden||!p){b.style.display='none';return;}b.style.display='';b.style.transform=`translate(${p[0]/dpr}px,${p[1]/dpr}px) translate(-50%,-50%)`;});
 requestAnimationFrame(render);
}
// Pointer rotation, scrolling zoom, right-button pan, pinch zoom + two-finger pan.
const pts=new Map();let pinch=null,clickStart=null;
function pan(dx,dy){let right=[Math.cos(state.yaw),0,-Math.sin(state.yaw)],up=[-Math.sin(state.yaw)*Math.sin(state.pitch),Math.cos(state.pitch),-Math.cos(state.yaw)*Math.sin(state.pitch)];let k=state.dist*.0019;state.target=sub(state.target,add(scale(right,dx*k),scale(up,-dy*k)));}
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);pts.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pts.size===1)clickStart={x:e.clientX,y:e.clientY,moved:0,btn:e.button};});
canvas.addEventListener('pointermove',e=>{let old=pts.get(e.pointerId);if(!old)return;let dx=e.clientX-old.x,dy=e.clientY-old.y;pts.set(e.pointerId,{x:e.clientX,y:e.clientY});if(clickStart)clickStart.moved+=Math.abs(dx)+Math.abs(dy);if(pts.size===1){if(e.buttons===2||e.shiftKey)pan(dx,dy);else{state.yaw+=dx*.009;state.pitch=Math.max(-1.15,Math.min(1.25,state.pitch+dy*.007));}}else if(pts.size===2){let p=[...pts.values()],d=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y),center=[(p[0].x+p[1].x)/2,(p[0].y+p[1].y)/2];if(pinch){state.dist=Math.max(7,Math.min(30,state.dist*pinch.d/d));pan(center[0]-pinch.x,center[1]-pinch.y);}pinch={d,x:center[0],y:center[1]};}});
function up(e){if(clickStart&&clickStart.moved<8&&pts.size===1&&clickStart.btn===0){let r=canvas.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1),pos=[(e.clientX-r.left)*dpr,(e.clientY-r.top)*dpr],best=null;for(let k of Object.keys(anchor)){let group=k.startsWith('coil')?(state.mode==='winding'?k+'Outer':k):k==='tank'?'tankwall':k,p=project(add(anchor[k],shift(group)));if(!p)continue;let dist=Math.hypot(p[0]-pos[0],p[1]-pos[1]);if(dist<45*dpr&&(!best||dist<best.dist))best={k,dist};}if(best)select(best.k);}pts.delete(e.pointerId);clickStart=null;pinch=null;}
canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',up);canvas.addEventListener('contextmenu',e=>e.preventDefault());canvas.addEventListener('wheel',e=>{e.preventDefault();state.dist=Math.max(6.7,Math.min(30,state.dist*Math.exp(e.deltaY*.001)));},{passive:false});
canvas.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')state.yaw-=.10;if(e.key==='ArrowRight')state.yaw+=.10;if(e.key==='ArrowUp')state.pitch+=.08;if(e.key==='ArrowDown')state.pitch-=.08;if(e.key==='+'||e.key==='=')state.dist=Math.max(7,state.dist*.9);if(e.key==='-')state.dist=Math.min(30,state.dist*1.1);});
msg.textContent='';root.dataset.ready='software';select('core');mode('cut');requestAnimationFrame(render);
})();


(()=>{
'use strict';
const wrap=document.getElementById('singlephase-3d');if(!wrap)return;
const canvas=wrap.querySelector('#p3d-canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
const info=wrap.querySelector('#p3d-detail');
let state={yaw:.63,pitch:.24,dist:9.9,center:[0,0,0],mode:'cut',selection:'core',flux:false};
const materials={core:'#8294a9',coreEdge:'#64788d',lv:'#e4a36c',lvShade:'#a86236',hv:'#3d83bb',hvShade:'#205985',ins:'#e5dcca',separator:'#9ec8bd',flux:'#039a96'};
const P=[], fluxPaths=[];
function lerp(a,b,t){return a.map((v,i)=>v*(1-t)+b[i]*t)}
function add(a,b){return a.map((v,i)=>v+b[i])}
function sub(a,b){return a.map((v,i)=>v-b[i])}
function mul(a,k){return a.map(v=>v*k)}
function dot(a,b){return a.reduce((v,x,i)=>v+x*b[i],0)}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function norm(a){return mul(a,1/(Math.hypot(...a)||1))}
function poly(v,color,part,group,alpha=1,stroke=null){P.push({v,color,part,group,alpha,stroke});}
function box(c,s,col,part,group){let [x,y,z]=c,[w,h,d]=s.map(v=>v/2),v=[[x-w,y-h,z-d],[x+w,y-h,z-d],[x+w,y+h,z-d],[x-w,y+h,z-d],[x-w,y-h,z+d],[x+w,y-h,z+d],[x+w,y+h,z+d],[x-w,y+h,z+d]];
for(const q of [[0,1,2,3],[4,7,6,5],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2]])poly(q.map(i=>v[i]),col,part,group,1,'#4e6276');}
function line(a,b,col,part,group,width=.014){P.push({v:[a,b],color:col,part,group,line:true,width,alpha:1});}
function annulus(x,cy,rIn,rOut,h,part,group,material,arc0=0,arc1=Math.PI*2){
 const seg=72, yy=cy-h/2, Y=cy+h/2,pt=(r,y,t)=>[x+r*Math.cos(t),y,r*Math.sin(t)];
 for(let j=0;j<seg;j++){
  let a=arc0+(arc1-arc0)*j/seg,b=arc0+(arc1-arc0)*(j+1)/seg;
  poly([pt(rOut,yy,a),pt(rOut,yy,b),pt(rOut,Y,b),pt(rOut,Y,a)],material,part,group,1,'#31536f');
  poly([pt(rIn,yy,b),pt(rIn,yy,a),pt(rIn,Y,a),pt(rIn,Y,b)],material,part,group,1);
  poly([pt(rIn,Y,a),pt(rOut,Y,a),pt(rOut,Y,b),pt(rIn,Y,b)],material,part,group,1);
  poly([pt(rOut,yy,a),pt(rIn,yy,a),pt(rIn,yy,b),pt(rOut,yy,b)],material,part,group,1);
 }
 if(arc1-arc0<6)for(let a of [arc0,arc1])poly([pt(rIn,yy,a),pt(rOut,yy,a),pt(rOut,Y,a),pt(rIn,Y,a)],material,part,group,1);
}
function ring(x,y,r,col,part,group,width=.011,start=0,end=2*Math.PI){let N=70;for(let i=0;i<N;i++){let a=start+(end-start)*i/N,b=start+(end-start)*(i+1)/N;line([x+r*Math.cos(a),y,r*Math.sin(a)],[x+r*Math.cos(b),y,r*Math.sin(b)],col,part,group,width)}}
for(let x of [-1.45,1.45])box([x,0,0],[.57,2.64,.62],materials.core,'core','core');
box([0,1.33,0],[3.55,.46,.64],materials.core,'core','core');box([0,-1.33,0],[3.55,.46,.64],materials.core,'core','core');
// Narrow lamination lines on exposed yoke top and ends.
for(let z of [-.19,-.08,.03,.14,.25]){
 line([-1.76,1.56,z],[1.76,1.56,z],'#aab8c5','core','core',.007);
 line([-1.76,-1.56,z],[1.76,-1.56,z],'#9cacbc','core','core',.007);
}
for(let x of [-1.45,1.45]){
 // Machine geometry intentionally separates low-voltage and high-voltage coils radially,
 // with core-to-LV insulation and a radial LV/HV main insulation duct.
 annulus(x,0,.47,.62,1.78,'secondary','lv','#d88b52');
 annulus(x,0,.655,.705,1.81,'insulation','ins','#e4dac8');
 annulus(x,0,.78,.97,1.84,'primary','hv','#3777ad');
 annulus(x,0,.78,.97,1.84,'primary','hvCut','#3777ad',2.63,6.79); // section window toward viewer
 for(let i=0;i<11;i++){
   let y=-.79+i*.158;
   ring(x,y,.626,'#b66a3f','secondary','lv',.009);
   ring(x,y,.975,'#8cb7d5','primary','hv',.012);
   ring(x,y,.975,'#8cb7d5','primary','hvCut',.012,2.63,6.79);
 }
 for(let a of [-.2,.3,2.8,3.3,4.4]){
    const r=.742;
    line([x+r*Math.cos(a),-.94,r*Math.sin(a)],[x+r*Math.cos(a),.94,r*Math.sin(a)],'#c4bda9','insulation','spacer',.018);
 }
 // end rings where winding protrudes above the iron-core window but does not overlap a yoke.
 ring(x,.925,.71,'#ddcbb4','insulation','ins',.023);
 ring(x,-.925,.71,'#ddcbb4','insulation','ins',.023);
}
// Magnetic flux closed path is a separate instructional overlay, not a second winding.
const path=[[-1.45,-1.22,0],[-1.45,1.28,0],[1.45,1.28,0],[1.45,-1.28,0],[-1.45,-1.28,0]];
for(let i=1;i<path.length;i++)fluxPaths.push([path[i-1],path[i]]);
function offset(group){if(state.mode!=='explode')return [0,0,0];if(group==='hv'||group==='hvCut')return [0,0,2.20];if(group==='lv')return [0,0,0.62];if(group==='ins'||group==='spacer')return [0,0,1.30];return [0,0,-.25];}
function visible(s){if(s.group==='hvCut')return state.mode==='cut';if(s.group==='hv')return state.mode!=='cut';return true;}
function colorToRgb(str){return [parseInt(str.substring(1,3),16),parseInt(str.substring(3,5),16),parseInt(str.substring(5,7),16)]}
const colors={};function shade(str,f){let c=colors[str]||(colors[str]=colorToRgb(str));return `rgb(${c.map(x=>Math.min(255,Math.max(0,Math.round(x*f)))).join(',')})`;}
let proj, canvasScale;
function render(time){
 if(!wrap.isConnected)return;
 let rect=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
 if(rect.width<1||rect.height<1){requestAnimationFrame(render);return;}
 let w=Math.round(rect.width*dpr),h=Math.round(rect.height*dpr);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}canvasScale=dpr;
 ctx.clearRect(0,0,w,h);
 let v=norm([Math.sin(state.yaw)*Math.cos(state.pitch),Math.sin(state.pitch),Math.cos(state.yaw)*Math.cos(state.pitch)]),right=norm(cross([0,1,0],v)),up=norm(cross(v,right));
 let eye=add(state.center,mul(v,state.dist)),focal=Math.min(w,h)*1.40;
 proj=pt=>{let d=sub(pt,eye),depth=-dot(d,v);if(depth<.08)return null;return [w/2+dot(d,right)*focal/depth,h/2-dot(d,up)*focal/depth,depth]};
 let all=[];for(let s of P){if(!visible(s))continue;let q=s.v.map(p=>proj(add(p,offset(s.group))));if(q.some(p=>!p))continue;
  let dep=q.reduce((a,p)=>a+p[2],0)/q.length;all.push({s,q,dep});}
 all.sort((a,b)=>b.dep-a.dep);
 for(let f of all){let {s,q,dep}=f;ctx.beginPath();ctx.moveTo(q[0][0],q[0][1]);for(let i=1;i<q.length;i++)ctx.lineTo(q[i][0],q[i][1]);
  if(s.line){ctx.lineWidth=Math.max(.65,Math.min(4,s.width*focal/dep*2));ctx.lineCap='round';ctx.strokeStyle=s.color;ctx.stroke();continue;}
  ctx.closePath();let v1=sub(s.v[1],s.v[0]),v2=sub(s.v[2],s.v[0]),n=norm(cross(v1,v2));let light=Math.max(.63,Math.min(1.17,.89+dot(n,norm([.45,1,.8]))*.25));
  ctx.fillStyle=s.part===state.selection?shade(s.color,Math.min(light*1.065,1.2)):shade(s.color,light);ctx.fill();ctx.lineWidth=.27*dpr;ctx.strokeStyle=s.stroke||shade(s.color,.83);ctx.globalAlpha=.37;ctx.stroke();ctx.globalAlpha=1;
 }
 if(state.flux){ctx.save();ctx.strokeStyle=materials.flux;ctx.lineWidth=2.5*dpr;ctx.setLineDash([10*dpr,7*dpr]);ctx.lineDashOffset=-time/90;for(const [a,b] of fluxPaths){let aa=proj(add(a,[0,0,-.37])),bb=proj(add(b,[0,0,-.37]));if(aa&&bb){ctx.beginPath();ctx.moveTo(aa[0],aa[1]);ctx.lineTo(bb[0],bb[1]);ctx.stroke();}}ctx.restore();}
 requestAnimationFrame(render);
}
function change(mode){state.mode=mode;wrap.querySelectorAll('[data-p3d-mode]').forEach(el=>el.classList.toggle('active',el.dataset.p3dMode===mode));state.dist=mode==='explode'?11.6:9.9;state.center=[0,0,mode==='explode'?.7:0];}
let infos={
 core:['叠片铁心','两根心柱与上下铁轭构成闭合主磁路。磁通沿铁心闭合，交链同一心柱上的高、低压绕组。'],
 primary:['一次／高压绕组 N₁','蓝色外层。在本降压示例中，一次绕组分置在两根心柱上并作电气串联，图中不把表面条纹当作实际匝数。'],
 secondary:['二次／低压绕组 N₂','铜色内层。与一次绕组同轴套装，靠近心柱；绕组之间有绝缘层和油道。两侧绕组并不电气连接。']
};
function select(id){state.selection=id;wrap.querySelectorAll('[data-p3d-select]').forEach(el=>el.classList.toggle('active',el.dataset.p3dSelect===id));info.innerHTML='<strong>'+infos[id][0]+'</strong><p>'+infos[id][1]+'</p>';}
wrap.querySelectorAll('[data-p3d-mode]').forEach(b=>b.onclick=()=>change(b.dataset.p3dMode));wrap.querySelectorAll('[data-p3d-select]').forEach(b=>b.onclick=()=>select(b.dataset.p3dSelect));
wrap.querySelector('#p3d-reset').onclick=()=>{state.yaw=.63;state.pitch=.24;state.dist=9.9;state.center=[0,0,0];change('cut');select('core');};
wrap.querySelector('#p3d-plus').onclick=()=>{state.dist=Math.max(4.6,state.dist*.82)};
wrap.querySelector('#p3d-minus').onclick=()=>{state.dist=Math.min(19,state.dist*1.2)};
let points=new Map(),last=null;
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);points.set(e.pointerId,{x:e.clientX,y:e.clientY});});
canvas.addEventListener('pointermove',e=>{let p=points.get(e.pointerId);if(!p)return;let dx=e.clientX-p.x,dy=e.clientY-p.y;points.set(e.pointerId,{x:e.clientX,y:e.clientY});if(points.size===1){if(e.buttons===2){let speed=.002*state.dist;state.center[0]-=dx*speed;state.center[1]+=dy*speed;}else{state.yaw+=dx*.012;state.pitch=Math.max(-1.12,Math.min(1.18,state.pitch+dy*.009));}}else if(points.size===2){let ps=[...points.values()],d=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);if(last)state.dist=Math.max(4.6,Math.min(19,state.dist*last/d));last=d;}});
let finish=e=>{points.delete(e.pointerId);last=null;};canvas.addEventListener('pointerup',finish);canvas.addEventListener('pointercancel',finish);canvas.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('wheel',e=>{e.preventDefault();state.dist=Math.min(19,Math.max(4.6,state.dist*Math.exp(e.deltaY*.0013)));},{passive:false});
canvas.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')state.yaw-=.12;else if(e.key==='ArrowRight')state.yaw+=.12;else if(e.key==='ArrowUp')state.pitch=Math.min(1.16,state.pitch+.10);else if(e.key==='ArrowDown')state.pitch=Math.max(-1.16,state.pitch-.10);else return;e.preventDefault();});
const toggle=wrap.querySelector('#p3d-flux');if(toggle)toggle.onchange=()=>state.flux=toggle.checked;
select('core');change('cut');requestAnimationFrame(render);
})();

};
window.LN_MOUNT_TRANSFORMER_QUIZ=function(){
(()=>{const b=document.getElementById('quiz-check');b?.addEventListener('click',()=>{const s=document.querySelector('input[name="heatQuiz"]:checked');const f=document.getElementById('quiz-feedback');if(!s){f.textContent='请先选择一项。';return;}f.textContent=s.value==='b'?'正确。热量从损耗源经固体、油、金属散热结构传至环境，主要靠油的对流、金属导热和空气对流及辐射。':'需要修正：油不直接透过油箱向外界辐射；储油柜也不是主循环散热器。答案是 B。';f.style.color=s.value==='b'?'#138b79':'#ba712e'})})();
};
