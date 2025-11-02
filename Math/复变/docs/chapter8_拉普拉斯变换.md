# 第八章 拉普拉斯变换

## 8.1 拉普拉斯变换的定义

### 8.1.1 拉普拉斯变换的定义

**定义 8.1.1（拉普拉斯变换）**  
设函数 $f(t)$ 在 $t \geq 0$ 上有定义，如果积分
$$\mathcal{L}\{f(t)\} = F(s) = \int_0^{+\infty} f(t) e^{-st} dt$$
在复平面 $s = \sigma + j\omega$ 的某个区域内收敛，则称 $F(s)$ 为函数 $f(t)$ 的拉普拉斯变换，记为 $\mathcal{L}\{f(t)\}$。

其中：
- $s$ 为复变量，称为拉普拉斯变换的复频率
- $f(t)$ 称为原函数
- $F(s)$ 称为像函数

**拉普拉斯逆变换**  
如果 $F(s)$ 是 $f(t)$ 的拉普拉斯变换，则
$$f(t) = \mathcal{L}^{-1}\{F(s)\} = \frac{1}{2\pi j} \int_{\sigma-j\infty}^{\sigma+j\infty} F(s) e^{st} ds$$
称为拉普拉斯逆变换。

### 8.1.2 拉普拉斯变换的收敛域

**定义 8.1.2（收敛域）**  
拉普拉斯变换 $F(s)$ 收敛的复数 $s$ 的集合称为拉普拉斯变换的收敛域（ROC）。

对于函数 $f(t)$，存在实数 $\sigma_0$，使得：
- 当 $\text{Re}(s) > \sigma_0$ 时，积分 $\int_0^{+\infty} f(t) e^{-st} dt$ 收敛
- 当 $\text{Re}(s) < \sigma_0$ 时，积分发散

$\sigma_0$ 称为收敛横坐标。

### 8.1.3 拉普拉斯变换的存在条件

**定理 8.1.1（拉普拉斯变换存在定理）**  
如果函数 $f(t)$ 满足以下条件：
1. 在 $t \geq 0$ 的任何有限区间上分段连续
2. 存在常数 $M > 0$ 和 $\sigma_0$，使得 $|f(t)| \leq M e^{\sigma_0 t}$ 对所有 $t \geq 0$ 成立
3. $f(t)$ 在 $t = 0$ 处至多有第一类间断点

则 $f(t)$ 的拉普拉斯变换 $F(s)$ 在 $\text{Re}(s) > \sigma_0$ 的半平面内收敛且解析。

<details>
<summary>证明过程</summary>

**证明：**  
设 $s = \sigma + j\omega$，其中 $\sigma > \sigma_0$。

由于 $|f(t)| \leq M e^{\sigma_0 t}$，有
$$|f(t) e^{-st}| = |f(t) e^{-\sigma t} e^{-j\omega t}| \leq M e^{\sigma_0 t} e^{-\sigma t} = M e^{-(\sigma - \sigma_0)t}$$

当 $\sigma > \sigma_0$ 时，积分 $\int_0^{+\infty} e^{-(\sigma - \sigma_0)t} dt$ 收敛，因此
$$\int_0^{+\infty} |f(t) e^{-st}| dt \leq M \int_0^{+\infty} e^{-(\sigma - \sigma_0)t} dt < +\infty$$

根据绝对收敛判别法，拉普拉斯变换在 $\text{Re}(s) > \sigma_0$ 时收敛。

$\square$
</details>

## 8.2 拉普拉斯变换的性质

### 8.2.1 线性性质

**定理 8.2.1（线性性质）**  
设 $\mathcal{L}\{f_1(t)\} = F_1(s)$，$\mathcal{L}\{f_2(t)\} = F_2(s)$，则对任意常数 $a, b$，有
$$\mathcal{L}\{a f_1(t) + b f_2(t)\} = a F_1(s) + b F_2(s)$$

<details>
<summary>证明过程</summary>

**证明：**  
$$\mathcal{L}\{a f_1(t) + b f_2(t)\} = \int_0^{+\infty} [a f_1(t) + b f_2(t)] e^{-st} dt$$
$$= a \int_0^{+\infty} f_1(t) e^{-st} dt + b \int_0^{+\infty} f_2(t) e^{-st} dt$$
$$= a F_1(s) + b F_2(s)$$

$\square$
</details>

### 8.2.2 微分性质

**定理 8.2.2（微分性质）**  
设 $\mathcal{L}\{f(t)\} = F(s)$，则
$$\mathcal{L}\{f'(t)\} = s F(s) - f(0^+)$$

更一般地，
$$\mathcal{L}\{f^{(n)}(t)\} = s^n F(s) - s^{n-1}f(0^+) - s^{n-2}f'(0^+) - \cdots - f^{(n-1)}(0^+)$$

<details>
<summary>证明过程</summary>

**证明：**  
对 $f'(t)$ 进行拉普拉斯变换：
$$\mathcal{L}\{f'(t)\} = \int_0^{+\infty} f'(t) e^{-st} dt$$

使用分部积分法：
$$\int_0^{+\infty} f'(t) e^{-st} dt = [f(t)e^{-st}]_0^{+\infty} + s \int_0^{+\infty} f(t) e^{-st} dt$$

由于 $f(t)$ 满足增长条件，$\lim_{t \to +\infty} f(t)e^{-st} = 0$，因此：
$$\mathcal{L}\{f'(t)\} = -f(0^+) + s F(s) = s F(s) - f(0^+)$$

$\square$
</details>

### 8.2.3 积分性质

**定理 8.2.3（积分性质）**  
设 $\mathcal{L}\{f(t)\} = F(s)$，则
$$\mathcal{L}\left\{\int_0^t f(\tau) d\tau\right\} = \frac{F(s)}{s}$$

更一般地，
$$\mathcal{L}\left\{\int_0^t \int_0^{\tau_1} \cdots \int_0^{\tau_{n-1}} f(\tau_n) d\tau_n \cdots d\tau_1\right\} = \frac{F(s)}{s^n}$$

### 8.2.4 卷积定理

**定理 8.2.4（卷积定理）**  
设 $\mathcal{L}\{f_1(t)\} = F_1(s)$，$\mathcal{L}\{f_2(t)\} = F_2(s)$，则
$$\mathcal{L}\{f_1(t) * f_2(t)\} = F_1(s) F_2(s)$$

其中卷积定义为：
$$f_1(t) * f_2(t) = \int_0^t f_1(\tau) f_2(t-\tau) d\tau$$

<details>
<summary>证明过程</summary>

**证明：**  
$$f_1(t) * f_2(t) = \int_0^t f_1(\tau) f_2(t-\tau) d\tau$$

对卷积进行拉普拉斯变换：
$$\mathcal{L}\{f_1(t) * f_2(t)\} = \int_0^{+\infty} \left[\int_0^t f_1(\tau) f_2(t-\tau) d\tau\right] e^{-st} dt$$

交换积分次序（由Fubini定理保证）：
$$= \int_0^{+\infty} f_1(\tau) \left[\int_{\tau}^{+\infty} f_2(t-\tau) e^{-st} dt\right] d\tau$$

令 $u = t - \tau$，则：
$$= \int_0^{+\infty} f_1(\tau) e^{-s\tau} \left[\int_0^{+\infty} f_2(u) e^{-su} du\right] d\tau$$
$$= F_1(s) F_2(s)$$

$\square$
</details>

### 8.2.5 拉普拉斯变换性质汇总表

| 性质名称 | 原函数 | 像函数 |
|---------|--------|--------|
| 线性性质 | $a f_1(t) + b f_2(t)$ | $a F_1(s) + b F_2(s)$ |
| 微分性质 | $f'(t)$ | $s F(s) - f(0^+)$ |
| 积分性质 | $\int_0^t f(\tau) d\tau$ | $\frac{F(s)}{s}$ |
| 延时性质 | $f(t-a)u(t-a)$ | $e^{-as} F(s)$ |
| 位移性质 | $e^{at} f(t)$ | $F(s-a)$ |
| 尺度变换 | $f(at)$ | $\frac{1}{\|a\|} F(\frac{s}{a})$ |
| 卷积性质 | $f_1(t) * f_2(t)$ | $F_1(s) F_2(s)$ |

## 8.3 常用函数的拉普拉斯变换

### 8.3.1 基本函数变换对

| 原函数 $f(t)$ | 像函数 $F(s)$ | 收敛域 |
|-------------|-------------|--------|
| $\delta(t)$ | 1 | 全平面 |
| $u(t)$ | $\frac{1}{s}$ | $\text{Re}(s) > 0$ |
| $t^n u(t)$ | $\frac{n!}{s^{n+1}}$ | $\text{Re}(s) > 0$ |
| $e^{at} u(t)$ | $\frac{1}{s-a}$ | $\text{Re}(s) > \text{Re}(a)$ |
| $\sin(\omega t) u(t)$ | $\frac{\omega}{s^2 + \omega^2}$ | $\text{Re}(s) > 0$ |
| $\cos(\omega t) u(t)$ | $\frac{s}{s^2 + \omega^2}$ | $\text{Re}(s) > 0$ |
| $e^{at} \sin(\omega t) u(t)$ | $\frac{\omega}{(s-a)^2 + \omega^2}$ | $\text{Re}(s) > \text{Re}(a)$ |
| $e^{at} \cos(\omega t) u(t)$ | $\frac{s-a}{(s-a)^2 + \omega^2}$ | $\text{Re}(s) > \text{Re}(a)$ |

## 8.4 拉普拉斯逆变换

### 8.4.1 部分分式法

当像函数 $F(s)$ 是有理函数时，可以使用部分分式法求拉普拉斯逆变换。

**步骤：**
1. 将 $F(s)$ 化为真分式
2. 将分母分解为一次因子和二次因子的乘积
3. 将 $F(s)$ 展开为部分分式
4. 求每个部分分式的逆变换

**例题：** 求 $F(s) = \frac{s+3}{s(s+1)(s+2)}$ 的逆变换。

**解：**  
设 $\frac{s+3}{s(s+1)(s+2)} = \frac{A}{s} + \frac{B}{s+1} + \frac{C}{s+2}$

两边同乘 $s(s+1)(s+2)$：
$$s+3 = A(s+1)(s+2) + Bs(s+2) + Cs(s+1)$$

令 $s = 0$：$3 = A(1)(2) \Rightarrow A = \frac{3}{2}$  
令 $s = -1$：$2 = B(-1)(1) \Rightarrow B = -2$  
令 $s = -2$：$1 = C(-2)(-1) \Rightarrow C = \frac{1}{2}$

因此：
$$F(s) = \frac{3/2}{s} - \frac{2}{s+1} + \frac{1/2}{s+2}$$

逆变换为：
$$f(t) = \frac{3}{2} - 2e^{-t} + \frac{1}{2}e^{-2t}, \quad t \geq 0$$

### 8.4.2 留数法

**定理 8.4.1（拉普拉斯反演公式）**  
如果 $F(s)$ 在 $\text{Re}(s) > \sigma_0$ 内解析，且 $\lim_{s \to \infty} F(s) = 0$，则
$$f(t) = \frac{1}{2\pi j} \int_{\sigma-j\infty}^{\sigma+j\infty} F(s) e^{st} ds = \sum \text{Res}[F(s)e^{st}, s_k]$$

其中 $s_k$ 是 $F(s)$ 在左半平面的所有奇点。

**例题：** 求 $F(s) = \frac{1}{(s+1)^2(s+2)}$ 的逆变换。

**解：**  
奇点：$s = -1$（二阶极点），$s = -2$（一阶极点）

留数计算：
- 在 $s = -1$ 处：$\text{Res} = \frac{1}{1!} \lim_{s \to -1} \frac{d}{ds}[(s+1)^2 F(s) e^{st}]$
  $$= \lim_{s \to -1} \frac{d}{ds}\left[\frac{e^{st}}{s+2}\right] = \lim_{s \to -1} \frac{te^{st}(s+2) - e^{st}}{(s+2)^2}$$
  $$= \frac{te^{-t}(1) - e^{-t}}{(1)^2} = (t-1)e^{-t}$$

- 在 $s = -2$ 处：$\text{Res} = \lim_{s \to -2} (s+2) F(s) e^{st} = \lim_{s \to -2} \frac{e^{st}}{(s+1)^2} = e^{-2t}$

因此：
$$f(t) = (t-1)e^{-t} + e^{-2t} = e^{-2t} + (t-1)e^{-t}, \quad t \geq 0$$

## 8.5 拉普拉斯变换的应用

### 8.5.1 微分方程求解

拉普拉斯变换在求解线性微分方程中具有重要应用。

**求解步骤：**
1. 对微分方程两边进行拉普拉斯变换
2. 利用微分性质，将微分方程转化为代数方程
3. 求解代数方程，得到像函数 $F(s)$
4. 求 $F(s)$ 的逆变换，得到原微分方程的解

**例题：** 求解微分方程 $y'' + 3y' + 2y = e^{-t}$，初始条件 $y(0) = 1$，$y'(0) = 0$。

**解：**  
对方程两边进行拉普拉斯变换：
$$\mathcal{L}\{y''\} + 3\mathcal{L}\{y'\} + 2\mathcal{L}\{y\} = \mathcal{L}\{e^{-t}\}$$

利用微分性质：
$$[s^2 Y(s) - sy(0) - y'(0)] + 3[sY(s) - y(0)] + 2Y(s) = \frac{1}{s+1}$$

代入初始条件：
$$[s^2 Y(s) - s \cdot 1 - 0] + 3[sY(s) - 1] + 2Y(s) = \frac{1}{s+1}$$

整理得：
$$s^2 Y(s) - s + 3sY(s) - 3 + 2Y(s) = \frac{1}{s+1}$$

$$(s^2 + 3s + 2)Y(s) = s + 3 + \frac{1}{s+1}$$

$$Y(s) = \frac{s+3}{s^2 + 3s + 2} + \frac{1}{(s+1)(s^2 + 3s + 2)}$$

化简分母：$s^2 + 3s + 2 = (s+1)(s+2)$

$$Y(s) = \frac{s+3}{(s+1)(s+2)} + \frac{1}{(s+1)^2(s+2)}$$

使用部分分式法：
$$Y(s) = \frac{2}{s+1} - \frac{1}{s+2} + \frac{1}{(s+1)^2(s+2)}$$

对最后一项进行部分分式分解：
$$\frac{1}{(s+1)^2(s+2)} = \frac{A}{s+1} + \frac{B}{(s+1)^2} + \frac{C}{s+2}$$

解得：$A = -1$，$B = 1$，$C = 1$

$$Y(s) = \frac{2}{s+1} - \frac{1}{s+2} - \frac{1}{s+1} + \frac{1}{(s+1)^2} + \frac{1}{s+2}$$

$$Y(s) = \frac{1}{s+1} + \frac{1}{(s+1)^2}$$

逆变换：
$$y(t) = e^{-t} + t e^{-t} = (1 + t)e^{-t}, \quad t \geq 0$$

### 8.5.2 控制系统中的应用

在控制系统中，拉普拉斯变换用于分析系统的传递函数和稳定性。

**传递函数：**  
线性时不变系统的传递函数定义为输出与输入拉普拉斯变换的比值：
$$G(s) = \frac{Y(s)}{X(s)}$$

**系统稳定性：**  
系统稳定的充要条件是传递函数的所有极点（分母的根）都具有负的实部，即位于左半平面。

**例题：** 分析系统 $G(s) = \frac{1}{s^2 + 2s + 5}$ 的稳定性。

**解：**  
特征方程：$s^2 + 2s + 5 = 0$

根：$s = -1 \pm 2j$

由于所有极点都具有负实部，系统稳定。

### 8.5.3 电路分析中的应用

拉普拉斯变换在电路分析中用于求解动态电路的响应。

**基本元件的拉普拉斯变换模型：**

| 元件 | 时域关系 | 拉普拉斯变换 |
|------|----------|-------------|
| 电阻 $R$ | $v_R(t) = R i(t)$ | $V_R(s) = R I(s)$ |
| 电感 $L$ | $v_L(t) = L \frac{di(t)}{dt}$ | $V_L(s) = L[sI(s) - i(0^-)]$ |
| 电容 $C$ | $i_C(t) = C \frac{dv(t)}{dt}$ | $I_C(s) = C[sV(s) - v(0^-)]$ |

**例题：** RLC串联电路，$R = 2\Omega$，$L = 1H$，$C = 0.5F$，初始条件为零，输入电压 $v_i(t) = u(t)$，求输出电压 $v_C(t)$。

**解：**  
电路方程：
$$v_i(t) = R i(t) + L \frac{di(t)}{dt} + v_C(t)$$

其中 $i(t) = C \frac{dv_C(t)}{dt}$

拉普拉斯变换：
$$\frac{1}{s} = 2I(s) + sI(s) + V_C(s)$$

$$I(s) = 0.5s V_C(s)$$

代入：
$$\frac{1}{s} = 2(0.5s V_C(s)) + s(0.5s V_C(s)) + V_C(s)$$

$$\frac{1}{s} = s V_C(s) + 0.5s^2 V_C(s) + V_C(s)$$

$$\frac{1}{s} = V_C(s)(0.5s^2 + s + 1)$$

$$V_C(s) = \frac{1}{s(0.5s^2 + s + 1)} = \frac{2}{s(s^2 + 2s + 2)}$$

逆变换：
$$v_C(t) = 1 - e^{-t}(\cos t + \sin t), \quad t \geq 0$$

## 8.6 重要定理和公式汇总

### 8.6.1 基本变换对

$$\mathcal{L}\{\delta(t)\} = 1$$
$$\mathcal{L}\{u(t)\} = \frac{1}{s}$$
$$\mathcal{L}\{t^n u(t)\} = \frac{n!}{s^{n+1}}$$
$$\mathcal{L}\{e^{at} u(t)\} = \frac{1}{s-a}$$
$$\mathcal{L}\{\sin(\omega t) u(t)\} = \frac{\omega}{s^2 + \omega^2}$$
$$\mathcal{L}\{\cos(\omega t) u(t)\} = \frac{s}{s^2 + \omega^2}$$

### 8.6.2 重要性质

**线性性质：** $\mathcal{L}\{a f_1(t) + b f_2(t)\} = a F_1(s) + b F_2(s)$

**微分性质：** $\mathcal{L}\{f'(t)\} = s F(s) - f(0^+)$

**积分性质：** $\mathcal{L}\left\{\int_0^t f(\tau) d\tau\right\} = \frac{F(s)}{s}$

**卷积定理：** $\mathcal{L}\{f_1(t) * f_2(t)\} = F_1(s) F_2(s)$

**位移定理：** $\mathcal{L}\{e^{at} f(t)\} = F(s-a)$

**延时定理：** $\mathcal{L}\{f(t-a)u(t-a)\} = e^{-as} F(s)$

### 8.6.3 拉普拉斯反演公式

$$f(t) = \frac{1}{2\pi j} \int_{\sigma-j\infty}^{\sigma+j\infty} F(s) e^{st} ds = \sum \text{Res}[F(s)e^{st}, s_k]$$

其中 $s_k$ 是 $F(s)$ 在左半平面的所有奇点。

## 8.7 练习题

1. 求下列函数的拉普拉斯变换：
   - $f(t) = t^2 e^{-2t} u(t)$
   - $f(t) = \sin(3t) \cos(3t) u(t)$
   - $f(t) = e^{-t} \sinh(t) u(t)$

2. 求下列像函数的逆变换：
   - $F(s) = \frac{s+1}{s(s-1)(s+2)}$
   - $F(s) = \frac{s^2 + 1}{s(s^2 + 4)}$
   - $F(s) = \frac{1}{(s+1)^2(s+3)}$

3. 求解微分方程：
   - $y'' + 4y = \cos(2t)$，$y(0) = 0$，$y'(0) = 1$
   - $y'' + 2y' + y = t$，$y(0) = 0$，$y'(0) = 0$

4. RLC串联电路，$R = 3\Omega$，$L = 1H$，$C = \frac{1}{6}F$，初始条件为零，输入 $v_i(t) = 3u(t)$，求电流 $i(t)$。

---

**本章小结**

拉普拉斯变换是工程数学中的重要工具，它将微分方程转化为代数方程，大大简化了求解过程。本章介绍了拉普拉斯变换的定义、性质、求解方法及其在微分方程、控制系统和电路分析中的应用。掌握拉普拉斯变换的基本理论和计算方法，对于解决工程问题具有重要意义。

