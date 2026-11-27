"use strict";
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const context=vm.createContext({window:{},document:{createElement:()=>({})}});
// Observe the private teaching models without adding a production API.
const source=fs.readFileSync(path.join(__dirname,'../courses/electromagnetic-compatibility/model/emc-labs.js'),'utf8');
vm.runInContext(source.replace('window.LN_MOUNT_EMC_LABS=mount;','window.__review=specs;window.LN_MOUNT_EMC_LABS=mount;'),context);
const models=context.window.__review;
// Rounded display oracles from independent units/closed-form calculations.
const expected={'mode-split':['I1=11 mA','I2=-9 mA','2 mA'],'lisn-two-port':['ID=10 mA','总共模=4 mA','U1=600 mV','U2=-400 mV'],'parasitic-current':['1 mA'],'cable-size':['l/λ=0.0333'],'pcb-loop':['200 mm²'],'oxide-field':['1 GV/m'],'induced-field':['1.57 mV/m'],'common-return':['0.400 V'],'skin-wire':['66.1 μm','7.57'],capacitive:['0.953 V','17.7°'],'skin-depth':['66.1 μm','13.1 dB'],filter:['50.3 kHz'],
 'capacitor-srf':['5.03 MHz','20 mΩ'],'line-reflection':['2.50 ns','1.65 V','3.30 V'],
 'eddy-shield':['15.9 kHz','0.200'],'probe-ideal':['31.4 mV'],'ground-rise':['3.18e+3 V','227 V'],
 'surge-lead':['600 V'],'impulse-shield':['25%','2.91 MHz'],switching:['15.9 kHz','200 kV']};
Object.assign(expected,{'ground-case':['110 V'],'ground-float':['地环路'],'ground-topology':['共用地线'],'ground-mixed':['15.9 Ω'],'ground-partition':['0 mV'],'ground-loop':['200 mA','10 mV'],'ground-flux':['3.14 mV'],'ground-suppression':['切断'],'ground-choke':['19.8 μH'],'ground-shield-point':['B点','40 mV'],'ground-shield-end':['单端'],'ground-length':['λ=10 m','0.500 m','1 m'],'ground-skin':['66.1 μm','3.03']});
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
