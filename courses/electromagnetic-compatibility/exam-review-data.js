window.LN_EMC_EXAM_REVIEW={
  "scope": "第1—10章；重点为课件明示概念与计算模型；不是教师公布的试卷范围。",
  "chapters": [
    {
      "n": 1,
      "title": "绪论",
      "focus": "能准确解释 EMC、EMI、抗扰度、干扰三要素，熟练完成共差模与分贝换算。",
      "rows": [
        {
          "id": "emc-1-1",
          "title": "兼容与干扰的判断",
          "formulas": [],
          "method": "EMC 要求设备在预期环境中正常运行且不对其他设备产生不可接受的干扰。区分发射与抗扰度；源→途径→敏感设备，缺少任一环节则特定干扰不能形成。",
          "trap": "不能只凭设备自己正常运行就认定兼容。",
          "extra": false
        },
        {
          "id": "emc-1-2",
          "title": "共差模、分贝及绝对单位",
          "formulas": [
            {
              "tex": "I_C=\\frac{I_1+I_2}{2},\\quad I_D=\\frac{I_1-I_2}{2}",
              "plain": "IC=(I1+I2)/2；ID=(I1−I2)/2"
            },
            {
              "tex": "L_P=10\\log_{10}\\frac{P}{P_0},\\quad L_U=20\\log_{10}\\frac{|U|}{U_0}",
              "plain": "LP=10lg(P/P0)；LU=20lg(|U|/U0)"
            },
            {
              "tex": "L_{\\mathrm{dBm}}=L_{\\mathrm{dBW}}+30,\\quad L_{\\mathrm{dB\\mu V}}=L_{\\mathrm{dBV}}+120",
              "plain": "dBm=dBW+30；dBμV=dBV+120"
            },
            {
              "tex": "L_{\\mathrm{dB\\mu V}}=L_{\\mathrm{dBm}}+90+10\\log_{10}R",
              "plain": "dBμV=dBm+90+10lg R"
            }
          ],
          "method": "两导线电流参考方向同向；共模每线 IC，差模每线 ±ID。功率参考 1 W/1 mW/1 μW，每级差 30 dB；电压、电流及 E、H 场相邻的毫、微等单位倍率 1000 差 60 dB。末式 R 为纯电阻 Ω、电压有效值，50 Ω 下相差约107 dB。",
          "trap": "幅值比用20lg；功率比用10lg；不同阻抗下不能仅用电压比代替功率比。",
          "extra": false
        },
        {
          "id": "emc-1-3",
          "title": "干扰源与瞬态",
          "formulas": [
            {
              "tex": "u_L=L\\frac{di}{dt},\\qquad i_C=C\\frac{du}{dt}",
              "plain": "uL=L di/dt；iC=C du/dt"
            }
          ],
          "method": "自然源：雷电、局部自然干扰；人为源：开关、电机、ESD、输电线路电晕和间隙放电、无线电及微波源。开关电感电流与电容电压不能突变，边沿而非重复频率单独决定高频成分。",
          "trap": "L 为恒定电感 H，C 为恒定电容 F；电压 V、电流 A。不能把所有瞬态视为单频。",
          "extra": false
        },
        {
          "id": "emc-1-4",
          "title": "危害的物理机制",
          "formulas": [
            {
              "tex": "W=\\frac12 CU^2,\\quad E_{\\mathrm{ox}}\\simeq\\frac{U_{\\mathrm{ox}}}{d_{\\mathrm{ox}}}",
              "plain": "W=CU²/2；Eox≈Uox/dox"
            }
          ],
          "method": "W 为静电储能 J，U 为电容电压 V，Eox 为栅氧平均场强 V/m，dox 为氧化层厚度 m。区分设备误动作、永久或潜在损坏、易燃物点燃风险、人体热/非热效应。",
          "trap": "课件中的历史健康结论不等于当前证实因果；不能把外部静电电压直接当栅氧电压。",
          "extra": false
        }
      ],
      "question": "同向参考的两线电流分别为 12 mA、−8 mA；求每线共模及差模。1 mV 是多少 dBμV？",
      "answer": "IC=(12−8)/2=2 mA；ID=(12+8)/2=10 mA。1 mV=1000 μV，20lg1000=60 dBμV。"
    },
    {
      "n": 2,
      "title": "传输和耦合",
      "focus": "本章计算主线：先选传导/辐射模型，再确定回流、源负载、场区和相量。",
      "rows": [
        {
          "id": "emc-2-1",
          "title": "传导与辐射的区分",
          "formulas": [],
          "method": "传导分电阻性、电容性、电感性；辐射分天线接收、导线感应、回路感应。线缆可以同时承载传导电流和辐射。",
          "trap": "传导不要求两设备有直流导通，寄生电容也能闭合交流回路。",
          "extra": false
        },
        {
          "id": "emc-2-2",
          "title": "导线阻抗与三种传导耦合",
          "formulas": [
            {
              "tex": "R_{\\rm DC}=\\frac{\\rho l}{S},\\quad\\delta=\\frac1{\\sqrt{\\pi f\\mu\\sigma}},\\quad R_{\\rm AC}\\simeq R_{\\rm DC}\\frac{d}{4\\delta}",
              "plain": "RDC=ρl/S；δ=1/√(πfμσ)；RAC≈RDC d/(4δ)"
            },
            {
              "tex": "\\delta_{\\rm mm}\\simeq\\frac{66}{\\sqrt{f\\mu_r\\sigma_r}},\\quad R_{\\rm strip}\\simeq\\frac{\\rho l}{w\\delta}",
              "plain": "δ(mm)≈66/√(f μr σr)；Rstrip≈ρl/(wδ)"
            },
            {
              "tex": "L_{\\rm round}\\simeq\\frac{\\mu_0l}{2\\pi}\\left(\\ln\\frac{4l}{d}-\\frac34\\right)",
              "plain": "Lround≈μ0l/(2π)[ln(4l/d)−3/4]"
            },
            {
              "tex": "L_{\\rm strip}\\simeq\\frac{\\mu_0l}{2\\pi}\\left(\\ln\\frac{2l}{w+t}+\\frac12\\right),\\quad Z_g=R_{\\rm AC}+j\\omega L",
              "plain": "Lstrip≈μ0l/(2π)[ln(2l/(w+t))+1/2]；Zg=RAC+jωL"
            },
            {
              "tex": "U_L=\\frac{R_LU_s}{R_s+2R_t+R_L},\\qquad U_g=Z_gI_g",
              "plain": "UL=RL Us/(Rs+2Rt+RL)；Ug=Zg Ig"
            },
            {
              "tex": "\\frac{U_2}{U_1}=\\frac{j\\omega R_2C_{12}}{1+j\\omega R_2(C_{12}+C_{2G})},\\qquad e_2=\\pm M\\frac{di_1}{dt}",
              "plain": "U2/U1=jωR2C12/[1+jωR2(C12+C2G)]；e2=±M di1/dt"
            },
            {
              "tex": "\\omega_c=\\frac{R_s}{L_s},\\quad\\frac{I_s}{I_1}=\\frac{j\\omega}{j\\omega+\\omega_c},\\quad\\frac{I_g}{I_1}=\\frac{\\omega_c}{j\\omega+\\omega_c}",
              "plain": "ωc=Rs/Ls；Is/I1=jω/(jω+ωc)；Ig/I1=ωc/(jω+ωc)"
            }
          ],
          "method": "ρ=1/σ (Ω·m)，l、d、w、t、δ 用 m；σr=σ/σ铜。强集肤圆线 δ≪d/2，扁带式按课件单一有效宽面模型，若两面或邻近效应不同需换模型。直导线电感为细长孤立导体近似（回流决定真实环路电感），ln 是自然对数。容性式为理想干扰源、受扰端 R2∥C2G；低频近似 jωR2C12，高频趋于 C12/(C12+C2G)。互感 M(H) 符号由参考方向定。双端接地屏蔽体闭合、近似 M1s=Ls，Is 取返回方向，Ig=I1−Is；ω≫ωc 时屏蔽层承担大部分回流。",
          "trap": "静电屏蔽单端有效不意味着磁屏蔽同样有效；不把复相量模值直接相加。课件直导线电感与实测回路电感不可混同。",
          "extra": true
        },
        {
          "id": "emc-2-3",
          "title": "近远场、共差模辐射及转移阻抗",
          "formulas": [
            {
              "tex": "k=\\frac{2\\pi}{\\lambda},\\quad\\lambda=\\frac cf,\\quad Z_0\\simeq377\\,\\Omega",
              "plain": "k=2π/λ；λ=c/f；Z0≈377 Ω"
            },
            {
              "tex": "|Z_E|\\simeq\\frac1{\\omega\\varepsilon_0r},\\qquad |Z_H|\\simeq\\omega\\mu_0r",
              "plain": "近场电偶极 |ZE|≈1/(ωε0r)；磁偶极 |ZH|≈ωμ0r"
            },
            {
              "tex": "|E_{C,\\max}|\\simeq1.257\\times10^{-6}\\frac{|I_C|fl}{r}",
              "plain": "|EC,max|≈1.257×10⁻⁶ |IC|fl/r"
            },
            {
              "tex": "|E_{D,\\max}|\\simeq1.316\\times10^{-14}\\frac{|I_D|f^2ld}{r}",
              "plain": "|ED,max|≈1.316×10⁻¹⁴ |ID|f²ld/r"
            },
            {
              "tex": "|u_{\\rm loop}|\\simeq\\omega A|B_n|,\\qquad Z_T=\\frac{U_{AB}}{I_s l}",
              "plain": "|uloop|≈ωA|Bn|；ZT=UAB/(Is l)"
            }
          ],
          "method": "自由空间小源，kr≪1 为近场，kr≫1 为远场；近场电偶极主要 E 随 r⁻³、H 随 r⁻²，磁偶极相反，远场两者主导项均 r⁻¹。最大辐射式要求 r≫l、kr≫1、两线电气短且电流均匀；f(Hz)、I(A)、l 线长、d 间距、r 距离(m)，结果 V/m。回路 A(m²)、Bn(T)，转移阻抗 Ω/m。",
          "trap": "377 Ω 不是任意近场阻抗；共模电流即使小也可能比差模辐射大。Z_T 是相量传递量，不是普通串联电阻。",
          "extra": true
        }
      ],
      "question": "100 MHz，l=0.1 m，d=2 mm，r=10 m，IC=1 mA，ID=10 mA。按小源远场公式比较两种最大场强。",
      "answer": "EC≈1.257×10⁻³ V/m，ED≈2.632×10⁻⁵ V/m；EC/ED≈47.76，约33.58 dB。虽然共模电流小10倍，辐射仍大得多。此例按均匀电流小源近似，不代表整机实测。"
    },
    {
      "n": 3,
      "title": "接地技术",
      "focus": "保护接地不可破坏；信号接地依频率、回路和参考点选择；地环路题先画等效电路。",
      "rows": [
        {
          "id": "emc-3-1",
          "title": "保护接地与信号接地",
          "formulas": [],
          "method": "保护接地服务于故障保护；信号接地提供信号参考与低阻抗返回路径。单点、多点、浮地是信号参考组织方式。",
          "trap": "浮地绝非可以拆除保护地。",
          "extra": false
        },
        {
          "id": "emc-3-2",
          "title": "串联/并联单点与多点",
          "formulas": [
            {
              "tex": "U_A=(I_1+I_2+I_3)R_1",
              "plain": "UA=(I1+I2+I3)R1"
            },
            {
              "tex": "U_B=U_A+(I_2+I_3)R_2,\\quad U_C=U_B+I_3R_3",
              "plain": "UB=UA+(I2+I3)R2；UC=UB+I3R3"
            },
            {
              "tex": "U_i=I_iR_i\\quad\\text{or}\\quad U_i=I_i(R_i+j\\omega L_i)",
              "plain": "并联单点 Ui=IiRi；多点局部 Ui=Ii(Ri+jωLi)"
            }
          ],
          "method": "串联单点各段流过下游电流之和；并联单点低频近似独立支路；高频多点按各局部引线阻抗。课件经验：高于10 MHz 多点；1–10 MHz 且最长引线短于 λ/20 才考虑单点；低频通常单点，宽频可混合（电容高频搭接、阻感低频通路视设计）。",
          "trap": "频段仅经验条件，不是法定界限；区分本章一般接地规则与3.4电缆屏蔽体规则。",
          "extra": true
        },
        {
          "id": "emc-3-3",
          "title": "地环路、平衡差分与隔离",
          "formulas": [
            {
              "tex": "U_N=\\left(\\frac{Z_1}{R_1+Z_1}-\\frac{Z_2}{R_2+Z_2}\\right)U_G",
              "plain": "UN=[Z1/(R1+Z1)−Z2/(R2+Z2)]UG"
            },
            {
              "tex": "\\frac{U_N}{U_G}=\\frac{j\\omega CR_L}{1+j\\omega CR_L}",
              "plain": "UN/UG=jωCRL/(1+jωCRL)"
            }
          ],
          "method": "第一式为两输入支路对地分压再相减，R1、R2 是源内阻加传输电阻，Z1、Z2 是各输入对参考地阻抗(Ω)；平衡要求两分压比相同，不仅电阻相同。第二式是绕组间寄生电容 C(F) 与负载 RL(Ω) 串联分压；ωCRL≪1 时幅值约ωCRL≪1，高频趋于1。纵向扼流圈对差模磁通相抵、共模磁通相加；光隔离阻断信号金属通路。",
          "trap": "课件3第20页低频极限写成≈1，与第19页等效电路不符；应为远小于1。不能只看放大器 CMRR，外部阻抗失配也会产生差模。",
          "extra": true
        },
        {
          "id": "emc-3-4",
          "title": "电缆屏蔽层的接地点",
          "formulas": [
            {
              "tex": "U_{\\rm int}\\simeq Z_T I_s l",
              "plain": "Uint≈ZT Is l"
            }
          ],
          "method": "低频静电屏蔽：源浮地、接收器接地则接接收器的公共参考；接收器浮地、源接地则接源参考。高频课件经验：超过1 MHz或长度超过λ/20采用多点，长线约每0.1λ搭接；实际结合连接阻抗、地电位差和安全。",
          "trap": "不能把所有屏蔽层规定为一律单端/双端；闭合磁场屏蔽回路和低频地环路是不同目标。",
          "extra": false
        }
      ],
      "question": "差分接收两支路 R1=R2=100 Ω，Z1=900 Ω，Z2=100 Ω，UG=1 V，求差模干扰。怎样令其为零？",
      "answer": "两分压比为0.9、0.5，UN=0.4 V；将两支路分压比调整相等才可理想抵消，例如保持R相等并令Z1=Z2。"
    },
    {
      "n": 4,
      "title": "屏蔽技术",
      "focus": "重点是按场型和几何选模型、磁路分流、良导体吸收/反射/多次反射三项计算。",
      "rows": [
        {
          "id": "emc-4-1",
          "title": "屏蔽效能定义",
          "formulas": [
            {
              "tex": "SE_E=20\\log_{10}\\frac{|E_0|}{|E_1|},\\quad SE_H=20\\log_{10}\\frac{|H_0|}{|H_1|}",
              "plain": "SE_E=20lg|E0/E1|；SE_H=20lg|H0/H1|"
            }
          ],
          "method": "同一激励、观测位置和场量比较前后；幅值线性比与 dB 区分。",
          "trap": "不能拿不同位置或不同输入功率的读数直接比较。",
          "extra": false
        },
        {
          "id": "emc-4-2",
          "title": "静电与交变电场屏蔽",
          "formulas": [
            {
              "tex": "\\frac{U_J}{U_S}=\\frac{j\\omega C_{SJ}}{Y_g+j\\omega(C_{SJ}+C_{JG}+C_{JR})}",
              "plain": "UJ/US=jωCSJ/[Yg+jω(CSJ+CJG+CJR)]"
            }
          ],
          "method": "理想参考接收端近似零电位时，屏蔽板 J 与源S、地G、接收端R的电容分别为 CSJ、CJG、CJR(F)，搭接导纳 Yg(S)。接地降低 UJ，进而降低对接收端位移电流。静电封闭导体内部无电荷时内部场可为零，接地决定屏蔽体电位。",
          "trap": "交变电场屏蔽需低阻抗搭接，屏蔽板本身可成为二次耦合源。该节点式是按上述条件独立列KCL的扩展。",
          "extra": false
        },
        {
          "id": "emc-4-3",
          "title": "低频磁路与高频短路匝",
          "formulas": [
            {
              "tex": "\\mathcal R_m=\\frac{l}{\\mu S},\\quad \\Phi=\\frac{\\mathcal F}{\\mathcal R_m}",
              "plain": "磁阻 ℛm=l/(μS)；Φ=ℱ/ℛm"
            },
            {
              "tex": "SE_{\\rm lin,axial}\\simeq\\frac{\\mu_r(r_s^2-r_1^2)+r_1^2}{r_s^2}",
              "plain": "课件轴向磁路近似 SE线性=[μr(rs²−r1²)+r1²]/rs²"
            },
            {
              "tex": "I_s=-\\frac{j\\omega M I}{R_s+j\\omega L_s}",
              "plain": "Is=−jωMI/(Rs+jωLs)"
            }
          ],
          "method": "课件轴向磁路模型：内外半径 r1、rs(m)，假设空腔与壳壁同磁势降、入射总磁通固定、忽略端部边缘效应。两支路并联分流得到 H0/H1；转 dB 再20lg。高频利用涡流，Rs(Ω)、Ls、M(H)，低阻抗闭合匝才能形成反磁场。",
          "trap": "轴向磁路近似与原正文无限长圆筒横向场的严格解不是同一题；不能互换。真实开口、饱和和场形会改变结果。",
          "extra": true
        },
        {
          "id": "emc-4-4",
          "title": "电磁屏蔽 A+R+B 计算",
          "formulas": [
            {
              "tex": "Z_m\\simeq(1+j)\\sqrt{\\frac{\\pi f\\mu}{\\sigma}},\\quad A=8.686\\frac{t}{\\delta}\\simeq0.1316t_{\\rm mm}\\sqrt{f\\mu_r\\sigma_r}",
              "plain": "Zm≈(1+j)√(πfμ/σ)；A=8.686t/δ≈0.1316 tmm√(f μr σr) dB"
            },
            {
              "tex": "R=20\\log_{10}\\left|\\frac{(Z_w+Z_m)^2}{4Z_wZ_m}\\right|",
              "plain": "R=20lg|(Zw+Zm)²/(4ZwZm)|"
            },
            {
              "tex": "R_p\\simeq168+10\\log_{10}\\frac{\\sigma_r}{\\mu_r f}",
              "plain": "远场 Rp≈168+10lg[σr/(μr f)]"
            },
            {
              "tex": "R_e\\simeq321.7+10\\log_{10}\\frac{\\sigma_r}{f^3r^2\\mu_r}",
              "plain": "近区电场 Re≈321.7+10lg[σr/(f³r²μr)]"
            },
            {
              "tex": "R_m\\simeq14.6+10\\log_{10}\\frac{fr^2\\sigma_r}{\\mu_r}",
              "plain": "近区磁场 Rm≈14.6+10lg[fr²σr/μr]"
            },
            {
              "tex": "\\Gamma=\\frac{Z_m-Z_w}{Z_m+Z_w},\\quad B=20\\log_{10}|1-\\Gamma^2e^{-2(1+j)t/\\delta}|,\\quad SE=A+R+B",
              "plain": "Γ=(Zm−Zw)/(Zm+Zw)；B=20lg|1−Γ²exp[−2(1+j)t/δ]|；SE=A+R+B"
            }
          ],
          "method": "f Hz、r m、tmm mm、σr 相对铜、μr 相对真空；A/R/B 单位 dB。先比较 r 与 λ/2π 选场型；经验反射式以 |Zw|≫|Zm| 为前提。B 保留复数相位；A≥10 dB 时往返因子幅值≤0.1，通常可忽略（要求更高精度仍计算）。近场用对应波阻抗是课件工程近似，严格平板传输解针对正入射平面波。",
          "trap": "课件第39–40页铁皮例的厚度、吸收项和波阻抗数值存在不一致，不能机械照抄结果。0.6 mm、100 kHz、μr=1、σr=0.15 时 A≈9.67 dB，近区电场 r=0.015 m 时 |Zw|≈12 MΩ 而不是1.2 kΩ；应从给定参数重算。",
          "extra": true
        },
        {
          "id": "emc-4-5",
          "title": "孔缝、穿孔板及截止波导",
          "formulas": [
            {
              "tex": "f_c=\\frac{c}{2a}\\quad(\\mathrm{TE}_{10}),\\qquad \\alpha=\\sqrt{(\\pi/a)^2-(2\\pi f/c)^2}",
              "plain": "矩形空气波导 fc=c/(2a)；截止下 α=√[(π/a)²−(2πf/c)²]"
            }
          ],
          "method": "a 为矩形宽边 m；低于截止的理想模式振幅随深度 z 按 exp(−αz) 衰减。对门缝、搭接、通风孔、观察窗检查最大开口尺寸、接触电阻与滤波穿墙路径。",
          "trap": "薄孔不是长波导；孔缝最大长度通常比总面积更重要。",
          "extra": false
        }
      ],
      "question": "按课件轴向磁路近似，μr=100，r1=9 mm，rs=10 mm；求线性与dB磁屏蔽效能。",
      "answer": "SE线性=[100(100−81)+81]/100=19.81；SEdB=20lg19.81≈25.94 dB。此题规定轴向分流近似，不用横向圆筒解。"
    },
    {
      "n": 5,
      "title": "滤波器与滤波",
      "focus": "必须掌握相同源负载条件下插入损耗、基本/多级拓扑、安规电容、共模扼流圈和安装失效。",
      "rows": [
        {
          "id": "emc-5-1",
          "title": "插入损耗与分类",
          "formulas": [
            {
              "tex": "IL=20\\log_{10}\\left|\\frac{U_{\\rm no}}{U_{\\rm filter}}\\right|",
              "plain": "IL=20lg|Uno/Ufilter|"
            }
          ],
          "method": "同一源、负载及频率下无滤波与有滤波的负载电压比。低通、高通、带通、带阻；反射式、吸收式、有源。",
          "trap": "不是简单地把源电压与输出电压之比当成插入损耗。",
          "extra": false
        },
        {
          "id": "emc-5-2",
          "title": "基本、多级反射式滤波",
          "formulas": [
            {
              "tex": "IL_C=10\\log_{10}[1+(\\omega RC/2)^2],\\quad IL_L=10\\log_{10}[1+(\\omega L/(2R))^2]",
              "plain": "Rs=RL=R时：IL_C=10lg[1+(ωRC/2)²]；IL_L=10lg[1+(ωL/2R)²]"
            },
            {
              "tex": "M_L=\\begin{bmatrix}1&j\\omega L\\\\0&1\\end{bmatrix},\\quad M_C=\\begin{bmatrix}1&0\\\\j\\omega C&1\\end{bmatrix}",
              "plain": "串联L矩阵[1,jωL;0,1]；并联C矩阵[1,0;jωC,1]"
            },
            {
              "tex": "IL=20\\log_{10}\\left|\\frac{A+B/R_L+R_s C_m+R_s D/R_L}{1+R_s/R_L}\\right|",
              "plain": "总矩阵[A,B;Cm,D]：IL=20lg|(A+B/RL+Rs Cm+RsD/RL)/(1+Rs/RL)|"
            },
            {
              "tex": "f_0=\\frac1{2\\pi\\sqrt{LC}},\\qquad Q=\\frac{\\omega_0L}{R}",
              "plain": "f0=1/(2π√LC)；串联RLC Q=ω0L/R"
            }
          ],
          "method": "同R的单级：无滤波时 U0=Us/2。并联电容看到 Rs∥RL=R/2；串联电感看到 Rs+RL=2R。用链矩阵从源端到负载端按序乘即可覆盖 Γ、反Γ、Π、T 四种（Cm 是矩阵下左元素，不是物理电容）。n 个独立有效电抗元件的常规低通远阻带斜率约20n dB/十倍频；具体插损由网络决定。高通、带通、带阻先找通过/阻断通路。",
          "trap": "原正文的单级传递函数默认理想源，不能直接套用课件等源负载插损；各级加载后不可随意相加 dB。寄生自谐振限制高频性能。",
          "extra": true
        },
        {
          "id": "emc-5-3",
          "title": "吸收式滤波与磁珠",
          "formulas": [
            {
              "tex": "Z_{\\rm bead}=R_{\\rm loss}+jX,\\quad P=I_{\\rm rms}^2R_{\\rm loss}",
              "plain": "Zbead=Rloss+jX；P=Irms²Rloss"
            }
          ],
          "method": "铁氧体复磁导导致频率相关损耗与感抗；吸收式将干扰能量耗散，反射式理想无损电抗改变能量传输路径。磁珠需核对阻抗频谱、偏置与温升。",
          "trap": "不能把磁珠当固定理想电感，频段改变时阻抗性质会变。",
          "extra": false
        },
        {
          "id": "emc-5-4",
          "title": "电源 EMI 滤波器",
          "formulas": [
            {
              "tex": "I_Y=2\\pi f C_YU_{\\rm rms},\\quad f_0\\simeq\\frac1{2\\pi\\sqrt{L_{\\rm DM}C_X}}",
              "plain": "IY=2πf CY Urms；f0≈1/(2π√(LDM CX))"
            }
          ],
          "method": "X 电容跨线抑制差模；Y 电容线到保护地/机壳抑制共模，按安规选择；共模扼流圈差模磁动势抵消、共模叠加，漏感亦可提供差模阻抗。输入/输出线分离，滤波器外壳低阻抗搭接。",
          "trap": "X/Y 不能按容量随意互换；单支路Y电容电流不是完整法定漏电流。",
          "extra": false
        },
        {
          "id": "emc-5-5",
          "title": "有源对消",
          "formulas": [
            {
              "tex": "S(j\\omega)=\\frac1{1+G(j\\omega)}",
              "plain": "S=1/(1+G)"
            }
          ],
          "method": "课件三类：有源电感、有源电容、有源对消；反馈对消要在目标频段幅值匹配、相位正确并稳定，有源低频与无源高频组合。此灵敏度式仅针对负反馈注入模型，G 为环路增益。",
          "trap": "相消不等于任意频率下都可消除；相位错误可能放大骚扰。",
          "extra": false
        }
      ],
      "question": "源内阻与负载均50 Ω，串联 L=100 μH，在100 kHz时求插入损耗。",
      "answer": "ωL=62.83 Ω；分母中的总电阻为100 Ω。IL=10lg[1+(62.83/100)²]≈1.45 dB。不能拿50 Ω代替总电阻。"
    },
    {
      "n": 6,
      "title": "电磁兼容测试技术",
      "focus": "实验题应会选择场地、探头、检波与发射/抗扰测试链，并正确换算场强。",
      "rows": [
        {
          "id": "emc-6-1",
          "title": "测试场地",
          "formulas": [],
          "method": "开阔场地有背景和地面反射；屏蔽室隔离外界但存在反射；电波暗室利用吸波材料控制反射；混响室利用多模场和搅拌实现统计均匀。",
          "trap": "暗室与普通屏蔽室不同，不能只靠金属围护获得自由空间条件。",
          "extra": false
        },
        {
          "id": "emc-6-2",
          "title": "探头、天线、检波",
          "formulas": [
            {
              "tex": "u_{\\rm oc}=-M\\frac{di}{dt},\\quad u_{\\rm loop}=-nA\\frac{dB}{dt}",
              "plain": "uoc=−M di/dt；uloop=−nA dB/dt"
            },
            {
              "tex": "U_{\\rm out}=Z_T I,\\quad AF=\\frac{E}{V_{\\rm ant}}",
              "plain": "Uout=ZT I；AF=E/Vant"
            }
          ],
          "method": "电压探头有输入阻抗负载效应；电流探头校准转移阻抗 ZT(Ω) 与电缆转移阻抗 Ω/m 不同；环形磁场探头 n匝、面积A(m²)，均匀法向B(T)。天线因子 AF(m⁻¹)。峰值、准峰值、平均值、有效值检波各自适用，准峰值重视脉冲重复率。",
          "trap": "不能把开路感应电势直接当50 Ω接收机读数；不同检波器结果不一定相同。",
          "extra": false
        },
        {
          "id": "emc-6-3",
          "title": "发射测量及修正",
          "formulas": [
            {
              "tex": "L_E=L_V+AF_{\\rm dB/m}+L_{\\rm cable}-G_{\\rm preamp}",
              "plain": "LE=LV+AFdB/m+Lcable−Gpreamp"
            }
          ],
          "method": "LISN 提供规定射频端口阻抗、隔离电网高频噪声并把 EUT 传导骚扰送给接收机；辐射测量用合适天线、场地、极化和距离。LV(dBμV)，LE(dBμV/m)，其余为dB或dB/m。",
          "trap": "发射是测设备发出的骚扰，不是主动向设备注入干扰；频段和检波应以试验要求为准。",
          "extra": false
        },
        {
          "id": "emc-6-4",
          "title": "抗扰度、场强及屏蔽测量",
          "formulas": [
            {
              "tex": "B(x)=\\frac{\\mu_0nIr^2}{2(r^2+x^2)^{3/2}},\\quad B_0=\\left(\\frac45\\right)^{3/2}\\frac{\\mu_0nI}{r}",
              "plain": "单环B(x)=μ0nIr²/[2(r²+x²)^(3/2)]；亥姆霍兹B0=(4/5)^(3/2)μ0nI/r"
            },
            {
              "tex": "E\\simeq\\frac Ud,\\quad SE_H=20\\log_{10}\\frac{|H_0|}{|H_1|}",
              "plain": "平行板 E≈U/d；SEH=20lg|H0/H1|"
            }
          ],
          "method": "EFT是快速脉冲群、浪涌常见组合波1.2/50 μs与8/20 μs、ESD为短上升沿放电；耦合网施加扰动、去耦网保护其他端口。磁场用亥姆霍兹线圈（两线圈距等于半径r），电场用天线、匹配平行板、TEM室；U为板间电压(V)、d(m)。大环法测较整体低频磁屏蔽，小环法查局部薄弱位置。",
          "trap": "波形参数只作为课程典型模型，不作当前合规限值。抗扰度看功能判据而非仅看施加电平。",
          "extra": false
        }
      ],
      "question": "两只半径0.25 m、各100匝的亥姆霍兹线圈通过1 A，中心磁感应强度多少？",
      "answer": "B0=(4/5)^(3/2)×4π×10⁻⁷×100/0.25≈3.60×10⁻⁴ T=360 μT。两环同向，线圈间距等于半径。"
    },
    {
      "n": 7,
      "title": "静电及防护",
      "focus": "会区分起电方式和放电模型，算电荷、储能与RC，解释器件失效和泄放路径。",
      "rows": [
        {
          "id": "emc-7-1",
          "title": "摩擦、感应、人体电容",
          "formulas": [
            {
              "tex": "Q=CU,\\qquad C\\simeq\\frac{\\varepsilon_0\\varepsilon_r A}{d}",
              "plain": "Q=CU；平行板 C≈ε0εrA/d"
            }
          ],
          "method": "接触分离时电荷转移；感应使电荷重新分布，孤立导体总电荷未必改变；人体与地面形成电容，可估算鞋底平行板电容。Q(C)，U(V)，A(m²)，d(m)。",
          "trap": "静电序列表只是定性排序，湿度、材料和接触状态影响实际电荷。",
          "extra": false
        },
        {
          "id": "emc-7-2",
          "title": "放电类型与模型",
          "formulas": [
            {
              "tex": "u_C(t)=U_0e^{-t/(RC)},\\quad i(t)=\\frac{U_0}{R}e^{-t/(RC)},\\quad \\tau=RC",
              "plain": "uC=U0 exp(−t/RC)；i=U0/R exp(−t/RC)；τ=RC"
            }
          ],
          "method": "课件区分火花、电晕等放电方式，以及人体放电、带电器件放电、电场感应放电模型。RC 为理想电容初压 U0、串联R；真实模型还有寄生电感和放电通道。",
          "trap": "器件级HBM、CDM与整机ESD试验不同，不能混用参数或用单RC拟合标准波形。",
          "extra": false
        },
        {
          "id": "emc-7-3",
          "title": "储能与损伤",
          "formulas": [
            {
              "tex": "W=\\frac12 CU^2=\\frac{Q^2}{2C}",
              "plain": "W=CU²/2=Q²/(2C)"
            }
          ],
          "method": "高电位强场、瞬时大电流、宽频电磁脉冲；可燃物点燃、人体电击、电子设备直接放电与场感应，器件可能永久或潜在损伤。",
          "trap": "相同储能不代表相同峰值电流或损坏程度。",
          "extra": false
        },
        {
          "id": "emc-7-4",
          "title": "静电接地和防护",
          "formulas": [
            {
              "tex": "u_{\\rm lead}=L\\frac{di}{dt}",
              "plain": "ulead=L di/dt"
            }
          ],
          "method": "合理泄放电荷、机壳连续屏蔽、端口过滤/钳位、短而低阻抗放电回流、屏蔽电缆和隔离，区分直接与二次放电。",
          "trap": "不能让泄放电流流经敏感参考点；不可断开保护接地。",
          "extra": false
        }
      ],
      "question": "理想 RC 模型 C=150 pF，R=330 Ω，初压2 kV。求能量、初始电流与时间常数。",
      "answer": "W=0.3 mJ；i(0)=2000/330≈6.06 A；τ=49.5 ns。仅为理想RC计算，不是整机标准放电波形。"
    },
    {
      "n": 8,
      "title": "电子设备电磁兼容设计",
      "focus": "元件寄生、自谐振、端接匹配和 PCB 返回路径应能从电路图分析。",
      "rows": [
        {
          "id": "emc-8-1",
          "title": "R/C/L非理想等效及二极管",
          "formulas": [
            {
              "tex": "Z_R=\\frac{R+j\\omega L_p}{1+j\\omega C_p(R+j\\omega L_p)}",
              "plain": "ZR=(R+jωLp)/[1+jωCp(R+jωLp)]"
            },
            {
              "tex": "Z_C=ESR+j\\left(\\omega ESL-\\frac1{\\omega C}\\right)",
              "plain": "ZC=ESR+j(ωESL−1/ωC)"
            },
            {
              "tex": "Z_L=\\frac{R+j\\omega L}{1+j\\omega C_p(R+j\\omega L)},\\quad f_{\\rm SR}\\simeq\\frac1{2\\pi\\sqrt{LC_p}}",
              "plain": "ZL=(R+jωL)/[1+jωCp(R+jωL)]；fSR≈1/(2π√(LCp))"
            }
          ],
          "method": "寄生L(H)、C(F)、R(Ω)；电容自谐振用 ESL 与 C，低频容性、高频感性；电感并联寄生电容使高频失去理想感性。二极管续流/钳位、封装和引线寄生影响瞬态。",
          "trap": "不能只比标称容量或电感量；器件选型需看频率、直流偏置、额定和布局。",
          "extra": false
        },
        {
          "id": "emc-8-2",
          "title": "传输线与五种终端",
          "formulas": [
            {
              "tex": "Z_0\\simeq\\sqrt{\\frac{L'}{C'}},\\quad v\\simeq\\frac1{\\sqrt{L'C'}},\\quad t_d=l/v",
              "plain": "Z0≈√(L'/C')；v≈1/√(L'C')；td=l/v"
            },
            {
              "tex": "\\Gamma_L=\\frac{Z_L-Z_0}{Z_L+Z_0},\\quad V_L^{(1)}=(1+\\Gamma_L)V^+",
              "plain": "ΓL=(ZL−Z0)/(ZL+Z0)；首波VL=(1+ΓL)V+"
            },
            {
              "tex": "V^+=V_s\\frac{Z_0}{Z_s+R_s+Z_0},\\quad R_1\\parallel R_2=Z_0",
              "plain": "V+=Vs Z0/(Zs+Rs+Z0)；Thevenin R1∥R2=Z0"
            }
          ],
          "method": "无损线 L′(H/m)、C′(F/m)，开路Γ=+1、短路−1、匹配0。串联源端 Rs+Zs=Z0；并联端接 Rp∥ZL=Z0；RC端接高频匹配、直流隔离；Thevenin 同时设置偏置和并联匹配；二极管端接非线性限幅。",
          "trap": "开路首波为两倍入射波而不是必然两倍源电压；传输线判断看边沿传播时延，而非只看时钟频率。",
          "extra": false
        },
        {
          "id": "emc-8-3",
          "title": "PCB布线、回流和去耦",
          "formulas": [
            {
              "tex": "u_{\\rm bounce}=L_{\\rm common}\\frac{di}{dt},\\quad i_{\\rm xtalk}=C_m\\frac{d(v_a-v_b)}{dt}",
              "plain": "ubounce=Lcommon di/dt；ixtalk=Cm d(va−vb)/dt"
            }
          ],
          "method": "短回路、连续参考平面、邻近去耦、输入输出分离、平行敏感走线减耦、阻抗连续，减少短截线与分割地回流绕行。Cm(F) 为互电容；Lcommon(H) 为公共回路电感。",
          "trap": "不是机械分割数模地；跨平面缝隙可能比短走线更糟。",
          "extra": false
        }
      ],
      "question": "无损50 Ω传输线，源阶跃1 V、源内阻50 Ω，末端开路。求入射电压、反射系数、首个到达末端的电压。",
      "answer": "入射0.5 V；ΓL=+1；首波末端1.0 V。源匹配吸收返回反射，不是末端2 V。"
    },
    {
      "n": 9,
      "title": "浪涌及抑制",
      "focus": "区分雷电与开关浪涌、静电/电磁传递、防雷接地、保护元件参数及分级配合。",
      "rows": [
        {
          "id": "emc-9-1",
          "title": "雷电过电压及变压器传递",
          "formulas": [
            {
              "tex": "e_{\\rm ind}=\\pm M\\frac{di}{dt},\\quad u_2(0^+)\\simeq\\frac{C_{12}}{C_{12}+C_{20}}u_0(0^+)",
              "plain": "eind=±M di/dt；u2(0+)≈C12/(C12+C20)·u0(0+)"
            }
          ],
          "method": "雷电直接与感应过电压；绕组开路、初始电容链集总化、初始电荷增量为零时，C12绕组间电容、C20低压绕组对地电容(F)；初始电容分压与工频变比无关，随后磁耦合参与。",
          "trap": "不能把冲击传递一律按工频变比换算；完整分布参数及端接会改变结果。",
          "extra": true
        },
        {
          "id": "emc-9-2",
          "title": "防雷、接地与PEN断线",
          "formulas": [
            {
              "tex": "u_g=Ri+L\\frac{di}{dt}",
              "plain": "ug=Ri+L di/dt"
            },
            {
              "tex": "V_{O'}=\\frac{Y_AV_A+Y_BV_B+Y_CV_C}{Y_A+Y_B+Y_C},\\quad U_{AO'}=V_A-V_{O'}",
              "plain": "VO'=(YA VA+YB VB+YC VC)/(YA+YB+YC)；UAO'=VA−VO'"
            }
          ],
          "method": "接闪器、引下线、接地装置、屏蔽、等电位与SPD协同。PEN断线后三相负载星点漂移，Y为各相负载导纳(S)，V为相电源相量(V)，式由星点KCL推出；平衡星点不移，不平衡可能过欠压。保护范围按题给模型及现行适用规范。",
          "trap": "课件历史接线讨论不作为带电操作指南，不得将保护地断开。",
          "extra": true
        },
        {
          "id": "emc-9-3",
          "title": "GDT/MOV/稳压二极管/TVS",
          "formulas": [
            {
              "tex": "I=K U^\\alpha,\\quad r_d=\\frac{dU}{dI},\\qquad P(t)=u(t)i(t)",
              "plain": "MOV局部 I=K U^α；rd=dU/dI；P=ui"
            }
          ],
          "method": "GDT通流强但击穿滞后/续流；MOV非线性、通流容量与寿命/电容；稳压管与TVS钳位，核对 VRWM、VBR、VC、IPP、脉冲功率/能量。α为指定工作区伏安指数，K依单位与器件。",
          "trap": "动作电压、钳位电压和残压不同，不能拿小电流击穿值代替大浪涌钳位。",
          "extra": false
        },
        {
          "id": "emc-9-4",
          "title": "分级端口保护",
          "formulas": [
            {
              "tex": "U_{\\rm pin}\\simeq U_{\\rm clamp}+L_{\\rm lead}\\frac{di}{dt}",
              "plain": "Upin≈Uclamp+Llead di/dt"
            }
          ],
          "method": "电源端分级泄流、限压和能量协调；信号端兼顾电容和带宽；地端控制电位差；按差模/共模画实际分流路径。",
          "trap": "不能只看TVS标称钳位；长引线的 Ldi/dt 会抬高残压。",
          "extra": false
        }
      ],
      "question": "绕组间 C12=200 pF，低压绕组对地 C20=1.8 nF，初始入侵电压10 kV。估算低压开路绕组初始电容分压。",
      "answer": "200/(200+1800)=0.1，u2≈1 kV。电容链简化只用于初始瞬态。"
    },
    {
      "n": 10,
      "title": "电力系统电磁兼容",
      "focus": "重点计算：整流谐波、地电位分布、LC合闸过压、冲击试验外皮干扰。",
      "rows": [
        {
          "id": "emc-10-1",
          "title": "傅里叶级数、换流器谐波与治理",
          "formulas": [
            {
              "tex": "x(t)=a_0+\\sum_{n=1}^{\\infty}(a_n\\cos n\\omega_1t+b_n\\sin n\\omega_1t)",
              "plain": "x=a0+Σ(an cos nω1t+bn sin nω1t)"
            },
            {
              "tex": "n_{\\rm AC}=kp\\pm1,\\quad n_{\\rm DC}=kp,\\quad I_1=\\frac{\\sqrt6}{\\pi}I_d,\\quad\\frac{I_n}{I_1}=\\frac1n",
              "plain": "p脉波：交流 kp±1，直流 kp；理想6脉波 I1=√6 Id/π，In/I1=1/n"
            },
            {
              "tex": "THD_I=\\frac{\\sqrt{\\sum_{n\\ge2}I_n^2}}{I_1},\\quad I_{\\rm rms}^2=I_0^2+\\sum_{n\\ge1}I_n^2",
              "plain": "THDI=√Σ(n≥2)In²/I1；Irms²=I0²+ΣIn²"
            }
          ],
          "method": "p为脉波数，k正整数。六脉波、直流电流Id恒定、对称且忽略换相重叠时，交流5/11次负序、7/13次正序、无3倍次；直流电压纹波6、12…次。变压器三次励磁谐波与接线、零序通路有关。治理采用多脉波、无源调谐与有源补偿。",
          "trap": "In/I1=1/n只用于上述理想六脉波特征阶次；实际谱依触发、换相及系统不平衡。THD不等于总有效值或损耗。",
          "extra": true
        },
        {
          "id": "emc-10-2",
          "title": "地电位、接触与跨步电压",
          "formulas": [
            {
              "tex": "U(r)=\\frac{\\rho I}{2\\pi r},\\quad R_g=\\frac{\\rho}{2\\pi r_0},\\quad U_{\\rm step}=\\frac{\\rho I a}{2\\pi r(r+a)}",
              "plain": "U(r)=ρI/(2πr)；Rg=ρ/(2πr0)；Ustep=ρIa/[2πr(r+a)]"
            },
            {
              "tex": "U_{\\rm touch}=U_{\\rm metal}-U_{\\rm foot}",
              "plain": "Utouch=Umetal−Ufoot"
            }
          ],
          "method": "均匀各向同性半无限土壤、半球电极、稳态径向电流I(A)，ρ(Ω·m)，r、r0、跨步a(m)。降低接地电阻、改善电位分布、等电位、屏蔽接地与设备接线共同限制干扰。",
          "trap": "复杂地网、分层土壤及暂态需更完整模型；人体安全不可用本简式直接认证。",
          "extra": false
        },
        {
          "id": "emc-10-3",
          "title": "开关暂态与GIS VFTO",
          "formulas": [
            {
              "tex": "\\omega_0=\\frac1{\\sqrt{L_sC_t}},\\quad u_C(t)=E+(U_0-E)\\cos\\omega_0t",
              "plain": "ω0=1/√(LsCt)；uC=E+(U0−E)cosω0t"
            },
            {
              "tex": "\\Gamma=\\frac{Z_t-Z_0}{Z_t+Z_0},\\quad U_t=(1+\\Gamma)U^+",
              "plain": "Γ=(Zt−Z0)/(Zt+Z0)；Ut=(1+Γ)U+"
            }
          ],
          "method": "无损LC、恒定源E、初始电感电流为零时，峰值由初始电容电压U0决定；U0=0且E正得2E，U0=−E得3E。GIS隔离开关重燃/击穿触发快沿行波，阻抗突变反射；影响绝缘、变压器匝间电位及二次系统。",
          "trap": "2E/3E是特定初始条件，不是所有开关过电压的固定倍数。",
          "extra": false
        },
        {
          "id": "emc-10-4",
          "title": "冲击试验外皮电流及测量干扰",
          "formulas": [
            {
              "tex": "u_{AB}=Ri+(L-M)\\frac{di}{dt}",
              "plain": "uAB=Ri+(L−M)di/dt"
            },
            {
              "tex": "Z_T=\\frac{R+j\\omega(L-M)}{l}=R'+j\\omega(L'-M')",
              "plain": "ZT=[R+jω(L−M)]/l=R'+jω(L'−M')"
            },
            {
              "tex": "i_2=\\frac{L_1}{L_1+L_2}i,\\qquad f_0=\\frac1{2\\pi\\sqrt{L_2C_s}}",
              "plain": "i2=L1/(L1+L2)·i；f0=1/(2π√(L2Cs))"
            }
          ],
          "method": "R(Ω)、L与M(H) 为整段外皮电阻、自感、芯皮互感，l(m)；撇号是单位长度参数。纯电感并联分流式仅在忽略电阻、互感且初值相容时成立。仪器接壳母线、电源线、直接辐射、仪器地电位均为干扰路径。",
          "trap": "理想同轴 L=M 仍可能有电阻压降；外皮两端电位与芯皮差模电压不能混为一谈。",
          "extra": true
        }
      ],
      "question": "50 Hz六脉波理想整流，Id=100 A，求基波有效值、5次与7次电流有效值及相序。",
      "answer": "I1=√6×100/π≈77.97 A；I5≈15.59 A，负序；I7≈11.14 A，正序。直流侧首个特征纹波为300 Hz。"
    }
  ]
};
