/* Independent topology/contact/vector-physics checks. node tests/model.test.cjs */
const assert=require('node:assert/strict');
const M=require('../courses/electrical-machines/model/motor-winding-model.js');
const near=(a,b,tol=1e-8)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
const count={models:0,angularStates:0,vectorIntegrals:0};
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function independentlyContacts(model,angle,shift){
 const p=model.parameters,step=2*Math.PI/p.slots,rot=angle*Math.PI/180,bs=shift*Math.PI/180;
 return Array.from({length:p.poles},(_,j)=>{
  const center=j*2*Math.PI/p.poles+bs,brush=[center-p.brushWidth*step/2,center+p.brushWidth*step/2];
  return Array.from({length:p.slots},(_,k)=>k+1).filter(k=>{
   const barCenter=rot+(k-1.5)*step,half=(1-p.micaRatio)*step/2;
   return [-2,-1,0,1,2].some(n=>Math.min(brush[1],barCenter+half+n*2*Math.PI)-Math.max(brush[0],barCenter-half+n*2*Math.PI)>1e-10);
  });
 });
}
for(const [poles,slots] of [[2,8],[2,32],[4,16],[4,24],[6,24],[6,36],[8,32],[8,64]])for(const brushWidth of [.25,.65,1.4]){
 const model=M.createModel({poles,slots,brushWidth});count.models++;
 assert.equal(model.coils.length,slots);assert.equal(new Set(model.coils.map(c=>c.upperSlot)).size,slots);assert.equal(new Set(model.coils.map(c=>c.lowerSlot)).size,slots);
 const degree=Array(slots).fill(0),visited=new Set();let bar=1;
 for(let i=0;i<slots;i++){
  assert.ok(!visited.has(bar));visited.add(bar);const c=model.coils[bar-1];degree[c.startBar-1]++;degree[c.endBar-1]++;
  assert.equal((c.lowerSlot-c.upperSlot+slots)%slots,slots/poles);assert.equal((c.endBar-c.startBar+slots)%slots,1);
  near(c.segments[0][0].a,(c.startBar-1.5)*model.pitch);near(c.segments[5].at(-1).a,(c.index+.5)*model.pitch);
  bar=c.endBar;
 }
 assert.equal(bar,1);assert.deepEqual(degree,Array(slots).fill(2));
 for(let angle=0;angle<360;angle+=2)for(const shift of [-10,0,10]){
  const e=M.electricalState(model,angle,shift);count.angularStates++;assert.ok(e.valid,e.errors.join('\n'));assert.equal(e.branches.length,poles);
  const contacts=independentlyContacts(model,angle,shift);e.brushes.forEach((b,i)=>assert.deepEqual(b.bars,contacts[i]));
  const used=e.branches.flatMap(b=>b.path.map(t=>t.coil+1)).concat(e.commutatingCoils);
  assert.equal(used.length,slots);assert.equal(new Set(used).size,slots);
  for(const b of e.branches){
   assert.equal(e.brushes[b.fromBrush-1].polarity,1);assert.equal(e.brushes[b.toBrush-1].polarity,-1);
   let potential=model.parameters.supplyVoltage;
   for(const edge of b.path){potential+=edge.direction*e.coils[edge.coil].emf-b.current*model.coils[edge.coil].resistance;}
   near(potential,0,1e-7);
  }
  near(e.estimate.powerResidual,0,1e-6);near(e.estimate.torquePowerResidual,0,1e-6);
 }
}
const model=M.createModel(),p=model.parameters;
const atZero=M.electricalState(model,0);assert.deepEqual(atZero.commutatingCoils,[1,5,9,13]);assert.deepEqual(atZero.branches.map(b=>b.path.map(x=>x.coil+1)),[[2,3,4],[8,7,6],[10,11,12],[16,15,14]]);
assert.deepEqual(M.electricalState(model,11.25).commutatingCoils,[]);
const wide=M.electricalState(M.createModel({brushWidth:1.4}),11.25);assert.equal(wide.brushes[0].bars.length,3);assert.equal(wide.commutatingCoils.length,8);
for(const coil of atZero.coils.filter(c=>c.commutating))near(coil.emf,0);
assert.notEqual(M.electricalState(model,90).coils[1].branchId,atZero.coils[1].branchId);
// Independently integrate motional EMF and Lorentz torque as 3-D vector products.
for(const angle of [0,13.4,67,122.5,288]){
 const e=M.electricalState(model,angle);
 for(const coil of model.coils){
  const a=(angle*Math.PI/180)+coil.index*model.pitch,b=a+model.span*model.pitch,omega=p.rpm*2*Math.PI/60;
  let emf=0,torquePerAmp=0;
  for(const [theta,radius,direction] of [[a,coil.topR/1000,-1],[b,coil.lowerR/1000,1]]){
   const position=[0,radius*Math.cos(theta),radius*Math.sin(theta)],velocity=cross([omega,0,0],position);
   const amplitude=p.fluxDensity*(radius/(p.rotorDiameter/2000))**(p.poles/2-1),br=-amplitude*Math.sin(p.poles/2*theta),bt=-amplitude*Math.cos(p.poles/2*theta);
   const field=[0,br*Math.cos(theta)-bt*Math.sin(theta),br*Math.sin(theta)+bt*Math.cos(theta)];
   const lengthVector=[direction*p.coreLength/1000,0,0];
   emf+=p.turns*dot(cross(velocity,field),lengthVector);
   torquePerAmp+=p.turns*cross(position,cross(lengthVector,field))[0];
  }
  near(emf,e.coils[coil.index].emf);near(torquePerAmp,e.coils[coil.index].torquePerAmp);count.vectorIntegrals++;
 }
}
const stopped=M.electricalState(M.createModel({rpm:0}));assert.ok(Number.isFinite(stopped.estimate.torque));near(stopped.estimate.conversionPower,0);
// Independent finite differences: divergence and curl of the prescribed reference field.
for(const theta of [.1,.7,1.9]){
 const rr=46,h=1e-3,k=1e-5,F=(r,t)=>M.fieldAt(model,r,t);
 const divergence=((rr+h)*F(rr+h,theta).radial-(rr-h)*F(rr-h,theta).radial)/(2*h*rr)+(F(rr,theta+k).tangential-F(rr,theta-k).tangential)/(2*k*rr);
 const curl=((rr+h)*F(rr+h,theta).tangential-(rr-h)*F(rr-h,theta).tangential)/(2*h*rr)-(F(rr,theta+k).radial-F(rr,theta-k).radial)/(2*k*rr);
 near(divergence,0,1e-8);near(curl,0,1e-8);
}
const temp20=M.createModel({temperature:20}),temp75=M.createModel({temperature:75});near(temp75.coils[0].resistance/temp20.coils[0].resistance,1+.00393*55);
assert.throws(()=>M.createModel({poles:6,slots:16}));assert.throws(()=>M.createModel({poles:4,slots:8,brushWidth:1.4}));assert.throws(()=>M.createModel({wireArea:100}));assert.throws(()=>M.createModel({commutatorGap:10}));assert.throws(()=>M.createModel({winding:'wave'}));assert.throws(()=>M.createModel({rpm:NaN}));
assert.deepEqual(M.createModel(JSON.parse(JSON.stringify(M.exportData(model,atZero))).parameters).pitches,model.pitches);
const report={passed:true,...count,checks:['single closed ring and slot-layer bijection','path endpoints match copper-bar geometry','interval-overlap contact comparison','coil partition and branch count through full rotation','positive-to-negative branch KVL','motional EMF from 3D cross product','Lorentz torque from 3D cross product','analytic reference field divergence and curl by finite differences','zero-speed torque without dividing by speed','temperature coefficient and invalid engineering inputs'],limits:'The checks verify this declared reference model, not an actual manufactured machine.'};
console.log(JSON.stringify(report,null,2));
