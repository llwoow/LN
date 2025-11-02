# 第二章 解析函数理论

## 2.1 解析函数的定义与性质

### 2.1.1 解析函数的定义

**定义2.1（可导）**  
设函数 $f(z)$ 在点 $z_0$ 的某个邻域内有定义，如果极限
$$\lim_{z \to z_0} \frac{f(z) - f(z_0)}{z - z_0}$$
存在且有限，则称 $f(z)$ 在点 $z_0$ **可导**。这个极限值称为 $f(z)$ 在 $z_0$ 处的**导数**，记作 $f'(z_0)$。

**定义2.2（解析函数）**  
如果函数 $f(z)$ 在点 $z_0$ 的某个邻域内的每一点都可导，则称 $f(z)$ 在点 $z_0$ **解析**。如果 $f(z)$ 在区域 $D$ 内的每一点都解析，则称 $f(z)$ 在区域 $D$ 内**解析**，或称 $f(z)$ 是 $D$ 内的**解析函数**。

**重要概念：**
- **解析点**：使函数解析的点
- **奇点**：函数不解析的点
- **解析域**：函数在其上解析的区域

### 2.1.2 解析函数的基本性质

**性质2.1（解析函数的代数运算）**  
如果 $f(z)$ 和 $g(z)$ 都在区域 $D$ 内解析，则：
- $f(z) + g(z)$ 在 $D$ 内解析
- $f(z) \cdot g(z)$ 在 $D$ 内解析  
- $\frac{f(z)}{g(z)}$ 在 $D$ 内解析（$g(z) \neq 0$）
- $f(g(z))$ 在相应区域内解析（复合函数）

**性质2.2（解析函数的导数）**  
如果 $f(z)$ 在区域 $D$ 内解析，则 $f'(z)$ 也在 $D$ 内解析。

**性质2.3（解析函数的幂级数展开）**  
如果 $f(z)$ 在圆盘 $|z - z_0| < R$ 内解析，则 $f(z)$ 可以展开为幂级数：
$$f(z) = \sum_{n=0}^{\infty} \frac{f^{(n)}(z_0)}{n!}(z - z_0)^n$$

## 2.2 解析函数的判定

### 2.2.1 柯西-黎曼条件

**定理2.1（柯西-黎曼条件）**  
设 $f(z) = u(x, y) + iv(x, y)$ 在区域 $D$ 内有定义，则 $f(z)$ 在 $D$ 内解析的充分必要条件是：
1. $u(x, y)$ 和 $v(x, y)$ 在 $D$ 内可微
2. 满足**柯西-黎曼方程**：
   $$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

<details>
<parameter name="summary">柯西-黎曼条件的详细推导
$$f'(z_0) = \lim_{\Delta z \to 0} \frac{f(z_0 + \Delta z) - f(z_0)}{\Delta z}$$

令 $\Delta z = \Delta x + i\Delta y$，则：
$$\frac{f(z_0 + \Delta z) - f(z_0)}{\Delta z} = \frac{[u(x_0+\Delta x, y_0+\Delta y) - u(x_0, y_0)] + i[v(x_0+\Delta x, y_0+\Delta y) - v(x_0, y_0)]}{\Delta x + i\Delta y}$$

当 $\Delta z$ 沿实轴方向趋近于0时（$\Delta y = 0$）：
$$f'(z_0) = \frac{\partial u}{\partial x} + i\frac{\partial v}{\partial x}$$

当 $\Delta z$ 沿虚轴方向趋近于0时（$\Delta x = 0$）：
$$f'(z_0) = -i\frac{\partial u}{\partial y} + \frac{\partial v}{\partial y}$$

令两个表达式相等，得到柯西-黎曼方程：
$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

反过来，如果柯西-黎曼方程成立且偏导数连续，则 $f(z)$ 可导，且：
$$f'(z) = \frac{\partial u}{\partial x} + i\frac{\partial v}{\partial x} = \frac{\partial v}{\partial y} - i\frac{\partial u}{\partial y}$$
**证明：**  
设 $|f(z)| \leq M$ 对所有 $z \in \mathbb{C}$ 成立。由柯西积分公式：
$$f'(z) = \frac{1}{2\pi i} \int_C \frac{f(\zeta)}{(\zeta-z)^2}d\zeta$$

其中 $C$ 为以 $z$ 为中心、半径为 $R$ 的圆周。取模：
$$|f'(z)| \leq \frac{1}{2\pi} \int_C \frac{|f(\zeta)|}{|\zeta-z|^2}|d\zeta| \leq \frac{1}{2\pi} \cdot \frac{M}{R^2} \cdot 2\pi R = \frac{M}{R}$$

令 $R \to \infty$，得 $|f'(z)| \leq 0$，即 $f'(z) = 0$。故 $f(z)$ 为常数。

**定理2.4（平均值性质）**  
如果 $f(z)$ 在 $|z - z_0| < R$ 内解析，则：
$$f(z_0) = \frac{1}{2\pi} \int_0^{2\pi} f(z_0 + re^{i\theta})d\theta$$

其中 $0 < r < R$。

**定理2.5（最大值模原理）**  
如果 $f(z)$ 在区域 $D$ 内解析且不恒为零，则 $|f(z)|$ 在 $D$ 内不能取得最大值。

<details>
<parameter name="summary">最大值模原理的证明**证明：**  
假设 $|f(z)|$ 在 $z_0 \in D$ 取得最大值。由解析函数的平均值性质：
$$f(z_0) = \frac{1}{2\pi} \int_0^{2\pi} f(z_0 + re^{i\theta})d\theta$$

取模：
$$|f(z_0)| \leq \frac{1}{2\pi} \int_0^{2\pi} |f(z_0 + re^{i\theta})|d\theta$$

如果 $|f(z_0)|$ 是最大值，则等号成立，这意味着 $f(z_0 + re^{i\theta})$ 在圆周上的辐角必须相同，即 $f(z)$ 在该圆周上为常数。由解析延拓，$f(z)$ 在整个连通分量上为常数。

## 2.6 总结

本章主要介绍了复变函数中解析函数理论的核心内容：

### 2.6.1 核心概念
1. **解析函数**：在区域内每点都可导的函数
2. **柯西-黎曼条件**：解析函数的判定条件
3. **共形映射**：保持角度和形状的映射

### 2.6.2 重要定理
| 定理名称 | 条件 | 结论 |
|----------|------|------|
| 柯西-黎曼定理 | 满足C-R方程且偏导数连续 | 函数解析 |
| 刘维尔定理 | 全平面解析且有界 | 必为常数 |
| 平均值性质 | 区域内解析 | 函数值等于圆周平均值 |
| 最大值模原理 | 区域内解析且不恒为零 | 模不能取得最大值 |

### 2.6.3 初等解析函数性质对比

| 函数 | 定义 | 解析域 | 导数 |
|------|------|--------|------|
| $e^z$ | $e^x(\cos y + i\sin y)$ | 全平面 | $e^z$ |
| $\operatorname{Log} z$ | $\ln r + i\theta$ | 割平面 | $\frac{1}{z}$ |
| $z^\alpha$ | $e^{\alpha \operatorname{Log} z}$ | 割平面 | $\alpha z^{\alpha-1}$ |
| $\sin z$ | $\frac{e^{iz}-e^{-iz}}{2i}$ | 全平面 | $\cos z$ |
| $\cos z$ | $\frac{e^{iz}+e^{-iz}}{2}$ | 全平面 | $-\sin z$ |

### 2.6.4 判定方法总结
1. **直接判定**：验证极限定义
2. **C-R条件**：验证柯西-黎曼方程
3. **级数展开**：泰勒级数收敛
4. **运算性质**：初等函数的解析性

解析函数理论是复变函数的核心内容，为后续的复积分、级数和留数定理奠定了重要基础。
