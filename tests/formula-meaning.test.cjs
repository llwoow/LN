'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const ctx=vm.createContext({window:{},document:{createElement:()=>({setAttribute(){}}),querySelector:()=>({append(){}}),addEventListener(){}},addEventListener(){}});
for(const file of ['glossary-index.js','courses/electromagnetic-compatibility/glossary-index.js','courses/robot-drive-engineering/glossary-index.js','courses/automatic-control/glossary-index.js','glossary.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),ctx);
const resolve=(cid,sid,key,eq)=>ctx.window.LNGlossary.resolveSymbol({id:cid},{id:sid},key,'symbol',eq);
const checks=[
 ['electromagnetic-compatibility','emc-1-1','M','D.1.1.1','互感'],
 ['electromagnetic-compatibility','emc-6-2','S','D.6.2.1','磁芯'],
 ['electromagnetic-compatibility','emc-6-2','S','D.6.2.3','接收天线'],
 ['electromagnetic-compatibility','emc-8-1','R','D.8.1.1','理想电阻'],
 ['electromagnetic-compatibility','emc-8-1','R','D.8.1.4','串联损耗'],
 ['electromagnetic-compatibility','emc-4-4','t','D.4.4.3','厚度'],
 ['electromagnetic-compatibility','emc-7-2','t','D.7.2.1','时间'],
 ['robot-drive-engineering','rd-cascade-control','u_k^*','R.4.8','未限幅'],
 ['robot-drive-engineering','rd-cascade-control','u_k','R.4.8','裁剪后'],
 ['robot-drive-engineering','rd-edge-inference','b','R.5.4','输入电压'],
 ['robot-drive-engineering','rd-edge-inference','b','R.6.4','偏置'],
 ['robot-drive-engineering','rd-edge-inference','hat:y_n','R.6.4','预测'],
 ['automatic-control','ac-3-6','G','U.3.6.7','PI控制器'],
 ['automatic-control','ac-3-6','G','U.3.6.1','总传递函数'],
];
for(const [cid,sid,key,eq,meaning] of checks){const e=resolve(cid,sid,key,eq);assert(e,JSON.stringify([sid,key,eq]));assert(e.description.includes(meaning),e.id+': '+e.description);}
assert.equal(resolve('electromagnetic-compatibility','emc-6-2','S',''),null,'Two local areas must not guess a meaning outside either equation.');
assert.equal(resolve('robot-drive-engineering','rd-edge-inference','b',''),null,'RL gain and regression bias have no interchangeable fallback.');
console.log('Local meanings, equation boundaries, hats, semantic stars and ambiguous fallbacks verified.');
