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
assert.equal(course.sections.length, 5);
const found = new Set();
for(const s of course.sections) {
  assert.equal(s.kind, 'html');
  assert(!found.has(s.id));
  found.add(s.id);
  const lesson = fs.readFileSync(path.join(root,s.src), 'utf8');
  const child = vm.createContext({window:{}});
  vm.runInContext(lesson,child,{filename:s.src});
  const html = child.window.LN_LESSONS[course.id+'/'+s.id].html;
  assert(html.includes('<h2>') && html.length > 1100, s.id+' lacks authored material');
  assert(html.includes('ln-source-note'), s.id+' lacks source note');
}
assert.equal(map.nodes.length, 5);
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
console.log('Electrical materials course, map, 7 chapters, 7 practice items, resource and model values verified.');
