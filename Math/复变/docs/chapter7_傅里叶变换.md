# 第7章 傅里叶变换

## 目录
1. [傅里叶级数](#1-傅里叶级数)
2. [傅里叶变换的定义与性质](#2-傅里叶变换的定义与性质)
3. [傅里叶变换的应用](#3-傅里叶变换的应用)
4. [快速傅里叶变换](#4-快速傅里叶变换)

---

## 1. 傅里叶级数

### 1.1 三角级数形式

**定义（周期函数的三角级数展开）**：

设函数 $f(x)$ 在区间 $[-\pi, \pi]$ 上可积，则它可以展开为三角级数：

$$f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty} (a_n \cos nx + b_n \sin nx)$$

其中傅里叶系数为：

$$a_n = \frac{1}{\pi} \int_{-\pi}^{\pi} f(x) \cos nx \, dx \quad (n = 0, 1, 2, \ldots)$$

$$b_n = \frac{1}{\pi} \int_{-\pi}^{\pi} f(x) \sin nx \, dx \quad (n = 1, 2, 3, \ldots)$$

### 1.2 复数形式

**复数形式的傅里叶级数**：

利用欧拉公式 $e^{inx} = \cos nx + i \sin nx$，三角级数可以写成复数形式：

$$f(x) = \sum_{n=-\infty}^{\infty} c_n e^{inx}$$

其中复数傅里叶系数为：

$$c_n = \frac{1}{2\pi} \int_{-\pi}^{\pi} f(x) e^{-inx} \, dx \quad (n = 0, \pm1, \pm2, \ldots)$$

**复数形式与三角形式的关系**：

$$c_0 = \frac{a_0}{2}, \quad c_n = \frac{a_n - ib_n}{2}, \quad c_{-n} = \frac{a_n + ib_n}{2} \quad (n = 1, 2, 3, \ldots)$$

### 1.3 收敛性定理

<details>
<summary><strong>定理7.1 狄利克雷收敛定理</strong></summary>

**定理内容**：
如果函数 $f(x)$ 在区间 $[-\pi, \pi]$ 上满足：
1. 连续或只有有限个第一类间断点
2. 只有有限个极值点

则 $f(x)$ 的傅里叶级数在每一点 $x$ 处收敛，且：
- 在连续点处，级数和等于 $f(x)$
- 在间断点处，级数和等于 $\frac{f(x^+) + f(x^-)}{2}$

**证明思路**：
利用三角函数系的正交性和贝塞尔不等式，结合部分和的积分表示，通过狄利克雷核的性质进行证明。
</details>

<details>
<summary><strong>定理7.2 帕塞瓦尔等式</strong></summary>

**定理内容**：
如果 $f(x)$ 在 $[-\pi, \pi]$ 上平方可积，则：

$$\frac{1}{\pi} \int_{-\pi}^{\pi} [f(x)]^2 \, dx = \frac{a_0^2}{2} + \sum_{n=1}^{\infty} (a_n^2 + b_n^2)$$

或等价地：

$$\frac{1}{2\pi} \int_{-\pi}^{\pi} [f(x)]^2 \, dx = \sum_{n=-\infty}^{\infty} |c_n|^2$$

**证明思路**：
利用傅里叶级数的部分和与原函数的平方误差，通过正交性计算内积并取极限。
</details>

### 1.4 常用函数的傅里叶级数

| 函数 | 傅里叶级数 | 收敛域 |
|------|------------|--------|
| $f(x) = x$ ($-\pi < x < \pi$) | $2\sum_{n=1}^{\infty} \frac{(-1)^{n+1}}{n} \sin nx$ | $(-\pi, \pi)$ |
| $f(x) = x^2$ ($-\pi \leq x \leq \pi$) | $\frac{\pi^2}{3} + 4\sum_{n=1}^{\infty} \frac{(-1)^n}{n^2} \cos nx$ | $[-\pi, \pi]$ |
| $f(x) = \begin{cases} 1, & 0 < x < \pi \\ -1, & -\pi < x < 0 \end{cases}$ | $\frac{4}{\pi} \sum_{n=1,3,5,\ldots}^{\infty} \frac{1}{n} \sin nx$ | $(-\pi, 0) \cup (0, \pi)$ |

---

## 2. 傅里叶变换的定义与性质

### 2.1 傅里叶变换的定义

**定义（傅里叶变换）**：

设函数 $f(t)$ 在 $(-\infty, +\infty)$ 上绝对可积，即 $\int_{-\infty}^{+\infty} |f(t)| \, dt < \infty$，则 $f(t)$ 的傅里叶变换定义为：

$$\mathcal{F}[f(t)] = F(\omega) = \int_{-\infty}^{+\infty} f(t) e^{-i\omega t} \, dt$$

其逆变换为：

$$\mathcal{F}^{-1}[F(\omega)] = f(t) = \frac{1}{2\pi} \int_{-\infty}^{+\infty} F(\omega) e^{i\omega t} \, d\omega$$

其中：
- $f(t)$ 称为原函数或时域函数
- $F(\omega)$ 称为像函数或频域函数
- $\omega$ 为角频率

### 2.2 傅里叶变换的基本性质

| 性质 | 时域 | 频域 |
|------|------|------|
| **线性** | $af(t) + bg(t)$ | $aF(\omega) + bG(\omega)$ |
| **时移** | $f(t-t_0)$ | $F(\omega)e^{-i\omega t_0}$ |
| **频移** | $f(t)e^{i\omega_0 t}$ | $F(\omega-\omega_0)$ |
| **尺度变换** | $f(at)$ | $\frac{1}{\|a\|}F(\frac{\omega}{a})$ |
| **微分** | $f'(t)$ | $i\omega F(\omega)$ |
| **积分** | $\int_{-\infty}^{t} f(\tau)d\tau$ | $\frac{F(\omega)}{i\omega} + \pi F(0)\delta(\omega)$ |
| **共轭** | $\overline{f(t)}$ | $\overline{F(-\omega)}$ |
| **时间反转** | $f(-t)$ | $F(-\omega)$ |

### 2.3 常用变换对

| 原函数 $f(t)$ | 傅里叶变换 $F(\omega)$ |
|---------------|------------------------|
| $\delta(t)$ | $1$ |
| $1$ | $2\pi\delta(\omega)$ |
| $e^{-at}u(t)$ $(a>0)$ | $\frac{1}{a+i\omega}$ |
| $e^{-a\|t\|}$ $(a>0)$ | $\frac{2a}{a^2+\omega^2}$ |
| $\text{rect}(t)$ | $\text{sinc}(\frac{\omega}{2})$ |
| $\text{sinc}(t)$ | $\pi \text{rect}(\frac{\omega}{2})$ |
| $e^{-\pi t^2}$ | $e^{-\pi \omega^2}$ |
| $\cos(\omega_0 t)$ | $\pi[\delta(\omega-\omega_0) + \delta(\omega+\omega_0)]$ |
| $\sin(\omega_0 t)$ | $i\pi[\delta(\omega+\omega_0) - \delta(\omega-\omega_0)]$ |

其中：
- $\text{rect}(t) = \begin{cases} 1, & |t| < \frac{1}{2} \\ 0, & |t| > \frac{1}{2} \end{cases}$
- $\text{sinc}(t) = \frac{\sin(\pi t)}{\pi t}$

### 2.4 卷积定理

<details>
<summary><strong>定理7.3 时域卷积定理</strong></summary>

**定理内容**：
如果 $f(t)$ 和 $g(t)$ 的傅里叶变换分别为 $F(\omega)$ 和 $G(\omega)$，则：

$$\mathcal{F}[f(t) * g(t)] = F(\omega) \cdot G(\omega)$$

其中卷积定义为：
$$(f * g)(t) = \int_{-\infty}^{+\infty} f(\tau)g(t-\tau) \, d\tau$$

**证明**：
$$\begin{align*}
\mathcal{F}[f * g] &= \int_{-\infty}^{+\infty} \left[\int_{-\infty}^{+\infty} f(\tau)g(t-\tau) \, d\tau\right] e^{-i\omega t} dt \\
&= \int_{-\infty}^{+\infty} f(\tau) \left[\int_{-\infty}^{+\infty} g(t-\tau) e^{-i\omega t} dt\right] d\tau \\
&= \int_{-\infty}^{+\infty} f(\tau) e^{-i\omega \tau} \left[\int_{-\infty}^{+\infty} g(u) e^{-i\omega u} du\right] d\tau \\
&= F(\omega) \cdot G(\omega)
\end{align*}$$
</details>

<details>
<summary><strong>定理7.4 频域卷积定理</strong></summary>

**定理内容**：
$$\mathcal{F}[f(t) \cdot g(t)] = \frac{1}{2\pi} F(\omega) * G(\omega)$$

其中频域卷积定义为：
$$(F * G)(\omega) = \int_{-\infty}^{+\infty} F(\Omega)G(\omega-\Omega) \, d\Omega$$

**证明**：
利用傅里叶变换的对偶性和时域卷积定理。
</details>

### 2.5 帕塞瓦尔定理

<details>
<summary><strong>定理7.5 帕塞瓦尔定理</strong></summary>

**定理内容**：
如果 $f(t)$ 和 $g(t)$ 的傅里叶变换分别为 $F(\omega)$ 和 $G(\omega)$，则：

$$\int_{-\infty}^{+\infty} f(t)\overline{g(t)} \, dt = \frac{1}{2\pi} \int_{-\infty}^{+\infty} F(\omega)\overline{G(\omega)} \, d\omega$$

特别地，当 $f(t) = g(t)$ 时：

$$\int_{-\infty}^{+\infty} |f(t)|^2 \, dt = \frac{1}{2\pi} \int_{-\infty}^{+\infty} |F(\omega)|^2 \, d\omega$$

**物理意义**：时域能量等于频域能量（相差因子 $2\pi$）
</details>

---

## 3. 傅里叶变换的应用

### 3.1 信号处理中的应用

#### 3.1.1 频谱分析

![傅里叶变换频谱分析](imgs/fourier-transform-frequency-spectrum-analysis-diagram.jpg)
*图7-1: 傅里叶变换的时域-频域对应关系*

**定义（频谱）**：
信号 $f(t)$ 的频谱定义为 $|F(\omega)|$，相位谱定义为 $\arg F(\omega)$。

**功率谱密度**：
$$S(\omega) = \frac{|F(\omega)|^2}{2\pi}$$

**频谱分析的意义：**
- **时域分析**：信号随时间的变化
- **频域分析**：信号包含的频率成分
- **频谱图**：显示各频率分量的幅度和相位信息

#### 3.1.2 滤波

**理想低通滤波器**：
$$H(\omega) = \begin{cases}
1, & |\omega| < \omega_c \\
0, & |\omega| > \omega_c
\end{cases}$$

**滤波过程**：
$$Y(\omega) = H(\omega)X(\omega)$$

#### 3.1.3 采样定理

<details>
<summary><strong>定理7.6 奈奎斯特采样定理</strong></summary>

**定理内容**：
如果信号 $f(t)$ 的频谱 $F(\omega)$ 满足 $F(\omega) = 0$ 对于 $|\omega| > \omega_m$，那么当采样频率 $\omega_s > 2\omega_m$ 时，信号可以完全从其采样值恢复。

**重建公式**：
$$f(t) = \sum_{n=-\infty}^{\infty} f(nT) \cdot \text{sinc}\left(\frac{t-nT}{T}\right)$$

其中 $T = \frac{2\pi}{\omega_s}$ 为采样周期。
</details>

### 3.2 偏微分方程求解中的应用

#### 3.2.1 热传导方程

**问题**：求解热传导方程
$$\frac{\partial u}{\partial t} = a^2 \frac{\partial^2 u}{\partial x^2}, \quad x \in \mathbb{R}, t > 0$$

**解法**：
1. 对 $x$ 进行傅里叶变换：$U(\omega, t) = \mathcal{F}[u(x, t)]$
2. 变换后方程：$\frac{\partial U}{\partial t} = -a^2 \omega^2 U$
3. 解为：$U(\omega, t) = U(\omega, 0)e^{-a^2\omega^2 t}$
4. 逆变换得到解

**解**：
$$u(x, t) = \frac{1}{2a\sqrt{\pi t}} \int_{-\infty}^{+\infty} u(\xi, 0) e^{-\frac{(x-\xi)^2}{4a^2 t}} \, d\xi$$

#### 3.2.2 波动方程

**问题**：求解一维波动方程
$$\frac{\partial^2 u}{\partial t^2} = c^2 \frac{\partial^2 u}{\partial x^2}, \quad x \in \mathbb{R}, t > 0$$

**解法**：
1. 对 $x$ 进行傅里叶变换
2. 得到常微分方程：$\frac{\partial^2 U}{\partial t^2} + c^2\omega^2 U = 0$
3. 解为：$U(\omega, t) = A(\omega)e^{i c \omega t} + B(\omega)e^{-i c \omega t}$

#### 3.2.3 拉普拉斯方程

**问题**：求解拉普拉斯方程的边值问题
$$\nabla^2 u = 0, \quad (x, y) \in \mathbb{R}^2_+$$

**解法**：
1. 对 $x$ 进行傅里叶变换
2. 得到常微分方程：$\frac{d^2 U}{dy^2} - \omega^2 U = 0$
3. 解为：$U(\omega, y) = A(\omega)e^{|\omega|y} + B(\omega)e^{-|\omega|y}$

### 3.3 其他应用

#### 3.3.1 图像处理
- 图像增强和去噪
- 图像压缩（JPEG）
- 图像滤波

#### 3.3.2 通信系统
- 调制解调
- 信道均衡
- 频分复用

#### 3.3.3 量子力学
- 薛定谔方程求解
- 动量空间波函数
- 不确定性原理

---

## 4. 快速傅里叶变换（FFT）

### 4.1 FFT算法原理

**问题背景**：
直接计算 $N$ 点离散傅里叶变换（DFT）需要 $O(N^2)$ 次运算，当 $N$ 很大时计算量巨大。

**DFT定义**：
$$X(k) = \sum_{n=0}^{N-1} x(n) e^{-i\frac{2\pi}{N}kn}, \quad k = 0, 1, \ldots, N-1$$

### 4.2 基2 FFT算法

**算法原理**：
将 $N$ 点DFT分解为两个 $N/2$ 点DFT，利用旋转因子的周期性。

**分解过程**：
$$X(k) = \sum_{n=0}^{N-1} x(n) W_N^{kn} = \sum_{n=0}^{N/2-1} x(n) W_N^{kn} + \sum_{n=N/2}^{N-1} x(n) W_N^{kn}$$

$$= \sum_{n=0}^{N/2-1} x(n) W_N^{kn} + \sum_{n=0}^{N/2-1} x(n+N/2) W_N^{k(n+N/2)}$$

$$= \sum_{n=0}^{N/2-1} [x(n) + x(n+N/2)W_N^{kN/2}] W_N^{kn}$$

其中 $W_N^{kN/2} = (-1)^k$，所以：

$$X(k) = \sum_{n=0}^{N/2-1} [x(n) + (-1)^k x(n+N/2)] W_N^{kn}$$

令：
- $x_1(n) = x(n) + x(n+N/2)$
- $x_2(n) = [x(n) - x(n+N/2)]W_N^{kn}$

则：
$$X(k) = \sum_{n=0}^{N/2-1} [x_1(n) + x_2(n)] W_N^{kn}$$

### 4.3 FFT算法流程

**蝶形运算**：
```
     x(n) --------+-------- x_1(n)
                  |
                  |  (-1)^k
                  |
     x(n+N/2) ----+-------- x_2(n)
```

**算法步骤**：
1. **分解**：将输入序列按奇偶位置重新排列
2. **计算**：进行 $\log_2 N$ 级蝶形运算
3. **合成**：得到最终的频域结果

### 4.4 FFT复杂度分析

**计算复杂度**：
- 直接DFT：$O(N^2)$ 次复数乘法
- FFT：$O(N \log_2 N)$ 次复数乘法

**加速比**：
$$\text{加速比} = \frac{N^2}{N \log_2 N} = \frac{N}{\log_2 N}$$

例如，当 $N = 1024$ 时，加速比约为 $\frac{1024}{10} = 102.4$

### 4.5 FFT的应用

| 应用领域 | 具体应用 |
|----------|----------|
| **数字信号处理** | 频谱分析、滤波器设计、信号检测 |
| **图像处理** | 图像压缩、图像滤波、特征提取 |
| **通信系统** | OFDM调制、信道估计、频偏校正 |
| **雷达系统** | 目标检测、速度估计、波形设计 |
| **音频处理** | 音乐分析、语音识别、噪声消除 |

### 4.6 实现注意事项

1. **输入长度**：通常要求 $N = 2^m$，如果不是需要补零
2. **数值稳定性**：注意浮点运算的精度问题
3. **内存管理**：合理安排数据存储顺序
4. **并行化**：利用多核处理器进行并行计算

---

## 小结

傅里叶变换是现代数学和工程中的重要工具，具有以下特点：

1. **理论完备性**：从傅里叶级数到傅里叶变换，形成了完整的理论体系
2. **应用广泛性**：在信号处理、偏微分方程求解、图像处理等领域有重要应用
3. **计算高效性**：FFT算法的出现使得大规模计算成为可能
4. **物理意义明确**：时域和频域的对应关系直观清晰

掌握傅里叶变换的理论和方法，对于深入理解现代科学技术具有重要意义。

---

## 参考文献

1. 奥里弗·亥维赛. 《傅里叶变换理论》
2. 罗纳德·N·布拉斯威尔. 《傅里叶变换及其应用》
3. 阿兰·V·奥本海姆. 《信号与系统》
4. 詹姆斯·W·贾斯特. 《数字信号处理：原理与应用》

---

*注：本章内容为傅里叶变换的入门教程，深入学习需要参考更多专业文献和实际应用案例。*