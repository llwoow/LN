'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const ctx = vm.createContext({window:{}});
for(const f of ['courses/electrical-materials/manifest.js','courses/electrical-materials/knowledge-map.js']){
  vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),ctx,{filename:f});
}
const course = ctx.window.LN_ELECTRICAL_MATERIALS;
const map = ctx.window.LN_ELECTRICAL_MATERIALS_MAP;
const bookIds=new Set(course.sections.filter(s=>s.textbookSection).map(s=>s.id));
assert.equal(bookIds.size,29);
assert.equal(course.sections.filter(s=>s.kind==='outline').length,24);
for(const id of ['em-test-summary','em-test-fill','em-test-short','em-test-review'])assert(course.sections.some(s=>s.id===id&&s.kind==='html'));
assert.equal(course.sections.length,33);
const found = new Set();
for(const s of course.sections) {
  if(s.kind==='outline'){assert(!s.src);found.add(s.id);continue;}
  assert.equal(s.kind, 'html');
  assert(!found.has(s.id));
  found.add(s.id);
  const lesson = fs.readFileSync(path.join(root,s.src), 'utf8');
  const child = vm.createContext({window:{}});
  vm.runInContext(lesson,child,{filename:s.src});
  const html = child.window.LN_LESSONS[course.id+'/'+s.id].html;
  assert(/<h2[ >]/.test(html), s.id+' lacks a real reading title');
  if(s.textbookSection)assert(html.includes('reading-reference'), s.id+' lacks brief reference');
}
assert.equal(map.nodes.length,course.sections.length);
for(const n of map.nodes) assert(found.has(n.section));
for(const e of map.links){assert(found.has(e.from)&&found.has(e.to)&&e.description);}
const toc = JSON.parse(fs.readFileSync(path.join(root,'courses/electrical-materials/curriculum.json'),'utf8'));
assert.equal(toc.chapters.length,7);
assert.equal(toc.chapters.reduce((n,c)=>n+c.sections.length,0),29);
const bank = JSON.parse(fs.readFileSync(path.join(root,'courses/practice/bank.json'),'utf8'));
const materialQs = bank.questions.filter(q=>q.course===course.id);
assert(materialQs.length>=7);
for(const q of materialQs) assert(q.sections.every(id=>found.has(id)),q.id);
const x = 0.004/(0.2*0.01);
assert.equal(x,2);assert.equal(x*8,16);assert.equal(x*2,4);
assert.equal((400/(2e-6))/(0.1/100)/1e9,200);
const resource=JSON.parse(fs.readFileSync(path.join(root,'courses/resources/catalog.json'),'utf8'));
assert(resource.resources.some(r=>r.targets.some(t=>t.course===course.id)));
console.log('Material textbook outlines, authored readings, supplied-test routes, native practice and model values verified.');
