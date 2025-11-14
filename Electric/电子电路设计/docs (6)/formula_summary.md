# 电子电路公式汇总

本文档整理了电子电路设计中的重要公式，按照不同章节分类汇总，方便学习和查阅。

---

## 1. 基础电路理论公式

### 1.1 欧姆定律
- **基本形式**：$V = IR$
- **变形形式**：$I = \frac{V}{R}$，$R = \frac{V}{I}$
- **功率公式**：$P = VI = I^2R = \frac{V^2}{R}$

**来源章节**：第1章 基础电路理论

### 1.2 基尔霍夫定律
- **基尔霍夫电流定律（KCL）**：$\sum_{k=1}^{n} I_k = 0$ 或 $\sum I_{in} = \sum I_{out}$
- **基尔霍夫电压定律（KVL）**：$\sum_{k=1}^{n} V_k = 0$

**来源章节**：第1章 基础电路理论

### 1.3 戴维南定理和诺顿定理
- **戴维南等效电压**：$V_{th} = V_{oc}$（开路电压）
- **戴维南等效电阻**：$R_{th} = \frac{V_{oc}}{I_{sc}}$（短路电流）
- **诺顿等效电流**：$I_{no} = I_{sc}$（短路电流）
- **诺顿等效电阻**：$R_{no} = R_{th}$
- **等效变换**：$V_{th} = I_{no}R_{no}$，$I_{no} = \frac{V_{th}}{R_{th}}$

**来源章节**：第1章 基础电路理论

### 1.4 交流电路基础
- **正弦交流电压**：$v(t) = V_m\sin(\omega t + \phi)$
- **阻抗复数表示**：$Z = \frac{\dot{V}}{\dot{I}} = R + jX$
- **容抗**：$X_C = \frac{1}{\omega C} = \frac{1}{2\pi f C}$
- **感抗**：$X_L = \omega L = 2\pi f L$
- **有功功率**：$P = V_{rms}I_{rms}\cos\phi$
- **无功功率**：$Q = V_{rms}I_{rms}\sin\phi$
- **视在功率**：$S = V_{rms}I_{rms} = \sqrt{P^2 + Q^2}$

**来源章节**：第1章 基础电路理论

---

## 2. 半导体器件公式

### 2.1 PN结和二极管方程
- **内建电势**：$V_{bi} = \frac{kT}{q} \ln\left(\frac{N_A N_D}{n_i^2}\right)$
- **二极管方程**：$I_D = I_S \left(e^{\frac{V_D}{nV_T}} - 1\right)$
- **反向饱和电流**：$I_S = qA\left(\frac{D_p p_{n0}}{L_p} + \frac{D_n n_{p0}}{L_n}\right)$
- **热电压**：$V_T = \frac{kT}{q}$（26mV @ 300K）
- **动态电阻**：$r_d = \frac{V_T}{I_{DQ}} = \frac{26mV}{I_{DQ}}$

**来源章节**：第2章 半导体器件基础

### 2.2 BJT三极管特性
- **电流传输关系**：$I_C = \alpha I_E$，$I_C = \beta I_B$
- **电流增益**：$\alpha = \frac{I_C}{I_E} \approx 0.95-0.99$，$\beta = \frac{I_C}{I_B} = \frac{\alpha}{1-\alpha} \approx 20-200$
- **输入特性**：$I_B = I_{ES}\left(e^{\frac{V_{BE}}{V_T}} - 1\right)\left(1 + \frac{V_{CE}}{V_A}\right)$
- **混合π模型参数**：
  - 输入电阻：$r_{\pi} = \frac{\beta V_T}{I_{CQ}}$
  - 跨导：$g_m = \frac{I_{CQ}}{V_T}$
  - 输出电阻：$r_o = \frac{V_A}{I_{CQ}}$
- **h参数**：$h_{11} = r_{\pi}$，$h_{21} = \beta$，$h_{22} = \frac{1}{r_o}$

**来源章节**：第2章 半导体器件基础

### 2.3 MOSFET方程
- **阈值电压**：$V_{th} = V_{FB} + 2\phi_F + \frac{\sqrt{2\varepsilon_s q N_A (2\phi_F + V_{SB})}}{C_{ox}}$
- **线性区电流**：$I_D = \mu_n C_{ox} \frac{W}{L}\left[(V_{GS} - V_{th})V_{DS} - \frac{V_{DS}^2}{2}\right]$
- **饱和区电流**：$I_D = \frac{1}{2} \mu_n C_{ox} \frac{W}{L}(V_{GS} - V_{th})^2$
- **跨导**：$g_m = \sqrt{2\mu_n C_{ox} \frac{W}{L} I_D}$
- **输出电阻**：$r_o = \frac{1}{\lambda I_D}$

**来源章节**：第2章 半导体器件基础

### 2.4 器件频率特性
- **BJT特征频率**：$f_T = \frac{g_m}{2\pi (C_{\pi} + C_{\mu})}$
- **MOSFET特征频率**：$f_T = \frac{g_m}{2\pi (C_{gs} + C_{gd})}$
- **最高振荡频率**：$f_{max} = \frac{f_T}{2\sqrt{g_m R_G}}$

**来源章节**：第2章 半导体器件基础

---

## 3. 放大电路公式

### 3.1 共射极放大器
- **电压增益（空载）**：$A_v = -\frac{\beta R_C}{r_{be}}$
- **电压增益（带负载）**：$A_v = -\frac{\beta R_L'}{r_{be}}$，其中$R_L' = R_C \parallel R_L$
- **输入电阻**：$r_i = R_B \parallel r_{be}$
- **输出电阻**：$r_o = R_C$
- **静态工作点**：
  - $I_{BQ} = \frac{V_{CC} - V_{BEQ}}{R_B}$
  - $I_{CQ} = \beta I_{BQ}$
  - $V_{CEQ} = V_{CC} - I_{CQ} R_C$

**来源章节**：第3章 基本放大电路

### 3.2 共集电极放大器（射极跟随器）
- **电压增益**：$A_v = \frac{(1+\beta)R_L'}{r_{be} + (1+\beta)R_L'} \approx 1$
- **输入电阻**：$r_i = R_B \parallel [r_{be} + (1+\beta)R_L']$
- **输出电阻**：$r_o = \frac{r_{be} + R_S'}{1+\beta} \parallel R_E$，其中$R_S' = R_S \parallel R_B$
- **电流增益**：$A_i \approx 1 + \beta$

**来源章节**：第3章 基本放大电路

### 3.3 共基极放大器
- **电压增益**：$A_v = \frac{\alpha R_L'}{r_{e}}$
- **输入电阻**：$r_i = \frac{r_{e}}{1-\alpha} \approx r_{e}$
- **输出电阻**：$r_o = R_C$
- **截止频率**：$f_{\alpha} = (1-\alpha)f_T$

**来源章节**：第3章 基本放大电路

### 3.4 多级放大器
- **总电压增益**：$A_v = A_{v1} \times A_{v2} \times \cdots \times A_{vn}$
- **总电流增益**：$A_i = A_{i1} \times A_{i2} \times \cdots \times A_{in}$
- **输入阻抗**：$R_i = R_{i1}$
- **输出阻抗**：$R_o = R_{on}$
- **下截止频率**：$\frac{1}{f_L^2} = \frac{1}{f_{L1}^2} + \frac{1}{f_{L2}^2} + \cdots$
- **上截止频率**：$\frac{1}{f_H^2} = \frac{1}{f_{H1}^2} + \frac{1}{f_{H2}^2} + \cdots$

**来源章节**：第4章 多级放大电路

---

## 4. 反馈理论公式

### 4.1 基本反馈方程
- **闭环增益**：$A_f = \frac{A}{1 + A\beta}$
- **环路增益**：$T = A\beta$
- **反馈深度**：$F = 1 + T = 1 + A\beta$
- **深度反馈条件**：$|1 + A\beta| \gg 1$，此时$A_f \approx \frac{1}{\beta}$

**来源章节**：第5章 反馈理论

### 4.2 四种反馈组态公式

#### 4.2.1 电压串联反馈
- **闭环电压增益**：$A_{vf} = \frac{A_v}{1 + A_v\beta_v}$
- **输入阻抗**：$R_{if} = R_i(1 + A_v\beta_v)$
- **输出阻抗**：$R_{of} = \frac{R_o}{1 + A_v\beta_v}$

#### 4.2.2 电压并联反馈
- **闭环互阻增益**：$A_{rf} = \frac{A_r}{1 + A_r\beta_g}$
- **输入阻抗**：$R_{if} = \frac{R_i}{1 + A_r\beta_g}$
- **输出阻抗**：$R_{of} = \frac{R_o}{1 + A_r\beta_g}$

#### 4.2.3 电流串联反馈
- **闭环互导增益**：$A_{gf} = \frac{A_g}{1 + A_g\beta_r}$
- **输入阻抗**：$R_{if} = R_i(1 + A_g\beta_r)$
- **输出阻抗**：$R_{of} = R_o(1 + A_g\beta_r)$

#### 4.2.4 电流并联反馈
- **闭环电流增益**：$A_{if} = \frac{A_i}{1 + A_i\beta_i}$
- **输入阻抗**：$R_{if} = \frac{R_i}{1 + A_i\beta_i}$
- **输出阻抗**：$R_{of} = R_o(1 + A_i\beta_i)$

**来源章节**：第5章 反馈理论

### 4.3 稳定性分析
- **相位裕度**：$PM = 180° + \phi_T(\omega_{gc})$
- **增益裕度**：$GM = -20\log|T(\omega_{180})|$ (dB)
- **稳定性条件**：$\phi_T(\omega_{180}) < -180°$ 或 $|T(\omega_{180})| < 1$

**来源章节**：第5章 反馈理论

---

## 5. 功率放大公式

### 5.1 A类功率放大器
- **输出功率**：$P_o = \frac{V_{om}^2}{2R_L}$
- **电源功率**：$P_{CC} = V_{CC} \cdot I_{CC}$
- **效率**：$\eta = \frac{P_o}{P_{CC}} = \frac{V_{om}^2}{2R_L V_{CC} I_{CC}}$
- **理论最大效率**：$\eta_{max} = 25\%$（电阻负载），$\eta_{max} = 50\%$（变压器耦合）

**来源章节**：第7章 功率放大电路

### 5.2 B类功率放大器
- **输出功率**：$P_o = \frac{V_{om}I_{om}}{2}$
- **电源功率**：$P_{CC} = \frac{2V_{CC}I_{om}}{\pi}$
- **效率**：$\eta = \frac{P_o}{P_{CC}} = \frac{\pi V_{om}}{4V_{CC}}$
- **理论最大效率**：$\eta_{max} = \frac{\pi}{4} \approx 78.5\%$

**来源章节**：第7章 功率放大电路

### 5.3 AB类功率放大器
- **效率特点**：介于A类和B类之间，通常在60%-70%范围内
- **无交越失真**：通过适当偏置消除交越失真

**来源章节**：第7章 功率放大电路

### 5.4 C类功率放大器
- **导通角**：$\theta = 2\arccos\left(\frac{V_{bias}}{V_{im}}\right)$
- **效率**：$\eta = \frac{\pi}{4} \cdot \frac{\sin\theta - \theta\cos\theta}{\theta - \sin\theta\cos\theta}$
- **理论最大效率**：$\eta_{max} \approx 85\%$

**来源章节**：第7章 功率放大电路

### 5.5 热管理公式
- **结温**：$T_j = T_a + P_d \cdot R_{θJA}$
- **总热阻**：$R_{θJA} = R_{θJC} + R_{θCS} + R_{θSA}$
- **功耗计算**：$P_d = \frac{V_{CE(sat)} \cdot I_C + V_{BE} \cdot I_B}{\eta}$

**来源章节**：第7章 功率放大电路

---

## 6. 运放应用公式

### 6.1 虚短虚断概念
- **虚短**：$V_+ = V_-$
- **虚断**：$I_+ = I_- = 0$

**来源章节**：第8章 运算放大器

### 6.2 反相放大器
- **电压增益**：$A_v = \frac{V_{out}}{V_{in}} = -\frac{R_f}{R_1}$
- **输入电阻**：$r_i = R_1$
- **平衡电阻**：$R_p = R_1 \parallel R_f$

**来源章节**：第8章 运算放大器

### 6.3 同相放大器
- **电压增益**：$A_v = \frac{V_{out}}{V_{in}} = 1 + \frac{R_f}{R_1}$
- **输入电阻**：$r_i \approx R_{in(op)}$（运放输入阻抗）
- **电压跟随器**：$A_v = 1$（当$R_f = 0$，$R_1 = \infty$）

**来源章节**：第8章 运算放大器

### 6.4 加法器
- **反相加法器**：$V_{out} = -R_f \left(\frac{V_1}{R_1} + \frac{V_2}{R_2} + \cdots + \frac{V_n}{R_n}\right)$
- **等值输入电阻时**：$V_{out} = -\frac{R_f}{R}(V_1 + V_2 + \cdots + V_n)$

**来源章节**：第8章 运算放大器

### 6.5 减法器（差分放大器）
- **输出电压**：$V_{out} = \frac{R_f}{R_1}(V_2 - V_1)$（当$R_1 = R_2$，$R_f = R_3$时）
- **差分增益**：$A_d = \frac{R_f}{R_1}$

**来源章节**：第8章 运算放大器

### 6.6 积分器和微分器
- **积分器**：$V_{out} = -\frac{1}{RC} \int V_{in} dt$
- **微分器**：$V_{out} = -RC \frac{dV_{in}}{dt}$

**来源章节**：第8章 运算放大器

---

## 7. 滤波器公式

### 7.1 一阶有源滤波器

#### 7.1.1 低通滤波器
- **传递函数**：$H(s) = \frac{A_v}{1 + sRC}$
- **截止频率**：$f_c = \frac{1}{2\pi RC}$
- **幅度响应**：$|H(j\omega)| = A_v \frac{1}{\sqrt{1 + (\omega RC)^2}}$
- **相位响应**：$\phi(\omega) = -\arctan(\omega RC)$

#### 7.1.2 高通滤波器
- **传递函数**：$H(s) = \frac{A_v sRC}{1 + sRC}$
- **截止频率**：$f_c = \frac{1}{2\pi RC}$
- **幅度响应**：$|H(j\omega)| = A_v \frac{\omega RC}{\sqrt{1 + (\omega RC)^2}}$
- **相位响应**：$\phi(\omega) = 90° - \arctan(\omega RC)$

**来源章节**：第9章 有源滤波器

### 7.2 二阶有源滤波器
- **标准形式**：$H(s) = \frac{K\omega_n^2}{s^2 + \frac{\omega_n}{Q}s + \omega_n^2}$
- **自然频率**：$\omega_n$
- **品质因数**：$Q$
- **增益常数**：$K$

**来源章节**：第9章 有源滤波器

### 7.3 巴特沃斯滤波器
- **二阶低通**：$H(s) = \frac{K\omega_c^2}{s^2 + \sqrt{2}\omega_c s + \omega_c^2}$
- **Q值**：$Q = \frac{1}{\sqrt{2}} \approx 0.707$
- **幅度响应**：$|H(j\omega)| = \frac{1}{\sqrt{1 + \left(\frac{\omega}{\omega_c}\right)^{2n}}}$

**来源章节**：第9章 有源滤波器

### 7.4 切比雪夫滤波器
- **幅度响应**：$|H(j\omega)| = \frac{1}{\sqrt{1 + \epsilon^2 T_n^2\left(\frac{\omega}{\omega_c}\right)}}$
- **Q值范围**：$Q = 0.5-10$

**来源章节**：第9章 有源滤波器

### 7.5 贝塞尔滤波器
- **二阶低通**：$H(s) = \frac{K\omega_c^2}{s^2 + \sqrt{3}\omega_c s + \omega_c^2}$
- **Q值**：$Q = \frac{1}{\sqrt{3}} \approx 0.577$
- **线性相位**：群延时在通带内近似为常数

**来源章节**：第9章 有源滤波器

### 7.6 品质因数和截止频率
- **品质因数定义**：$Q = \frac{\omega_0}{\Delta\omega}$
- **截止频率定义**：$|H(j\omega_c)| = \frac{|H(j0)|}{\sqrt{2}}$（低通），$|H(j\omega_c)| = \frac{|H(j\infty)|}{\sqrt{2}}$（高通）

**来源章节**：第9章 有源滤波器

---

## 8. 振荡器公式

### 8.1 振荡条件（巴克豪森准则）
- **幅度条件**：$|A(\omega) \beta(\omega)| \geq 1$
- **相位条件**：$\phi_A(\omega) + \phi_\beta(\omega) = 2n\pi$（$n = 0, 1, 2, \ldots$）

**来源章节**：第10章 振荡器

### 8.2 LC振荡器

#### 8.2.1 哈特莱振荡器
- **振荡频率**：$\omega_0 = \frac{1}{\sqrt{L_{eq}C}}$，其中$L_{eq} = L_1 + L_2 + 2M$
- **振荡条件**：$A_v \geq \frac{L_1}{L_2}$

#### 8.2.2 考比兹振荡器
- **振荡频率**：$\omega_0 = \frac{1}{\sqrt{L_{eq}C_{eq}}}$，其中$C_{eq} = \frac{C_1C_2}{C_1 + C_2}$
- **振荡条件**：$A_v \geq \frac{C_2}{C_1}$

#### 8.2.3 克拉普振荡器
- **振荡频率**：$\omega_0 = \frac{1}{\sqrt{L\left(C_3 + \frac{C_1C_2}{C_1 + C_2}\right)}}$
- **近似频率**：$\omega_0 \approx \frac{1}{\sqrt{LC_3}}$（当$C_3 \ll \frac{C_1C_2}{C_1 + C_2}$时）

**来源章节**：第10章 振荡器

### 8.3 RC振荡器

#### 8.3.1 文氏电桥振荡器
- **振荡频率**：$f_0 = \frac{1}{2\pi RC}$
- **反馈系数**：$\beta(\omega_0) = \frac{1}{3}$
- **振荡条件**：$A_v \geq 3$

#### 8.3.2 相移振荡器
- **振荡频率**：$f_0 = \frac{1}{2\pi\sqrt{6}RC}$
- **振荡条件**：$A_v \geq 29$

**来源章节**：第10章 振荡器

### 8.4 石英晶体振荡器
- **串联谐振频率**：$\omega_s = \frac{1}{\sqrt{L_qC_q}}$
- **并联谐振频率**：$\omega_p = \omega_s\sqrt{1 + \frac{C_q}{C_0}} \approx \omega_s\left(1 + \frac{C_q}{2C_0}\right)$
- **频率温度系数**：$\frac{\Delta f}{f_0} = a(\Delta T) + b(\Delta T)^2 + c(\Delta T)^3$

**来源章节**：第10章 振荡器

### 8.5 频率合成技术
- **锁相环基本方程**：$\theta_e(t) = \theta_i(t) - \frac{\theta_o(t)}{N}$
- **稳态频率关系**：$\omega_o = N \cdot \omega_{ref}$
- **频率分辨率**：$\Delta f_{min} = \frac{f_{ref}}{N_{max}}$

**来源章节**：第10章 振荡器

---

## 9. 稳压电源公式

### 9.1 线性稳压器

#### 9.1.1 基本关系
- **输出电压**：$V_{out} = V_{ref} \left(1 + \frac{R_1}{R_2}\right)$
- **调整管功耗**：$P_D = (V_{in} - V_{out}) \times I_{out}$
- **效率**：$\eta = \frac{V_{out}}{V_{in}}$

#### 9.1.2 稳压系数
- **绝对稳压系数**：$S_v = \frac{\Delta V_{out}/V_{out}}{\Delta V_{in}/V_{in}}$
- **相对稳压系数**：$S_v = \frac{\Delta V_{out}}{\Delta V_{in}} \times \frac{V_{in}}{V_{out}}$
- **近似关系**：$S_v \approx \frac{1}{\beta \times A_{OL}}$

#### 9.1.3 输出阻抗
- **直流输出阻抗**：$Z_{out} = \frac{R_{out}}{1 + A_{OL} \times \beta}$
- **交流输出阻抗**：$Z_{out}(j\omega) = \frac{R_{out}}{1 + A_{OL}(j\omega) \times \beta}$

**来源章节**：第11章 稳压电源

### 9.2 开关稳压器

#### 9.2.1 降压型（Buck）
- **占空比**：$D = \frac{T_{on}}{T_s}$
- **输出电压**：$V_{out} = D \times V_{in}$
- **纹波电流**：$\Delta I_L = \frac{(V_{in} - V_{out}) \times T_{on}}{L}$
- **纹波电压**：$\Delta V_{ripple} = \frac{\Delta I_L}{8 \times f_s \times C_{out}}$

#### 9.2.2 升压型（Boost）
- **输出电压**：$V_{out} = \frac{V_{in}}{1 - D}$
- **电感设计**：$L \geq \frac{V_{in} \times D}{f_s \times \Delta I_L}$
- **电容设计**：$C_{out} \geq \frac{I_{out} \times D}{f_s \times \Delta V_{ripple}}$

#### 9.2.3 反转型（Buck-Boost）
- **输出电压**：$V_{out} = -\frac{D}{1 - D} \times V_{in}$

#### 9.2.4 开关损耗
- **开关损耗**：$P_{switch} = \frac{1}{2} \times V_{ds} \times I_{ds} \times f_s \times (t_r + t_f)$
- **总效率**：$\eta = \frac{V_{out} \times I_{out}}{V_{in} \times I_{in} + P_{switch} + P_{gate} + P_{core}}$

**来源章节**：第11章 稳压电源

### 9.3 滤波电路
- **单电容滤波（半波）**：$V_{dc} = V_{peak} - \frac{I_{dc}}{4fC}$，$V_{ripple} = \frac{I_{dc}}{fC}$
- **单电容滤波（全波）**：$V_{dc} = V_{peak} - \frac{I_{dc}}{2fC}$，$V_{ripple} = \frac{I_{dc}}{2fC}$
- **LC滤波器谐振频率**：$f_0 = \frac{1}{2\pi\sqrt{LC}}$
- **LC滤波器品质因数**：$Q = \frac{\sqrt{L/C}}{R}$

**来源章节**：第11章 稳压电源

### 9.4 保护电路
- **电流检测**：$V_{sense} = I_{load} \times R_{sense}$
- **限流阈值**：$I_{limit} = \frac{V_{ref}}{R_{sense}}$
- **齐纳保护电压**：$V_{protection} = V_Z + I_Z \times R_{series}$
- **热敏电阻**：$R_T = R_0 \times e^{\beta(\frac{1}{T} - \frac{1}{T_0})}$

**来源章节**：第11章 稳压电源

---

## 10. 频率响应公式

### 10.1 频率响应基本概念
- **频率响应**：$G(j\omega) = G(s)|_{s=j\omega}$
- **复数形式**：$G(j\omega) = |G(j\omega)|e^{j\angle G(j\omega)}$
- **幅值和相位**：$G(j\omega) = A(\omega)e^{j\phi(\omega)}$

**来源章节**：第12章 频率响应和波特图

### 10.2 一阶系统频率响应

#### 10.2.1 一阶低通系统
- **传递函数**：$G(s) = \frac{K}{\tau s + 1}$
- **频率响应**：$G(j\omega) = \frac{K}{j\omega\tau + 1}$
- **幅频特性**：$|G(j\omega)| = \frac{K}{\sqrt{(\omega\tau)^2 + 1}}$
- **相频特性**：$\angle G(j\omega) = -\arctan(\omega\tau)$
- **截止频率**：$\omega_c = \frac{1}{\tau}$

#### 10.2.2 一阶高通系统
- **传递函数**：$G(s) = \frac{K\tau s}{\tau s + 1}$
- **频率响应**：$G(j\omega) = \frac{Kj\omega\tau}{j\omega\tau + 1}$
- **幅频特性**：$|G(j\omega)| = \frac{K\omega\tau}{\sqrt{(\omega\tau)^2 + 1}}$
- **相频特性**：$\angle G(j\omega) = 90° - \arctan(\omega\tau)$
- **截止频率**：$\omega_c = \frac{1}{\tau}$

**来源章节**：第12章 频率响应和波特图

### 10.3 二阶系统频率响应
- **标准传递函数**：$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$
- **幅频特性**：$|G(j\omega)| = \frac{\omega_n^2}{\sqrt{(\omega_n^2 - \omega^2)^2 + (2\zeta\omega_n\omega)^2}}$
- **相频特性**：$\angle G(j\omega) = -\arctan\left(\frac{2\zeta\omega_n\omega}{\omega_n^2 - \omega^2}\right)$
- **共振频率**：$\omega_r = \omega_n\sqrt{1 - 2\zeta^2}$
- **峰值增益**：$M_r = \frac{1}{2\zeta\sqrt{1-\zeta^2}}$

**来源章节**：第12章 频率响应和波特图

### 10.4 波特图绘制规则
- **常数项**：$20\log_{10}K$ dB
- **积分因子**：$-20$ dB/十倍频程，$-90°$相位
- **微分因子**：$+20$ dB/十倍频程，$+90°$相位
- **一阶因子**：在$\omega = \frac{1}{\tau}$处转折，$\pm 3$ dB修正
- **二阶因子**：在$\omega = \omega_n$处转折，根据$\zeta$修正

**来源章节**：第12章 频率响应和波特图

### 10.5 增益带宽积
- **定义**：$GBW = A_{v0} \times BW$
- **一阶系统**：$GBW = \frac{1}{2\pi\tau}$
- **频率关系**：$A_v(f) = \frac{GBW}{f}$
- **截止频率处**：$A_v(f_H) = \frac{GBW}{\sqrt{2}f_H}$

**来源章节**：第12章 频率响应和波特图

### 10.6 频率补偿
- **滞后补偿**：$G_c(s) = \frac{s + \omega_z}{s + \omega_p}$（$\omega_z < \omega_p$）
- **超前补偿**：$G_c(s) = \frac{s + \omega_p}{s + \omega_z}$（$\omega_p > \omega_z$）
- **滞后-超前补偿**：$G_c(s) = \frac{(s + \omega_{z1})(s + \omega_{z2})}{(s + \omega_{p1})(s + \omega_{p2})}$

**来源章节**：第12章 频率响应和波特图

---

## 11. 差分放大器公式

### 11.1 差模和共模信号
- **差模信号**：$V_{dm} = V_{in1} - V_{in2}$
- **共模信号**：$V_{cm} = \frac{V_{in1} + V_{in2}}{2}$
- **信号分解**：$V_{in1} = V_{cm} + \frac{V_{dm}}{2}$，$V_{in2} = V_{cm} - \frac{V_{dm}}{2}$

**来源章节**：第6章 差分放大电路

### 11.2 共模抑制比（CMRR）
- **定义**：$CMRR = \frac{A_{dm}}{A_{cm}}$
- **分贝表示**：$CMRR_{dB} = 20\log_{10}\left(\frac{A_{dm}}{A_{cm}}\right)$
- **差模增益**：$A_{dm} = -\frac{\beta R_C}{r_{\pi} + (1+\beta)R_E} \approx -\frac{R_C}{r_e}$
- **共模增益**：$A_{cm} = -\frac{R_C}{2R_E(1+\beta) + r_{\pi}} \approx -\frac{R_C}{2\beta R_E}$
- **CMRR计算**：$CMRR_{dB} = 20\log_{10}\left(\frac{2\beta R_E}{r_e}\right)$

**来源章节**：第6章 差分放大电路

### 11.3 失调电压和失调电流
- **输入失调电压**：$V_{OS} = V_{BE1} - V_{BE2}$
- **输入失调电流**：$I_{OS} = |I_{B1} - I_{B2}|$
- **输出失调电压**：$V_{out,OS} = A_{dm}V_{OS} + A_{cm}I_{OS}R_S$

**来源章节**：第6章 差分放大电路

### 11.4 传输特性
- **差模跨导**：$g_m = \frac{I_{EE}}{4V_T}$
- **差模输入电阻**：$r_{id} = 2r_{\pi}$
- **共模输入电阻**：$r_{ic} = \frac{r_{\pi} + (1+\beta)R_E}{2}$

**来源章节**：第6章 差分放大电路

### 11.5 恒流源
- **镜像恒流源**：$I_{out} \approx I_{ref} = \frac{V_{cc} - V_{BE3}}{R}$
- **Widlar恒流源**：$I_{out} = \frac{V_T}{R_E}\ln\left(\frac{I_{ref}}{I_{out}}\right)$
- **Wilson恒流源**：$I_{out} = I_{ref}\left(1 - \frac{2}{\beta^2 + 2\beta + 2}\right)$

**来源章节**：第6章 差分放大电路

---

## 附录：常用物理常数

- **玻尔兹曼常数**：$k = 1.38 \times 10^{-23}$ J/K
- **电子电荷**：$q = 1.6 \times 10^{-19}$ C
- **热电压**：$V_T = \frac{kT}{q} \approx 26$ mV（@ 300K）
- **本征载流子浓度（硅）**：$n_i \approx 1.5 \times 10^{10}$ cm⁻³（@ 300K）

---

**文档说明**：
1. 所有公式均使用LaTeX语法表示
2. 每个公式都标注了来源章节
3. 公式按章节分类，便于查阅
4. 建议结合具体章节内容深入理解公式的物理意义

**使用建议**：
- 熟记基础公式，理解物理概念
- 掌握公式的推导过程和应用条件
- 通过实际电路分析巩固公式应用
- 注意公式的近似条件和适用范围

---

*本公式汇总基于电子电路设计课程内容整理，供学习参考使用。*