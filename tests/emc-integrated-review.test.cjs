"use strict";
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const dir=path.join(__dirname,'../courses/electromagnetic-compatibility');
const read=p=>fs.readFileSync(path.join(dir,p),'utf8');
const window={},location={},context=vm.createContext({window,location,CSS:{escape:s=>s},requestAnimationFrame:()=>{},document:{createElement:()=>({})}});
vm.runInContext(read('exam-review-data.js'),context);
vm.runInContext(read('model/emc-labs.js').replace('window.LN_MOUNT_EMC_LABS=mount;','window.reviewModels=specs;window.LN_MOUNT_EMC_LABS=mount;'),context);
vm.runInContext(read('exam-review.js'),context);
function render(anchor){
 const events={},content={innerHTML:'',isConnected:true,querySelector:()=>null};
 const select={addEventListener:(k,f)=>events.change=f};
 const search={value:'',addEventListener:(k,f)=>events.search=f};
 const root={innerHTML:'',querySelector:s=>s==='#emc-review-content'?content:s==='#emc-review-search'?search:select};
 window.LNEmcExam.render(root,anchor,async()=>{},null);
 return {root,content,search,events};
}
let all=new Set();
for(const n of [1,2,3]){
 const {root,content,events}=render('chapter-'+n);
 assert(root.innerHTML.includes('value="'+n+'" selected'));
 assert(content.innerHTML.includes('重点难点与推导复习'));
 for(const m of content.innerHTML.matchAll(/data-emc-lab="([^"]+)"/g)){assert(window.reviewModels[m[1]],m[1]);all.add(m[1]);}
 events.change({target:{value:'integrated'}});
 assert(location.hash.endsWith('/exam-review/integrated'));
}
assert.equal(all.size,20);
const x=render('integrated');
assert(x.root.innerHTML.includes('value="integrated" selected'));
assert(x.content.innerHTML.includes('综合例题')&&x.content.innerHTML.includes('独立掌握自测'));
x.search.value='栅氧';x.events.search();assert(x.content.innerHTML.includes('第1章 · 分贝、源与危害'));
const rest=render('chapter-4');assert(!rest.content.innerHTML.includes('重点难点与推导复习'));
console.log('EMC integrated review routes, search and 20 existing model references verified.');
