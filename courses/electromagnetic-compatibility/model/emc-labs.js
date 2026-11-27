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
    'mode-split':{inputs:[{key:'d',title:'差模 ID',min:0,max:20,step:.5,value:10,format:v=>fmt(v)+' mA'},{key:'c',title:'每线共模 IC',min:-5,max:5,step:.5,value:1,format:v=>fmt(v)+' mA'}],run:p=>({text:'I1='+fmt(p.d+p.c)+' mA；I2='+fmt(p.c-p.d)+' mA；外部回流 '+fmt(2*p.c)+' mA（负值表示反向）。',plot:makePlot('两线净电流随每线共模分量变化',Array.from({length:101},(_,i)=>2*(-5+i/10)),'总共模 (mA)','IC: −5 → 5 mA')})},
    'lisn-two-port':{inputs:[{key:'d',title:'差模源电压 VD',min:0,max:2,step:.05,value:1,format:v=>fmt(v)+' V'},{key:'c',title:'共模源电压 VC',min:0,max:1,step:.05,value:.1,format:v=>fmt(v)+' V'},{key:'r',title:'外部串联回流电阻',min:0,max:100,step:5,value:0,format:v=>fmt(v)+' Ω'}],run:p=>{const id=p.d/100,it=p.c/(25+p.r),v1=50*(id+it/2),v2=50*(-id+it/2);return {text:'ID='+fmt(id*1000)+' mA；总共模='+fmt(it*1000)+' mA；U1='+fmt(v1*1000)+' mV；U2='+fmt(v2*1000)+' mV（同相实数源、理想双50Ω、纯电阻回流模型）。',plot:makePlot('固定VC时总共模电流随回流电阻变化',Array.from({length:101},(_,i)=>p.c/(25+i)*1000),'总共模 (mA)','Rg: 0 → 100 Ω')}}},
    'parasitic-current':{inputs:[{key:'c',title:'寄生电容',min:1,max:100,step:1,value:10,format:v=>fmt(v)+' pF'},{key:'s',title:'电压变化率',min:0,max:1000,step:10,value:100,format:v=>fmt(v)+' V/μs'}],run:p=>({text:'线性斜坡位移电流 '+fmt(p.c*p.s*.001)+' mA；假设电容固定，回路允许相应电流。',plot:makePlot('固定电容时电流随电压变化率变化',Array.from({length:101},(_,i)=>p.c*i*.01),'i (mA)','0 → 1000 V/μs')})},
    'cable-size':{inputs:[{key:'f',title:'频率',min:1,max:300,step:1,value:100,format:v=>fmt(v)+' MHz'},{key:'l',title:'有效长度',min:.01,max:2,step:.01,value:.1,format:v=>fmt(v)+' m'},{key:'i',title:'等效净共模电流',min:.01,max:10,step:.01,value:1,format:v=>fmt(v)+' mA'}],run:p=>{const ratio=p.l*p.f/300;const e=6.2831853e-7*p.i*.001*p.f*1e6*p.l/10;const kr=2*Math.PI*10*p.f/300;return {text:'l/λ='+fmt(ratio)+'；λ='+fmt(300/p.f)+' m；'+(ratio<=.1&&kr>=10?'均匀短电流元、10 m远场近似：最大E≈'+fmt(e*1000)+' mV/m':'未满足本演示电气短且kr≥10条件，不估算场强或谐振。'),plot:makePlot('固定长度时电气长度随频率变化',Array.from({length:101},(_,i)=>p.l*(1+i*2.99)/300),'l/λ','1 → 300 MHz')}}},
    'pcb-loop':{inputs:[{key:'l',title:'正向路径长度',min:1,max:30,step:1,value:10,format:v=>fmt(v)+' cm'},{key:'d',title:'回线间距',min:1,max:50,step:1,value:2,format:v=>fmt(v)+' mm'}],run:p=>({text:'矩形小环面积 '+fmt(p.l*10*p.d)+' mm²；相对同长度1 mm间距的场强比 '+fmt(p.d)+'（电气小、固定电流和频率）。',plot:makePlot('固定长度时回路面积随回线间距变化',Array.from({length:50},(_,i)=>p.l*10*(i+1)),'A (mm²)','1 → 50 mm')})},

    'oxide-field':{inputs:[{key:'d',title:'氧化层厚度',min:2,max:50,step:1,value:5,format:v=>fmt(v)+' nm'},{key:'u',title:'介质电压',min:0,max:15,step:.5,value:5,format:v=>fmt(v)+' V'}],run:p=>({text:'平均电场 ≈ '+fmt(p.u/p.d)+' GV/m；非击穿判定。',plot:makePlot('固定厚度时平均电场随电压变化',Array.from({length:61},(_,i)=>i*.25/p.d),'E (GV/m)','0 → 15 V')})},
    'induced-field':{inputs:[{key:'f',title:'频率',min:1,max:1000,step:1,value:50,format:v=>fmt(v)+' Hz'},{key:'r',title:'回路半径',min:1,max:30,step:1,value:10,format:v=>fmt(v)+' cm'},{key:'b',title:'磁感应强度幅值',min:1,max:1000,step:1,value:100,format:v=>fmt(v)+' μT'}],run:p=>{const e=Math.PI*p.f*p.r*.01*p.b*1e-3;return {text:'感应电场幅值 ≈ '+fmt(e)+' mV/m；理想回路，非人体安全判定。',plot:makePlot('正弦磁场对应的切向感应电场',Array.from({length:101},(_,i)=>-e*Math.cos(2*Math.PI*i/100)),'Eφ (mV/m)','0 → 一个周期')}}},
    'common-return':{inputs:[{key:'r',title:'公共电阻',min:1,max:200,step:1,value:100,format:v=>fmt(v)+' mΩ'},{key:'l',title:'公共电感',min:0,max:100,step:1,value:10,format:v=>fmt(v)+' nH'},{key:'i',title:'电流终值',min:.1,max:5,step:.1,value:2,format:v=>fmt(v)+' A'},{key:'s',title:'上升时间',min:10,max:1000,step:10,value:100,format:v=>fmt(v)+' ns'}],run:p=>{const vr=p.r*.001*p.i,vl=p.l*p.i/p.s;return {text:'斜坡末端前的压降 ≈ '+fmt(vr+vl)+' V（电阻 '+fmt(vr)+' V，电感 '+fmt(vl)+' V）',plot:makePlot('线性电流上升及保持时的公共压降',Array.from({length:101},(_,i)=>i<50?vr*i/50+vl:vr),'u (V)','0 → 2倍上升时间')}}},
    'skin-wire':{inputs:[{key:'logf',title:'频率（对数）',min:1,max:8,step:.1,value:6,format:v=>fmt(10**v)+' Hz'},{key:'d',title:'圆线直径',min:.1,max:10,step:.1,value:2,format:v=>fmt(v)+' mm'},{key:'mur',title:'相对磁导率',min:1,max:100,step:1,value:1},{key:'sig',title:'相对铜电导率',min:.1,max:1.1,step:.1,value:1}],run:p=>{const delta=1/Math.sqrt(Math.PI*10**p.logf*4*Math.PI*1e-7*p.mur*5.8e7*p.sig),a=p.d*.0005;return {text:'δ ≈ '+fmt(delta*1e6)+' μm；a/δ = '+fmt(a/delta)+'；'+(a/delta>=10?'强集肤近似 RAC/RDC ≈ '+fmt(a/(2*delta)):'未达到本演示 a/δ≥10 的近似判据，不给出薄层电阻比。'),plot:makePlot('平面近似电流密度幅值',Array.from({length:101},(_,i)=>Math.exp(-i*5/100)),'|J|/|J₀|','0 → 5δ')}}},
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
    'ground-rise':{
      inputs:[
        {key:'rho',title:'土壤电阻率 ρ',min:20,max:500,step:10,value:100,format:v=>fmt(v)+' Ω·m'},
        {key:'current',title:'恒定入地电流 I',min:10,max:500,step:10,value:100,format:v=>fmt(v)+' A'},
        {key:'r0',title:'半球电极半径 r₀',min:.2,max:2,step:.1,value:.5,format:v=>fmt(v)+' m'},
        {key:'a',title:'跨步间距 a',min:.2,max:1.5,step:.1,value:.8,format:v=>fmt(v)+' m'}
      ],
      run:p=>{
        const potential=r=>p.rho*p.current/(2*Math.PI*r);
        const at=p.r0+1.5,step=potential(at)-potential(at+p.a);
        const points=Array.from({length:121},(_,i)=>potential(p.r0+(i/120)*10));
        return {text:'静态电极表面电位 U(r₀)='+fmt(potential(p.r0))+' V；接地电阻 Rg='+fmt(p.rho/(2*Math.PI*p.r0))+' Ω；在 r=r₀+1.5 m 两点相隔 a 的电位差='+fmt(step)+' V。只用于均匀土壤半球模型，不是人员安全判据。',
          plot:makePlot('均匀土壤半球电极静态电位，横轴距电极中心从 r₀ 到 r₀+10m',points,'U(r) (V)','r₀ → r₀+10 m')};
      }
    },
    'surge-lead':{
      inputs:[
        {key:'l',title:'连接线等效电感 L',min:.1,max:3,step:.1,value:.6,format:v=>fmt(v)+' μH'},
        {key:'di',title:'电流上升率 di/dt',min:.1,max:10,step:.1,value:1,format:v=>fmt(v)+' kA/μs'}
      ],
      run:p=>{
        const voltage=p.l*p.di*1000;
        const points=Array.from({length:101},(_,i)=>p.l*(i*.1)*1000);
        return {text:'引线电感单独产生的电压幅度≈'+fmt(voltage)+' V。需再考虑保护器件动态箝位、方向、源阻抗和实际波形；并非可直接用于施工的SPD残压估算。',
          plot:makePlot('连接线电感电压与电流前沿（0—10 kA/μs）',points,'uL (V)','di/dt: 0 → 10 kA/μs')};
      }
    },
    'impulse-shield':{
      inputs:[
        {key:'l1',title:'分压器接地引线 L₁',min:.2,max:5,step:.1,value:1,format:v=>fmt(v)+' μH'},
        {key:'l2',title:'电缆外皮回路 L₂',min:.5,max:8,step:.1,value:3,format:v=>fmt(v)+' μH'},
        {key:'cs',title:'示波器对地寄生电容 Cs',min:100,max:3000,step:100,value:1000,format:v=>fmt(v)+' pF'}
      ],
      run:p=>{
        const portion=p.l1/(p.l1+p.l2);
        const f0=1/(2*Math.PI*Math.sqrt(p.l2*1e-6*p.cs*1e-12));
        const points=Array.from({length:121},(_,i)=>p.l1/(p.l1+.5+i*7.5/120)*100);
        return {text:'理想并联电感分流：外皮电流约占 '+fmt(portion*100)+'%；独立 LC 寄生谐振假设 f₀≈'+fmt(f0/1e6)+' MHz。两种模型的回路边界条件不同，不能直接组合解释高压现场。不得断开保护地进行试验。',
          plot:makePlot('理想并联电感的外皮分流比例随 L₂ 变化',points,'i₂/i (%)','L₂: 0.5 → 8 μH')};
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

  // Chapter 3 teaching diagrams. Colours distinguish signal, reference and disturbance.
  const diagram=(title,inner,desc='')=>{const el=document.createElement('div');el.className='emc-lab-plot emc-grounding-diagram';el.innerHTML='<svg viewBox="0 0 540 245" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="'+title+'"><title>'+title+'</title><g font-family="sans-serif" font-size="15" fill="currentColor">'+inner+'</g><text x="270" y="233" text-anchor="middle" font-size="14" fill="currentColor">'+desc+'</text></svg>';return el;};
  const line=(d,c='currentColor',w=2,dash='')=>'<path d="'+d+'" fill="none" stroke="'+c+'" stroke-width="'+w+'" '+(dash?'stroke-dasharray="'+dash+'"':'')+'/>';
  const label=(x,y,s,c='currentColor')=>'<text x="'+x+'" y="'+y+'" fill="'+c+'" text-anchor="middle">'+s+'</text>';
  const dot=(x,y,c='#16834a')=>'<circle cx="'+x+'" cy="'+y+'" r="4" fill="'+c+'"/>';
  const block=(x,y,s,w=104,h=42)=>'<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="5" fill="none" stroke="currentColor"/>'+label(x+w/2,y+h/2+5,s);
  const blue='#3276d9', green='#16834a', red='#d64a3a', orange='#b97812', grey='#8994a2';
  const ground=(y=200)=>line('M22 '+y+' H518',green,3)+Array.from({length:25},(_,i)=>line('M'+(30+i*20)+' '+y+' l-8 9',green,1)).join('');
  const cap=(x,y,c=blue)=>line('M'+x+' '+(y-24)+' v18 m-12 0 h24 m-24 10 h24 m-12 0 v20',c,2.5);
  const coil=(x,y,c=blue)=>line('M'+x+' '+(y-22)+' q16 5 0 10 q16 5 0 10 q16 5 0 10 q16 5 0 10',c,2.5);
  const fieldSpec=(key,title,min,max,step,value,unit='')=>({key,title,min,max,step,value,format:v=>fmt(v)+unit});
  const modeSpec=(key,title,names,value=0)=>({key,title,min:0,max:names.length-1,step:1,value,format:v=>names[v]});
  const freqs=fieldSpec('logf','频率（Hz，对数）',1,8,.1,6);freqs.format=v=>fmt(10**v)+' Hz';
  const basePair=()=>block(25,30,'信号源')+block(411,30,'接收器')+line('M129 45 H411',orange,3)+line('M129 62 H411',blue,3)+label(270,38,'信号线',orange)+label(270,83,'信号回流线',blue);
  Object.assign(specs,{
    'ground-case':{inputs:[fieldSpec('c1','火线-机壳电容',.1,5,.1,1,' nF'),fieldSpec('c2','中性线-机壳电容',.1,5,.1,1,' nF'),modeSpec('pe','保护连接模型',['机壳悬浮','PE：理想1 Ω'])],run:p=>{const w=2*Math.PI*50,a=w*p.c1*1e-9,b=w*(p.c1+p.c2)*1e-9,u=220*a/Math.hypot(p.pe?1:0,b);return {text:'机壳电压 '+fmt(u)+' V（220 V、50 Hz，忽略电阻泄漏，仅教学计算）。',plot:diagram('机壳分压',label(130,20,'L：220 V')+label(410,20,'N：0 V')+line('M130 27 V54',orange)+cap(130,78)+line('M130 102 V120 H410 V102',blue,3)+cap(410,78)+line('M410 54 V27')+label(130,110,'C₁')+label(410,110,'C₂')+block(210,120,'金属机壳',120,35)+line('M270 155 V200',p.pe?green:grey,2,p.pe?'':'5 5')+ground(),p.pe?'PE接入':'PE支路开路')}}},
    'ground-float':{inputs:[modeSpec('m','参考地连接',['两端接地','仅源端连接','整体浮地'])],run:p=>({text:['两端直接连接形成可能的地环路。','信号系统整体单点接地，直接地环路断开。','内部系统地与大地绝缘；两端仍可保留机壳PE。'][p.m],plot:diagram('信号地浮置',basePair()+[77,463].map((x,i)=>block(x-52,112,'机壳',104,32)+line('M'+x+' 144 V200',green,3)+(p.m===2||(p.m===1&&i===1)?line('M'+x+' 72 V89 M'+x+' 105 V112',grey,2)+line('M'+x+' 89 l13 12',red,2)+label(x+30,100,'绝缘',red):line('M'+x+' 72 V112',blue,2)+dot(x,112))).join('')+ground()+(p.m===0?line('M77 85 H463 V188 H77 Z',red,2,'6 4'):''),'PE不变；浮置的是内部信号参考')})},
    'ground-topology':{inputs:[modeSpec('m','接地拓扑',['串联单点','并联单点','局部多点','浮地'])],run:p=>{let body=[90,270,450].map((x,i)=>block(x-52,20,'电路'+(i+1))).join('');if(p.m===0)body+=[90,270,450].map(x=>line('M'+x+' 62 V112',blue,3)+dot(x,112,blue)).join('')+line('M45 200 V112 H450',blue,3)+[135,315].map(x=>block(x-18,99,'Z',36,26)).join('')+ground()+dot(45,200);else if(p.m===1)body+=[90,270,450].map(x=>line('M'+x+' 62 V85 L270 155',blue,2)).join('')+dot(270,155,blue)+line('M270 155 V200',green,3)+ground();else body+=[90,270,450].map(x=>line('M'+x+' 62 V120',blue,3)+dot(x,120,blue)).join('')+line('M30 120 H510',blue,8)+ground()+(p.m===2?[90,270,450].map(x=>line('M'+x+' 120 V200',green,2)).join(''):label(270,160,'无直接对地连接',red));return {text:['共用地线，靠近参考点处承载总回流。','各支路独立返回同一汇接点。','就近连接参考平面；实际平面非理想等电位。','仍有内部回流，外部直接接地为零。'][p.m],plot:diagram('四种接地结构',body,'绿色：公共参考地；蓝色：系统地')}}},
    'ground-mixed':{inputs:[modeSpec('m','接地支路',['电容 C','电感 L']),freqs,fieldSpec('v','C (nF) 或 L (μH)',1,100,1,10)],run:p=>{const f=10**p.logf,z=p.m?2*Math.PI*f*p.v*1e-6:1/(2*Math.PI*f*p.v*1e-9);return {text:'理想支路电抗 '+fmt(z)+' Ω；'+(p.m?'频率越高阻抗越大。':'频率越高阻抗越小。')+'是否近似开路须比较其余阻抗。',plot:diagram('混合接地',basePair()+line('M77 72 V200',green,3)+line('M463 72 V'+(p.m?126:124),green,2)+(p.m?coil(463,148,green):cap(463,148,green))+line('M463 '+(p.m?166:172)+' V200',green,2)+ground()+label(405,149,p.m?'L':'C',green)+label(270,185,'第二回流支路',green),'两条支路；同轴TEM有用信号不按此简单分流')}}},
    'ground-partition':{inputs:[modeSpec('m','地线布置',['共用阻抗','独立回流'],1),fieldSpec('r','共享电阻',.01,.2,.01,.05,' Ω'),fieldSpec('i','电流波动',0,5,.1,2,' A')],run:p=>{let d=line('M35 12 V200',orange,7)+line('M70 12 V200',blue,7);['射频','中频','显示/扫频','差放/记录'].forEach((name,i)=>{let y=12+i*45;d+=label(145,y+14,name)+line('M35 '+(y+4)+' H215',orange,1.7)+line('M70 '+(y+33)+' H510',blue,5);[255,365,475].forEach((x,j)=>{if(i===3&&j===2)return;d+=block(x-36,y,'模块'+(j+1),72,21)+line('M'+x+' '+(y+21)+' L'+(i<2?x:255)+' '+(y+33),blue,1.8);});});d+=line('M35 200 H70',green,7)+ground(205)+(p.m?'':line('M35 20 H70 V190',red,3,'5 4')+label(122,190,'共享回流',red));return {text:'电源波动产生的共享电阻压降 '+fmt(p.m?0:p.r*p.i*1000)+' mV；独立回流为理想无共用段模型。',plot:diagram('分层混合接地',d,'橙：电源地；蓝：信号地；底部汇接')}}},
    'ground-loop':{inputs:[fieldSpec('u','开路地电位差',0,500,10,100,' mV'),fieldSpec('r','环路电阻',.1,2,.05,.5,' Ω'),fieldSpec('s','共享电阻',.005,.1,.005,.05,' Ω')],run:p=>{const i=p.u/p.r,n=i*p.s;return {text:'环流 '+fmt(i)+' mA；干扰 '+fmt(n)+' mV；相对1 mV信号 '+fmt(n)+' 倍。',plot:diagram('闭合地环路',basePair()+line('M77 72 V200 M463 72 V200',green,3)+ground()+line('M90 90 H450 V185 H90 Z',red,2.5,'6 4')+label(270,135,'Iloop = '+fmt(i)+' mA',red)+label(270,157,'Un = '+fmt(n)+' mV',red),'纯电阻模型；共享电阻属于环路总电阻')}}},
    'ground-flux':{inputs:[fieldSpec('s','环路面积',.01,1,.01,.1,' m²'),fieldSpec('b','法向磁场峰值',1,1000,1,100,' μT'),fieldSpec('f','频率',10,1000,10,50,' Hz')],run:p=>{const h=20+145*p.s,e=2*Math.PI*p.f*p.b*1e-3*p.s;return {text:'感应电动势峰值 '+fmt(e)+' mV；均匀法向正弦磁场。',plot:diagram('环路磁通',Array.from({length:48},(_,i)=>label(45+i%8*64,35+Math.floor(i/8)*29,'⊙',grey)).join('')+'<rect x="70" y="'+(115-h/2)+'" width="400" height="'+h+'" fill="none" stroke="'+blue+'" stroke-width="3"/>'+label(270,110,'S = '+fmt(p.s)+' m²',blue),'磁通 Φ=BS；电动势 ∝ 面积')}}},
    'ground-suppression':{inputs:[modeSpec('m','抑制方式',['浮地','隔离变压器','光耦','差分接收'])],run:p=>{let d=block(25,30,'发送端')+block(411,30,'接收端')+block(25,120,'机壳',104,28)+block(411,120,'机壳',104,28)+line('M77 148 V200 M463 148 V200',green,2.5)+ground();if(p.m===0){d+=line('M129 42 H411 M129 60 H411',blue,2.5)+line('M77 72 V120',blue,2)+line('M463 72 V89 M463 107 V120',grey,2)+line('M463 89 l13 13',red,2)+label(270,88,'正常信号去程与回流')+label(432,104,'绝缘',red);}if(p.m===1){d+=line('M129 42 H246 V36 M129 60 H246 V76 M285 36 V42 H411 M285 76 V60 H411',blue,2)+coil(246,58,blue)+coil(285,58,blue)+line('M265 31 V81',grey,3)+label(270,109,'磁耦合，无直接导电');}if(p.m===2){d+=line('M129 42 H203 M129 60 H203 M350 42 H411 M350 60 H411',blue,2)+block(203,31,'LED',55,42)+block(295,31,'光敏',55,42)+label(276,56,'→',orange)+label(270,109,'光耦合，无直接导电');}if(p.m===3){d+=line('M129 42 H411 M129 60 H411',blue,3)+label(270,100,'(Us+Un)−Un=Us')+line('M77 72 V120 M463 72 V120',blue,2)+line('M77 87 H463 V185 H77 Z',red,2,'5 4');}return {text:['浮地：切断信号参考到机壳的直接连接。','隔离变压器：互感传输交流；仍有绕组间电容。','光耦：光传输，输出电源也须隔离。','差分接收：抑制共模转换，不一定消除环流。'][p.m],plot:diagram('抑制地环路或受扰响应',d,'保护接地保持连续')}}},
        'ground-choke':{inputs:[modeSpec('m','电流模式',['共模','差模']),fieldSpec('l','单绕组自感',1,100,1,10,' μH'),fieldSpec('k','耦合系数',0,1,.01,.98)],run:p=>{let d='<rect x="215" y="40" width="110" height="120" rx="20" fill="none" stroke="'+grey+'" stroke-width="12"/>';[62,138].forEach((y,i)=>{d+=line('M20 '+y+' H205 q10 -20 20 0 q10 -20 20 0 q10 -20 20 0 q10 -20 20 0 q10 -20 20 0 q10 -20 20 0 H520',blue,3)+dot(200,y-7,blue)+label(100,y-13,p.m&&i?'← I₂':'I'+(i+1)+' →',red);});d+=label(270,100,p.m?'磁通抵消':'磁通叠加',orange);return {text:'每绕组等效电感 '+fmt(p.l*(1+(p.m?-1:1)*p.k))+' μH（对称耦合模型）。',plot:diagram('共模扼流圈',d,'同名端在左，M=kL')}}},
    'ground-shield-point':{inputs:[modeSpec('side','已接地设备',['接收器（图3-23）','信号源（图3-24）']),modeSpec('m','屏蔽接法',['远端大地','信号参考点','当地大地']),fieldSpec('c','C₁',10,500,10,100,' pF'),fieldSpec('c12','C₁₂',10,500,10,200,' pF'),fieldSpec('u1','Ug₁',0,200,5,30,' mV'),fieldSpec('u2','Ug₂',0,500,5,150,' mV')],run:p=>{const du=[p.u2-p.u1,0,-p.u1][p.m],u=p.c/(p.c+p.c12)*du,pt=p.side?['D','A','B'][p.m]:['B','C','D'][p.m];let d=line('M80 30 V145',blue,12)+label(45,90,'屏蔽')+line('M80 30 H200 M212 30 H410 V78 M410 90 V145 H212 M200 145 H80',blue,2)+line('M200 18 V42 M212 18 V42 M200 133 V157 M212 133 V157 M398 78 H422 M398 90 H422',blue,2)+label(206,16,'C₁')+label(206,166,'C₂')+label(448,88,'C₁₂')+dot(410,30)+dot(410,145)+label(430,30,'1')+label(430,145,'2')+line('M410 145 V158 M410 182 V205',orange,2)+'<circle cx="410" cy="170" r="12" fill="none" stroke="'+red+'"/>'+label(410,175,'~',red)+label(460,173,'Ug₁',red)+line('M135 205 H258 M282 205 H410',grey,2)+'<circle cx="270" cy="205" r="12" fill="none" stroke="'+red+'"/>'+label(270,210,'~',red)+label(270,188,'Ug₂',red)+line('M135 205 v8 m-10 0 h20 m-16 5 h12 M410 205 v8 m-10 0 h20 m-16 5 h12',green,1.5)+(p.m===1?line('M80 145 V151 H410 V145',green,3):p.m===2?line('M80 145 V197 H410 V205',green,3):line('M80 145 V205 H135',green,3))+label(90,184,'接 '+pt+' 点',green);return {text:pt+'点；屏蔽相对参考电压 '+fmt(du)+' mV；差模干扰 '+fmt(u)+' mV（同相有符号干扰源、纯电容网络）。',plot:diagram('屏蔽接地点等效电路',d,'C₂与串联分压支路并联；参考点连接最佳')}}},
    'ground-shield-end':{inputs:[modeSpec('m','屏蔽层接地',['浮置','单端','双端','沿线多点'],1),modeSpec('f','寄生耦合',['低频','高频'])],run:p=>{let d=basePair()+'<rect x="140" y="20" width="260" height="75" rx="10" fill="none" stroke="'+blue+'" stroke-width="4"/>'+ground();const xs=p.m===0?[]:p.m===1?[140]:p.m===2?[140,400]:[140,205,270,335,400];xs.forEach(x=>d+=line('M'+x+' 95 V200',green,3)+dot(x,200));[172,237,302,367].forEach(x=>d+=line('M'+x+' 95 V125',grey,1,'4 4')+cap(x,149,p.f?orange:grey)+line('M'+x+' 173 V200',grey,1,'4 4'));return {text:['屏蔽浮置，电位未受直接约束。','低频单端抑制导电地环路。','双端可降低高频连接阻抗，也可能形成低频环路。','缩短每段电气长度，降低高频局部电压风险。'][p.m]+(p.f?' 高频寄生电容提供附加交流路径。':''),plot:diagram('电缆屏蔽端接',d,'虚线及电容：分布式寄生路径')}}},
    'ground-length':{inputs:[fieldSpec('f','骚扰频率',1,300,1,30,' MHz'),fieldSpec('v','传播速度 v/c',.5,1,.01,1),fieldSpec('l','电缆长度',.1,10,.1,2,' m')],run:p=>{const lam=300*p.v/p.f,phase=360*p.l/lam;let d=line('M25 100 H515',blue,5)+ground();const segments=Math.min(24,Math.max(1,Math.ceil(p.l/(lam/10))));for(let i=0;i<=segments;i++){const x=25+490*i/segments;d+=line('M'+x+' 100 V200',green,2)+dot(x,200);}d+=line('M25 60 H515',grey,1)+label(270,45,'l = '+fmt(p.l)+' m')+label(270,125,'分段示意；最多画24段');return {text:'λ='+fmt(lam)+' m；λ/20='+fmt(lam/20)+' m；0.1λ='+fmt(lam/10)+' m；传播相位 '+fmt(phase)+'°。',plot:diagram('高频接地间距',d,'λ/10为经验间距，不是通用强制标准')}}},
    'ground-skin':{inputs:[freqs,fieldSpec('t','铜层厚度',.01,.5,.01,.2,' mm')],run:p=>{const delta=1000/Math.sqrt(Math.PI*10**p.logf*4*Math.PI*1e-7*5.8e7);let d='<rect x="55" y="35" width="430" height="150" fill="'+grey+'" fill-opacity=".12" stroke="'+grey+'"/>';for(let i=0;i<100;i++){const x=55+i*4.3;d+='<rect x="'+x+'" y="35" width="4.4" height="150" fill="'+blue+'" opacity="'+(.45*Math.exp(-i/99*p.t/delta))+'"/><rect x="'+x+'" y="35" width="4.4" height="150" fill="'+red+'" opacity="'+(.45*Math.exp(-(99-i)/99*p.t/delta))+'"/>';}[blue,red].forEach((c,j)=>d+=line(Array.from({length:101},(_,i)=>(i?'L':'M')+(55+i*4.3)+' '+(185-140*Math.exp(-(j?100-i:i)/100*p.t/delta))).join(' '),c,2.5));d+=label(105,22,'内表面：信号回流',blue)+label(430,22,'外表面：共模',red)+label(270,206,'铜层厚度 '+fmt(p.t)+' mm');return {text:'δ='+fmt(delta*1000)+' μm；t/δ='+fmt(p.t/delta)+'；平面近似单侧穿透幅值比 '+fmt(Math.exp(-p.t/delta))+'。',plot:diagram('内外表面集肤效应',d,'指数衰减示意；不代表有限厚度的精确边界解')}}}
  });

  const mount = (body) => {
    if(window.katex?.render) body.querySelectorAll('[data-emc-tex]').forEach(el=>{try{window.katex.render(el.dataset.emcTex,el,{throwOnError:true,trust:false,output:'htmlAndMathml'});}catch(_){/* readable fallback remains */}});
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
