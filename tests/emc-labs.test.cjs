"use strict";
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const context=vm.createContext({window:{},document:{createElement:()=>({})}});
// Observe the private teaching models without adding a production API.
const source=fs.readFileSync(path.join(__dirname,'../courses/electromagnetic-compatibility/model/emc-labs.js'),'utf8');
vm.runInContext(source.replace('window.LN_MOUNT_EMC_LABS=mount;','window.__review=specs;window.LN_MOUNT_EMC_LABS=mount;'),context);
const models=context.window.__review;
// Rounded display oracles from independent units/closed-form calculations.
const expected={capacitive:['0.953 V','17.7°'],'skin-depth':['66.1 μm','13.1 dB'],filter:['50.3 kHz'],
 'capacitor-srf':['5.03 MHz','20 mΩ'],'line-reflection':['2.50 ns','1.65 V','3.30 V'],
 'eddy-shield':['15.9 kHz','0.200'],'probe-ideal':['31.4 mV'],'ground-rise':['3.18e+3 V','227 V'],
 'surge-lead':['600 V'],'impulse-shield':['25%','2.91 MHz'],switching:['15.9 kHz','200 kV']};
assert.equal(Object.keys(models).length,Object.keys(expected).length);
for(const [name,model] of Object.entries(models)){
 const initial=Object.fromEntries(model.inputs.map(s=>[s.key,s.value]));
 const text=model.run(initial).text;
 for(const fragment of expected[name])assert(text.includes(fragment),name+': expected '+fragment+' in '+text);
 for(const input of model.inputs)for(const extreme of [input.min,input.max]){
  const result=model.run({...initial,[input.key]:extreme});
  assert(!/NaN|Infinity|未定义/.test(result.text),name+': non-finite output');
  assert(!/NaN|Infinity/.test(result.plot.innerHTML),name+': non-finite curve');
 }
}
console.log('All EMC interactive models match independent baseline values and remain finite at control limits.');
