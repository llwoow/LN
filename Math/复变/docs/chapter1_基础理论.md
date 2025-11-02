# 复变函数基础理论

## 目录
1. [复数与复平面](#1-复数与复平面)
2. [复变函数概念](#2-复变函数概念)
3. [极限与连续性](#3-极限与连续性)
4. [导数与微分](#4-导数与微分)
5. [柯西-黎曼方程](#5-柯西-黎曼方程)

---

## 1. 复数与复平面

### 1.1 复数的定义与表示

#### 1.1.1 代数形式
复数 $z$ 可以表示为：
$$z = x + iy$$

其中：
- $x = \operatorname{Re}(z)$ 为实部
- $y = \operatorname{Im}(z)$ 为虚部
- $i = \sqrt{-1}$ 为虚数单位

#### 1.1.2 共轭复数
复数 $z = x + iy$ 的共轭复数为：
$$\bar{z} = x - iy$$

**重要性质：**
- $z \cdot \bar{z} = |z|^2 = x^2 + y^2$
- $\overline{z_1 + z_2} = \bar{z_1} + \bar{z_2}$
- $\overline{z_1 \cdot z_2} = \bar{z_1} \cdot \bar{z_2}$

### 1.2 复数的四则运算

设 $z_1 = x_1 + iy_1$，$z_2 = x_2 + iy_2$

#### 1.2.1 加法运算
$$z_1 + z_2 = (x_1 + x_2) + i(y_1 + y_2)$$

#### 1.2.2 乘法运算
$$z_1 \cdot z_2 = (x_1x_2 - y_1y_2) + i(x_1y_2 + x_2y_1)$$

#### 1.2.3 除法运算
$$\frac{z_1}{z_2} = \frac{z_1 \cdot \bar{z_2}}{|z_2|^2} = \frac{(x_1 + iy_1)(x_2 - iy_2)}{x_2^2 + y_2^2}$$

### 1.3 复数的三角形式与指数形式

#### 1.3.1 三角形式
$$z = r(\cos\theta + i\sin\theta)$$

![复数的三角形式](imgs/complex-number-polar-trigonometric-representation-diagram.jpg)
*图1-2: 复数的三角形式和极坐标表示*

其中：
- $r = |z| = \sqrt{x^2 + y^2}$ 为模
- $\theta = \arg(z)$ 为辐角，满足 $\cos\theta = \frac{x}{r}$，$\sin\theta = \frac{y}{r}$

#### 1.3.2 指数形式（欧拉公式）
$$z = re^{i\theta}$$

其中 $e^{i\theta} = \cos\theta + i\sin\theta$

**重要关系：**
- $x = r\cos\theta$
- $y = r\sin\theta$
- $\theta = \arctan\left(\frac{y}{x}\right)$（注意象限）

#### 1.3.3 模与辐角的重要性质

| 性质 | 公式 | 说明 |
|------|------|------|
| 模的乘积 | $\|z_1 z_2\| = \|z_1\| \cdot \|z_2\|$ | 模的乘积等于乘积的模 |
| 模的商 | $\left\|\frac{z_1}{z_2}\right\| = \frac{\|z_1\|}{\|z_2\|}$ | 模的商等于商的模 |
| 辐角的和 | $\arg(z_1 z_2) = \arg(z_1) + \arg(z_2)$ | 辐角的可加性 |
| 辐角的差 | $\arg\left(\frac{z_1}{z_2}\right) = \arg(z_1) - \arg(z_2)$ | 辐角的可减性 |

### 1.4 复平面

复数 $z = x + iy$ 可以用平面上的点 $(x, y)$ 表示，其中：
- 横坐标表示实部 $x$
- 纵坐标表示虚部 $y$

![复平面图示](imgs/complex-plane-argand-diagram-illustration.jpg)
*图1-1: 复平面（Argand图）示意图*

**重要概念：**
- 原点：$z = 0$
- 实轴：$\operatorname{Im}(z) = 0$
- 虚轴：$\operatorname{Re}(z) = 0$

**几何意义：**
- 复数可以用从原点到该点的向量表示
- 向量的长度表示复数的模 $|z| = \sqrt{x^2 + y^2}$
- 向量与正实轴的夹角表示复数的辐角 $\arg(z)$

---

## 2. 复变函数概念

### 2.1 复变函数的定义

设 $D$ 是复平面上的一个区域，$f$ 是定义在 $D$ 上的函数，如果对每个 $z \in D$，都有唯一确定的复数 $w$ 与之对应，则称 $f$ 是定义在 $D$ 上的**复变函数**，记作：
$$w = f(z)$$

其中 $z \in D$，$w \in \mathbb{C}$。

### 2.2 复变函数的表示方法

#### 2.2.1 代数表示
设 $f(z) = u(x, y) + iv(x, y)$，其中：
- $u(x, y) = \operatorname{Re}[f(z)]$ 为实部函数
- $v(x, y) = \operatorname{Im}[f(z)]$ 为虚部函数

#### 2.2.2 极坐标表示
设 $z = re^{i\theta}$，则：
$$f(z) = f(re^{i\theta}) = \rho(r, \theta)e^{i\phi(r, \theta)}$$

其中 $\rho = |f(z)|$ 为模函数，$\phi = \arg[f(z)]$ 为辐角函数。

### 2.3 复变函数的几何意义

复变函数 $w = f(z)$ 可以看作是从 $z$ 平面到 $w$ 平面的映射：

![复变函数映射](imgs/complex-exponential-function-mapping-z-plane-to-w-plane.jpg)
*图2-1: 复指数函数 $w = e^z$ 的映射示例*

1. **点映射**：$z$ 平面上的点 $z_0$ 映射到 $w$ 平面上的点 $w_0 = f(z_0)$
2. **曲线映射**：$z$ 平面上的曲线映射到 $w$ 平面上的曲线
3. **区域映射**：$z$ 平面上的区域映射到 $w$ 平面上的区域

**映射的几何性质：**
- **伸缩变换**：映射的导数 $f'(z)$ 的模 $|f'(z)|$ 表示局部伸缩比
- **旋转变换**：映射的导数 $f'(z)$ 的辐角 $\arg[f'(z)]$ 表示局部旋转角
- **保角性**：解析函数在其定义域内具有保角性质（保持角度不变）

### 2.4 常用的基本复变函数

#### 2.4.1 幂函数
$$f(z) = z^n, \quad n \in \mathbb{N}$$

#### 2.4.2 指数函数
$$f(z) = e^z = e^{x+iy} = e^x(\cos y + i\sin y)$$

**重要性质：**
- $|e^z| = e^x$
- $\arg(e^z) = y + 2k\pi, \quad k \in \mathbb{Z}$

#### 2.4.3 对数函数
$$f(z) = \operatorname{Log} z = \ln|z| + i\arg(z)$$

其中 $\arg(z)$ 是多值函数，通常取主值 $\arg(z) \in (-\pi, \pi]$。

#### 2.4.4 三角函数
$$\sin z = \frac{e^{iz} - e^{-iz}}{2i}, \quad \cos z = \frac{e^{iz} + e^{-iz}}{2}$$

---

## 3. 极限与连续性

### 3.1 复变函数的极限

#### 3.1.1 极限的定义
设 $f(z)$ 在 $z_0$ 的去心邻域内有定义，如果存在复数 $A$，使得对任意 $\epsilon > 0$，总存在 $\delta > 0$，当 $0 < |z - z_0| < \delta$ 时，都有 $|f(z) - A| < \epsilon$，则称 $A$ 为 $f(z)$ 在 $z_0$ 处的极限，记作：
$$\lim_{z \to z_0} f(z) = A$$

#### 3.1.2 极限的四则运算
如果 $\lim_{z \to z_0} f(z) = A$，$\lim_{z \to z_0} g(z) = B$，则：
- $\lim_{z \to z_0} [f(z) \pm g(z)] = A \pm B$
- $\lim_{z \to z_0} [f(z) \cdot g(z)] = A \cdot B$
- $\lim_{z \to z_0} \frac{f(z)}{g(z)} = \frac{A}{B} \quad (B \neq 0)$

#### 3.1.3 极限存在的充要条件
$\lim_{z \to z_0} f(z) = A$ 当且仅当：
$$\lim_{z \to z_0} u(x, y) = \operatorname{Re}(A), \quad \lim_{z \to z_0} v(x, y) = \operatorname{Im}(A)$$

其中 $f(z) = u(x, y) + iv(x, y)$，$A = \operatorname{Re}(A) + i\operatorname{Im}(A)$。

<details>
<summary><strong>证明：</strong>极限存在的充要条件</summary>

**必要性**：若 $\lim_{z \to z_0} f(z) = A$，则对任意 $\epsilon > 0$，存在 $\delta > 0$，当 $0 < |z - z_0| < \delta$ 时，有 $|f(z) - A| < \epsilon$。

由于 $|u(x, y) - \operatorname{Re}(A)| \leq |f(z) - A|$ 和 $|v(x, y) - \operatorname{Im}(A)| \leq |f(z) - A|$，可得：
$$|u(x, y) - \operatorname{Re}(A)| < \epsilon, \quad |v(x, y) - \operatorname{Im}(A)| < \epsilon$$

因此 $\lim_{z \to z_0} u(x, y) = \operatorname{Re}(A)$，$\lim_{z \to z_0} v(x, y) = \operatorname{Im}(A)$。

**充分性**：若 $\lim_{z \to z_0} u(x, y) = \operatorname{Re}(A)$，$\lim_{z \to z_0} v(x, y) = \operatorname{Im}(A)$，则对任意 $\epsilon > 0$，存在 $\delta_1, \delta_2 > 0$，使得：
- 当 $0 < |z - z_0| < \delta_1$ 时，$|u(x, y) - \operatorname{Re}(A)| < \frac{\epsilon}{2}$
- 当 $0 < |z - z_0| < \delta_2$ 时，$|v(x, y) - \operatorname{Im}(A)| < \frac{\epsilon}{2}$

取 $\delta = \min(\delta_1, \delta_2)$，则当 $0 < |z - z_0| < \delta$ 时：
$$|f(z) - A| = \sqrt{[u(x, y) - \operatorname{Re}(A)]^2 + [v(x, y) - \operatorname{Im}(A)]^2} < \sqrt{\left(\frac{\epsilon}{2}\right)^2 + \left(\frac{\epsilon}{2}\right)^2} = \frac{\epsilon}{\sqrt{2}} < \epsilon$$

故 $\lim_{z \to z_0} f(z) = A$。
</details>

### 3.2 复变函数的连续性

#### 3.2.1 连续的定义
设 $f(z)$ 在 $z_0$ 的邻域内有定义，如果：
$$\lim_{z \to z_0} f(z) = f(z_0)$$

则称 $f(z)$ 在 $z_0$ 处连续。

#### 3.2.2 连续函数的性质
1. **局部有界性**：连续函数在每点附近有界
2. **四则运算**：连续函数的和、差、积、商（分母不为零）仍连续
3. **复合函数**：连续函数的复合函数仍连续

#### 3.2.3 连续性的判别方法
$f(z) = u(x, y) + iv(x, y)$ 在 $z_0 = x_0 + iy_0$ 处连续当且仅当 $u(x, y)$ 和 $v(x, y)$ 在 $(x_0, y_0)$ 处连续。

### 3.3 一致连续性

#### 3.3.1 一致连续的定义
设 $f(z)$ 在区域 $D$ 内有定义，如果对任意 $\epsilon > 0$，存在 $\delta > 0$，使得对任意 $z_1, z_2 \in D$，当 $|z_1 - z_2| < \delta$ 时，都有 $|f(z_1) - f(z_2)| < \epsilon$，则称 $f(z)$ 在 $D$ 内一致连续。

#### 3.3.2 重要定理
**海涅-博雷尔定理**：有界闭区域上的连续函数必一致连续。

---

## 4. 导数与微分

### 4.1 复变函数导数的定义

#### 4.1.1 导数的定义
设 $f(z)$ 在 $z_0$ 的邻域内有定义，如果极限：
$$\lim_{\Delta z \to 0} \frac{f(z_0 + \Delta z) - f(z_0)}{\Delta z}$$

存在且有限，则称 $f(z)$ 在 $z_0$ 处可导，该极限称为 $f(z)$ 在 $z_0$ 处的导数，记作：
$$f'(z_0) = \lim_{\Delta z \to 0} \frac{f(z_0 + \Delta z) - f(z_0)}{\Delta z}$$

#### 4.1.2 微分的定义
如果 $f(z)$ 在 $z_0$ 处可导，则称：
$$df(z_0) = f'(z_0) dz$$

为 $f(z)$ 在 $z_0$ 处的微分，其中 $dz = \Delta z$。

### 4.2 导数的几何意义

复变函数 $w = f(z)$ 的导数 $f'(z_0)$ 具有明确的几何意义：

1. **模的意义**：$|f'(z_0)|$ 表示映射在 $z_0$ 处的伸缩比
2. **辐角的意义**：$\arg[f'(z_0)]$ 表示映射在 $z_0$ 处的旋转角

<details>
<summary><strong>推导：</strong>导数的几何意义</summary>

设 $z = z_0 + \Delta z$，$w = f(z) = f(z_0 + \Delta z)$，则：
$$\Delta w = f(z_0 + \Delta z) - f(z_0) = f'(z_0)\Delta z + o(\Delta z)$$

当 $\Delta z$ 充分小时，$o(\Delta z)$ 可以忽略，因此：
$$\Delta w \approx f'(z_0)\Delta z$$

设 $f'(z_0) = |f'(z_0)|e^{i\theta}$，$\Delta z = |\Delta z|e^{i\phi}$，则：
$$\Delta w \approx |f'(z_0)|e^{i\theta} \cdot |\Delta z|e^{i\phi} = |f'(z_0)||\Delta z|e^{i(\theta + \phi)}$$

这表明：
1. 长度伸缩比为 $|f'(z_0)|$
2. 角度旋转角为 $\theta = \arg[f'(z_0)]$
</details>

### 4.3 求导法则

#### 4.3.1 基本求导法则
| 法则 | 公式 |
|------|------|
| 常数法则 | $\frac{d}{dz}[C] = 0$ |
| 幂法则 | $\frac{d}{dz}[z^n] = nz^{n-1}$ |
| 指数法则 | $\frac{d}{dz}[e^z] = e^z$ |
| 对数法则 | $\frac{d}{dz}[\log z] = \frac{1}{z}$ |
| 三角法则 | $\frac{d}{dz}[\sin z] = \cos z$，$\frac{d}{dz}[\cos z] = -\sin z$ |

#### 4.3.2 运算法则
1. **线性法则**：$\frac{d}{dz}[af(z) + bg(z)] = af'(z) + bg'(z)$
2. **乘积法则**：$\frac{d}{dz}[f(z)g(z)] = f'(z)g(z) + f(z)g'(z)$
3. **商法则**：$\frac{d}{dz}\left[\frac{f(z)}{g(z)}\right] = \frac{f'(z)g(z) - f(z)g'(z)}{g^2(z)}$
4. **链式法则**：$\frac{d}{dz}[f(g(z))] = f'(g(z)) \cdot g'(z)$

### 4.4 解析函数

#### 4.4.1 解析的定义
如果 $f(z)$ 在 $z_0$ 的邻域内可导，则称 $f(z)$ 在 $z_0$ 处解析。

如果 $f(z)$ 在区域 $D$ 内的每点都解析，则称 $f(z)$ 在 $D$ 内解析。

#### 4.4.2 解析函数的性质
1. **无限可微性**：解析函数具有任意阶导数
2. **幂级数展开**：解析函数可以展开为泰勒级数
3. **平均值性质**：解析函数在圆周上的平均值等于圆心的函数值

---

## 5. 柯西-黎曼方程

### 5.1 柯西-黎曼方程的推导

设 $f(z) = u(x, y) + iv(x, y)$ 在 $z_0 = x_0 + iy_0$ 处可导，则：
$$f'(z_0) = \lim_{\Delta z \to 0} \frac{f(z_0 + \Delta z) - f(z_0)}{\Delta z}$$

令 $\Delta z = \Delta x + i\Delta y$，则：
$$\frac{f(z_0 + \Delta z) - f(z_0)}{\Delta z} = \frac{[u(x_0+\Delta x, y_0+\Delta y) + iv(x_0+\Delta x, y_0+\Delta y)] - [u(x_0, y_0) + iv(x_0, y_0)]}{\Delta x + i\Delta y}$$

<details>
<summary><strong>推导过程：</strong>柯西-黎曼方程</summary>

分别沿实轴和虚轴取极限：

**沿实轴取极限**（$\Delta y = 0$，$\Delta x \to 0$）：
$$f'(z_0) = \lim_{\Delta x \to 0} \frac{u(x_0+\Delta x, y_0) - u(x_0, y_0) + i[v(x_0+\Delta x, y_0) - v(x_0, y_0)]}{\Delta x}$$
$$= \frac{\partial u}{\partial x}\bigg|_{(x_0,y_0)} + i\frac{\partial v}{\partial x}\bigg|_{(x_0,y_0)}$$

**沿虚轴取极限**（$\Delta x = 0$，$\Delta y \to 0$）：
$$f'(z_0) = \lim_{\Delta y \to 0} \frac{u(x_0, y_0+\Delta y) - u(x_0, y_0) + i[v(x_0, y_0+\Delta y) - v(x_0, y_0)]}{i\Delta y}$$
$$= \frac{1}{i}\left[\frac{\partial u}{\partial y}\bigg|_{(x_0,y_0)} + i\frac{\partial v}{\partial y}\bigg|_{(x_0,y_0)}\right]$$
$$= -i\frac{\partial u}{\partial y}\bigg|_{(x_0,y_0)} + \frac{\partial v}{\partial y}\bigg|_{(x_0,y_0)}$$

由于两个极限都等于 $f'(z_0)$，因此实部和虚部分别相等：

实部：$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}$
虚部：$\frac{\partial v}{\partial x} = -\frac{\partial u}{\partial y}$

即得到柯西-黎曼方程。
</details>

### 5.2 柯西-黎曼方程

**柯西-黎曼方程**（C-R方程）：
$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial v}{\partial x} = -\frac{\partial u}{\partial y}$$

或者写成：
$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

### 5.3 柯西-黎曼方程的充分必要条件

#### 5.3.1 必要条件
如果 $f(z) = u(x, y) + iv(x, y)$ 在 $z_0$ 处可导，则在 $z_0$ 处必有：
$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

#### 5.3.2 充分条件
如果 $u(x, y)$ 和 $v(x, y)$ 在 $z_0$ 的邻域内：
1. 连续可微（即偏导数存在且连续）
2. 满足柯西-黎曼方程

则 $f(z)$ 在 $z_0$ 处可导，且：
$$f'(z_0) = \frac{\partial u}{\partial x} + i\frac{\partial v}{\partial x} = \frac{\partial v}{\partial y} - i\frac{\partial u}{\partial y}$$

<details>
<summary><strong>证明：</strong>充分条件</summary>

由于 $u$ 和 $v$ 连续可微，利用全微分公式：
$$du = \frac{\partial u}{\partial x}dx + \frac{\partial u}{\partial y}dy$$
$$dv = \frac{\partial v}{\partial x}dx + \frac{\partial v}{\partial y}dy$$

由柯西-黎曼方程：
$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

因此：
$$df = du + idv = \left(\frac{\partial u}{\partial x}dx + \frac{\partial u}{\partial y}dy\right) + i\left(\frac{\partial v}{\partial x}dx + \frac{\partial v}{\partial y}dy\right)$$
$$= \frac{\partial u}{\partial x}dx + \frac{\partial u}{\partial y}dy + i\frac{\partial v}{\partial x}dx + i\frac{\partial u}{\partial x}dy$$
$$= \frac{\partial u}{\partial x}(dx + idy) + i\frac{\partial v}{\partial x}(dx + idy)$$
$$= \left(\frac{\partial u}{\partial x} + i\frac{\partial v}{\partial x}\right)(dx + idy)$$

这表明 $df = f'(z)dz$，其中 $f'(z) = \frac{\partial u}{\partial x} + i\frac{\partial v}{\partial x}$，故 $f(z)$ 在 $z_0$ 处可导。
</details>

### 5.4 柯西-黎曼方程的几何意义

柯西-黎曼方程反映了复变函数映射的保角性质：

1. **正交性**：等值曲线 $u(x, y) = c_1$ 和 $v(x, y) = c_2$ 在交点处正交
2. **保角性**：映射保持两条曲线的夹角大小和方向

**证明**：等值曲线 $u(x, y) = c_1$ 的法向量为 $\nabla u = \left(\frac{\partial u}{\partial x}, \frac{\partial u}{\partial y}\right)$，等值曲线 $v(x, y) = c_2$ 的法向量为 $\nabla v = \left(\frac{\partial v}{\partial x}, \frac{\partial v}{\partial y}\right)$。

由柯西-黎曼方程：
$$\nabla u \cdot \nabla v = \frac{\partial u}{\partial x}\frac{\partial v}{\partial x} + \frac{\partial u}{\partial y}\frac{\partial v}{\partial y}$$
$$= \frac{\partial u}{\partial x}\left(-\frac{\partial u}{\partial y}\right) + \frac{\partial u}{\partial y}\frac{\partial u}{\partial x} = 0$$

因此两法向量正交，即两等值曲线正交。

### 5.5 调和函数

#### 5.5.1 调和函数的定义
如果函数 $\phi(x, y)$ 在区域 $D$ 内具有连续的二阶偏导数，且满足拉普拉斯方程：
$$\frac{\partial^2 \phi}{\partial x^2} + \frac{\partial^2 \phi}{\partial y^2} = 0$$

则称 $\phi(x, y)$ 为调和函数。

#### 5.5.2 解析函数与调和函数的关系
如果 $f(z) = u(x, y) + iv(x, y)$ 在区域 $D$ 内解析，则：
1. $u(x, y)$ 和 $v(x, y)$ 都是调和函数
2. $u(x, y)$ 和 $v(x, y)$ 互为共轭调和函数

**证明**：由柯西-黎曼方程：
$$\frac{\partial^2 u}{\partial x^2} = \frac{\partial}{\partial x}\left(\frac{\partial v}{\partial y}\right) = \frac{\partial^2 v}{\partial x\partial y}$$
$$\frac{\partial^2 u}{\partial y^2} = \frac{\partial}{\partial y}\left(-\frac{\partial v}{\partial x}\right) = -\frac{\partial^2 v}{\partial y\partial x}$$

由混合偏导数的连续性（施瓦茨定理），$\frac{\partial^2 v}{\partial x\partial y} = \frac{\partial^2 v}{\partial y\partial x}$，因此：
$$\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} = \frac{\partial^2 v}{\partial x\partial y} - \frac{\partial^2 v}{\partial y\partial x} = 0$$

同理可证 $v(x, y)$ 也是调和函数。

---

## 重要公式总结表

| 概念 | 公式 | 备注 |
|------|------|------|
| 复数表示 | $z = x + iy = r(\cos\theta + i\sin\theta) = re^{i\theta}$ | 代数、三角、指数形式 |
| 模与辐角 | $\|z\| = \sqrt{x^2 + y^2}$，$\arg(z) = \theta$ | 主值 $\theta \in (-\pi, \pi]$ |
| 共轭复数 | $\bar{z} = x - iy$，$z\bar{z} = \|z\|^2 | 重要性质 |
| 复数运算 | $z_1z_2 = r_1r_2e^{i(\theta_1+\theta_2)}$ | 模相乘，辐角相加 |
| 导数定义 | $f'(z_0) = \lim_{\Delta z \to 0}\frac{f(z_0+\Delta z)-f(z_0)}{\Delta z}$ | 复导数定义 |
| 柯西-黎曼方程 | $\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}$，$\frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$ | 可导的充要条件 |
| 导数表达式 | $f'(z) = \frac{\partial u}{\partial x} + i\frac{\partial v}{\partial x}$ | 实部虚部表示 |
| 拉普拉斯方程 | $\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} = 0$ | 调和函数定义 |

---

## 典型例题

### 例题1：复数运算
**题目**：计算 $(1 + i)^4$

**解答**：
$$1 + i = \sqrt{2}e^{i\pi/4}$$
$$(1 + i)^4 = (\sqrt{2})^4 e^{i\pi} = 4(\cos\pi + i\sin\pi) = 4(-1 + 0i) = -4$$

### 例题2：极限计算
**题目**：计算 $\lim_{z \to i} \frac{z^2 + 1}{z - i}$

**解答**：
$$z^2 + 1 = (z - i)(z + i)$$
$$\lim_{z \to i} \frac{z^2 + 1}{z - i} = \lim_{z \to i} (z + i) = i + i = 2i$$

### 例题3：柯西-黎曼方程
**题目**：验证 $f(z) = z^2$ 满足柯西-黎曼方程

**解答**：
$$f(z) = z^2 = (x + iy)^2 = x^2 - y^2 + 2ixy$$
$$u(x, y) = x^2 - y^2, \quad v(x, y) = 2xy$$

$$\frac{\partial u}{\partial x} = 2x, \quad \frac{\partial v}{\partial y} = 2x$$
$$\frac{\partial u}{\partial y} = -2y, \quad \frac{\partial v}{\partial x} = 2y$$

满足 $\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}$ 和 $\frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$，故满足柯西-黎曼方程。

---

**注**：本章节为复变函数的基础理论，是后续学习复积分、级数和留数定理的重要基础。掌握这些基本概念和定理对于深入理解复变函数理论至关重要。