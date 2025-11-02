# 第九章 Z变换

## 9.1 Z变换的定义

### 9.1.1 Z变换的定义

对于离散时间序列 $x[n]$，其**双边Z变换**定义为：

$$X(z) = \mathcal{Z}\{x[n]\} = \sum_{n=-\infty}^{\infty} x[n]z^{-n}$$

其中 $z$ 是复变量，通常表示为 $z = re^{j\omega}$。

**单边Z变换**定义为：

$$X(z) = \mathcal{Z}\{x[n]\} = \sum_{n=0}^{\infty} x[n]z^{-n}$$

### 9.1.2 收敛域（ROC）

![Z变换收敛域](imgs/z-transform-sequences-poles-region-of-convergence-diagram.jpg)
*图9-1: Z变换的收敛域(ROC)和零极点图*

Z变换的**收敛域**是使无穷级数绝对收敛的 $z$ 值集合：

$$ROC = \{z : \sum_{n=-\infty}^{\infty} |x[n]z^{-n}| < \infty\}$$

#### 收敛域的性质：

1. **ROC是环状区域**：ROC在z平面上是一个环形区域（双边Z变换）或圆外/圆内区域（单边Z变换）
2. **ROC内不包含极点**：ROC内不能包含 $X(z)$ 的任何极点
3. **有限长序列**：ROC是整个z平面（除去可能的 $z=0$ 或 $z=\infty$）
4. **右边序列**：ROC是某个圆的外部区域
5. **左边序列**：ROC是某个圆的内部区域
6. **双边序列**：ROC是环形区域

**收敛域的图形表示：**
- **极点位置**：用×标记
- **零点位置**：用○标记  
- **ROC区域**：用阴影区域表示
- **单位圆**：$|z| = 1$（系统稳定性判断）

### 9.1.3 存在条件

Z变换存在的充分必要条件是：

$$\sum_{n=-\infty}^{\infty} |x[n]z^{-n}| < \infty$$

对于右边序列 $x[n] = 0, n < n_0$：

$$\sum_{n=n_0}^{\infty} |x[n]||z|^{-n} < \infty$$

这要求 $|z| > \lim_{n \to \infty} \sqrt[n]{|x[n]|}$

## 9.2 Z变换的性质

### 9.2.1 线性性质

如果：
$$X_1(z) = \mathcal{Z}\{x_1[n]\}, \quad ROC = R_1$$
$$X_2(z) = \mathcal{Z}\{x_2[n]\}, \quad ROC = R_2$$

则：
$$\mathcal{Z}\{a x_1[n] + b x_2[n]\} = a X_1(z) + b X_2(z)$$

ROC是 $R_1 \cap R_2$（可能需要去掉极点）

<details>
<summary><strong>证明：</strong></summary>

$$\mathcal{Z}\{a x_1[n] + b x_2[n]\} = \sum_{n=-\infty}^{\infty} [a x_1[n] + b x_2[n]]z^{-n}$$
$$= a \sum_{n=-\infty}^{\infty} x_1[n]z^{-n} + b \sum_{n=-\infty}^{\infty} x_2[n]z^{-n}$$
$$= a X_1(z) + b X_2(z)$$

证毕。
</details>

### 9.2.2 移位性质

#### 右移位（延迟）：
$$\mathcal{Z}\{x[n-k]\} = z^{-k}X(z), \quad k > 0$$

ROC与 $X(z)$ 相同，可能增加 $z=0$（若 $k > 0$）或 $z=\infty$（若 $k < 0$）

#### 左移位（超前）：
$$\mathcal{Z}\{x[n+k]\} = z^{k}X(z) - \sum_{m=0}^{k-1} x[m]z^{k-m}, \quad k > 0$$

<details>
<summary><strong>证明（右移位）：</strong></summary>

$$\mathcal{Z}\{x[n-k]\} = \sum_{n=-\infty}^{\infty} x[n-k]z^{-n}$$
令 $m = n-k$，则：
$$= \sum_{m=-\infty}^{\infty} x[m]z^{-(m+k)} = z^{-k} \sum_{m=-\infty}^{\infty} x[m]z^{-m} = z^{-k}X(z)$$

证毕。
</details>

### 9.2.3 尺度变换性质

如果 $X(z) = \mathcal{Z}\{x[n]\}$，ROC为 $R$，则：

$$\mathcal{Z}\{a^n x[n]\} = X\left(\frac{z}{a}\right)$$

ROC为 $|a|R = \{z : \frac{z}{a} \in R\}$

### 9.2.4 时间反转性质

$$\mathcal{Z}\{x[-n]\} = X\left(\frac{1}{z}\right)$$

ROC为 $\{z : \frac{1}{z} \in R\}$，即 $R$ 的倒数变换

### 9.2.5 差分性质

#### 一阶后向差分：
$$\mathcal{Z}\{\nabla x[n]\} = \mathcal{Z}\{x[n] - x[n-1]\} = (1 - z^{-1})X(z)$$

#### 一阶前向差分：
$$\mathcal{Z}\{\Delta x[n]\} = \mathcal{Z}\{x[n+1] - x[n]\} = (z - 1)X(z) - z x[0]$$

### 9.2.6 卷积定理

如果：
$$y[n] = x[n] * h[n] = \sum_{k=-\infty}^{\infty} x[k]h[n-k]$$

则：
$$Y(z) = X(z)H(z)$$

ROC是 $R_x \cap R_h$（可能去掉极点）

<details>
<summary><strong>证明：</strong></summary>

$$Y(z) = \mathcal{Z}\{x[n] * h[n]\} = \sum_{n=-\infty}^{\infty} \left[\sum_{k=-\infty}^{\infty} x[k]h[n-k]\right]z^{-n}$$
$$= \sum_{k=-\infty}^{\infty} x[k] \sum_{n=-\infty}^{\infty} h[n-k]z^{-n}$$
令 $m = n-k$，则：
$$= \sum_{k=-\infty}^{\infty} x[k]z^{-k} \sum_{m=-\infty}^{\infty} h[m]z^{-m} = X(z)H(z)$$

证毕。
</details>

### 9.2.7 初值定理

对于右边序列（$x[n] = 0, n < 0$）：
$$x[0] = \lim_{z \to \infty} X(z)$$

如果 $x[n]$ 是因果序列，且 $x[1], x[2], \ldots$ 存在：
$$x[1] = \lim_{z \to \infty} [z(X(z) - x[0])]$$

### 9.2.8 终值定理

如果 $X(z)$ 的所有极点都在单位圆内（$|z| = 1$ 内），或在 $z = 1$ 处只有一阶极点，则：

$$\lim_{n \to \infty} x[n] = \lim_{z \to 1} (z-1)X(z)$$

<details>
<summary><strong>证明：</strong></summary>

考虑 $(z-1)X(z)$ 的留数：
$$(z-1)X(z) = \sum_{k} \text{Res}[X(z), p_k] + \text{Res}[X(z), 1]$$

其中 $p_k$ 是除 $z=1$ 外的所有极点。

当 $z \to 1$ 时：
$$(z-1)X(z) \to \text{Res}[X(z), 1] = \sum_{n=0}^{\infty} x[n] = \lim_{n \to \infty} \sum_{k=0}^{n} x[k]$$

由Z变换定义和终值定理的条件可得：
$$\lim_{n \to \infty} x[n] = \lim_{z \to 1} (z-1)X(z)$$

证毕。
</details>

## 9.3 常用Z变换对

| 序列 $x[n]$ | Z变换 $X(z)$ | ROC |
|-------------|-------------|-----|
| $\delta[n]$ | $1$ | 整个z平面 |
| $\delta[n-k]$ | $z^{-k}$ | $z \neq 0$（若 $k > 0$）|
| $u[n]$ | $\frac{1}{1-z^{-1}}$ | $\|z\| > 1$ |
| $-u[-n-1]$ | $\frac{1}{1-z^{-1}}$ | $\|z\| < 1$ |
| $a^n u[n]$ | $\frac{1}{1-az^{-1}}$ | $\|z\| > \|a\|$ |
| $-a^n u[-n-1]$ | $\frac{1}{1-az^{-1}}$ | $\|z\| < \|a\|$ |
| $n a^n u[n]$ | $\frac{az^{-1}}{(1-az^{-1})^2}$ | $\|z\| > \|a\|$ |
| $\cos(\omega_0 n) u[n]$ | $\frac{1 - \cos(\omega_0)z^{-1}}{1 - 2\cos(\omega_0)z^{-1} + z^{-2}}$ | $\|z\| > 1$ |
| $\sin(\omega_0 n) u[n]$ | $\frac{\sin(\omega_0)z^{-1}}{1 - 2\cos(\omega_0)z^{-1} + z^{-2}}$ | $\|z\| > 1$ |

## 9.4 Z逆变换

Z逆变换定义为：
$$x[n] = \mathcal{Z}^{-1}\{X(z)\} = \frac{1}{2\pi j} \oint_C X(z)z^{n-1}dz$$

其中 $C$ 是包围ROC的闭合积分路径。

### 9.4.1 部分分式展开法

当 $X(z)$ 是有理函数时，可表示为：
$$X(z) = \frac{N(z)}{D(z)} = \frac{b_m z^m + b_{m-1}z^{m-1} + \cdots + b_0}{a_n z^n + a_{n-1}z^{n-1} + \cdots + a_0}$$

**步骤：**
1. 将 $X(z)$ 表示为 $z^{-1}$ 的多项式比
2. 进行部分分式展开
3. 求每一项的逆Z变换

**示例：**
$$X(z) = \frac{1}{(1-z^{-1})(1-2z^{-1})}$$

展开为：
$$X(z) = \frac{A}{1-z^{-1}} + \frac{B}{1-2z^{-1}}$$

求得：$A = -1$，$B = 2$

$$X(z) = -\frac{1}{1-z^{-1}} + \frac{2}{1-2z^{-1}}$$

逆变换：
$$x[n] = -u[n] + 2 \cdot 2^n u[n] = (-1 + 2^{n+1})u[n]$$

### 9.4.2 幂级数展开法

将 $X(z)$ 展开为 $z^{-1}$ 的幂级数：
$$X(z) = \sum_{n=-\infty}^{\infty} c_n z^{-n}$$

则 $x[n] = c_n$

**示例：**
$$X(z) = \frac{1}{1-z^{-1}} = \sum_{n=0}^{\infty} z^{-n}$$

所以 $x[n] = u[n]$

### 9.4.3 留数法

根据留数定理：
$$x[n] = \sum_{k} \text{Res}[X(z)z^{n-1}, p_k]$$

其中 $p_k$ 是被积函数在ROC内的极点。

**一阶极点留数：**
$$\text{Res}[F(z), p_k] = \lim_{z \to p_k} (z-p_k)F(z)$$

**m阶极点留数：**
$$\text{Res}[F(z), p_k] = \frac{1}{(m-1)!} \lim_{z \to p_k} \frac{d^{m-1}}{dz^{m-1}}[(z-p_k)^m F(z)]$$

## 9.5 Z变换在离散系统中的应用

### 9.5.1 差分方程求解

考虑线性常系数差分方程：
$$\sum_{k=0}^{N} a_k y[n-k] = \sum_{m=0}^{M} b_m x[n-m]$$

**求解步骤：**
1. 对差分方程两边进行Z变换
2. 利用移位性质和线性性质
3. 解出 $Y(z)$
4. 进行Z逆变换得到 $y[n]$

**示例：**
求解 $y[n] - 0.5y[n-1] = x[n]$，其中 $x[n] = u[n]$，$y[-1] = 0$

**解：**
1. Z变换：
$$Y(z) - 0.5z^{-1}Y(z) = X(z)$$

2. 解出 $Y(z)$：
$$Y(z) = \frac{X(z)}{1-0.5z^{-1}}$$

3. $X(z) = \frac{1}{1-z^{-1}}$，代入：
$$Y(z) = \frac{1}{(1-z^{-1})(1-0.5z^{-1})}$$

4. 部分分式展开：
$$Y(z) = \frac{2}{1-z^{-1}} - \frac{1}{1-0.5z^{-1}}$$

5. 逆变换：
$$y[n] = (2 - 0.5^n)u[n]$$

### 9.5.2 系统函数与频率响应

**系统函数定义为：**
$$H(z) = \frac{Y(z)}{X(z)} = \frac{\sum_{k=0}^{M} b_k z^{-k}}{\sum_{k=0}^{N} a_k z^{-k}}$$

**频率响应：**
$$H(e^{j\omega}) = H(z)|_{z=e^{j\omega}} = \frac{\sum_{k=0}^{M} b_k e^{-jk\omega}}{\sum_{k=0}^{N} a_k e^{-jk\omega}}$$

### 9.5.3 数字滤波器设计

#### 9.5.3.1 IIR滤波器设计

**巴特沃斯低通滤波器：**
$$|H(e^{j\omega})|^2 = \frac{1}{1 + (\omega_c/\omega)^{2N}}$$

其中 $N$ 是滤波器阶数，$\omega_c$ 是截止频率。

**双线性变换法：**
$$s = \frac{2}{T} \frac{1-z^{-1}}{1+z^{-1}}$$

将模拟滤波器 $H_a(s)$ 转换为数字滤波器 $H(z)$：
$$H(z) = H_a\left(\frac{2}{T} \frac{1-z^{-1}}{1+z^{-1}}\right)$$

#### 9.5.3.2 FIR滤波器设计

**窗函数法：**
理想频率响应 $H_d(e^{j\omega})$ 的单位脉冲响应：
$$h_d[n] = \frac{1}{2\pi} \int_{-\pi}^{\pi} H_d(e^{j\omega})e^{j\omega n}d\omega$$

实际滤波器：
$$h[n] = h_d[n] \cdot w[n]$$

其中 $w[n]$ 是窗函数。

**常用窗函数：**

| 窗函数 | 表达式 | 主瓣宽度 | 旁瓣衰减 |
|--------|--------|----------|----------|
| 矩形窗 | $w[n] = 1$ | $4\pi/N$ | -13dB |
| 汉宁窗 | $w[n] = 0.5(1-\cos(2\pi n/(N-1)))$ | $8\pi/N$ | -31dB |
| 汉明窗 | $w[n] = 0.54-0.46\cos(2\pi n/(N-1))$ | $8\pi/N$ | -41dB |
| 布莱克曼窗 | $w[n] = 0.42-0.5\cos(2\pi n/(N-1)) + 0.08\cos(4\pi n/(N-1))$ | $12\pi/N$ | -58dB |

### 9.5.4 系统稳定性分析

**稳定性条件：**
- 连续系统：所有极点位于左半s平面
- 离散系统：所有极点位于单位圆内（$|z| < 1$）

**BIBO稳定性：**
系统是BIBO稳定的当且仅当：
$$\sum_{n=-\infty}^{\infty} |h[n]| < \infty$$

在Z域中，这等价于ROC包含单位圆 $|z| = 1$。

### 9.5.5 状态空间分析

**状态方程：**
$$\begin{cases}
\mathbf{x}[n+1] = \mathbf{A}\mathbf{x}[n] + \mathbf{B}\mathbf{u}[n] \\
\mathbf{y}[n] = \mathbf{C}\mathbf{x}[n] + \mathbf{D}\mathbf{u}[n]
\end{cases}$$

**系统矩阵：**
$$\mathbf{H}(z) = \mathbf{C}(z\mathbf{I} - \mathbf{A})^{-1}\mathbf{B} + \mathbf{D}$$

**特征多项式：**
$$\det(z\mathbf{I} - \mathbf{A}) = 0$$

系统稳定的条件是所有特征值位于单位圆内。

## 9.6 Z变换的MATLAB实现

### 9.6.1 基本函数

```matlab
% Z变换和逆Z变换
syms z n
x = n*(0.5)^n;           % 序列
X = ztrans(x, n, z);     % Z变换
x_inv = iztrans(X, z, n); % 逆Z变换

% 有理函数的Z变换
num = [1 0];             % 分子系数
den = [1 -0.5];          % 分母系数
[r, p, k] = residuez(num, den); % 部分分式展开
```

### 9.6.2 频率响应分析

```matlab
% 系统函数
b = [1 0.5];             % 分子系数
a = [1 -0.8 0.64];       % 分母系数

% 频率响应
[H, w] = freqz(b, a, 1024);
mag = abs(H);
phase = angle(H);

% 绘制频率响应
figure;
subplot(2,1,1);
plot(w/pi, 20*log10(mag));
xlabel('归一化频率 \omega/\pi');
ylabel('幅度 (dB)');
title('幅度响应');

subplot(2,1,2);
plot(w/pi, phase*180/pi);
xlabel('归一化频率 \omega/\pi');
ylabel('相位 (度)');
title('相位响应');
```

### 9.6.3 滤波器设计

```matlab
% IIR滤波器设计
fs = 1000;               % 采样频率
fc = 100;                % 截止频率
N = 4;                   % 阶数
[b, a] = butter(N, fc*2/fs); % 巴特沃斯滤波器

% FIR滤波器设计
fc = 100;                % 截止频率
N = 50;                  % 阶数
b = fir1(N, fc*2/fs);    % 窗函数法设计
```

## 9.7 小结

Z变换是分析离散时间系统的有力工具，主要特点：

1. **定义简单**：基于幂级数展开
2. **性质丰富**：线性、移位、卷积等性质便于分析
3. **应用广泛**：差分方程求解、滤波器设计、系统分析
4. **数值计算友好**：易于在计算机上实现

**关键概念：**
- 收敛域的重要性
- 极点与系统特性的关系
- Z变换与傅里叶变换的联系
- 数字滤波器设计方法

**实际应用：**
- 数字信号处理
- 控制系统
- 通信系统
- 图像处理

掌握Z变换的理论和方法，为深入学习数字信号处理和离散系统分析奠定了坚实基础。