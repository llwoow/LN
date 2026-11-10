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

    'capacitor-srf':{
      inputs:[
        {key:'logc',title:'标称电容 C（对数）',min:-9,max:-5,step:.1,value:-6,format:v=>fmt(Math.pow(10,v)*1e9)+' nF'},
        {key:'esl',title:'串联等效电感 ESL',min:.2,max:5,step:.2,value:1,format:v=>fmt(v)+' nH'},
        {key:'esr',title:'串联等效电阻 ESR',min:5,max:100,step:5,value:20,format:v=>fmt(v)+' mΩ'}
      ],
      run:p=>{
        const C=Math.pow(10,p.logc),L=p.esl*1e-9,R=p.esr*1e-3;
        const f0=1/(2*Math.PI*Math.sqrt(L*C));
        const points=Array.from({length:121},(_,i)=>{
          const f=Math.pow(10,3+i*5/120),w=2*Math.PI*f;
          return Math.log10(Math.hypot(R,w*L-1/(w*C)));
        });
        return {text:'理想串联模型自谐振 f₀≈'+fmt(f0/1e6)+' MHz；在自谐振附近的理论最小 |Z|≈'+fmt(p.esr)+' mΩ。图只展示固定ESR/ESL的一阶模型，不含直流偏置、多个电容反谐振或PCB寄生参数。',
          plot:makePlot('假设的ESR+ESL+C串联模型阻抗频响（1 kHz—100 MHz，对数频率）',points,'log₁₀ |Z/Ω|','1 kHz → 100 MHz')};
      }
    },
    'line-reflection':{
      inputs:[
        {key:'z0',title:'线路特征阻抗 Z₀',min:30,max:120,step:5,value:50,format:v=>fmt(v)+' Ω'},
        {key:'zs',title:'驱动源阻抗 Zs',min:0,max:80,step:5,value:10,format:v=>fmt(v)+' Ω'},
        {key:'rs',title:'源端串联电阻 Rs',min:0,max:100,step:5,value:40,format:v=>fmt(v)+' Ω'},
        {key:'load',title:'负载端 ZL（典型档位）',min:0,max:5,step:1,value:5,format:v=>['0 Ω（短路）','25 Ω','50 Ω','100 Ω','1 kΩ','理想开路'][v]},
        {key:'length',title:'线长 ℓ',min:.1,max:5,step:.1,value:.5,format:v=>fmt(v)+' m'}
      ],
      run:p=>{
        const loads=[0,25,50,100,1000,Infinity],Zl=loads[p.load];
        const gl=Number.isFinite(Zl)?(Zl-p.z0)/(Zl+p.z0):1;
        const sourceZ=p.zs+p.rs,gs=(sourceZ-p.z0)/(sourceZ+p.z0);
        const launched=3.3*p.z0/(sourceZ+p.z0),td=p.length/2e8;
        const first=launched*(1+gl);
        const values=Array.from({length:161},(_,i)=>{
          const t=i*8/160;
          let voltage=0;
          for(let n=0;n<=3;n++){
            if(t>=2*n+1-1e-9)voltage+=first*Math.pow(gl*gs,n);
          }
          return voltage;
        });
        return {text:'单程传播延迟 tₑ='+fmt(td*1e9)+' ns；ΓL='+fmt(gl)+'；ΓS='+fmt(gs)+'；源端发出 V⁺='+fmt(launched)+' V；首次负载变化 ΔVL='+fmt(first)+' V。3.3 V理想阶跃、传播速度2×10⁸ m/s、无损单一线路；负载电容和非线性未计入。',
          plot:makePlot('理想阶跃从源端出发后，负载端电压随单程延迟倍数变化',values,'Vload (V)','t / td: 0 → 8')};
      }
    },
    'eddy-shield':{
      inputs:[
        {key:'res',title:'屏蔽等效电阻 Rs',min:.01,max:1,step:.01,value:.1,format:v=>fmt(v)+' Ω'},
        {key:'ind',title:'屏蔽等效自感 Ls',min:.2,max:5,step:.2,value:1,format:v=>fmt(v)+' μH'}
      ],
      run:p=>{
        const R=p.res,L=p.ind*1e-6,M=.2e-6;
        const fc=R/(2*Math.PI*L);
        const points=Array.from({length:121},(_,i)=>{
          const f=Math.pow(10,3+i*4/120),w=2*Math.PI*f;
          return w*M/Math.hypot(R,w*L);
        });
        return {text:'令互感 M=0.2 μH（教学假设）。等效交界 f≈Rs/(2πLs)='+fmt(fc/1e3)+' kHz；高频极限 |Is/I|≈M/Ls='+fmt(M/L)+'。此数仅是短路匝电流幅比，不是屏蔽空腔内的磁场，也不是整机SE。',
          plot:makePlot('理想互感与短路匝电流幅比随频率变化（1 kHz—10 MHz）',points,'|Is/I|','1 kHz → 10 MHz')};
      }
    },
    'probe-ideal':{
      inputs:[
        {key:'logf',title:'频率（理想近似）',min:2,max:6,step:.1,value:5,format:v=>fmt(Math.pow(10,v))+' Hz'},
        {key:'m',title:'互感 M',min:.1,max:2,step:.1,value:.5,format:v=>fmt(v)+' μH'},
        {key:'i',title:'被测正弦电流峰值',min:.02,max:1,step:.02,value:.1,format:v=>fmt(v)+' A'}
      ],
      run:p=>{
        const f=Math.pow(10,p.logf),M=p.m*1e-6,I=p.i;
        const voltage=2*Math.PI*f*M*I;
        const points=Array.from({length:121},(_,i)=>2*Math.PI*Math.pow(10,2+i*4/120)*M*I*1000);
        return {text:'理想开路感应电压峰值 |uoc|≈'+fmt(voltage*1000)+' mV（忽略次级负载、频散和饱和）。真实电流探头必须用对应频率和端接下的校准转移阻抗 ZT(f)，不能以此曲线充当实测响应。',
          plot:makePlot('只供推导用的理想互感开路电压（100 Hz—1 MHz）',points,'|uoc| (mV)','100 Hz → 1 MHz')};
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
