# FPGA时序分析与约束:理论、公式、模板与实战

## 导言与执行摘要

在FPGA项目中,时序分析与时序约束是连通车规级可靠性与系统吞吐的“共同语言”。一方面,它们以静态时序分析(STA)为框架,将数据路径、时钟特性与接口契约统一到一套可计算、可复现的规则体系中;另一方面,它们又是实现工具的“目标函数”,驱动综合与布局布线在数以万计的选项中做出有利于时序收敛的选择。简言之:约束定义目标,STA验证结果,收敛迭代优化,三者共同构成工程落地的闭环。

本报告面向FPGA开发工程师、硬件工程师与电子类相关专业研究生,系统回答以下问题:如何用STA的视角理解建立(Setup)、保持(Hold)与时钟偏斜(Skew)之间的定量关系?时钟约束(频率/相位/抖动)如何建模,I/O时序约束如何正确表达?典型时序路径如何分类与检查,时序报告如何解读与定位关键路径?当出现违例时,有哪些可复用的收敛方法与约束模板?同时,报告给出完整的公式推导与计算示例,并汇总常用XDC/SDC命令模板,便于直接复用。

方法论上,本报告以AMD/Xilinx UG903官方文档为约束与流程主线,辅以Intel Quartus Timing Analyzer官方文档与AN1016的收敛流程参考,并在关键结论处提供必要的出处标注与一致性说明[^1][^2][^4][^5][^6][^7][^8][^9][^19][^20][^21][^22][^23][^24][^25]。报告采用“理论—约束—路径—报告—收敛—模板”的叙事结构,从概念到公式,从模板到案例,力求既严谨又可操作。

阅读建议:如果你正处在项目初期,请优先阅读“时序分析基础与STA原理”“时钟约束”“I/O时序约束”;若你正在调试时序违例,请直达“时序路径分析”“时序报告解读”“时序收敛方法”;若你需要快速落地约束,请直接使用“约束模板与命令索引”。在全文中,所有公式均以统一的变量定义展开,并通过一个贯穿全文的“基准设计案例”串联计算示例,确保理论与实践的一致性与可复现性。

最后,需要明确的信息边界:不同器件与速度等级的建立/保持时间、抖动/偏斜具体数值、I/O时序模板(如DDR SDRAM)均依赖具体器件手册与接口规范;本报告给出的是通用建模方法、公式与模板,实际项目请结合官方数据手册与IP约束脚本进行校核与替换[^8][^9]。

---

## 时序分析基础与STA原理

静态时序分析(Static Timing Analysis, STA)的核心思想,是在不依赖激励的前提下,对所有时序路径进行穷尽式检查,计算每条路径的“数据到达时间(Data Arrival Time)”与“数据要求时间(Data Required Time)”,并以Slack(裕量)作为判断标准:Slack为正表示满足要求,Slack为负表示违例。STA之所以成为主流,是因为它速度快、覆盖全、结果可重复,适合驱动布局布线工具在巨大的解空间中寻找更优解[^4][^5]。

在数字同步电路中,建立时间(Setup Time, Tsu)与保持时间(Hold Time, Th)是触发器对输入数据的“时间窗口”要求:在时钟有效沿到来之前,数据必须稳定至少Tsu;在时钟有效沿到来之后,数据必须继续稳定至少Th。时钟偏斜(Skew)则源于时钟树节点间到达时间的差异;抖动(Jitter)刻画的是时钟沿在时间轴上的不确定度。Slack是连接这些要素的“统一度量”:对于建立检查,Slack = 要求时间 − 到达时间;对于保持检查,Slack = 到达时间 − 要求时间。只要Slack > 0,即满足时序要求[^10][^11]。

为便于统一变量,表1汇总了STA常用符号与含义。

表1 变量与符号对照表(统一口径)

| 符号/缩写 | 含义 | 说明 |
|---|---|---|
| Tclk | 时钟周期 | 主频的倒数 |
| Tsu | 建立时间 | 触发器对数据在时钟沿前的稳定时间要求 |
| Th | 保持时间 | 触发器对数据在时钟沿后的稳定时间要求 |
| Tco | 时钟到输出延迟(寄存器传播延迟) | 触发器时钟有效沿到Q端变化的时间 |
| Tdp | 数据路径组合逻辑延迟 | 组合逻辑总延迟(含线延迟) |
| Tskew | 时钟偏斜 | 捕获沿时钟与发射沿时钟到达时刻差 |
| Tjit | 时钟抖动 | 周期抖动/相位抖动的综合建模 |
| Tarr | 数据到达时间 | 发射沿后数据实际到达的时间 |
| Treq | 数据要求时间 | 为满足Tsu/Th,数据最晚/最早到达的界限 |
| Slack | 裕量 | Setup: Treq − Tarr;Hold: Tarr − Treq |

上述变量构成了后续所有公式与示例的“公共语言”。需要强调两点:其一,Skew既可能帮助Setup(正偏斜)也可能加剧Hold风险(负偏斜),工程上通常通过时钟树综合将其最小化;其二,Jitter是“时变不确定性”,通常以保守方式纳入要求时间中,作为安全裕度的扣除项[^10][^11]。

### 建立时间与保持时间的数学定义与推导

考虑一条寄存器到寄存器的路径:发射触发器(Launch FF)在时钟沿L发出数据,经过Tco与Tdp后到达捕获触发器(Capture FF)的D端;捕获沿C在Tclk之后到达。若捕获触发器建立时间为Tsu,要求数据在C之前稳定Tsu,则建立检查要求:

Tarr = Tco + Tdp ≤ Tclk + Tskew − Tsu

将所有项移到一侧,得到:

Slack_su = (Tclk + Tskew − Tsu) − (Tco + Tdp)

或者从更准确的角度，使用标准STA公式：
- Data Arrival Time = Tclk1 + Tco + Tdata
- Data Required Time = Tcycle + Tclk2 - Tsu
- Setup Slack = Data Required Time - Data Arrival Time
- Setup Slack = Tcycle + Tclk2 - Tsu - (Tclk1 + Tco + Tdata)

当Slack_su ≥ 0时,建立时间满足。类似地,保持时间要求数据在捕获沿之后稳定至少Th,考虑最短路径与最坏Skew(通常取最不利于保持的偏斜),得到:

Tarr_min ≥ Tskew + Th

以到达时间下限与要求时间上限表达:

Slack_h = (Tco_min + Tdp_min) − (Tskew + Th)

或者从更准确的角度，使用标准STA公式：
- Data Arrival Time = Tclk1 + Tco + Tdata + Tcycle
- Data Required Time = Tcycle + Tclk2 + Th
- Hold Slack = Data Arrival Time - Data Required Time
- Hold Slack = Tclk1 + Tco + Tdata - (Tclk2 + Th)

当Slack_h ≥ 0时,保持时间满足。上述推导与常见教材一致,变量定义与裕量计算口径可参见[^10][^11][^17]。

### 时钟偏斜与抖动:定义、来源与对时序的影响

时钟偏斜(Skew)来源于时钟树各分支的物理差异(线长、负载、缓冲器级数),是空间上的差异;抖动(Jitter)来源于时钟源、电源噪声、温度变化等,是时间上的不确定度。工程上,Skew通常通过时钟树综合(CTS)最小化,并在跨域或跨列/跨SLR时通过约束(如DELAY_GROUP、CLOCK_ROOT)控制;Jitter则以保守裕度纳入时序要求,或通过时钟管理模块(如MMCM/PLL)降低其影响[^10][^12]。

从公式可见,正偏斜(Tcapture > Tlaunch)有利于Setup,但若偏斜过大,可能在保持检查中引发风险;负偏斜则相反。合理的做法是将Skew收敛到最小,并在约束中以“保守最差情形”建模,确保工具在所有角落(corner)都能满足要求[^10][^12]。

### 时序路径分类与检查类型

典型时序路径可分四类:寄存器到寄存器(R2R)、寄存器到输出(R2O)、输入到寄存器(I2R)、输入到输出(I2O)。不同类型对应不同的检查与约束重点:R2R由时钟周期与Tco/Tdp主导;I2R与R2O依赖I/O延迟约束;I2O通常用于纯组合输出,受输出负载与外部时序共同影响。异步信号(异步复位、跨时钟域路径)不适用STA的同步检查,需要通过约束明确false path或异步约束,并采用同步器/握手等 CDC 策略处理[^4][^5]。

表2 时序路径类型与检查要点

| 路径类型 | 典型要素 | 主要检查 | 常见约束 |
|---|---|---|---|
| R2R | Tco、Tdp、Tskew、Tsu/Th | Setup/Hold | create_clock、TNM_NET、set_max_delay |
| I2R | Tsu、外部输入延迟 | Setup/Hold | set_input_delay、create_clock |
| R2O | Tco、外部输出负载 | Setup/Hold | set_output_delay、create_clock |
| I2O | Tdp、负载/外部时序 | 组合时序 | set_output_delay、set_max_delay(必要时) |
| 异步/CDC | 亚稳态、握手/同步器 | 不适用STA | set_false_path、set_clock_groups(CDC策略) |

---

## 时钟约束:频率、相位与抖动

时钟约束是时序分析的“基准面”。在XDC/SDC中,核心命令包括:create_clock(定义主频/占空比/相位)、create_generated_clock(定义分/倍频与相位关系)、set_clock_groups(定义时钟域关系)、set_input_jitter/set_system_jitter(定义抖动)、set_clock_uncertainty(定义不确定度,覆盖抖动与偏斜的保守裕度)。在Vivado中,约束向导(Constraints Wizard)可辅助快速建立基本时钟与不确定度;在Quartus中,Timing Analyzer以行业标准SDC方法进行分析[^1][^2][^4][^5][^6]。

表3 时钟约束命令速查(XDC/SDC)

| 命令 | 关键参数 | 作用 | 备注 |
|---|---|---|---|
| create_clock | -period、-waveform、-name | 定义主时钟 | 占空比与相位由-waveform给出 |
| create_generated_clock | -source、-divide_by/-multiply_by、-phase、-edges、-edge_shift、-combinational | 定义生成时钟 | 需正确指定源时钟与相位关系 |
| set_clock_groups | -asynchronous、-exclusive | 定义时钟域关系 | CDC与跨域隔离的基础 |
| set_input_jitter | 数值(ps) | 定义输入抖动 | 工具可据此提升保守性 |
| set_system_jitter | 数值(ps) | 定义系统抖动 | 全局抖动预算 |
| set_clock_uncertainty | 数值(ps) | 覆盖抖动/偏斜/裕度 | 建议在项目早期统一配置 |

### 时钟约束的官方数学公式

#### 主时钟定义
- **周期定义**: `Period = 纳秒单位的时间间隔`
- **波形定义**: `Waveform = {上升沿时间 下降沿时间}`，必须包含偶数个值
- **占空比**: 默认50%，可通过-waveform指定
- **相位偏移**: 默认0纳秒，可通过-waveform指定

#### 生成时钟计算公式
1. **分频计算**:
   - 分频系数: `f_out = f_in ÷ N`
   - 周期: `T_out = T_in × N`

2. **倍频计算**:
   - 倍频系数: `f_out = f_in × M`
   - 周期: `T_out = T_in ÷ M`

3. **同时倍频和分频**:
   - 综合系数: `f_out = f_in × (M/N)`
   - 周期: `T_out = T_in × (N/M)`

4. **相位偏移计算**:
   - 第i个边沿时间: `T_edge(i) = T_master_edge(i) + Shift(i)`
   - 其中Shift(i)为第i个边的偏移量

#### 传播时钟特性
- **时钟网络延迟**: 时钟边沿延迟
- **时钟不确定性**: 包含时钟抖动、相位误差、额外不确定性
- **Slack计算**: 时钟延迟和不确定性包含在slack计算中

Vivado约束向导会基于工程结构建议主时钟、生成时钟与uncertainty的初始值;随着实现结果稳定,应逐步将uncertainty收敛到更接近真实的抖动/偏斜预算,从而避免过度保守或约束不足[^1][^2]。Intel侧亦建议在Timing Analyzer中采用标准SDC约束与报告流程,确保多角落一致性[^4][^5]。

### 频率与周期约束

频率约束是绝大多数路径的“上限”。create_clock定义主频与占空比;create_generated_clock定义分/倍频与相位关系,尤其在时钟由MMCM/PLL或逻辑分频产生时,必须显式声明其与源时钟的相位与倍数关系,否则STA会基于不正确的时序参考给出误导性报告[^1][^2]。

### 相位与生成时钟

相位关系通过-waveform指定(上升/下降沿时刻),生成时钟通过-source指向源时钟,并声明-divide_by/-multiply_by与-phase。Vivado/Quartus均建议将生成时钟的相位/占空比与物理实现(时钟资源与布线)保持一致,避免工具在布局阶段“猜错”相位关系[^1][^4]。

### 抖动与不确定度

抖动(Jitter)来源于时钟源与分配网络,通常以ps量级建模;不确定度(Uncertainty)则作为“保守裕度”覆盖抖动、偏斜与版图不确定性。在项目早期,推荐设置统一的uncertainty初值;当设计稳定后,逐步细化到模块级或端口级,以反映真实的抖动/偏斜分布[^10]。Intel与AMD文档均建议在Timing Analyzer/Vivado中明确输入/系统抖动与uncertainty,确保报告一致性与可复现性[^1][^4][^5]。

---

## I/O时序约束

I/O时序约束用于定义FPGA与外部器件之间的时序契约。对于输入端口,set_input_delay描述外部数据相对于参考时钟的到达窗口;对于输出端口,set_output_delay描述外部器件相对于参考时钟的采样窗口。正确设置I/O延迟,是将外部时序“翻译”为FPGA内部STA可理解语言的关键步骤[^1][^4][^8]。

在源同步接口中,时钟与数据同源,常见对齐策略是中心对齐(数据有效窗口中心对时钟沿),可降低对板级Skew与器件抖动的敏感性;在DDR场景,需要同时约束上升/下降沿的输入/输出延迟,并使用-add_delay与-clock_fall覆盖第二条边沿[^8][^13]。

表4 I/O约束命令与参数速查

| 场景 | 关键命令 | 核心参数 | 说明 |
|---|---|---|---|
| 输入延迟 | set_input_delay | -clock、-max/-min、-clock_fall、-add_delay | 定义外部数据相对时钟的到达窗口 |
| 输出延迟 | set_output_delay | -clock、-max/-min、-clock_fall、-add_delay | 定义外部采样相对时钟的窗口 |
| 参考时钟 | create_clock/create_generated_clock | -period、-waveform、-source | I/O延迟的时序参考 |
| 源同步 | set_input_delay / set_output_delay | 上升/下降沿分别约束 | DDR/中心对齐常用 |

### I/O约束的官方数学公式和计算方法

#### 输入延迟约束数学模型
- **输入延迟定义**: 输入延迟表示外部芯片数据通过电路板传播到FPGA输入封装引脚与相对参考板时钟之间的相位差
- **数学表达式**: `Input_Delay = T_data_board - T_clock_board`
- **延迟值可为正或负**: 取决于时钟和数据在设备接口处的相对相位

#### 输出延迟约束数学模型
- **输出延迟定义**: 输出延迟表示FPGA输出封装引脚数据通过电路板传播到另一设备与相对参考板时钟之间的相位差
- **数学表达式**: `Output_Delay = T_data_board - T_clock_board`
- **延迟值可为正或负**: 取决于FPGA外部时钟和数据的相对相位

#### DDR接口的数学计算
对于DDR接口，需要同时约束上升沿和下降沿：
- **上升沿约束**: `-max` 和 `-min` 值分别用于建立时间和保持时间分析
- **下降沿约束**: 使用 `-clock_fall -add_delay` 选项
- **计算公式**: DDR总延迟 = 上升沿延迟 + 下降沿延迟

#### 组合路径延迟计算
对于I/O端口间的组合路径：
- **组合路径延迟 = 时钟周期 - 输入延迟 - 输出延迟**
- **示例**: 10ns周期 - 4ns输入延迟 - 1ns输出延迟 = 5ns组合路径约束

#### 多周期路径计算
在多周期路径约束中：
- **保持周期数 = 建立周期数 - 1 - 源周期数**
- **默认情况下，建立路径乘数是相对于目标时钟定义的**
- **要相对于源时钟修改建立要求，使用 `-start` 选项**
- **保持路径乘数默认相对于源时钟定义**
- **要相对于目标时钟修改保持要求，使用 `-end` 选项**

### 输入/输出延迟建模

-max对应最晚到达(或外部采样最严格要求),-min对应最早到达(或外部采样最宽松要求)。在源同步DDR场景,需要分别对上升沿与下降沿设置输入/输出延迟,并使用-clock_fall与-add_delay确保两条边沿都被约束覆盖。Vivado/Quartus均建议以接口规范(如器件数据手册或DDR控制器指南)提取数据有效窗口参数,并换算为-max/-min的输入/输出延迟[^1][^4][^8][^13]。

### 源同步与DDR约束模板

以中心对齐的源同步接口为例,数据有效窗口中心与时钟沿对齐。设输入时钟周期为Tclk,上升沿前/后数据有效时间分别为dv_bre/dv_are,下降沿前/后数据有效时间分别为dv_bfe/dv_afe,则可按下述模板设置输入延迟(示例来自工程实践)[^13]:

- 上升沿:
  - max: Tclk/2 − dv_bfe
  - min: dv_are
- 下降沿:
  - max: Tclk/2 − dv_bre
  - min: dv_afe
- 使用-clock_fall与-add_delay覆盖下降沿约束

上述模板将外部“数据有效窗口”转换为FPGA内部STA可验证的输入延迟边界。实际项目中,dv_*参数应由器件数据手册或控制器IP的约束脚本给出;若使用Intel DDR控制器,官方建议直接采用其提供的约束脚本以确保一致性[^8]。

---

## 时序路径分析

路径分析的目标是定位关键路径并量化瓶颈。在R2R路径中,关键要素包括:Tco(触发器固有延迟)、Tdp(组合逻辑延迟)、Tskew(时钟偏斜)、Tsu/Th(触发器时序要求)。在I2R与R2O路径中,外部延迟与I/O约束成为主导;在I2O路径中,组合逻辑与外部负载共同决定时序。报告解读的基本流程是:从Slack最小的路径看起,逐段分解延迟构成,定位是逻辑层级过多、资源拥挤、还是时钟偏斜/抖动导致[^4][^5][^10][^11]。

表5 路径类型与典型延迟构成对照

| 路径类型 | 延迟构成 | 主导因素 | 优化思路 |
|---|---|---|---|
| R2R | Tco + Tdp + Tskew、Tsu/Th | 逻辑层级、资源占用 | 流水线/重定时、逻辑复用、布局优化 |
| I2R | 外部输入延迟 + Tdp + Tsu | 接口窗口、I/O约束 | 调整输入延迟、优化组合逻辑 |
| R2O | Tco + Tdp + 外部输出延迟 | 外部负载、输出驱动 | 增强驱动、缩短走线、拆分逻辑 |
| I2O | Tdp + 外部负载 | 组合路径长度 | 拆分路径、插寄存器、减少负载 |

### 寄存器到寄存器路径(R2R)

R2R是最常见的时序路径。Setup检查决定主频上限;Hold检查决定在同一个沿附近的稳定性。典型违例的根因包括:组合逻辑层级过深(导致Tdp过大)、高扇入/扇出导致布线拥塞、资源选择不当(如跨列/跨SLR布线)、以及时钟偏斜未受控。诊断时,应先核对Tco/Tdp/Tskew的分解是否与实现报告一致,再结合逻辑层级与布局热力图判断是否需要流水线化或重定时[^10][^11]。

### 输入到寄存器路径(I2R)

I2R路径的时序由外部输入延迟与内部Tdp/Tsu共同决定。常见问题包括:输入延迟设置过于乐观(与器件实际不符)、跨时钟域信号未做同步、路径上组合逻辑过长。调试时,建议在时序报告中核对“外部延迟”是否与约束一致,并检查是否存在跨域或异步信号误判为同步路径[^4][^5]。

### 寄存器到输出路径(R2O)

R2O路径受外部器件的采样窗口与输出负载影响较大。违例时,一方面可收紧输出延迟约束以反映更严格的外部要求,另一方面可从内部优化Tco与Tdp,并通过增强驱动、缩短走线、减少负载来提升裕量[^4]。

### 输入到输出路径(I2O)

I2O是纯组合路径,常用于快速路径或需要绕过寄存器的场景。由于组合路径对工艺与温度更敏感,建议设置set_output_delay与必要的set_max_delay,确保工具在布局阶段给予足够关注[^4]。

---

## 时序报告解读

时序报告是定位违例的“地图”。一条典型的时序路径报告通常包含:路径概述(起点/终点/时钟域)、延迟分解(逻辑/布线/时钟到达差)、检查类型(Setup/Hold)、Slack值与违例字段(如果存在)。快速定位关键路径的技巧包括:按Slack升序排序、过滤相同起点/终点或相同模块的路径、查看逻辑层级与资源占用热力图,以区分是“逻辑太多”还是“布线太紧”[^1][^4][^5][^15]。

表6 时序报告字段解读对照

| 字段 | 含义 | 关注点 |
|---|---|---|
| Slack | 裕量(正为满足,负为违例) | 绝对值与分布,是否集中在特定模块 |
| Arrival Time | 数据到达时间 | 分解为Tco + Tdp,核对是否与实现一致 |
| Required Time | 数据要求时间 | 反映Tclk、Tsu、Tskew、uncertainty等 |
| Clock Path Skew | 时钟偏斜 | 是否过大、是否跨列/跨SLR |
| Logic Level | 逻辑层级 | 是否过长、是否可流水线化 |
| Resource | 资源类型 | 是否跨列/跨SLR、是否高扇出 |
| Corner/Mode | 角落/模式 | 多角落一致性,是否特定模式违例 |

### Setup/Hold检查与Slack计算

报告中的Setup Slack = Required Time(Setup) − Arrival Time;Hold Slack = Arrival Time − Required Time(Hold)。负值即违例。调试顺序上,建议先看Setup违例(决定主频),再看Hold违例(决定同沿稳定性)。在Vivado/Quartus中,均可通过交互式报告或脚本化方式导出路径延迟分解,便于脚本化分析与回归[^1][^4][^5]。

### 常见误读与核对清单

常见误读包括:将异步路径当作同步路径解读、忽略时钟组与false path设置、混淆外部延迟与内部路径延迟。核对清单包括:时钟定义是否完整(主时钟/生成时钟)、时钟组关系是否正确、false path是否合理、I/O延迟是否与外部规范一致、uncertainty是否与抖动/偏斜预算匹配[^1][^4]。

---

## 时序收敛方法

时序收敛是“约束、RTL与实现”三方协同的结果。实践上,建议以“约束先行、报告驱动、渐进收敛”为策略:早期建立合理的时钟与I/O约束,使用统一的不确定度预算;中期以报告定位瓶颈,结合流水线、重定时与资源约束优化;后期细化uncertainty与跨域约束,确保多角落与多模式稳定收敛[^1][^4][^7]。

表7 常见违例与对策矩阵

| 症状 | 可能根因 | 快速修复 | 结构性优化 |
|---|---|---|---|
| Setup违例 | 逻辑层级过长、Tdp过大、Skew偏大 | 插流水线/重定时、收紧uncertainty、布局指令 | 架构拆分、模块复用、时钟域重构 |
| Hold违例 | 短路径、数据更新太快、Skew不利 | 插缓冲/延迟、调整布局、扩大uncertainty | 时钟树优化、路径改线、资源约束 |
| I/O违例 | 输入/输出延迟不匹配、负载过大 | 校正I/O约束、增强驱动、缩短走线 | 接口时序重构、PHY/控制器参数优化 |
| 跨域违例 | CDC策略缺失、false path不当 | 同步器/握手、修正时钟组与false path | CDC架构优化、带宽/握手协议调整 |
| 抖动敏感 | 不确定度过大、时钟源不稳 | 降低uncertainty、MMCM/PLL配置优化 | 时钟源选型、供电/布局优化 |

### 逻辑与架构层面的优化

流水线与重定时是提升主频的“第一性杠杆”:将长组合逻辑拆分为多级寄存器,在保持功能等价的前提下降低Tdp;重定时则通过在寄存器间“移动”组合逻辑,平衡两级延迟,兼顾Setup与Hold。逻辑复用与资源共享可降低高扇出与资源占用;跨SLR/跨列的路径应尽量避免或通过约束引导布局,缩短跨域走线[^10]。

### 时钟树与Skew控制

Skew控制的工程要点包括:从clock capable管脚输入时钟;移除时钟路径上的组合逻辑与多余缓冲;使用专用分频/高扇出缓冲器;合理设置DELAY_GROUP与CLOCK_ROOT,避免时钟跨列/跨SLR驱动分散逻辑;必要时使用BUFH/BUFR/BUFIO等专用时钟资源,但要防止驱动分散导致Skew反弹[^12]。

### 约束修正与I/O策略

I/O违例常源于约束与外部现实不匹配:需以器件手册或控制器脚本为准,校正输入/输出延迟;在源同步DDR场景,务必同时约束上升/下降沿,并使用-add_delay与-clock_fall;对高负载或长走线的输出,可增强驱动、缩短走线或通过外部终端匹配改善边沿[^8][^13]。

---

## 数学公式与计算方法总表

为便于工程计算,本节汇总核心公式并以统一变量定义为基础展开。

表8 公式总表(变量、含义、适用条件)

| 类别 | 公式 | 变量定义 | 适用条件/备注 |
|---|---|---|---|
| Setup检查 | Tarr = Tco + Tdp;Req = Tclk + Tskew − Tsu;Slack_su = Req − Tarr | 见“变量与符号对照表” | 统一到同一沿;uncertainty可并入Req |
| Hold检查 | Tarr_min = Tco_min + Tdp_min;Req = Tskew + Th;Slack_h = Tarr_min − Req | 同上 | 关注最短路径与最差Skew |
| Skew定义 | Tskew = Tcapture − Tlaunch | 捕获沿与发射沿到达差 | 正偏斜利Setup,负偏斜利Hold |
| Jitter建模 | Req’ = Req − Tjit(或以uncertainty覆盖) | Tjit为抖动 | 建议以uncertainty统一覆盖 |
| I/O延迟 | Input/Output Delay由外部窗口换算 | 上升/下降沿分别计算 | DDR需-clock_fall与-add_delay |
| DDR中心对齐(示例) | rise max: Tclk/2 − dv_bfe;rise min: dv_are;fall max: Tclk/2 − dv_bre;fall min: dv_afe | dv_*为数据有效窗口参数 | 实际参数以器件手册为准 |

上述公式与变量定义与常见教材与工程实践一致,计算示例详见下一节[^10][^11][^13]。

### 公式推导与适用条件

- 建立检查的推导基于“发射沿数据到达时间不晚于捕获沿前Tsu”,将Tarr与Req在统一沿对齐后得到Slack_su表达式;若存在uncertainty J,可将其并入Req(Req = Tclk + Tskew − Tsu − J)以做保守估计。
- 保持检查的推导基于“数据在捕获沿后稳定至少Th”,关注最短路径与最不利Skew,Slack_h = (Tco_min + Tdp_min) − (Tskew + Th)。
- 适用条件包括:同沿检查、角落一致性、路径分类正确(同步/异步)、I/O延迟与外部窗口一致。跨时钟域与异步路径不适用上述同步检查,需采用CDC策略或false path约束[^10][^11]。

### 计算示例(基准设计案例)

设某R2R路径参数如下:Tclk = 10 ns,Tco_max/min = (0.4, 0.2) ns,Tdp_max/min = (3.0, 1.0) ns,Tsu = 0.2 ns,Th = 0.1 ns,Tskew = 0.3 ns,uncertainty J = 0.2 ns(覆盖抖动/偏斜)。

- Setup:
  - Tarr_max = 0.4 + 3.0 = 3.4 ns
  - Req = 10 + 0.3 − 0.2 − 0.2 = 9.9 ns
  - Slack_su = 9.9 − 3.4 = 6.5 ns(满足)
- Hold:
  - Tarr_min = 0.2 + 1.0 = 1.2 ns
  - Req = 0.3 + 0.1 = 0.4 ns
  - Slack_h = 1.2 − 0.4 = 0.8 ns(满足)

若Tdp_max上升至7.0 ns:
- Setup:Slack_su = 9.9 − (0.4 + 7.0) = 2.5 ns(仍满足,但裕量显著下降)

若Tskew变为−0.4 ns(捕获沿滞后发射沿):
- Setup:Req = 10 − 0.4 − 0.2 − 0.2 = 9.2 ns;Slack_su = 9.2 − 3.4 = 5.8 ns(略降)
- Hold:Req = −0.4 + 0.1 = −0.3 ns;Slack_h = 1.2 − (−0.3) = 1.5 ns(提升)

该示例表明:正偏斜有利于Setup但可能压缩Hold裕量,负偏斜相反。工程上应将Skew最小化,并以uncertainty覆盖抖动与残留偏斜[^10][^11]。

---

## 约束模板与命令索引(XDC/SDC)

本节汇总常用约束模板,覆盖主时钟、生成时钟、I/O延迟、时钟组与false path、抖动/不确定度与Skew控制。模板中的具体数值需由项目数据手册或IP脚本替换。

表9 约束模板速查表

| 场景 | 命令/模板 | 说明 |
|---|---|---|
| 主时钟 | create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports sys_clk] | 100 MHz,50%占空比 |
| 生成时钟(分频) | create_generated_clock -name sys_clk_div2 -source [get_pins mmcm/CLKOUT] -divide_by 2 -waveform {0.000 5.000} [get_pins mmcm/CLKOUT] | 声明与源时钟关系 |
| 生成时钟(相位) | create_generated_clock -name sys_clk_phase -source [get_pins mmcm/CLKOUT] -phase 90 [get_pins mmcm/CLKOUT] | 90°相位偏移 |
| 输入延迟(中心对齐) | set_input_delay -clock sys_clk -max [expr {$period/2 - $dv_bfe}] [get_ports {din[*]}] | 上升沿max |
| 输入延迟(中心对齐) | set_input_delay -clock sys_clk -min $dv_are [get_ports {din[*]}] | 上升沿min |
| 输入延迟(DDR下降沿) | set_input_delay -clock sys_clk -max [expr {$period/2 - $dv_bre}] [get_ports {din[*]}] -clock_fall -add_delay | 下降沿max |
| 输入延迟(DDR下降沿) | set_input_delay -clock sys_clk -min $dv_afe [get_ports {din[*]}] -clock_fall -add_delay | 下降沿min |
| 输出延迟 | set_output_delay -clock sys_clk -max 2.000 [get_ports {dout[*]}] | 外部采样最严格要求 |
| 输出延迟 | set_output_delay -clock sys_clk -min 0.200 [get_ports {dout[*]}] | 外部采样最宽松要求 |
| 时钟组(异步域) | set_clock_groups -asynchronous -group {clk_a} -group {clk_b} | 跨时钟域隔离 |
| False Path | set_false_path -from [get_cells sync_*] -to [get_cells dst_*] | 异步路径忽略STA |
| 输入抖动 | set_input_jitter 0.200 [get_clocks sys_clk] | 200 ps(示例) |
| 系统抖动 | set_system_jitter 0.250 | 250 ps(示例) |
| 时钟不确定度 | set_clock_uncertainty -setup 0.300 [get_clocks sys_clk] | 统一预算(示例) |
| Skew控制(延迟组) | set_clock_delay_group -name grp_sys | 约束跨域偏斜 |
| Skew控制(时钟根) | set_clock_root -mode auto [get_pins mmcm/CLKOUT] | 建议时钟根位置 |

上述模板基于XDC/SDC标准语法,Vivado与Quartus均支持;具体数值需结合器件与接口规范替换。对于DDR场景,建议优先采用控制器IP提供的约束脚本以确保一致性[^1][^2][^4][^8][^12][^13][^19][^20][^21][^22][^23][^24][^25]。

### 基于官方文档的完整约束示例

#### 官方推荐的约束序列
根据Xilinx UG903官方文档，建议按以下顺序组织约束：

```tcl
# 时序断言部分
# 1. 主时钟
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports sys_clk]

# 2. 虚拟时钟
create_clock -name clk_virt -period 10.000

# 3. 生成时钟
create_generated_clock -name sys_clk_div2 -source [get_pins mmcm/CLKIN] -divide_by 2 [get_pins mmcm/CLKOUT]
create_generated_clock -name clkshift -source [get_pins mmcm/CLKIN] -edges {1 2 3} -edge_shift {2.5 0 2.5} [get_pins mmcm/CLKOUT]
create_generated_clock -name clk43 -source [get_pins mmcm/CLKIN] -multiply_by 4 -divide_by 3 [get_pins mmcm/CLKOUT]

# 4. 时钟组
set_clock_groups -asynchronous -group {clk_a} -group {clk_b}

# 5. 总线偏斜约束
set_bus_skew -from [get_clocks clk_a] -to [get_clocks clk_b] 2.000

# 6. 输入输出延迟约束
set_input_delay -clock sys_clk -max 4.000 [get_ports {din[*]}]
set_input_delay -clock sys_clk -min 1.000 [get_ports {din[*]}]
set_output_delay -clock sys_clk -max 2.000 [get_ports {dout[*]}]
set_output_delay -clock sys_clk -min 0.500 [get_ports {dout[*]}]

# 时序异常部分
# 7. 假路径
set_false_path -from [get_cells sync_*] -to [get_cells dst_*]

# 8. 最大/最小延迟
set_max_delay -from [get_cells src_reg[*]] -to [get_cells dst_reg[*]] 8.000
set_min_delay -from [get_cells src_reg[*]] -to [get_cells dst_reg[*]] 0.500

# 9. 多周期路径
set_multicycle_path -setup -from [get_cells {src_reg[*]}] -to [get_cells {dst_reg[*]}] 2
set_multicycle_path -hold -from [get_cells {src_reg[*]}] -to [get_cells {dst_reg[*]}] 1

# 10. 案例分析
set_case_analysis 0 [get_bits config_reg[0]]

# 11. 禁用时序
disable_timing -from REG1/C -to REG1/Q [get_cells {pipeline_reg[*]}]

# 物理约束部分
# 12. I/O物理约束
set_property IOSTANDARD LVDS_25 [get_ports {lvds_data_p[*]}]
set_property IOSTANDARD LVDS_25 [get_ports {lvds_data_n[*]}]
set_property PACKAGE_PIN H16 [get_ports sys_clk]
```

#### 官方DDR接口约束示例
```tcl
# DDR输入约束（基于官方示例）
create_clock -name clk_ddr -period 6.000 [get_ports DDR_CLK_IN]
set_input_delay -clock clk_ddr -max 2.100 [get_ports DDR_IN]
set_input_delay -clock clk_ddr -max 1.900 [get_ports DDR_IN] -clock_fall -add_delay
set_input_delay -clock clk_ddr -min 0.900 [get_ports DDR_IN]
set_input_delay -clock clk_ddr -min 1.100 [get_ports DDR_IN] -clock_fall -add_delay

# DDR输出约束（基于官方示例）
set_output_delay -clock clk_ddr -max 2.100 [get_ports DDR_OUT]
set_output_delay -clock clk_ddr -max 1.900 [get_ports DDR_OUT] -clock_fall -add_delay
set_output_delay -clock clk_ddr -min 0.900 [get_ports DDR_OUT]
set_output_delay -clock clk_ddr -min 1.100 [get_ports DDR_OUT] -clock_fall -add_delay
```

#### 官方STARTUPE3约束示例
```tcl
# STARTUPE3内部引脚约束（UltraScale+设备）
create_generated_clock -name clk_sck \
  -source [get_pins -hierarchical axi_quad_spi_0/ext_spi_clk] \
  [get_pins STARTUP/CCLK] -edges {3 5 7}
set_output_delay -clock clk_sck -max 6.000 [get_pins STARTUP/DATA_OUT[]]
set_output_delay -clock clk_sck -min 1.000 [get_pins STARTUP/DATA_OUT[]]
set_input_delay -clock clk_sck -max 7.000 [get_pins STARTUP/DATA_IN[]] -clock_fall
set_input_delay -clock clk_sck -min 1.000 [get_pins STARTUP/DATA_IN[]] -clock_fall
```

### 高级约束模板

#### 多时钟域约束
```tcl
# 主时钟定义
create_clock -period 10.000 -name main_clk -waveform {0.000 5.000} [get_ports main_clk]
create_clock -period 8.000 -name fast_clk -waveform {0.000 4.000} [get_ports fast_clk]

# 时钟组设置
set_clock_groups -asynchronous -group {main_clk} -group {fast_clk}

# 跨时钟域路径忽略
set_false_path -from [get_clocks main_clk] -to [get_clocks fast_clk]
set_false_path -from [get_clocks fast_clk] -to [get_clocks main_clk]
```

#### I/O标准约束
```tcl
# LVDS输入约束
set_property IOSTANDARD LVDS_25 [get_ports {lvds_data_p[*]}]
set_property IOSTANDARD LVDS_25 [get_ports {lvds_data_n[*]}]

# 高速差分输出约束
set_property IOSTANDARD LVDS_25 [get_ports {diff_data_out_p[*]}]
set_property IOSTANDARD LVDS_25 [get_ports {diff_data_out_n[*]}]

# DDR SDRAM接口约束
create_clock -period 7.500 -name ddr_clk -waveform {0.000 3.750} [get_ports ddr_clk]
set_input_delay -clock ddr_clk -max 2.000 [get_ports {ddr_dq[*]}]
set_input_delay -clock ddr_clk -min 0.500 [get_ports {ddr_dq[*]}]
set_output_delay -clock ddr_clk -max 2.000 [get_ports {ddr_dq[*]}]
set_output_delay -clock ddr_clk -min 0.500 [get_ports {ddr_dq[*]}]
```

#### 时钟管理约束
```tcl
# MMCM/PLL生成时钟
create_generated_clock -name sys_clk_2x -source [get_pins mmcm/CLKIN] -multiply_by 2 [get_pins mmcm/CLKOUT]

# 时钟缓冲器约束
set_property CLOCK_BUFFER_TYPE BUFG [get_pins mmcm/CLKOUT]
set_property CLOCK_BUFFER_TYPE BUFH [get_pins mmcm/CLKOUT2]

# 时钟域分组
set_property CLOCK_DOMAIN main_clk [get_cells {top/main_domain/*}]
set_property CLOCK_DOMAIN fast_clk [get_cells {top/fast_domain/*}]
```

#### 时序异常约束
```tcl
# 多周期路径
set_multicycle_path -setup -from [get_cells {src_reg[*]}] -to [get_cells {dst_reg[*]}] 2
set_multicycle_path -hold -from [get_cells {src_reg[*]}] -to [get_cells {dst_reg[*]}] 1

# 假路径约束
set_false_path -from [get_cells reset_sync] -to [get_cells {*_reg[*]}]
set_false_path -from [get_cells {debug_reg[*]}] -to [get_cells {*_reg[*]}]

# 最小脉冲宽度约束
set_min_pulse_width -high -time 2.000 [get_clocks sys_clk]
set_min_pulse_width -low -time 2.000 [get_clocks sys_clk]
```

---

## 附录:术语表与参考链接

表10 术语与缩略语对照

| 术语/缩写 | 英文 | 中文释义 | 备注 |
|---|---|---|---|
| STA | Static Timing Analysis | 静态时序分析 | 穷尽路径、速度快的分析方法 |
| Tsu | Setup Time | 建立时间 | 时钟沿前数据稳定时间 |
| Th | Hold Time | 保持时间 | 时钟沿后数据稳定时间 |
| Tco | Clock-to-Output | 时钟到输出延迟 | 触发器固有传播延迟 |
| Tdp | Data Path Delay | 数据路径延迟 | 组合逻辑与线延迟之和 |
| Skew | Clock Skew | 时钟偏斜 | 不同节点时钟到达差 |
| Jitter | Clock Jitter | 时钟抖动 | 周期/相位的时间不确定度 |
| Slack | — | 裕量 | Setup:Req−Arr;Hold:Arr−Req |
| CDC | Clock Domain Crossing | 跨时钟域 | 需同步器/握手/约束 |
| XDC/SDC | — | 约束文件格式 | 主流时序约束语言 |

信息边界与替换建议:
- 器件与速度等级的Tsu/Th、Tco、抖动/偏斜等数值需以官方数据手册替换。
- DDR等高速接口的具体时序模板建议使用官方IP约束脚本。
- 报告字段与截图因工具版本差异可能略有不同,需以实际版本为准。
- 跨列/跨SLR、专用时钟资源等器件族差异需参考对应架构指南。
- 案例项目的RTL与实现细节不在本报告范围,建议结合实际工程补充。

---

## 参考文献

**官方文档（实际提取内容）**
[^1]: Xilinx. UG903 Vivado Design Suite User Guide: Using Constraints (v2022.1). https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_1/ug903-vivado-using-constraints.pdf
[^2]: AMD. Vivado Design Suite User Guide: Using Constraints (UG903). https://docs.amd.com/r/en-US/ug903-vivado-using-constraints
[^3]: AMD. Vivado Design Suite User Guide: System-Level Design Entry (UG895) – Working with Constraints. https://docs.amd.com/r/en-US/ug895-vivado-system-level-design-entry/Working-with-Constraints
[^4]: Intel. Intel Quartus Prime Timing Analyzer Cookbook. https://www.intel.com/programmable/technical-pdfs/683081.pdf
[^5]: Intel. Quartus Prime Standard Edition User Guide: Timing Analyzer. https://cdrdv2-public.intel.com/683068/667035/ug-qps-timing-analyzer-683068-667035.pdf
[^6]: Intel. 使用 Intel Quartus Prime Timing Analyzer. https://www.intel.cn/content/www/cn/zh/docs/programmable/683068/18-1/using-the-timing-analyzer.html
[^7]: Intel. AN 1016: Timing Closure Methodology Quick Reference. https://cdrdv2-public.intel.com/836193/an1016-836192-836193.pdf
[^8]: Intel. DDR Timing Cookbook. https://www.intel.com/content/dam/support/us/en/programmable/support-resources/fpga-wiki/asset02/ddr-timing-cookbook.pdf
[^9]: Microchip. PolarFire FPGA Timing Constraints User Guide (UG0730). https://ww1.microchip.com/downloads/aemdocuments/documents/fpga/core-docs/Libero/pf_2_1_0/Tool/pf_timing_constr_flow_ug.pdf

**官方教程和指南**
[^10]: AMD. Timing Constraints Tutorial. https://adaptivesupport.amd.com/s/question/0D52E00006hpMODSA2/timing-constraints-tutorial?language=zh_CN
[^11]: AMD. 7 Series CLB Timing Guide. https://docs.amd.com/r/en-US/ug474_7Series_CLB/Timing
[^12]: Intel. Timing Constraints and Analysis Guide. https://www.intel.com/content/www/us/en/docs/programmable/683861/current/timing-constraints-and-analysis.html
[^13]: Intel. Intel FPGA Timing Analysis Official Guide. https://www.intel.com/content/www/us/en/docs/programmable/813929/25-1/fpga-timing-analysis.html

**开源教程资源**
[^14]: GitHub. FPGA时序约束教程资源. https://github.com/FouriersCat/FPGA-Timing-Constraint-Turorials
[^15]: Xilinx. Adaptive Computing Support. https://www.xilinx.com/content/xilinx/en/support.html
[^16]: Xilinx. UltraScale Architecture-Based FPGAs Memory IP v1.4. https://www.xilinx.com/support/documents/ip_documentation/ultrascale_memory_ip/v1_4/pg150-ultrascale-memory-ip.pdf
[^17]: Xilinx. Zynq-7000 All Programmable SoC and 7 Series Devices MIG. https://www.xilinx.com/support/documents/ip_documentation/mig_7series/v4_1/ug586_7Series_MIS.pdf

**技术博客和实践资源**
[^18]: CSDN. 时序分析基础(Slack、Setup、Hold、Jitter、Skew). https://blog.csdn.net/hzmscut/article/details/139804860
[^19]: CSDN. FPGA 时序约束:Setup/Hold Time 计算与 STA 工具使用. https://blog.csdn.net/2501_93893195/article/details/154155735
[^20]: 腾讯云. FPGA中降低时钟skew的几种方法. https://cloud.tencent.com/developer/article/2399558
[^21]: CSDN. 高速FPGA时序约束设计分析:IO延时约束方法(3). https://blog.csdn.net/qq_40052606/article/details/117514666
[^22]: 21IC电子网. FPGA时序约束添加与跨时钟域问题解决策略. https://www.21ic.com/a/994312.html
[^23]: 知乎专栏. timing report如何看懂? https://www.zhihu.com/question/287188109
[^24]: 知乎专栏. setup time和hold time. https://zhuanlan.zhihu.com/p/690561665
[^25]: CSDN. 静态时序分析（STA）自学笔记_setup slack. https://blog.csdn.net/ICer_CoolDong/article/details/124864265

**说明**: 本文档中的数学公式、约束语法和计算方法主要基于Xilinx UG903官方文档的实际内容提取。参考文献中标记为“官方文档（实际提取内容）”的条目是真正从官方文档中提取了技术内容的资源。

---