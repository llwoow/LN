'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const entry=(id,section,aliases,reuseAliases=[])=>({id,kind:'term',source:{section},sections:[section],aliases,reuseAliases});
const entries=[
  entry('dna','definition',['DNA','deoxyribonucleic acid'],['DNA','deoxyribonucleic acid']),
  entry('local-dna','local',['DNA']),
  entry('first-conflict','a',['shared'],['shared']),
  entry('second-conflict','b',['shared'],['shared']),
  {...entry('ph','definition',['pH'],['pH']),caseSensitiveAliases:['pH']},
  {id:'scalar-k',kind:'symbol',keys:['K'],sections:['definition'],source:{section:'definition'},group:'one'}
];
const context=vm.createContext({
  window:{LN_GLOSSARY:{demo:{entries}}},
  document:{createElement:()=>({setAttribute(){}}),querySelector:()=>({append(){}}),addEventListener(){}},
  addEventListener(){}
});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../glossary.js'),'utf8'),context);
const glossary=context.window.LNGlossary;
let aliases=glossary.termAliases({id:'demo'},{id:'another',group:'one'});
assert.equal(aliases.find(a=>a.text==='DNA').entry.id,'dna','A reviewed term should reuse its original definition');
assert(!aliases.some(a=>a.text==='shared'),'Conflicting reused aliases must not silently select a definition');
assert(aliases.find(a=>a.text==='pH').caseSensitive,'pH must retain its reviewed case');
assert.equal(glossary.resolveSymbol({id:'demo'},{id:'another',group:'one'},'K'),null,'A local symbol must not follow terminology reuse');
aliases=glossary.termAliases({id:'demo'},{id:'local',group:'one'});
assert.equal(aliases.find(a=>a.text==='DNA').entry.id,'local-dna','A local definition must take precedence');
console.log('Reviewed term reuse, ambiguity guards, case sensitivity and local-symbol boundaries verified.');
