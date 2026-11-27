(function(){
  'use strict';
  const e=1.602176634e-19;
  const defaults=Object.freeze({E:1000,muN:1350,muP:480,logN:16,logP:16});
  function calculate({E,muN,muP,logN,logP}){
    const mn=muN*1e-4,mp=muP*1e-4,n=10**logN,p=10**logP;
    const vn=-mn*E,vp=mp*E,sn=e*n*mn,sp=e*p*mp,sigma=sn+sp;
    return {vn,vp,sigma,rho:1/sigma,jn:sn*E,jp:sp*E,j:sigma*E};
  }
  function mount(body){
    const lab=body.querySelector('[data-mobility-lab]');
    if(!lab||lab.dataset.mounted)return;
    lab.dataset.mounted='true';
    const inputs=[...lab.querySelectorAll('[data-mobility-input]')];
    const find=(type,key)=>lab.querySelector('[data-mobility-'+type+'="'+key+'"]');
    const fmt=v=>v===0?'0':Number(v.toPrecision(4)).toString();
    function draw(name,value){
      const line=find('arrow',name),sign=Math.sign(value);
      line.style.visibility=sign?'visible':'hidden';
      const start=name==='E'?170-85*sign:175+14*sign;
      const end=name==='E'?170+85*sign:start+sign*Math.min(86,Math.abs(value)*.44);
      line.setAttribute('x1',start);line.setAttribute('x2',end);
    }
    function update(){
      const v=Object.fromEntries(inputs.map(i=>[i.dataset.mobilityInput,Number(i.value)]));
      for(const [k,x] of Object.entries(v))find('value',k).textContent=String(x);
      const r=calculate(v),units={vn:'m/s',vp:'m/s',sigma:'S/m',rho:'Ω·m',jn:'A/m²',jp:'A/m²',j:'A/m²'};
      for(const [k,x] of Object.entries(r))find('result',k).textContent=fmt(x)+' '+units[k];
      draw('E',v.E);draw('n',r.vn);draw('p',r.vp);
      for(const side of ['left','right']){
        const polarity=Math.sign(v.E)*(side==='left'?1:-1);
        find('sign',side).textContent=polarity>0?'+':polarity<0?'−':'0';
        find('plate',side).setAttribute('fill',polarity>0?'#dc8841':polarity<0?'#3885df':'#888888');
      }
    }
    inputs.forEach(i=>i.addEventListener('input',update));
    lab.querySelector('[data-mobility-reset]').addEventListener('click',()=>{inputs.forEach(i=>i.value=defaults[i.dataset.mobilityInput]);update();});
    update();
  }
  window.LN_MobilityLab={mount,calculate,defaults};
})();
