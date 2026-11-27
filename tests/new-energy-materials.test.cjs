'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const context={window:{}};vm.createContext(context);
const load=f=>vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),context,{filename:f});
load('courses/new-energy-materials/manifest.js');load('courses/new-energy-materials/knowledge-map.js');
const c=context.window.LN_NEW_ENERGY_MATERIALS,m=context.window.LN_NEW_ENERGY_MATERIALS_MAP;
assert.equal(c.id,'new-energy-materials');assert.equal(c.sections.length,52);
assert.equal(new Set(c.sections.map(s=>s.id)).size,c.sections.length);
const ids=new Set(c.sections.map(s=>s.id));
assert.ok(c.sections.every(s=>s.kind==='html'&&s.src));
assert.ok(m.nodes.every(n=>ids.has(n.section)));
assert.ok(m.links.every(l=>ids.has(l.from)&&ids.has(l.to)&&l.description));
for(const file of new Set(c.sections.map(s=>s.src)))load(file);
for(const s of c.sections){const key=c.id+'/'+s.id;const html=context.window.LN_LESSONS[key]?.html||'';assert.ok(html.length>100,key);assert.ok(html.includes('id="'+s.id+'"'),key);}
const q=context.window.LN_LESSONS['new-energy-materials/nem-homework'].html;
assert.ok(q.includes('第1题')&&q.includes('第2题')&&q.includes('机械能')&&q.includes('化学能'));
console.log('new-energy-materials: catalog, lesson loading, graph and 2 exercises PASS');

const pv=context.window.LN_LESSONS['new-energy-materials/nem-3-1'].html;
for(const id of ['pv-mode-0','pv-mode-1','pv-mode-2','pv-formation-figure','pv-circuit-figure','pv-field-table','pv-eq-gauss'])assert.ok(pv.includes('id="'+id+'"'),id);
assert.equal((pv.match(/type="radio" name="pv-stage"/g)||[]).length,3);
assert.ok(pv.includes('value="2" checked')&&pv.includes('#pv-mode-1:checked')&&pv.includes('#pv-mode-2:checked'));
assert.equal((pv.match(/<svg /g)||[]).length,2);
assert.equal((pv.match(/<math /g)||[]).length,5);
assert.ok(pv.includes('外部电流为零，不表示内部电场为零'));
console.log('photoinduced field: three states, SVGs, equations and boundary checks PASS');
