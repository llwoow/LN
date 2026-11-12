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
