# 复变函数积分章节

## 目录
1. [复积分的定义与性质](#1-复积分的定义与性质)
2. [柯西定理](#2-柯西定理)
3. [柯西积分公式](#3-柯西积分公式)
4. [高阶导数公式](#4-高阶导数公式)
5. [莫雷拉定理](#5-莫雷拉定理)

---

## 1. 复积分的定义与性质

### 1.1 复积分的定义

设函数 $f(z) = u(x,y) + iv(x,y)$ 在区域 $D$ 内有定义，$C$ 是 $D$ 内一条有向光滑曲线，参数方程为：
$$z(t) = x(t) + iy(t), \quad a \leq t \leq b$$

![复积分路径](imgs/contour-integration-path-complex-plane.jpg)
*图3-1: 复平面上的积分路径示意图*

**定义：** 复积分定义为
$$\int_C f(z)dz = \int_a^b f(z(t))z'(t)dt = \int_a^b [u(x(t),y(t)) + iv(x(t),y(t))][x'(t) + iy'(t)]dt$$

展开后得：
$$\int_C f(z)dz = \int_C (udx - vdy) + i\int_C (vdx + udy)$$

**几何意义：**
- 复积分是沿复平面上曲线的线积分
- $dz = dx + idy$ 表示复平面上的微分元素
- 积分结果是一个复数，包含实部和虚部

### 1.2 复积分的计算方法

| 积分类型 | 计算方法 | 适用条件 |
|---------|---------|---------|
| 参数方程法 | $\int_C f(z)dz = \int_a^b f(z(t))z'(t)dt$ | 曲线有参数方程 |
| 原函数法 | $\int_C f(z)dz = F(z_2) - F(z_1)$ | $f(z)$ 有原函数 |
| 分部积分法 | $\int_C udv = [uv]_C - \int_C vdu$ | 适用于乘积形式 |

### 1.3 复积分的基本性质

**性质1（线性性质）：**
$$\int_C [af(z) + bg(z)]dz = a\int_C f(z)dz + b\int_C g(z)dz$$

**性质2（路径性质）：**
$$\int_{-C} f(z)dz = -\int_C f(z)dz$$
其中 $-C$ 表示与 $C$ 方向相反的曲线。

**性质3（路径可加性）：**
若 $C = C_1 + C_2$，则：
$$\int_C f(z)dz = \int_{C_1} f(z)dz + \int_{C_2} f(z)dz$$

**性质4（估值不等式）：**
$$\left|\int_C f(z)dz\right| \leq \int_C |f(z)||dz| \leq M \cdot L$$
其中 $M = \max_{z \in C} |f(z)|$，$L$ 为曲线 $C$ 的长度。

---

## 2. 柯西定理

### 2.1 柯西定理（柯西-古萨定理）

**定理陈述：** 若函数 $f(z)$ 在单连通区域 $D$ 内解析，且 $C$ 是 $D$ 内任意一条闭曲线，则：
$$\oint_C f(z)dz = 0$$

<details>
<summary><strong>证明：</strong></summary>

**证明：** 由于 $f(z) = u(x,y) + iv(x,y)$ 在 $D$ 内解析，根据柯西-黎曼方程：
$$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$

复积分可表示为：
$$\oint_C f(z)dz = \oint_C (udx - vdy) + i\oint_C (vdx + udy)$$

应用格林公式：
$$\oint_C (Pdx + Qdy) = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right)dxdy$$

对于实部：
$$\oint_C (udx - vdy) = \iint_D \left(-\frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}\right)dxdy = 0$$

对于虚部：
$$\oint_C (vdx + udy) = \iint_D \left(\frac{\partial u}{\partial x} - \frac{\partial v}{\partial y}\right)dxdy = 0$$

因此 $\oint_C f(z)dz = 0$。
</details>

### 2.2 复合闭路定理

**定理陈述：** 若 $f(z)$ 在多连通区域 $D$ 内解析，$C$ 是 $D$ 内的一条外闭路，$C_1, C_2, ..., C_n$ 是 $D$ 内的内闭路，则：
$$\oint_C f(z)dz = \oint_{C_1} f(z)dz + \oint_{C_2} f(z)dz + ... + \oint_{C_n} f(z)dz$$

**说明：** 沿外闭路的积分等于沿所有内闭路积分之和（方向一致）。

### 2.3 闭路变形原理

**原理：** 在解析区域内，解析函数的闭路积分只与闭路的同伦类有关，与具体路径形状无关。

**推论：** 
1. 若 $C_1$ 和 $C_2$ 是两条同伦的闭路，则 $\oint_{C_1} f(z)dz = \oint_{C_2} f(z)dz$
2. 若 $C$ 可以连续收缩为一点，则 $\oint_C f(z)dz = 0$

### 2.4 柯西定理的应用

| 应用类型 | 计算方法 | 典型例题 |
|---------|---------|---------|
| 直接计算 | 利用定理判断积分为0 | $\oint_{\|z\|=1} \frac{dz}{z^2+1}$ |
| 路径无关性 | 选择便于计算的路径 | $\int_1^i \frac{dz}{z}$ |
| 分段计算 | 将复杂路径分解 | 矩形围线积分 |

---

## 3. 柯西积分公式

### 3.1 基本柯西积分公式

**定理陈述：** 若 $f(z)$ 在单连通区域 $D$ 内解析，$C$ 是 $D$ 内任意一条正向闭路，$z_0$ 是 $C$ 内部一点，则：
$$f(z_0) = \frac{1}{2\pi i} \oint_C \frac{f(z)}{z-z_0}dz$$

<details>
<summary><strong>证明：</strong></summary>

**证明：** 考虑函数 $g(z) = \frac{f(z)}{z-z_0}$。由于 $f(z)$ 在 $z_0$ 处解析，$g(z)$ 在 $z_0$ 处有孤立奇点。

在 $z_0$ 附近作小圆周 $\gamma$，根据复合闭路定理：
$$\oint_C g(z)dz = \oint_\gamma g(z)dz$$

在 $\gamma$ 上，$z = z_0 + re^{i\theta}$，$dz = ire^{i\theta}d\theta$，代入得：
$$\oint_\gamma \frac{f(z)}{z-z_0}dz = \int_0^{2\pi} \frac{f(z_0 + re^{i\theta})}{re^{i\theta}} \cdot ire^{i\theta}d\theta = i\int_0^{2\pi} f(z_0 + re^{i\theta})d\theta$$

令 $r \to 0^+$，由于 $f(z)$ 连续：
$$\lim_{r \to 0^+} i\int_0^{2\pi} f(z_0 + re^{i\theta})d\theta = i \cdot 2\pi f(z_0)$$

因此：
$$\oint_C \frac{f(z)}{z-z_0}dz = 2\pi i f(z_0)$$
即：
$$f(z_0) = \frac{1}{2\pi i} \oint_C \frac{f(z)}{z-z_0}dz$$
</details>

### 3.2 柯西积分公式的推广形式

**推广公式1（高阶导数形式）：**
$$f^{(n)}(z_0) = \frac{n!}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^{n+1}}dz$$

**推广公式2（多极点形式）：**
若 $z_0$ 是 $C$ 内孤立奇点，则：
$$\oint_C \frac{f(z)}{(z-z_0)^{k+1}}dz = \frac{2\pi i}{k!} f^{(k)}(z_0)$$

### 3.3 柯西积分公式的应用

| 应用类型 | 计算公式 | 适用条件 |
|---------|---------|---------|
| 函数值计算 | $f(z_0) = \frac{1}{2\pi i} \oint_C \frac{f(z)}{z-z_0}dz$ | $f$ 解析，$z_0$ 在 $C$ 内 |
| 导数计算 | $f^{(n)}(z_0) = \frac{n!}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^{n+1}}dz$ | $f$ 解析，$z_0$ 在 $C$ 内 |
| 留数计算 | $\text{Res}(f,z_0) = \frac{1}{2\pi i} \oint_C f(z)dz$ | $f$ 有孤立奇点 |

---

## 4. 高阶导数公式

### 4.1 高阶导数的存在性

**定理：** 若函数 $f(z)$ 在区域 $D$ 内解析，则 $f(z)$ 在 $D$ 内有任意阶导数，且各阶导数也在 $D$ 内解析。

**重要推论：** 解析函数的导数仍然是解析函数。

### 4.2 高阶导数公式

**柯西积分公式的导数形式：**
$$f^{(n)}(z_0) = \frac{n!}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^{n+1}}dz$$

其中 $C$ 是包含 $z_0$ 的任意正向简单闭曲线。

<details>
<parameter name="summary"><strong>证明：</strong></summary>

**证明：** 由基本柯西积分公式：
$$f(z) = \frac{1}{2\pi i} \oint_C \frac{f(\zeta)}{\zeta-z}d\zeta$$

对 $z$ 求 $n$ 阶导数：
$$f^{(n)}(z) = \frac{n!}{2\pi i} \oint_C \frac{f(\zeta)}{(\zeta-z)^{n+1}}d\zeta$$

令 $z = z_0$，得到：
$$f^{(n)}(z_0) = \frac{n!}{2\pi i} \oint_C \frac{f(\zeta)}{(\zeta-z_0)^{n+1}}d\zeta$$
</details>

### 4.3 高阶导数的计算

| 导数阶数 | 计算公式 | 典型应用 |
|---------|---------|---------|
| 一阶导数 | $f'(z_0) = \frac{1}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^2}dz$ | 斜率计算 |
| 二阶导数 | $f''(z_0) = \frac{2!}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^3}dz$ | 曲率计算 |
| n阶导数 | $f^{(n)}(z_0) = \frac{n!}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^{n+1}}dz$ | 泰勒展开系数 |

### 4.4 高阶导数公式的应用

**应用1：解析函数的泰勒展开**
$$f(z) = \sum_{n=0}^{\infty} \frac{f^{(n)}(z_0)}{n!}(z-z_0)^n$$

**应用2：解析函数的唯一性**
若两个解析函数在某个区域内有相同的各阶导数值，则它们在该区域内恒等。

---

## 5. 莫雷拉定理

### 5.1 莫雷拉定理的陈述

**定理陈述：** 若函数 $f(z)$ 在单连通区域 $D$ 内连续，且对 $D$ 内任意一条闭曲线 $C$，都有：
$$\oint_C f(z)dz = 0$$
则 $f(z)$ 在 $D$ 内解析。

<details>
<summary><strong>证明：</strong></summary>

**证明：** 
1. **构造原函数：** 定义
$$F(z) = \int_{z_0}^z f(\zeta)d\zeta$$
其中积分路径为 $D$ 内任意一条从 $z_0$ 到 $z$ 的曲线。

2. **证明 $F'(z) = f(z)$：** 
对于任意 $z \in D$，有：
$$\frac{F(z+h)-F(z)}{h} = \frac{1}{h} \int_z^{z+h} f(\zeta)d\zeta$$

当 $h \to 0$ 时，由于 $f$ 连续：
$$\lim_{h \to 0} \frac{F(z+h)-F(z)}{h} = f(z)$$

3. **证明 $F'(z)$ 解析：** 
由于 $f$ 连续，$F'(z) = f(z)$ 连续。由柯西-黎曼方程的逆定理，$F(z)$ 解析。

4. **结论：** $f(z) = F'(z)$ 解析。
</details>

### 5.2 莫雷拉定理的应用

| 应用场景 | 验证方法 | 实际意义 |
|---------|---------|---------|
| 函数解析性判定 | 验证闭路积分为0 | 判断函数是否可导 |
| 原函数存在性 | 验证路径积分只与端点有关 | 求解不定积分 |
| 解析延拓 | 通过局部性质判断整体解析性 | 扩大定义域 |

### 5.3 莫雷拉定理与其他定理的关系

**与柯西定理的关系：**
- 柯西定理：解析函数 → 闭路积分为0
- 莫雷拉定理：闭路积分为0 → 函数解析

**与柯西-黎曼方程的关系：**
- 柯西-黎曼方程：充分必要条件（需偏导连续）
- 莫雷拉定理：无需偏导连续条件

### 5.4 莫雷拉定理的应用实例

**例题1：** 判定函数 $f(z) = e^x\cos y + i e^x\sin y$ 的解析性。

**解：** 
1. $f(z) = e^x(\cos y + i\sin y) = e^z$
2. 验证：$\oint_C e^z dz = 0$（因为 $e^z$ 解析）
3. 由莫雷拉定理，$f(z)$ 解析。

**例题2：** 求解积分 $\int_C \frac{dz}{z-1}$，其中 $C$ 为 $|z|=2$。

**解：** 
1. 被积函数 $f(z) = \frac{1}{z-1}$ 在 $|z|=2$ 内有奇点 $z=1$
2. 由柯西积分公式：$\oint_C \frac{dz}{z-1} = 2\pi i \cdot f(1) = 2\pi i$

---

## 总结

复变函数积分理论的核心内容包括：

1. **复积分定义**：将实积分推广到复数域
2. **柯西定理**：解析函数闭路积分为0的重要定理
3. **柯西积分公式**：连接函数值与边界积分的桥梁
4. **高阶导数公式**：解析函数具有任意阶导数
5. **莫雷拉定理**：从积分性质判断函数解析性

这些定理构成了复变函数理论的基础，在实际应用中具有重要意义，特别是在计算复杂积分、求解微分方程等方面发挥着重要作用。

---

*注：本笔记涵盖了复变函数积分的主要理论内容，建议结合具体例题进行深入理解。*