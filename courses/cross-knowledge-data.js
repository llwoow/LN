window.LN_CROSS_KNOWLEDGE_DATA={
  "topics": [
    {
      "id": "induction",
      "title": "电磁感应与互感",
      "description": "场的环量、绕组磁链与非有意耦合"
    },
    {
      "id": "materials",
      "title": "材料与电磁场分布",
      "description": "导电机制、场扩散、涡流与损耗"
    },
    {
      "id": "devices",
      "title": "器件结构与绝缘",
      "description": "从栅氧结构到瞬态损伤"
    },
    {
      "id": "switching",
      "title": "开关暂态与回流",
      "description": "器件边沿、驱动、逆变器与布线"
    },
    {
      "id": "control",
      "title": "采样与闭环误差",
      "description": "传导干扰怎样进入测量和控制"
    },
    {
      "id": "filter-response",
      "title": "频响、数字滤波与控制延迟",
      "description": "连续/离散频响、采样与抗混叠的边界"
    }
  ],
  "nodes": [
    {
      "id": "faraday-field",
      "topic": "induction",
      "course": "electromagnetic-compatibility",
      "section": "emc-1-4",
      "title": "磁通与电场环量",
      "match": "固定半径 r 的圆形回路 L 以逆时针为正",
      "note": "法拉第定律的场形式"
    },
    {
      "id": "faraday-machine",
      "topic": "induction",
      "course": "electrical-machines",
      "section": "transformer-2",
      "title": "绕组感应电压",
      "match": "若绕组压降较小",
      "note": "法拉第定律的绕组形式"
    },
    {
      "id": "mutual-emc",
      "topic": "induction",
      "course": "electromagnetic-compatibility",
      "section": "emc-2-2",
      "title": "互感耦合",
      "match": "把两回路的耦合用互感 M 表示",
      "note": "变化磁链产生受扰电压"
    },
    {
      "id": "mutual-machine",
      "topic": "induction",
      "course": "electrical-machines",
      "section": "magnetic-sec14",
      "title": "绕组互感",
      "match": "反转一个绕组的电流或电压参考时",
      "note": "互感符号、耦合系数与储能"
    },
    {
      "id": "skin-field",
      "topic": "materials",
      "course": "electromagnetic-compatibility",
      "section": "emc-2-2",
      "title": "集肤效应",
      "match": "取均匀半无限良导体 x≥0",
      "note": "电导率与磁导率决定深度"
    },
    {
      "id": "conductivity",
      "topic": "materials",
      "course": "electrical-materials",
      "section": "em-2-3",
      "title": "材料导电性",
      "match": "载流子更多却导电更差并不矛盾",
      "note": "浓度与迁移率共同决定电导率"
    },
    {
      "id": "shield-eddy",
      "topic": "materials",
      "course": "electromagnetic-compatibility",
      "section": "emc-4-3",
      "title": "涡流磁屏蔽",
      "match": "快速变化的外部磁通穿过良导体后",
      "note": "涡流反抗磁通变化"
    },
    {
      "id": "core-eddy",
      "topic": "materials",
      "course": "electrical-machines",
      "section": "magnetic-sec12",
      "title": "铁芯涡流损耗",
      "match": "铁心可导电，交变磁通会在内部形成感应电场",
      "note": "叠片改变涡流路径"
    },
    {
      "id": "oxide-emc",
      "topic": "devices",
      "course": "electromagnetic-compatibility",
      "section": "emc-1-4",
      "title": "栅氧击穿",
      "match": "传统 MOS 的栅极、绝缘氧化层与半导体构成电容结构",
      "note": "介质电场和瞬态应力"
    },
    {
      "id": "oxide-device",
      "topic": "devices",
      "course": "power-semiconductors",
      "section": "vdmos-structure",
      "title": "VDMOS 栅结构",
      "match": "栅氧隔开 G 和硅",
      "note": "栅氧位置、源体短接与介质"
    },
    {
      "id": "switch-device",
      "topic": "switching",
      "course": "power-semiconductors",
      "section": "switching",
      "title": "硬开关瞬态",
      "match": "示例只取图2.7的降压段",
      "note": "开关损耗与漏感尖峰"
    },
    {
      "id": "gate-drive",
      "topic": "switching",
      "course": "robot-drive-engineering",
      "section": "rd-mosfet-driver",
      "title": "栅极驱动与边沿",
      "match": "两者相差500倍；驱动器、门极电阻和回流电感",
      "note": "瞬态门极电流与回路"
    },
    {
      "id": "switch-emc",
      "topic": "switching",
      "course": "electromagnetic-compatibility",
      "section": "emc-2-2",
      "title": "三种传导耦合",
      "match": "同一开关节点可能通过 C₁₂ 把位移电流注入采样输入",
      "note": "电容、互感与共阻抗路径"
    },
    {
      "id": "pcb-return",
      "topic": "switching",
      "course": "electromagnetic-compatibility",
      "section": "emc-8-3",
      "title": "PCB 回流路径",
      "match": "PCB布线不是只看两块焊盘是否导通",
      "note": "回流连续性及环路"
    },
    {
      "id": "inverter-cm",
      "topic": "switching",
      "course": "robot-drive-engineering",
      "section": "rd-inverter",
      "title": "逆变器共模电位",
      "match": "状态000和111时三个极点相同",
      "note": "相电压与对机壳共模电位"
    },
    {
      "id": "common-return",
      "topic": "control",
      "course": "electromagnetic-compatibility",
      "section": "emc-2-2",
      "title": "共地采样误差",
      "match": "传感器与 ADC 参考点不同也可能产生测量误差",
      "note": "公共回流压降进入测量"
    },
    {
      "id": "sampling",
      "topic": "control",
      "course": "robot-drive-engineering",
      "section": "rd-sampling-time",
      "title": "PWM 同步采样",
      "match": "DMA不会自动确定PWM同步的采样时刻",
      "note": "采样时刻、延迟与硬件"
    },
    {
      "id": "feedback",
      "topic": "control",
      "course": "automatic-control",
      "section": "ac-3-6",
      "title": "扰动位置与反馈",
      "match": "研究扰动误差时令 R(s)=0",
      "note": "扰动位置决定传递关系"
    },
    {
      "id": "compare-error",
      "topic": "control",
      "course": "automatic-control",
      "section": "ac-3-6",
      "title": "测量与实际误差",
      "match": "可直接测得的比较点误差与输出相对期望值的偏差",
      "note": "信号标定与误差定义"
    },
    {
      "id": "dsp-linear-phase",
      "topic": "filter-response",
      "course": "digital-signal-processing",
      "section": "dsp-7-2",
      "title": "线性相位与时间延迟",
      "match": "相位延迟描述单个正弦分量",
      "note": "相位斜率、数字频率与采样周期"
    },
    {
      "id": "dsp-filter-engineering",
      "topic": "filter-response",
      "course": "digital-signal-processing",
      "section": "dsp-7-6",
      "title": "数字滤波、采样与反馈",
      "match": "即使测量 FIR 本身稳定",
      "note": "群延迟和闭环相位裕度"
    },
    {
      "id": "control-frequency-measure",
      "topic": "filter-response",
      "course": "automatic-control",
      "section": "ac-5-1",
      "title": "从正弦测量到伯德图",
      "match": "在这个线性电路里，稳态输出和输入同频",
      "note": "幅值比和相位差"
    },
    {
      "id": "emc-filter-insertion",
      "topic": "filter-response",
      "course": "electromagnetic-compatibility",
      "section": "emc-5-1",
      "title": "滤波频率选择性",
      "match": "滤波器的通带、阻带与截止频率描述频率选择性",
      "note": "端接与实际插入损耗"
    }
  ],
  "links": [
    {
      "from": "faraday-field",
      "to": "faraday-machine",
      "label": "场积分到绕组",
      "description": "同一法拉第定律：圆周电场环量对应闭合路径感应电动势，绕组需对各匝磁链求和；变压器正弦公式另有波形与匝间链磁通假设。"
    },
    {
      "from": "mutual-emc",
      "to": "mutual-machine",
      "label": "互感与参考方向",
      "description": "受扰回路的感应电势由互感磁链变化率决定；电机学的互感符号、耦合系数和储能约束说明 M 不能任意选取。"
    },
    {
      "from": "faraday-machine",
      "to": "mutual-emc",
      "label": "有意与非有意耦合",
      "description": "变压器利用交变磁链传输能量，EMC 关注漏磁对敏感回路的非有意耦合；不能将理想变压器的完全耦合假设直接用于串扰。"
    },
    {
      "from": "skin-field",
      "to": "conductivity",
      "label": "微观材料到场扩散",
      "description": "电工材料解释电导率的物理来源，EMC 将 σ 作为良导体模型的材料参数；温度、频率和材料机制改变时须重新核对 σ、μ。"
    },
    {
      "from": "shield-eddy",
      "to": "core-eddy",
      "label": "同一涡流，不同目标",
      "description": "交变磁通驱动闭合涡流并产生反作用磁场和热损耗；磁屏蔽利用其反磁场，铁芯叠片通过缩小闭合路径抑制不希望出现的损耗。"
    },
    {
      "from": "skin-field",
      "to": "shield-eddy",
      "label": "电流分布与屏蔽",
      "description": "两者均涉及导体内部感应电流与场分布；平面趋肤模型描述深度衰减，短路线圈模型描述闭合屏蔽回路，适用几何不同。"
    },
    {
      "from": "oxide-emc",
      "to": "oxide-device",
      "label": "从介质位置到失效",
      "description": "VDMOS 剖面定位栅氧与半导体，EMC 以实际介质分压和厚度估算电场。栅源额定值与材料击穿场强不等同，结区雪崩也不是栅氧击穿。"
    },
    {
      "from": "switch-device",
      "to": "gate-drive",
      "label": "栅电荷与驱动权衡",
      "description": "驱动电流、米勒阶段与门极回路影响开关边沿；加大门极电阻可能降低振铃，却增加电压电流重叠损耗，需核对波形和温升。"
    },
    {
      "from": "switch-device",
      "to": "switch-emc",
      "label": "从开关尖峰到骚扰路径",
      "description": "快速电压边沿可驱动寄生电容位移电流，快速电流边沿可产生互感电压和公共阻抗压降；器件开关频率不等于骚扰最高频率。"
    },
    {
      "from": "gate-drive",
      "to": "pcb-return",
      "label": "驱动与回流布局",
      "description": "栅极驱动的参考是源极，门极充放电闭环与功率回流的公共寄生电感可改变实际栅源电压；PCB 连续回流用于限制环路与共享阻抗。"
    },
    {
      "from": "inverter-cm",
      "to": "switch-emc",
      "label": "零矢量与共模",
      "description": "逆变器 000 和 111 都产生零相电压，却有不同对机壳共模电位；寄生电容和返回路径决定实际共模电流，零转矩电压不等于零骚扰。"
    },
    {
      "from": "switch-emc",
      "to": "pcb-return",
      "label": "耦合路径与几何",
      "description": "寄生电容、互感、公共阻抗由实际几何和回路决定；连续返回平面及合理布局减少共享路径，不能仅靠机械分割地平面。"
    },
    {
      "from": "common-return",
      "to": "sampling",
      "label": "采样参考与时序",
      "description": "共阻抗压降可改变 ADC 所见模拟电压；同步采样能避开某些开关瞬态，却不能自动消除静态地偏差或所有噪声。"
    },
    {
      "from": "common-return",
      "to": "compare-error",
      "label": "测量偏差与真实偏差",
      "description": "传感器与 ADC 参考点的电位差会改变反馈读数，即使比较点误差为零，实际输出也未必达到目标；先区分标定、测量与被控量。"
    },
    {
      "from": "sampling",
      "to": "feedback",
      "label": "扰动的注入位置",
      "description": "采样链产生的误差应放在真实测量或反馈节点，不能直接套用对象输入扰动公式；采样延迟另会改变相位，需单独建模。"
    },
    {
      "from": "feedback",
      "to": "compare-error",
      "label": "反馈误差的定义",
      "description": "比较点、实际输出、对象输入扰动与测量噪声位置不同，对应的传递关系不同；不由开环型别单独判断所有误差。"
    },
    {
      "from": "dsp-linear-phase",
      "to": "control-frequency-measure",
      "label": "正弦稳态与相位",
      "description": "同一 LTI 特征函数关系；连续Ω与离散ω需用采样周期转换，不能把数字群延迟直接当秒。"
    },
    {
      "from": "dsp-filter-engineering",
      "to": "emc-filter-insertion",
      "label": "模拟抑制与数字滤波",
      "description": "都按有用/干扰频段选通阻带；数字 FIR 无法消除已混叠分量，模拟插入损耗则随真实端接和耦合变化。"
    },
    {
      "from": "dsp-filter-engineering",
      "to": "control-frequency-measure",
      "label": "滤波延迟与反馈",
      "description": "恒定群延迟不代表闭环稳定，必须计入测量链总相位并重新判断裕度。"
    }
  ],
  "pending": [
    {
      "title": "电磁场",
      "description": "麦克斯韦方程、斯托克斯定理、良导体场扩散。当前尚无独立课程正文；从电磁兼容和电机学已具备的推导阅读，不创建空课程或虚假链接。",
      "nodes": [
        "faraday-field",
        "skin-field"
      ]
    },
    {
      "title": "信号与系统",
      "description": "频谱、傅里叶变换、采样与混叠。待独立课程正文接入后再建立对应链接。",
      "nodes": [
        "switch-emc",
        "sampling"
      ]
    },
    {
      "title": "自动控制原理·频域章节",
      "description": "滤波传递函数和 Bode 图的对应章节目前仅有目录，暂不作为已审查的图谱连接。",
      "nodes": []
    },
    {
      "title": "新能源材料与器件",
      "description": "现有储能内容与电介质、热损耗的潜在联系待核对具体适用模型，不能把电化学双电层电容等同于普通绝缘介质。",
      "nodes": []
    }
  ]
};
