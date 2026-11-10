'use strict';
(() => {
  const rootStyle = '--emc-plot';
  const fmt = (x, digits=3) => Number.isFinite(x) ? Number(x).toPrecision(digits).replace(/\.0+($|e)/, '$1') : '未定义';
  const field = (spec) => {
    const label = document.createElement('label'); label.className='emc-lab-field';
    const name=document.createElement('span'); name.textContent=spec.title;
    const input=document.createElement('input'); input.type='range'; input.min=spec.min; input.max=spec.max; input.step=spec.step; input.value=spec.value; input.setAttribute('aria-label',spec.title);
    const output=document.createElement('output'); output.textContent='';
    label.append(name,input,output);
    return {key:spec.key,input,output,format:spec.format||((v)=>fmt(v)) ,label};
  };
  const makePlot = (title, values, yAxis, xAxis) => {
    const width=710,height=205,left=57,right=24,top=20,bottom=40;
    const clean=values.map(Number).filter(Number.isFinite);
    const min=Math.min(...clean), max=Math.max(...clean);
    const low=(min===max?min-Math.max(1,Math.abs(min)*.1):min);
    const high=(min===max?max+Math.max(1,Math.abs(max)*.1):max);
    const X=i=>left+(width-left-right)*i/(values.length-1);
    const Y=v=>top+(height-top-bottom)*(high-v)/(high-low);
    const points=values.map((v,i)=>X(i).toFixed(1)+','+Y(v).toFixed(1)).join(' ');
    const esc=(s)=>String(s).replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
    const el=document.createElement('div');el.className='emc-lab-plot';
    el.innerHTML='<svg role="img" aria-label="'+esc(title)+'" viewBox="0 0 710 205" xmlns="http://www.w3.org/2000/svg"><title>'+esc(title)+'</title>'+
    '<g stroke="currentColor" fill="none" opacity=".45" stroke-width="1.4"><path d="M57 20 V165 H686"/></g>'+
    '<polyline points="'+points+'" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'+
    '<g fill="currentColor" font-family="sans-serif" font-size="14"><text x="7" y="20">'+esc(fmt(high))+'</text><text x="7" y="165">'+esc(fmt(low))+'</text><text x="57" y="190">'+esc(xAxis)+'</text><text x="685" y="190" text-anchor="end">'+esc(yAxis)+'</text></g></svg>';
    return el;
  };
  const specs={
    capacitive:{
      inputs:[
        {key:'logf',title:'频率 f（Hz 对数）',min:3,max:8,step:.1,value:6,format:v=>fmt(Math.pow(10,v))+' Hz'},
        {key:'c12',title:'互电容 C₁₂',min:1,max:50,step:1,value:5,format:v=>fmt(v)+' pF'},
        {key:'c2g',title:'对地电容 C₂G',min:5,max:200,step:5,value:45,format:v=>fmt(v)+' pF'},
        {key:'logr',title:'受扰端电阻 R₂（Ω 对数）',min:2,max:7,step:.1,value:4,format:v=>fmt(Math.pow(10,v))+' Ω'},
        {key:'u1',title:'源电压幅值 U₁',min:1,max:20,step:1,value:10,format:v=>fmt(v)+' V'}
      ],
      run:p=>{
        const f=Math.pow(10,p.logf),R=Math.pow(10,p.logr),c=p.c12*1e-12,cs=(p.c12+p.c2g)*1e-12;
        const response=ff=>{const x=2*Math.PI*ff*R*c,y=2*Math.PI*ff*R*cs;return x/Math.sqrt(1+y*y);};
        const H=response(f),phase=Math.atan2(1,2*Math.PI*f*R*cs)*180/Math.PI;
        const points=Array.from({length:91},(_,i)=>p.u1*response(Math.pow(10,3+i*(5/90))));
        return {text:'|U₂| = '+fmt(p.u1*H)+' V；|U₂/U₁| = '+fmt(H)+'；相位约 +'+fmt(phase)+'°；高频电容分压极限 = '+fmt(p.u1*p.c12/(p.c12+p.c2g))+' V。',plot:makePlot('电容耦合的源到受扰端幅频特性（横轴频率由1 kHz到100 MHz，对数分布）',points,'|U₂| (V)','1 kHz → 100 MHz')}
      }
    },
    'skin-depth':{
      inputs:[
        {key:'logf',title:'频率 f（Hz 对数）',min:3,max:9,step:.1,value:6,format:v=>fmt(Math.pow(10,v))+' Hz'},
        {key:'t',title:'金属厚度 t',min:.01,max:1,step:.01,value:.1,format:v=>fmt(v)+' mm'}
      ],
      run:p=>{
        const mu=4*Math.PI*1e-7,sigma=5.8e7;
        const depth=ff=>Math.sqrt(2/(2*Math.PI*ff*mu*sigma));
        const f=Math.pow(10,p.logf),delta=depth(f),A=8.685889638*p.t*1e-3/delta;
        const points=Array.from({length:91},(_,i)=>8.685889638*p.t*1e-3/depth(Math.pow(10,3+i*(6/90))));
        return {text:'铜的理想集肤深度 δ = '+fmt(delta*1e6)+' μm；金属内部吸收损耗 A ≈ '+fmt(A)+' dB。注意：A 不是含孔缝和端接的整机 SE。',plot:makePlot('良导体平面波近似下铜层的吸收损耗（1 kHz 到 1 GHz）',points,'A (dB)','1 kHz → 1 GHz')}
      }
    },
    filter:{
      inputs:[
        {key:'l',title:'实际差模串联电感 LDM',min:5,max:1000,step:5,value:100,format:v=>fmt(v)+' μH'},
        {key:'c',title:'X 类电容 CX（只作电路计算）',min:5,max:1000,step:5,value:100,format:v=>fmt(v)+' nF'}
      ],
      run:p=>{
        const L=p.l*1e-6,C=p.c*1e-9,f0=1/(2*Math.PI*Math.sqrt(L*C));
        const points=Array.from({length:91},(_,i)=>{const f=Math.pow(10,3+i*4/90);return Math.log10((2*Math.PI*f)*(2*Math.PI*f)*L*C);});
        return {text:'理想 LC 特征频率 f₀ ≈ '+fmt(f0/1e3)+' kHz；横轴曲线为 log₁₀(|Xᴸ|/|Xᶜ|)，过零点才是两电抗模相等的位置，不是实测插入损耗。',plot:makePlot('理想元件电抗比随频率变化（1 kHz 到 10 MHz）',points,'log₁₀ |XL/XC|','1 kHz → 10 MHz')}
      }
    },
    switching:{
      inputs:[
        {key:'l',title:'线路等效电感 Ls',min:.1,max:10,step:.1,value:1,format:v=>fmt(v)+' mH'},
        {key:'c',title:'线路等效电容 Ct',min:.01,max:1,step:.01,value:.1,format:v=>fmt(v)+' μF'},
        {key:'e',title:'合闸后恒定源电压 E',min:20,max:200,step:5,value:100,format:v=>fmt(v)+' kV'},
        {key:'initial',title:'初始电压 U₀/E',min:-1,max:1,step:.1,value:0,format:v=>fmt(v)}
      ],
      run:p=>{
        const L=p.l*1e-3,C=p.c*1e-6,omega=1/Math.sqrt(L*C),f=omega/(2*Math.PI),u0=p.e*p.initial;
        const points=Array.from({length:121},(_,i)=>p.e+(u0-p.e)*Math.cos(i*4*Math.PI/120));
        const peak=p.e+Math.abs(p.e-u0);
        return {text:'f₀ ≈ '+fmt(f/1e3)+' kHz；无损模型第一正峰值约 '+fmt(peak)+' kV；初始值 '+fmt(u0)+' kV。初始储能、损耗和断路器重燃会改变实际波形。',plot:makePlot('理想 LC 合闸后电容端口电压，横轴为两个固有振荡周期',points,'电压 (kV)','0 → 2T₀')}
      }
    }
  };
  const mount = (body) => {
    body.querySelectorAll('[data-emc-lab]').forEach(host => {
      if(host.dataset.emcMounted==='yes')return;
      const config=specs[host.dataset.emcLab];if(!config)return;
      host.dataset.emcMounted='yes';
      const ui=document.createElement('div');ui.className='emc-lab-ui';
      const controls=document.createElement('div');controls.className='emc-lab-inputs';
      const fields=config.inputs.map(field);fields.forEach(f=>controls.append(f.label));
      const result=document.createElement('p');result.className='emc-lab-result';result.setAttribute('role','status');result.setAttribute('aria-live','polite');
      const plotSlot=document.createElement('div');
      ui.append(controls,result,plotSlot);
      host.querySelector('.emc-lab-fallback')?.replaceWith(ui);
      const update=()=>{
        const values={};
        for(const f of fields){values[f.key]=Number(f.input.value);f.output.textContent=f.format(values[f.key]);}
        const state=config.run(values);
        result.textContent=state.text;
        plotSlot.replaceChildren(state.plot);
      };
      fields.forEach(f=>f.input.addEventListener('input',update));
      update();
    });
  };
  window.LN_MOUNT_EMC_LABS=mount;
})();
