'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ctx=vm.createContext({window:{}});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../courses/automatic-control/root-locus-lab.js'),'utf8'),ctx);
const api=ctx.window.LN_ROOT_LOCUS;
assert(api, 'root-locus numerical model missing');
const distance=(x,y)=>Math.hypot(x.re-y.re,x.im-y.im);
for(const k of [0,0.01,0.5,1,4.1,4.331570416,4.34,5,8.16,20,80]){
  const roots=api.solve(k);
  assert.equal(roots.length,4);
  for(const s of roots){
    assert(Number.isFinite(s.re)&&Number.isFinite(s.im), 'non-finite computed root');
    const p=api.polynomial(s,k);
    const residual=Math.hypot(p.re,p.im);
    assert(residual<2e-6, 'K='+k+' root='+s.re+'+'+s.im+'j residual '+residual);
  }
}
const roots5=api.solve(5);
for(const expected of [{re:-2.33751858,im:0.348769},{re:-2.33751858,im:-0.348769},{re:-0.16248142,im:0.93206947},{re:-0.16248142,im:-0.93206947}]){
 assert(roots5.some(z=>distance(z,expected)<1e-5), 'K=5 expected root '+expected.re+'+j'+expected.im);
}
const rootsBoundary=api.solve(8.16);
for(const im of [-Math.sqrt(1.2),Math.sqrt(1.2)])assert(rootsBoundary.some(z=>Math.abs(z.re)<1e-7&&Math.abs(z.im-im)<1e-6),'imaginary-axis crossing');
assert.equal(api.group(0).leftReal.re,-3);
assert.equal(api.group(0).rightReal.re,0);
assert(api.group(20).leftUpper.re<0&&api.group(20).rightUpper.re>0);
console.log('Numerical root-locus solver matches independent polynomial and sample roots.');

// Marker colour follows the branch origin, including the root starting at zero.
for(const k of [0,1,5,8.16,20]){
 const g=api.group(k);
 for(const z of [g.leftReal,g.rightReal,g.leftUpper,g.leftLower].filter(Boolean))assert.equal(api.originFamily(k,z),'real');
 for(const z of [g.rightUpper,g.rightLower])assert.equal(api.originFamily(k,z),'complex');
}


const synthCtx=vm.createContext({window:{}});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../courses/automatic-control/root-locus-synthesis.js'),'utf8'),synthCtx);
const cubic=synthCtx.window.LN_AC_SYNTHESIS;
assert(cubic, 'cubic root-locus model unavailable');
for(const k of [0,0.1,2,3.9,4,4.1,6,10,20]){
 const rs=cubic.roots(k);
 assert.equal(rs.length,3);
 assert(Math.abs(rs[1].re-rs[2].re)<1e-10,'real conjugacy');
 assert(Math.abs(rs[1].im+rs[2].im)<1e-10,'imaginary conjugacy');
 for (const z of rs) {
   const p=cubic.polynomial(z,k);
   assert(Math.hypot(p.re,p.im)<1e-9,'cubic residual K='+k+' at '+JSON.stringify(z));
 }
}
const k0=cubic.roots(0);
assert(k0.some(z=>distance(z,{re:0,im:0})<1e-10));
assert(k0.some(z=>distance(z,{re:-1,im:1})<1e-10));
assert(k0.some(z=>distance(z,{re:-1,im:-1})<1e-10));
const k1=cubic.roots(1);
assert(k1.some(z=>distance(z,{re:-1,im:0})<1e-10));
assert(k1.some(z=>distance(z,{re:-0.5,im:Math.sqrt(3)/2})<1e-10));
assert(k1.some(z=>distance(z,{re:-0.5,im:-Math.sqrt(3)/2})<1e-10));
assert(Math.abs(-k1[1].re/Math.hypot(k1[1].re,k1[1].im)-0.5)<1e-10,'zeta=0.5 at K=1');
const k4=cubic.roots(4);
assert(k4.some(z=>distance(z,{re:-2,im:0})<1e-10));
assert(k4.some(z=>distance(z,{re:0,im:Math.sqrt(2)})<1e-10));
assert(k4.some(z=>distance(z,{re:0,im:-Math.sqrt(2)})<1e-10));
assert(cubic.roots(3.9).every(z=>z.re<0));
assert(cubic.roots(4.1).some(z=>z.re>0));
// Cubic breakaway candidate: non-real K invalidates real positive-gain root locus.
for(const sign of [-1,1]){
 const root={re:-2/3,im:sign*Math.sqrt(2)/3};
 const kp={re:20/27,im:-sign*4*Math.sqrt(2)/27};
 const p=cubic.polynomial(root,kp.re);
 assert(Math.abs(p.im+kp.im)<1e-9,'nonreal gain candidate not accounted for');
}
console.log('Cubic 4.3.1 roots, conjugacy, imaginary crossing, and candidate exclusion verified.');
