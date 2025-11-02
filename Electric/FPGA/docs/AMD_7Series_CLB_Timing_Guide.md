# AMD 7系列FPGA CLB时序指南技术文档

## 概述

本文档基于AMD官方技术文档UG474，详细介绍了7系列FPGA中可配置逻辑块（CLB）的时序模型、参数和计算方法。

## 时序命名约定

### 基本命名规则
- 参数命名格式：`T<sub>source</sub><sub>destination</sub>`
- 建立时间：`TXXCK`（例如：TAS - A输入建立时间）
- 保持时间：`TCKXX`（例如：TAH - A输入保持时间）

### 路径命名示例
- `TILO`: LUT A/B/C/D → A/B/C/D
- `TCKO`: FF时钟 → AQ/BQ/CQ/DQ
- `TXXCK`: 建立时间
- `TCKXX`: 保持时间

## 1. 通用Slice组合延迟

### 1.1 基本组合延迟
- **TILO**: LUT A/B/C/D → A/B/C/D（直接输出）
- **TITO**: LUT A/B/C/D → AQ/BQ/CQ/DQ（通过锁存器）

### 1.2 时序特性
这些参数定义了信号通过LUT和锁存器的传播延迟，是FPGA设计中计算组合逻辑路径延迟的基础。

## 2. 通用Slice时序延迟

### 2.1 时钟到输出延迟
- **TCKO**: FF时钟 → AQ/BQ/CQ/DQ
- **TCKLO**: 锁存器时钟 → AQ/BQ/CQ/DQ
- **TSHCKO**: FF时钟 → AMUX/BMUX/CMUX/DMUX

### 2.2 应用场景
这些参数用于计算时钟信号到寄存器输出的传播时间，是时序分析中的关键指标。

## 3. 通用Slice建立/保持时间

### 3.1 数据输入时序
- **TAS/TAH**: A/B/C/D输入建立/保持时间
- **TDICK/TCKDI**: AX/BX/CX/DX输入建立/保持时间

### 3.2 控制信号时序
- **TCECK/TCKCE**: CE（时钟使能）建立/保持时间
- **TSRCK/TCKSR**: SR（同步复位）建立/保持时间

### 3.3 计算方法
建立时间 + 保持时间 = 数据必须稳定的最短时间窗口

## 4. 置位/复位特性

### 4.1 关键参数
- **TRPW (TSRMIN)**: 最小SR脉冲宽度
- **TRQ**: 异步SR传播到输出的延迟
- **FTOG**: FF最大切换频率（出口管制）

### 4.2 设计考虑
- 最小脉冲宽度确保复位信号的有效性
- 异步复位传播延迟影响系统响应时间
- 最大切换频率限制时序设计

## 5. 宽多路复用器时序参数

### 5.1 输入到多路复用器延迟
- **TAXA/TAXB/TBXB/TCXB/TCXC**: AX/BX/CX输入 → AMUX/BMUX/CMUX
- **TOPAB/TOPBA/TOPBB/TOPCB/TOPDB/TOPDC**: A/B/C/D输入 → AMUX/BMUX/CMUX
- **TILO_2**: A/C → AMUX/CMUX（通过F7/F8）

### 5.2 应用场景
这些参数用于计算多路复用器路径的时序延迟，特别是在实现宽位宽选择器时。

## 6. 进位链时序参数

### 6.1 进位传播延迟
- **TAXA–TDXD**: AX/BX/CX/DX → AMUX/BMUX/CMUX/DMUX（通过进位）
- **TAXCY/TBXCY/TCXCY/TDXCY**: AX/BX/CX/DX → COUT
- **TBYP**: CIN → COUT（进位旁路）

### 6.2 进位链特殊参数
- **TOPCYA–TOPCYD**: A/B/C/D → COUT
- **TCINA–TCIND**: CIN → AMUX/BMUX/CMUX/DMUX（通过XOR）
- **TCINCK/TCKCIN**: CIN相对于CLK的建立/保持时间

### 6.3 进位链使用注意事项
1. 进位逻辑垂直放置在SLICEL/M的每隔一列
2. AMD工具自动放置在列中
3. 作为组进行布局规划以避免中断
4. 在SSI器件中无法跨SLR级联

## 7. 分布式RAM时序（仅SLICEM）

### 7.1 时钟到输出延迟
- **TSHCKO**: CLK → A/B/C/D和AMUX/BMUX/CMUX/DMUX输出（写操作后）

### 7.2 地址时序
- **TAS/TAH**: A/B/C/D地址建立/保持时间

### 7.3 数据时序
- **TDS/TDH**: DI数据建立/保持时间
- **TWS/TWH**: WE写使能建立/保持时间

### 7.4 时钟特性
- **TMPW**: 最小时钟脉冲宽度
- **TMCP**: 地址写周期时序的最小时钟周期

## 8. SRL移位寄存器时序（仅SLICEM）

### 8.1 标准SRLC32E参数
包含时钟、CE/SR路径的建立/保持时间以及时钟到输出时序。

### 8.2 应用特性
- 用于静态/动态长度移位寄存器
- 支持可选的寄存器输出
- 适用于需要移位功能的时序设计

## 9. 时序解释和使用

### 9.1 分析工具配合
- 与AMD Timing Analyzer配合使用
- 结合器件数据手册的开关特性
- 参数名称和路径与时序报告对齐

### 9.2 设计指导
- CLB进位逻辑改善加法器/计数器/比较器性能
- 对于更宽的算术运算，根据性能/功耗和资源使用情况，可优先考虑DSP48E1切片（UG479）

## 10. 实际应用建议

### 10.1 时序分析
1. 使用这些模型进行精确的时序分析
2. 结合器件数据手册获取具体的延迟值
3. 在时序报告中验证参数使用

### 10.2 设计优化
1. 合理使用进位链提高算术运算性能
2. 考虑分布式RAM和SRL的资源利用
3. 避免跨SLR的进位链级联

### 10.3 验证方法
1. 使用AMD Timing Analyzer进行时序验证
2. 在实际硬件上进行时序验证
3. 考虑温度和电压变化对时序的影响

## 相关文档链接

- [7系列FPGA可配置逻辑块用户指南(UG474)](https://docs.amd.com/r/en-US/ug474_7Series_CLB)
- [7系列DSP48E1切片用户指南(UG479)](https://docs.amd.com/r/en-US/ug479_7Series_DSP48E1)
- [AMD时序分析器文档](https://docs.amd.com/)

---

*本文档基于AMD官方技术文档UG474整理，时效性截至2025年11月2日。*