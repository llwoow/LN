'use strict';
const assert=require('node:assert/strict');
const {projection,plan,sample}=require('../courses/robot-drive-engineering/model/drive-labs.js');
assert(Math.abs(projection(2,30).q+1)<1e-12);
for(let t=-180;t<=180;t+=3){const r=projection(2,t);assert(Math.abs(r.d*r.d+r.q*r.q-4)<1e-12);}
for(const distance of [-2,-.1,0,.1,1,2]){
 const p=plan(distance,1,2);let area=0;
 for(let i=0;i<10000;i++){
  const r=sample(p,p.total*(i+.5)/10000);area+=r.v*p.total/10000;
  assert(Math.abs(r.v)<=1+1e-10);assert(Math.abs(r.a)<=2+1e-10);
 }
 assert(Math.abs(area-distance)<1e-7);
 assert.equal(sample(p,p.total).x,distance);assert(Math.abs(sample(p,p.total).v)<1e-12);
 assert(Math.abs(sample(p,0).v)<1e-12);
}
assert.equal(plan(1,1,2).total,1.5);
assert.equal(plan(.1,1,2).kind,'三角形');
assert(Math.abs(plan(.1,1,2).total-Math.sqrt(.2))<1e-12);
assert.throws(()=>plan(1,0,2),RangeError);
console.log('Drive projection invariants and signed constrained trajectories verified.');
