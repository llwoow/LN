# 图形渲染管线核心技术研究:数学原理与算法实现

## 导言与研究范围

本报告系统研究图形渲染管线的核心技术与数学原理,面向计算机图形学初学者与进阶开发者、实时渲染工程师及图形API(如OpenGL/WebGL)使用者,聚焦于算法实现与数学推导的完整呈现。全文遵循从空间与坐标(What)到变换与算法(How),再到工程启示(So What)的叙事脉络,覆盖以下主题:几何变换与MVP矩阵、投影矩阵推导、光栅化算法、纹理映射与采样、深度缓冲(Z-buffer)与深度测试、渲染管线阶段职责与数据流,以及常见工程问题与优化策略。

在现代可编程渲染管线中,顶点着色器负责执行模型-视图-投影(Model-View-Projection, MVP)变换,图元装配后进入光栅化与片段处理,纹理采样与深度测试等步骤以可编程或固定功能形式协同工作,最终生成图像[^1][^2]。本报告的数学推导与算法描述以齐次坐标、仿射变换与相似三角形等基础理论为工具,并在必要处给出矩阵形式或伪代码,强调实现细节与可操作性。

信息缺口说明:出于访问限制与资料来源的局限,本报告不包含扫描线多边形填充算法的完整源码与详细图示(仅给出原理与数据结构要点);纹理采样部分以双线性与mipmap为主,各项异性过滤(如EWA/Ripmap)仅作概念性介绍;深度测试的Z-fighting、Early-Z等硬件细节仅做概述;投影矩阵的OpenGL/DirectX差异不在本文范围;视口变换矩阵的标准化推导以原则性说明为主。

## 几何变换与MVP矩阵(模型、视图、投影)

渲染管线的几何阶段以空间层次为主线:模型空间(Object Space)通过模型变换(Model Transform)进入世界空间(World Space),再经视图变换(View Transform)进入观察空间(View Space),最后通过投影变换(Projection Transform)进入裁剪空间(Clip Space)。在顶点着色器中执行MVP变换,是将三维模型坐标转换为裁剪坐标的标准流程,后续通过透视除法与视口变换映射到屏幕坐标[^3][^4][^5][^6]。

模型变换通常由平移(T)、旋转(R)、缩放(S)组合而成,顺序一般为先旋转后平移,再施加缩放(例如 M = T · R · S),以避免因交换顺序导致的几何错误。视图变换的核心是建立以相机为原点的观察坐标系:将相机位置 e 平移至原点,并将相机朝向 g 旋转至 −Z 轴,上方向 t 旋转至 Y 轴。投影变换将视锥体(平截头体)映射到标准视体(Canonical View Volume),一般为 [-1, 1]^3 的立方体,以便裁剪与后续屏幕映射[^3][^4]。

为便于工程实现,表1总结了MVP矩阵各元素、输入输出空间与典型操作。

表1 MVP矩阵要素总览(空间、矩阵、操作、输入输出)

| 空间 | 典型矩阵 | 主要操作 | 输入 | 输出 |
|---|---|---|---|---|
| 模型空间 → 世界空间 | M = T · R · S | 平移、旋转、缩放(先旋转后平移) | 局部坐标 | 世界坐标 |
| 世界空间 → 观察空间 | M_view = R_view · T_view | 平移至相机原点;旋转 g→−Z、t→Y、g×t→X | 世界坐标 | 观察坐标 |
| 观察空间 → 裁剪空间 | 正交或透视投影矩阵 | 映射视锥体到 [-1,1]^3 | 观察坐标 | 裁剪坐标(齐次) |
| 裁剪空间 → 屏幕空间 | 视口变换 | 透视除法后映射到像素坐标 | NDC坐标 | 屏幕像素坐标 |

上述矩阵构建与空间语义在多平台API中具有一致性,理解其数学原理是编写稳定顶点着色器与处理相机控制的基础[^3][^4][^5][^6]。

### 模型变换(Model Transform)

模型变换将模型从自身局部坐标系转换到世界坐标系,常由平移、旋转与缩放组合。组合顺序直接影响结果:例如先平移后旋转会导致模型围绕世界原点而非自身中心旋转,从而产生错误的几何布局。因此,实践中通常采用“先旋转、后平移”的顺序,并在需要时叠加非均匀缩放。模型矩阵的分解与重组还用于动画与物理模拟中提取局部旋转、分离缩放影响等用途[^4][^3]。

### 视图变换(View Transform)

视图变换建立观察空间,使相机处于原点且朝向 −Z 轴,上方向为 Y 轴。一种实现方式是对世界坐标先平移(减去相机位置 e),再旋转(将 g 旋转到 −Z,t 旋转到 Y,g×t 旋转到 X)。由于旋转矩阵是正交矩阵,其逆矩阵等于转置矩阵,视图矩阵的计算可利用这一性质简化实现。相机参数包括位置 e、朝向 g 与上方向 t,它们决定了从世界空间到观察空间的唯一仿射变换[^4][^3]。

### 投影变换(Projection Transform)

投影变换决定可见体积与透视效果。正交投影将长方体视域直接映射到标准立方体,透视投影通过“挤压”将平截头体变为长方体,再执行正交投影。相似三角形关系是透视投影的核心几何依据:y' = n/z · y,x' = n/z · x,其中 n 为近平面距离。工程上,透视矩阵常由视场角(FOV)与宽高比(aspect)推导,近远平面(near/far)决定深度范围与精度[^4][^3][^5]。

## 投影变换:正交投影与透视投影的矩阵推导

正交投影(Orthographic Projection)与透视投影(Perspective Projection)分别服务于无透视场景与近大远小的真实感场景。两者共同目标是将观察空间中的点映射到标准视体([-1,1]^3),以统一裁剪与屏幕映射流程。

正交投影的思路是平移后缩放:先将要观察的长方体中心平移到原点,再按各轴长度缩放到 [-1,1] 范围。透视投影的思路是先通过齐次坐标的“挤压”将平截头体变为长方体(保持相对深度比例与近平面坐标不变),再按正交投影映射到标准立方体[^4][^3][^5]。

表2给出典型透视投影矩阵参数与FOV/aspect的关系。

表2 透视投影参数与矩阵元素映射(FOV、aspect、near、far)

| 参数 | 含义 | 与矩阵元素关系 |
|---|---|---|
| fov_y | 垂直视场角 | 矩阵中 n/scale_y 与 fov_y 相关,scale_y = 1 / (n · tan(fov_y/2)) |
| aspect | 宽高比(宽度/高度) | 矩阵中 n/scale_x 与 aspect 相关,scale_x = aspect · scale_y |
| near(n) | 近平面距离 | 透视挤压后保持近平面坐标不变 |
| far(f) | 远平面距离 | 影响矩阵第三行的组合项(n+f, -n·f),决定深度映射 |

上述元素在典型透视矩阵中以齐次形式出现,推导详见下文[^4][^3][^5]。

### 正交投影矩阵推导

设正交视域为 [l, r] × [b, t] × [n, f](左右、下上、近远),将中心平移到原点:

- 平移:将中心 ( (l+r)/2, (b+t)/2, (n+f)/2 ) 移至原点。
- 缩放:各轴长度分别为 (r−l)、(t−b)、(f−n),缩放到 [-1,1] 即除以半长,得到缩放因子 2/(r−l)、2/(t−b)、2/(f−n)。

因此正交投影矩阵可写为平移与缩放的组合,工程实现简洁稳定[^4]。

### 透视投影矩阵推导(相似三角形与齐次坐标)

相似三角形给出 x' = n/z · x,y' = n/z · y。为在齐次坐标中实现这一关系,构造透视挤压矩阵,将点 (x,y,z,1) 映射为 (n·x, n·y, ?, z)。深度项的选取需保证:

- 近平面 (z=n) 上的点变换后 xyz 不变;
- 远平面 (z=f) 上的点变换后 z 不变,中心点 (x=0,y=0) 的 x/y 也不变。

常用选择是第三行取 (0, 0, n+f, −n·f),得到透视到正交的挤压矩阵:

M_persp→ortho = 
[ [n, 0,   0,     0],
  [0, n,   0,     0],
  [0, 0, n+f, −n·f],
  [0, 0,   1,     0] ]

最终透视投影矩阵为 M_persp = M_ortho · M_persp→ortho。工程上,常以FOV与宽高比推导矩阵元素,便于与相机参数对接[^4][^3][^5]。

## 光栅化算法:DDA、Bresenham、扫描线

光栅化是将几何图元转换为屏幕像素的过程。直线绘制是基础,常用算法包括数值微分(DDA)与Bresenham;多边形填充常用扫描线算法。不同算法在精度、效率与实现复杂度上各有取舍。

DDA(Digital Differential Analyzer)以增量方式沿最大位移方向步进,通过浮点累加逼近直线;Bresenham以误差判别式替代浮点运算,仅用整数即可高效绘制直线。扫描线填充通过求交与区间填充高效处理多边形内部像素[^7][^8][^9][^10][^11]。

表3比较了DDA与Bresenham直线算法的关键特征。

表3 DDA与Bresenham直线算法比较

| 维度 | DDA | Bresenham |
|---|---|---|
| 核心思想 | 增量步进,最大位移方向每次 +1 | 误差累积判别,仅整数运算 |
| 数值类型 | 浮点累加 | 整数与符号判断 |
| 效率 | 较低(浮点开销) | 较高(无浮点,适合硬件) |
| 精度 | 直观,误差可控 | 误差判别稳定,像素选择最优 |
| 适用斜率 | 任意(需分象限处理) | 典型实现覆盖 0≤k≤1,可扩展 |
| 实现复杂度 | 低 | 中(需处理多象限) |

上述特征决定了DDA适合教学与快速原型,Bresenham更适合生产环境与硬件实现[^7][^8][^9][^10]。

### DDA直线算法

DDA算法根据斜率确定最大位移方向,每步在最大位移方向上加1,另一方向按斜率累加浮点增量并四舍五入到最近像素。优点是直观易懂,缺点是浮点运算开销较大且在极端斜率下可能引入累积误差。工程上,DDA常作为入门算法或验证基准[^7][^8]。

### Bresenham直线算法

Bresenham算法通过误差判别式 e 的符号决定是否在次要方向上步进,消除浮点运算,仅用整数实现。它在效率与精度之间取得良好平衡,是直线光栅化的经典方法。实际实现需处理垂直线、水平线、负斜率与多象限情况,可通过对称性与坐标交换统一处理[^7][^9][^10]。

### 扫描线多边形填充(概述)

扫描线填充的基本思想是:用水平扫描线自上而下(或自下而上)扫描多边形,求扫描线与多边形边的交点,将交点排序配对,形成填充区间,逐区间绘制像素。为高效处理,常用数据结构包括:

- 边表(Edge Table):按扫描线组织边的索引,记录每条边的ymax、xmin、斜率倒数等;
- 活动边表(Active Edge Table):当前扫描线与之相交的边的集合,维护交点x坐标与增量。

在工程中,扫描线填充可与直线光栅化协同工作,统一在帧缓冲中写入颜色;边界像素需一致地处理配对与奇偶性,避免漏填或重绘。出于资料与图示限制,本文不展开源码细节与复杂凹多边形、孔洞处理的完整实现[^11]。

## 纹理映射:UV坐标、重心坐标插值与采样

纹理映射将二维纹理图像贴合到三维模型表面,核心步骤包括:为顶点分配UV坐标、在三角形内进行重心坐标插值得到片元的UV坐标,再在纹理空间进行采样。采样在放大与缩小场景下需采用不同滤波策略,以平衡清晰度与伪影[^12][^13][^14][^15][^16]。

表4总结了常见纹理采样方法的滤波核与适用场景。

表4 纹理采样方法与滤波核/适用场景

| 方法 | 滤波核/机制 | 适用场景 | 特点 |
|---|---|---|---|
| 最近邻(Nearest) | Box(单位核) | 放大/像素风格 | 简单快速,硬边与锯齿 |
| 双线性(Bilinear) | Tent(三角核) | 放大,适度缩小 | 平滑过渡,软化细节 |
| 三线性(Trilinear) | 双线性 + 层间线性 | 缩小,mipmap层级间 | 平滑层级过渡,开销适中 |
| 各向异性(Anisotropic) | EWA/Ripmap等 | 倾斜视角矩形查询 | 减少模糊与拉伸伪影,开销较高 |

上述方法的选择取决于质量与性能权衡;工程中常以双线性+mipmap作为默认组合,在需要时启用各向异性过滤以处理视角倾斜导致的各向拉伸[^12][^13][^16]。

### UV坐标与投影映射

UV坐标取值范围通常为 [0,1],常见坐标系以左下角为原点,u向右、v向上。顶点UV分配可由美术建模时手工指定,或由算法自动生成(UV展开)。投影映射方法包括球面、平面、立方体与柱面等,适用于不同几何特征与需求。工程实践中,UV展开需考虑接缝、拉伸与纹理密度均匀性,以避免采样伪影与美术资源浪费[^12][^14]。

### 重心坐标插值

在三角形内,任意点的属性(包括UV坐标、颜色、法线等)可由顶点属性的重心坐标线性插值得到。重心坐标 (α, β, γ) 满足 α+β+γ=1 且 α,β,γ≥0。插值公式为 V = α·A + β·B + γ·C。数值稳定性方面,重心坐标计算可基于面积比或解线性系统;在狭长三角形中需注意精度损失与插值误差,必要时采用重心坐标的鲁棒计算与亚像素精度优化[^15][^13]。

### 纹理采样与过滤

放大时最近邻采样产生硬边与锯齿,双线性采样在四个纹素间进行两次线性插值,显著改善视觉质量。缩小时由于多个纹素覆盖一个屏幕像素,需使用mipmap以多级纹理降低高频伪影;三线性插值在mipmap层级间再插值,使层级过渡更平滑。各向异性过滤(如EWA、Ripmap)针对矩形查询区域的主方向进行加权采样,减轻倾斜视角下的模糊与拉伸伪影,但开销较高[^12][^16]。

## 深度缓冲(Z-buffer)与深度测试

深度缓冲(Z-buffer)是图像空间的隐藏面消除算法,通过为每个像素维护深度值与颜色值,逐像素比较并更新,实现遮挡关系的正确判定。算法初始化时将深度缓冲设为最大值(无穷远),帧缓冲设为背景色;对每个三角形内部采样点计算深度值,与缓冲中当前深度比较,若更近则更新深度与颜色[^17][^18][^19]。

表5给出Z-buffer算法流程与数据结构。

表5 Z-buffer算法流程与数据结构

| 步骤 | 说明 | 数据结构 |
|---|---|---|
| 初始化 | 深度缓冲 = ∞,帧缓冲 = 背景色 | 深度缓冲、帧缓冲 |
| 深度计算 | 对采样点计算 z(x,y)(观察空间或屏幕空间) | 深度缓冲单元 |
| 深度比较 | 新深度 < 当前深度 → 可见 | 深度比较逻辑 |
| 更新 | 写入颜色与深度 | 帧缓冲、深度缓冲 |

优点是原理简单、易于硬件实现与并行化,适合实时渲染;局限在于透明与半透明处理困难(仅能保留最近面),以及深度精度非线性导致的Z-fighting问题。改进方向包括A-buffer(维护每个像素的多边形列表以支持透明与反走样)与区间扫描线(在子区间内保证唯一可见面),但实现复杂度与存储开销相应增加[^18][^19]。

## 渲染管线总览:顶点处理、图元装配、光栅化、片段处理

现代可编程渲染管线由若干阶段组成,数据在阶段间传递并逐步转换为最终图像。顶点处理阶段执行MVP变换与自定义顶点着色器逻辑;图元装配将顶点组织成点、线、三角形等图元,并在光栅化前执行裁剪与背面剔除;光栅化阶段生成片元并插值属性(如UV、法线);片段处理阶段执行纹理采样、深度测试、模板测试与混合,最终写入帧缓冲[^1][^2][^20][^21][^22]。

表6总结各阶段输入/输出与典型操作。

表6 渲染管线阶段与输入/输出/典型操作

| 阶段 | 输入 | 输出 | 典型操作 |
|---|---|---|---|
| 顶点处理 | 顶点(位置、法线、UV等) | 裁剪空间顶点 | MVP变换、逐顶点计算 |
| 图元装配 | 顶点序列 | 图元(点/线/三角) | 裁剪、背面剔除、屏幕映射 |
| 光栅化 | 图元 | 片元队列 | 扫描转换、重心坐标插值 |
| 片段处理 | 片元(插值属性) | 像素(颜色、深度) | 纹理采样、深度/模板测试、混合 |

在可编程阶段中,顶点着色器负责空间变换与逐顶点计算,片段着色器负责逐片元着色与采样;固定功能阶段如深度测试、模板测试与混合则提供可配置的像素级处理。理解数据流与阶段职责,有助于在着色器与管线配置之间进行清晰的职责划分与性能优化[^1][^2][^20][^21][^22]。

## 工程实践与优化建议

从算法到工程落地,常见问题包括纹理放大锯齿、深度冲突(Z-fighting)、透明排序与性能瓶颈。以下建议聚焦于可操作的策略与权衡。

- 纹理放大/缩小:放大采用双线性或三线性插值以改善清晰度与过渡;缩小启用mipmap并视需求采用各向异性过滤,以减少模糊与拉伸伪影。默认组合为双线性+mipmap,质量与性能均衡[^12][^16]。
- 深度精度与Z-fighting:近远平面距离比过大导致深度压缩与精度下降,可通过提高near平面距离、降低far/near比值、启用非均匀深度映射或高深度精度缓冲来缓解;在多边形接近共面时适当倾斜多边形或使用法线偏移以避免精确重合[^19]。
- 透明渲染:Z-buffer仅保留最近面,难以正确处理半透明物体的累积颜色。工程上可采用亲深度排序(先画远后近,或按材质排序)、多通道渲染或A-buffer类方法,权衡复杂度与质量[^18]。
- 性能优化:减少不必要的图元与片段着色器复杂度;在光栅化前通过背面剔除与裁剪降低进入片段阶段的片元数量;在硬件支持时启用Early-Z(在片段着色前进行深度预测试)以减少过度绘制;谨慎使用各向异性过滤与高阶采样核,评估开销与视觉收益[^18][^19]。

上述策略需结合场景特征与硬件能力综合权衡,避免单一优化手段在复杂场景中失效。

## 结论与后续研究方向

本报告系统梳理了渲染管线的核心技术与数学原理,强调MVP矩阵的构建与空间语义、投影矩阵的推导(正交与透视)、光栅化算法的增量思想与整数优化(DDA与Bresenham)、纹理映射中的UV与重心坐标插值与采样过滤,以及Z-buffer的逐像素深度比较与工程优化路径。理解这些基础原理与算法细节,是在可编程管线中编写正确着色器、实现高效渲染与诊断常见问题的关键[^3][^4][^12][^17]。

后续研究方向包括:扫描线填充算法的源码级实现与复杂多边形(含孔洞与自交)处理的工程化方案;各项异性过滤(如EWA、Summed-Area Table、 Ripmap)的深入实现与性能评估;Early-Z、Z-fighting缓解与透明渲染的硬件行为与API差异;以及OpenGL与DirectX在投影矩阵与NDC约定上的差异分析与跨平台一致性策略。

---

## 核心算法完整代码实现

本章节提供图形渲染管线中核心算法的完整C++实现代码，包括DDA算法、Bresenham算法、Z-buffer深度测试、双线性插值、扫描线填充算法以及MVP矩阵变换的完整实现。

### 1. DDA直线光栅化算法完整实现

```cpp
#include <iostream>
#include <vector>
#include <iomanip>
#include <cmath>
#include <algorithm>

using namespace std;

struct Point {
    int x, y;
    Point(int x = 0, int y = 0) : x(x), y(y) {}
};

// DDA直线光栅化算法实现
vector<Point> DDA(int x1, int y1, int x2, int y2) {
    vector<Point> points;
    
    int dx = x2 - x1;
    int dy = y2 - y1;
    int steps = max(abs(dx), abs(dy));
    
    float xIncrement = static_cast<float>(dx) / steps;
    float yIncrement = static_cast<float>(dy) / steps;
    
    float x = x1;
    float y = y1;
    
    points.push_back(Point(x1, y1));
    
    for (int i = 0; i < steps; i++) {
        x += xIncrement;
        y += yIncrement;
        points.push_back(Point(static_cast<int>(round(x)), static_cast<int>(round(y))));
    }
    
    return points;
}

// 打印网格显示直线
void printGrid(const vector<Point>& points, int width, int height) {
    vector<vector<char>> grid(height, vector<char>(width, '.'));
    
    for (const auto& point : points) {
        if (point.x >= 0 && point.x < width && point.y >= 0 && point.y < height) {
            grid[height - 1 - point.y][point.x] = '*';
        }
    }
    
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            cout << grid[i][j] << " ";
        }
        cout << endl;
    }
}

// 打印坐标点序列
void printPoints(const vector<Point>& points) {
    cout << "坐标点序列: ";
    for (const auto& point : points) {
        cout << "(" << point.x << "," << point.y << ") ";
    }
    cout << endl;
}

int main() {
    // 测试DDA算法
    cout << "=== DDA直线光栅化算法测试 ===" << endl;
    
    // 测试用例1: 从(2,3)到(7,5)的直线
    cout << "\n测试用例1: 从(2,3)到(7,5)" << endl;
    vector<Point> line1 = DDA(2, 3, 7, 5);
    printPoints(line1);
    printGrid(line1, 10, 10);
    
    // 测试用例2: 垂直线
    cout << "\n测试用例2: 垂直线从(3,1)到(3,8)" << endl;
    vector<Point> line2 = DDA(3, 1, 3, 8);
    printPoints(line2);
    printGrid(line2, 10, 10);
    
    // 测试用例3: 水平线
    cout << "\n测试用例3: 水平线从(1,4)到(8,4)" << endl;
    vector<Point> line3 = DDA(1, 4, 8, 4);
    printPoints(line3);
    printGrid(line3, 10, 10);
    
    return 0;
}
```

### 2. Bresenham直线算法完整实现

```cpp
#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

struct Point {
    int x, y;
    Point(int x = 0, int y = 0) : x(x), y(y) {}
};

// Bresenham直线算法 - 处理所有象限
vector<Point> Bresenham(int x0, int y0, int x1, int y1) {
    vector<Point> points;
    
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;
    int err = dx - dy;
    
    points.push_back(Point(x0, y0));
    
    while (!(x0 == x1 && y0 == y1)) {
        int e2 = 2 * err;
        
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
        
        points.push_back(Point(x0, y0));
    }
    
    return points;
}

// Bresenham算法 - 传统实现（主要针对第一象限）
vector<Point> BresenhamTraditional(int x0, int y0, int x1, int y1) {
    vector<Point> points;
    
    int x = x0;
    int y = y0;
    int dx = x1 - x0;
    int dy = y1 - y0;
    int p = 2 * dy - dx;  // 初始决策参数
    
    points.push_back(Point(x, y));
    
    while (x < x1) {
        x++;
        
        if (p < 0) {
            p = p + 2 * dy;
        } else {
            y++;
            p = p + 2 * dy - 2 * dx;
        }
        
        points.push_back(Point(x, y));
    }
    
    return points;
}

// 打印网格显示直线
void printGrid(const vector<Point>& points, int width, int height) {
    vector<vector<char>> grid(height, vector<char>(width, '.'));
    
    for (const auto& point : points) {
        if (point.x >= 0 && point.x < width && point.y >= 0 && point.y < height) {
            grid[height - 1 - point.y][point.x] = '*';
        }
    }
    
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            cout << grid[i][j] << " ";
        }
        cout << endl;
    }
}

int main() {
    cout << "=== Bresenham直线算法测试 ===" << endl;
    
    // 测试用例1: 斜率 < 1
    cout << "\n测试用例1: 斜率 < 1 (2,3) 到 (10,6)" << endl;
    vector<Point> line1 = Bresenham(2, 3, 10, 6);
    printGrid(line1, 15, 10);
    
    // 测试用例2: 斜率 > 1
    cout << "\n测试用例2: 斜率 > 1 (3,2) 到 (6,10)" << endl;
    vector<Point> line2 = Bresenham(3, 2, 6, 10);
    printGrid(line2, 10, 15);
    
    // 测试用例3: 负斜率
    cout << "\n测试用例3: 负斜率 (10,8) 到 (3,2)" << endl;
    vector<Point> line3 = Bresenham(10, 8, 3, 2);
    printGrid(line3, 15, 10);
    
    // 测试用例4: 垂直线
    cout << "\n测试用例4: 垂直线 (5,1) 到 (5,10)" << endl;
    vector<Point> line4 = Bresenham(5, 1, 5, 10);
    printGrid(line4, 10, 15);
    
    // 测试用例5: 水平线
    cout << "\n测试用例5: 水平线 (2,5) 到 (12,5)" << endl;
    vector<Point> line5 = Bresenham(2, 5, 12, 5);
    printGrid(line5, 15, 10);
    
    return 0;
}
```

### 3. Z-buffer深度测试算法实现

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <limits>
#include <algorithm>

using namespace std;

struct Vec3 {
    float x, y, z;
    Vec3(float x = 0, float y = 0, float z = 0) : x(x), y(y), z(z) {}
};

struct Color {
    float r, g, b;
    Color(float r = 0, float g = 0, float b = 0) : r(r), g(g), b(b) {}
};

struct Triangle {
    Vec3 v0, v1, v2;
    Color color;
    
    Triangle(const Vec3& v0, const Vec3& v1, const Vec3& v2, const Color& color)
        : v0(v0), v1(v1), v2(v2), color(color) {}
};

class ZBuffer {
private:
    int width, height;
    vector<float> depthBuffer;
    vector<Color> frameBuffer;
    
public:
    ZBuffer(int width, int height) : width(width), height(height) {
        depthBuffer.resize(width * height, numeric_limits<float>::infinity());
        frameBuffer.resize(width * height, Color(0, 0, 0));
    }
    
    // 获取像素索引
    int getIndex(int x, int y) const {
        return y * width + x;
    }
    
    // 检查像素是否在屏幕范围内
    bool isInBounds(int x, int y) const {
        return x >= 0 && x < width && y >= 0 && y < height;
    }
    
    // 计算三角形内点的深度（重心坐标插值）
    float interpolateZ(const Vec3& p0, const Vec3& p1, const Vec3& p2, 
                      float alpha, float beta, float gamma) const {
        return alpha * p0.z + beta * p1.z + gamma * p2.z;
    }
    
    // 计算重心坐标
    void computeBarycentric(const Vec3& p, const Vec3& a, const Vec3& b, const Vec3& c,
                           float& alpha, float& beta, float& gamma) const {
        Vec3 v0 = {b.x - a.x, b.y - a.y, b.z - a.z};
        Vec3 v1 = {c.x - a.x, c.y - a.y, c.z - a.z};
        Vec3 v2 = {p.x - a.x, p.y - a.y, p.z - a.z};
        
        float d00 = v0.x * v0.x + v0.y * v0.y;
        float d01 = v0.x * v1.x + v0.y * v1.y;
        float d11 = v1.x * v1.x + v1.y * v1.y;
        float d20 = v2.x * v0.x + v2.y * v0.y;
        float d21 = v2.x * v1.x + v2.y * v1.y;
        
        float denom = d00 * d11 - d01 * d01;
        beta = (d11 * d20 - d01 * d21) / denom;
        gamma = (d00 * d21 - d01 * d20) / denom;
        alpha = 1.0f - beta - gamma;
    }
    
    // 光栅化三角形
    void rasterizeTriangle(const Triangle& tri) {
        // 计算三角形的包围盒
        int minX = max(0, (int)min({tri.v0.x, tri.v1.x, tri.v2.x}));
        int maxX = min(width - 1, (int)max({tri.v0.x, tri.v1.x, tri.v2.x}));
        int minY = max(0, (int)min({tri.v0.y, tri.v1.y, tri.v2.y}));
        int maxY = min(height - 1, (int)max({tri.v0.y, tri.v1.y, tri.v2.y}));
        
        // 遍历包围盒内的所有像素
        for (int y = minY; y <= maxY; y++) {
            for (int x = minX; x <= maxX; x++) {
                // 检查像素是否在三角形内
                Vec3 pixel = {(float)x + 0.5f, (float)y + 0.5f, 0};
                
                float alpha, beta, gamma;
                computeBarycentric(pixel, tri.v0, tri.v1, tri.v2, alpha, beta, gamma);
                
                // 如果重心坐标都在[0,1]范围内，则像素在三角形内
                if (alpha >= 0 && beta >= 0 && gamma >= 0) {
                    // 计算像素的深度值
                    float z = interpolateZ(tri.v0, tri.v1, tri.v2, alpha, beta, gamma);
                    
                    // 深度测试
                    int index = getIndex(x, y);
                    if (z < depthBuffer[index]) {
                        depthBuffer[index] = z;
                        frameBuffer[index] = tri.color;
                    }
                }
            }
        }
    }
    
    // 渲染场景
    void render(const vector<Triangle>& triangles) {
        for (const auto& triangle : triangles) {
            rasterizeTriangle(triangle);
        }
    }
    
    // 获取像素颜色
    Color getPixel(int x, int y) const {
        if (isInBounds(x, y)) {
            return frameBuffer[getIndex(x, y)];
        }
        return Color(0, 0, 0);
    }
    
    // 获取像素深度
    float getDepth(int x, int y) const {
        if (isInBounds(x, y)) {
            return depthBuffer[getIndex(x, y)];
        }
        return numeric_limits<float>::infinity();
    }
    
    // 清除缓冲区
    void clear() {
        fill(depthBuffer.begin(), depthBuffer.end(), numeric_limits<float>::infinity());
        fill(frameBuffer.begin(), frameBuffer.end(), Color(0, 0, 0));
    }
    
    // 保存为PPM格式
    void savePPM(const string& filename) const {
        ofstream file(filename);
        file << "P3\n" << width << " " << height << "\n255\n";
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                Color color = getPixel(x, y);
                int r = (int)min(255, max(0, color.r * 255));
                int g = (int)min(255, max(0, color.g * 255));
                int b = (int)min(255, max(0, color.b * 255));
                file << r << " " << g << " " << b << " ";
            }
            file << "\n";
        }
        
        file.close();
    }
};

int main() {
    cout << "=== Z-buffer深度测试算法测试 ===" << endl;
    
    // 创建Z-buffer
    ZBuffer zbuffer(800, 600);
    
    // 创建测试三角形
    vector<Triangle> triangles;
    
    // 三角形1: 红色，在前景
    triangles.push_back(Triangle(
        Vec3(200, 150, 0.5f),   // v0
        Vec3(400, 150, 0.5f),   // v1
        Vec3(300, 350, 0.5f),   // v2
        Color(1.0f, 0.0f, 0.0f) // 红色
    ));
    
    // 三角形2: 蓝色，在背景
    triangles.push_back(Triangle(
        Vec3(250, 200, 1.0f),   // v0
        Vec3(450, 200, 1.0f),   // v1
        Vec3(350, 400, 1.0f),   // v2
        Color(0.0f, 0.0f, 1.0f) // 蓝色
    ));
    
    // 三角形3: 绿色，在中间
    triangles.push_back(Triangle(
        Vec3(100, 100, 0.8f),   // v0
        Vec3(500, 100, 0.8f),   // v1
        Vec3(300, 500, 0.8f),   // v2
        Color(0.0f, 1.0f, 0.0f) // 绿色
    ));
    
    // 渲染场景
    cout << "正在渲染场景..." << endl;
    zbuffer.render(triangles);
    
    // 保存结果
    zbuffer.savePPM("zbuffer_test.ppm");
    cout << "结果已保存到 zbuffer_test.ppm" << endl;
    
    // 测试深度查询
    cout << "\n深度测试:" << endl;
    cout << "像素(300,250)的深度值: " << zbuffer.getDepth(300, 250) << endl;
    
    return 0;
}
```

### 4. 双线性插值纹理映射算法实现

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

using namespace std;

struct Color {
    float r, g, b;
    Color(float r = 0, float g = 0, float b = 0) : r(r), g(g), b(b) {}
};

class Texture {
private:
    int width, height;
    vector<Color> data;
    
public:
    Texture(int width, int height) : width(width), height(height) {
        data.resize(width * height, Color(0, 0, 0));
    }
    
    // 设置像素颜色
    void setPixel(int x, int y, const Color& color) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            data[y * width + x] = color;
        }
    }
    
    // 获取像素颜色
    Color getPixel(int x, int y) const {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            return data[y * width + x];
        }
        return Color(0, 0, 0);
    }
    
    // 双线性插值
    Color bilinearSample(float u, float v) const {
        // 将UV坐标映射到纹理坐标
        float x = u * (width - 1);
        float y = v * (height - 1);
        
        int x1 = (int)floor(x);
        int y1 = (int)floor(y);
        int x2 = min(x1 + 1, width - 1);
        int y2 = min(y1 + 1, height - 1);
        
        float fx = x - x1;
        float fy = y - y1;
        
        // 获取四个角点的颜色
        Color c11 = getPixel(x1, y1);
        Color c21 = getPixel(x2, y1);
        Color c12 = getPixel(x1, y2);
        Color c22 = getPixel(x2, y2);
        
        // 双线性插值
        Color result;
        result.r = c11.r * (1 - fx) * (1 - fy) + 
                   c21.r * fx * (1 - fy) + 
                   c12.r * (1 - fx) * fy + 
                   c22.r * fx * fy;
        
        result.g = c11.g * (1 - fx) * (1 - fy) + 
                   c21.g * fx * (1 - fy) + 
                   c12.g * (1 - fx) * fy + 
                   c22.g * fx * fy;
        
        result.b = c11.b * (1 - fx) * (1 - fy) + 
                   c21.b * fx * (1 - fy) + 
                   c12.b * (1 - fx) * fy + 
                   c22.b * fx * fy;
        
        return result;
    }
    
    // 最近邻采样
    Color nearestSample(float u, float v) const {
        int x = (int)round(u * (width - 1));
        int y = (int)round(v * (height - 1));
        return getPixel(x, y);
    }
    
    int getWidth() const { return width; }
    int getHeight() const { return height; }
};

// 纹理映射到三角形
void mapTextureToTriangle(const Texture& texture, 
                         const vector<pair<float, float>>& uvCoords,
                         const vector<Color>& vertexColors,
                         const vector<pair<float, float>>& screenCoords) {
    
    cout << "纹理映射测试:" << endl;
    cout << "纹理尺寸: " << texture.getWidth() << "x" << texture.getHeight() << endl;
    
    // 测试不同UV坐标的采样
    vector<pair<float, float>> testUVs = {
        {0.0f, 0.0f}, {0.5f, 0.0f}, {1.0f, 0.0f},
        {0.0f, 0.5f}, {0.5f, 0.5f}, {1.0f, 0.5f},
        {0.0f, 1.0f}, {0.5f, 1.0f}, {1.0f, 1.0f}
    };
    
    cout << "\n双线性插值采样结果:" << endl;
    for (const auto& uv : testUVs) {
        Color color = texture.bilinearSample(uv.first, uv.second);
        cout << "UV(" << uv.first << "," << uv.second << ") -> "
             << "RGB(" << color.r << "," << color.g << "," << color.b << ")" << endl;
    }
    
    cout << "\n最近邻采样结果:" << endl;
    for (const auto& uv : testUVs) {
        Color color = texture.nearestSample(uv.first, uv.second);
        cout << "UV(" << uv.first << "," << uv.second << ") -> "
             << "RGB(" << color.r << "," << color.g << "," << color.b << ")" << endl;
    }
}

int main() {
    cout << "=== 双线性插值纹理映射算法测试 ===" << endl;
    
    // 创建测试纹理 (8x8)
    Texture texture(8, 8);
    
    // 填充测试纹理
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            float r = x / 7.0f;  // 红色渐变
            float g = y / 7.0f;  // 绿色渐变
            float b = 0.5f;      // 固定蓝色
            texture.setPixel(x, y, Color(r, g, b));
        }
    }
    
    // 创建测试三角形UV坐标和顶点颜色
    vector<pair<float, float>> uvCoords = {
        {0.0f, 0.0f}, {1.0f, 0.0f}, {0.5f, 1.0f}
    };
    
    vector<Color> vertexColors = {
        Color(1.0f, 0.0f, 0.0f),  // 红色
        Color(0.0f, 1.0f, 0.0f),  // 绿色
        Color(0.0f, 0.0f, 1.0f)   // 蓝色
    };
    
    vector<pair<float, float>> screenCoords = {
        {100.0f, 100.0f}, {200.0f, 100.0f}, {150.0f, 200.0f}
    };
    
    // 执行纹理映射测试
    mapTextureToTriangle(texture, uvCoords, vertexColors, screenCoords);
    
    return 0;
}
```

### 5. 扫描线多边形填充算法实现

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

using namespace std;

struct Point {
    float x, y;
    Point(float x = 0, float y = 0) : x(x), y(y) {}
};

struct Edge {
    int y_max;      // 边的最大y坐标
    float x;        // 当前扫描线与边的交点x坐标
    float dx;       // 斜率的倒数 (Δx)
    Edge* pNext;    // 下一条边
    
    Edge(int y_max, float x, float dx) : y_max(y_max), x(x), dx(dx), pNext(nullptr) {}
};

class ScanLineFiller {
private:
    int width, height;
    vector<vector<char>> grid;
    
    // 创建边表
    vector<Edge*> createEdgeTable(const vector<Point>& vertices) {
        int n = vertices.size();
        vector<Edge*> edgeTable(height, nullptr);
        
        for (int i = 0; i < n; i++) {
            Point p1 = vertices[i];
            Point p2 = vertices[(i + 1) % n];
            
            // 跳过水平边
            if (abs(p1.y - p2.y) < 1e-6) continue;
            
            // 确保从下到上处理边
            Point start = (p1.y < p2.y) ? p1 : p2;
            Point end = (p1.y < p2.y) ? p2 : p1;
            
            int y_max = (int)end.y;
            float x_start = start.x;
            float dx = (end.x - start.x) / (end.y - start.y);
            
            // 创建边节点
            Edge* newEdge = new Edge(y_max, x_start, dx);
            
            // 插入边表
            int y_min = (int)start.y;
            newEdge->pNext = edgeTable[y_min];
            edgeTable[y_min] = newEdge;
        }
        
        return edgeTable;
    }
    
    // 更新活化边表
    void updateActiveEdgeTable(vector<Edge*>& activeEdges, const vector<Edge*>& edgeTable, int y) {
        // 从边表添加新边
        Edge* newEdge = edgeTable[y];
        while (newEdge != nullptr) {
            activeEdges.push_back(newEdge);
            newEdge = newEdge->pNext;
        }
        
        // 移除超出扫描线的边
        activeEdges.erase(
            remove_if(activeEdges.begin(), activeEdges.end(),
                     [y](Edge* edge) { return edge->y_max <= y; }),
            activeEdges.end()
        );
        
        // 按x坐标排序
        sort(activeEdges.begin(), activeEdges.end(), 
             [](Edge* a, Edge* b) { return a->x < b->x; });
    }
    
    // 填充扫描线
    void fillScanLine(int y, const vector<Edge*>& activeEdges) {
        if (activeEdges.size() < 2) return;
        
        // 配对边
        for (size_t i = 0; i + 1 < activeEdges.size(); i += 2) {
            int x_start = (int)ceil(activeEdges[i]->x);
            int x_end = (int)floor(activeEdges[i + 1]->x);
            
            for (int x = x_start; x <= x_end && x < width; x++) {
                if (x >= 0 && y >= 0 && x < width && y < height) {
                    grid[y][x] = '*';
                }
            }
        }
        
        // 更新边的x坐标
        for (Edge* edge : activeEdges) {
            edge->x += edge->dx;
        }
    }
    
public:
    ScanLineFiller(int width, int height) : width(width), height(height) {
        grid.resize(height, vector<char>(width, '.'));
    }
    
    // 扫描线填充算法
    void fillPolygon(const vector<Point>& vertices) {
        // 创建边表
        vector<Edge*> edgeTable = createEdgeTable(vertices);
        
        // 初始化活化边表
        vector<Edge*> activeEdges;
        
        // 从最小y坐标开始扫描
        int minY = height, maxY = 0;
        for (const auto& vertex : vertices) {
            minY = min(minY, (int)vertex.y);
            maxY = max(maxY, (int)vertex.y);
        }
        
        for (int y = minY; y <= maxY && y < height; y++) {
            // 更新活化边表
            updateActiveEdgeTable(activeEdges, edgeTable, y);
            
            // 填充当前扫描线
            fillScanLine(y, activeEdges);
        }
        
        // 清理内存
        for (auto edgePtr : edgeTable) {
            while (edgePtr != nullptr) {
                Edge* temp = edgePtr;
                edgePtr = edgePtr->pNext;
                delete temp;
            }
        }
    }
    
    // 打印网格
    void printGrid() const {
        for (int i = height - 1; i >= 0; i--) {
            for (int j = 0; j < width; j++) {
                cout << grid[i][j] << " ";
            }
            cout << endl;
        }
    }
    
    // 清除网格
    void clear() {
        for (int i = 0; i < height; i++) {
            fill(grid[i].begin(), grid[i].end(), '.');
        }
    }
};

int main() {
    cout << "=== 扫描线多边形填充算法测试 ===" << endl;
    
    ScanLineFiller filler(20, 15);
    
    // 测试用例1: 三角形
    cout << "\n测试用例1: 三角形" << endl;
    vector<Point> triangle = {
        Point(5, 2), Point(15, 2), Point(10, 12)
    };
    filler.fillPolygon(triangle);
    filler.printGrid();
    
    filler.clear();
    
    // 测试用例2: 矩形
    cout << "\n测试用例2: 矩形" << endl;
    vector<Point> rectangle = {
        Point(3, 3), Point(12, 3), Point(12, 10), Point(3, 10)
    };
    filler.fillPolygon(rectangle);
    filler.printGrid();
    
    filler.clear();
    
    // 测试用例3: 五边形
    cout << "\n测试用例3: 五边形" << endl;
    vector<Point> pentagon = {
        Point(6, 4), Point(10, 2), Point(14, 4), Point(12, 10), Point(8, 10)
    };
    filler.fillPolygon(pentagon);
    filler.printGrid();
    
    return 0;
}
```

### 6. MVP矩阵变换完整实现

```cpp
#include <iostream>
#include <cmath>
#include <array>
#include <stdexcept>

using namespace std;

class Matrix4 {
public:
    static const int M00 = 0, M10 = 1, M20 = 2, M30 = 3;
    static const int M01 = 4, M11 = 5, M21 = 6, M31 = 7;
    static const int M02 = 8, M12 = 9, M22 = 10, M32 = 11;
    static const int M03 = 12, M13 = 13, M23 = 14, M33 = 15;
    
    array<float, 16> m;
    
    // 构造函数
    Matrix4() {
        m.fill(0.0f);
        m[M00] = m[M11] = m[M22] = m[M33] = 1.0f; // 单位矩阵
    }
    
    // 矩阵乘法
    Matrix4 operator*(const Matrix4& other) const {
        Matrix4 result;
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 4; col++) {
                result.m[row * 4 + col] = 0.0f;
                for (int k = 0; k < 4; k++) {
                    result.m[row * 4 + col] += m[row * 4 + k] * other.m[k * 4 + col];
                }
            }
        }
        return result;
    }
    
    // 矩阵-向量乘法
    array<float, 4> operator*(const array<float, 4>& vec) const {
        array<float, 4> result;
        for (int i = 0; i < 4; i++) {
            result[i] = m[i * 4 + 0] * vec[0] + 
                       m[i * 4 + 1] * vec[1] + 
                       m[i * 4 + 2] * vec[2] + 
                       m[i * 4 + 3] * vec[3];
        }
        return result;
    }
    
    // 平移矩阵
    static Matrix4 translation(float x, float y, float z) {
        Matrix4 mat;
        mat.m[M03] = x;
        mat.m[M13] = y;
        mat.m[M23] = z;
        return mat;
    }
    
    // 缩放矩阵
    static Matrix4 scaling(float x, float y, float z) {
        Matrix4 mat;
        mat.m[M00] = x;
        mat.m[M11] = y;
        mat.m[M22] = z;
        return mat;
    }
    
    // 旋转矩阵 - X轴
    static Matrix4 rotationX(float angle) {
        float rad = angle * M_PI / 180.0f;
        float c = cos(rad), s = sin(rad);
        Matrix4 mat;
        mat.m[M11] = c;
        mat.m[M12] = -s;
        mat.m[M21] = s;
        mat.m[M22] = c;
        return mat;
    }
    
    // 旋转矩阵 - Y轴
    static Matrix4 rotationY(float angle) {
        float rad = angle * M_PI / 180.0f;
        float c = cos(rad), s = sin(rad);
        Matrix4 mat;
        mat.m[M00] = c;
        mat.m[M02] = s;
        mat.m[M20] = -s;
        mat.m[M22] = c;
        return mat;
    }
    
    // 旋转矩阵 - Z轴
    static Matrix4 rotationZ(float angle) {
        float rad = angle * M_PI / 180.0f;
        float c = cos(rad), s = sin(rad);
        Matrix4 mat;
        mat.m[M00] = c;
        mat.m[M01] = -s;
        mat.m[M10] = s;
        mat.m[M11] = c;
        return mat;
    }
    
    // 视图矩阵
    static Matrix4 lookAt(float eyeX, float eyeY, float eyeZ,
                         float centerX, float centerY, float centerZ,
                         float upX, float upY, float upZ) {
        
        // 计算前向量
        float fx = centerX - eyeX;
        float fy = centerY - eyeY;
        float fz = centerZ - eyeZ;
        float fLen = sqrt(fx*fx + fy*fy + fz*fz);
        fx /= fLen; fy /= fLen; fz /= fLen;
        
        // 计算右向量
        float sx = fy * upZ - fz * upY;
        float sy = fz * upX - fx * upZ;
        float sz = fx * upY - fy * upX;
        float sLen = sqrt(sx*sx + sy*sy + sz*sz);
        sx /= sLen; sy /= sLen; sz /= sLen;
        
        // 计算上向量
        float ux = sy * fz - sz * fy;
        float uy = sz * fx - sx * fz;
        float uz = sx * fy - sy * fx;
        
        Matrix4 mat;
        mat.m[M00] = sx; mat.m[M01] = sy; mat.m[M02] = sz;
        mat.m[M10] = ux; mat.m[M11] = uy; mat.m[M12] = uz;
        mat.m[M20] = -fx; mat.m[M21] = -fy; mat.m[M22] = -fz;
        mat.m[M03] = -(sx * eyeX + sy * eyeY + sz * eyeZ);
        mat.m[M13] = -(ux * eyeX + uy * eyeY + uz * eyeZ);
        mat.m[M23] = (fx * eyeX + fy * eyeY + fz * eyeZ);
        
        return mat;
    }
    
    // 透视投影矩阵
    static Matrix4 perspective(float fovY, float aspect, float near, float far) {
        float f = 1.0f / tan(fovY * M_PI / 360.0f);
        Matrix4 mat;
        
        mat.m[M00] = f / aspect;
        mat.m[M11] = f;
        mat.m[M22] = (far + near) / (near - far);
        mat.m[M23] = (2 * far * near) / (near - far);
        mat.m[M32] = -1;
        mat.m[M33] = 0;
        
        return mat;
    }
    
    // 正交投影矩阵
    static Matrix4 orthographic(float left, float right, float bottom, float top, float near, float far) {
        Matrix4 mat;
        
        mat.m[M00] = 2 / (right - left);
        mat.m[M11] = 2 / (top - bottom);
        mat.m[M22] = -2 / (far - near);
        mat.m[M03] = -(right + left) / (right - left);
        mat.m[M13] = -(top + bottom) / (top - bottom);
        mat.m[M23] = -(far + near) / (far - near);
        
        return mat;
    }
    
    // 打印矩阵
    void print() const {
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                cout << m[i * 4 + j] << " ";
            }
            cout << endl;
        }
    }
};

struct Vec3 {
    float x, y, z;
    Vec3(float x = 0, float y = 0, float z = 0) : x(x), y(y), z(z) {}
};

// MVP变换测试
void testMVP() {
    cout << "=== MVP矩阵变换测试 ===" << endl;
    
    // 创建模型矩阵
    Matrix4 model = Matrix4::rotationY(45.0f) * Matrix4::scaling(2.0f, 1.0f, 1.0f);
    cout << "\n模型矩阵 (旋转45度 + 缩放):" << endl;
    model.print();
    
    // 创建视图矩阵
    Matrix4 view = Matrix4::lookAt(0, 0, 5, 0, 0, 0, 0, 1, 0);
    cout << "\n视图矩阵 (相机位置(0,0,5), 看向原点):" << endl;
    view.print();
    
    // 创建投影矩阵
    Matrix4 projection = Matrix4::perspective(45.0f, 800.0f/600.0f, 0.1f, 100.0f);
    cout << "\n投影矩阵 (FOV=45度, 宽高比=4/3):" << endl;
    projection.print();
    
    // 计算MVP矩阵
    Matrix4 mvp = projection * view * model;
    cout << "\nMVP矩阵:" << endl;
    mvp.print();
    
    // 测试点变换
    Vec3 point(1, 1, 1);
    array<float, 4> homogeneous = {point.x, point.y, point.z, 1.0f};
    array<float, 4> transformed = mvp * homogeneous;
    
    cout << "\n点变换测试:" << endl;
    cout << "原始点: (" << point.x << ", " << point.y << ", " << point.z << ")" << endl;
    cout << "变换后: (" << transformed[0] << ", " << transformed[1] << ", " << transformed[2] << ", " << transformed[3] << ")" << endl;
    
    if (abs(transformed[3]) > 1e-6) {
        cout << "透视除法后: (" << transformed[0]/transformed[3] << ", " 
             << transformed[1]/transformed[3] << ", " << transformed[2]/transformed[3] << ")" << endl;
    }
}

int main() {
    testMVP();
    return 0;
}
```

### 7. 透视投影矩阵推导与实现

```cpp
#include <iostream>
#include <cmath>

using namespace std;

class PerspectiveProjection {
public:
    // 基于相似三角形推导透视投影矩阵
    static void derivePerspectiveMatrix() {
        cout << "=== 透视投影矩阵数学推导 ===" << endl;
        
        cout << "\n1. 相似三角形关系:" << endl;
        cout << "   对于观察空间中的点 (x, y, z)，投影到近平面 z = -n" << endl;
        cout << "   x' = (n / -z) * x" << endl;
        cout << "   y' = (n / -z) * y" << endl;
        cout << "   其中 n 是近平面距离" << endl;
        
        cout << "\n2. 齐次坐标表示:" << endl;
        cout << "   原始点: [x, y, z, 1]" << endl;
        cout << "   透视变换: [n*x, n*y, ?, z]" << endl;
        
        cout << "\n3. 深度项确定:" << endl;
        cout << "   近平面 (z = -n): 变换后 z' = n" << endl;
        cout << "   远平面 (z = -f): 变换后 z' = f" << endl;
        cout << "   线性插值: z' = (f + n) + (-f*n)/z" << endl;
        
        cout << "\n4. 最终透视投影矩阵:" << endl;
        cout << "   [ n     0     0      0  ]" << endl;
        cout << "   [ 0     n     0      0  ]" << endl;
        cout << "   [ 0     0   n+f   -f*n  ]" << endl;
        cout << "   [ 0     0     1      0  ]" << endl;
    }
    
    // 基于FOV和宽高比的透视投影矩阵
    static void perspectiveFromFOV(float fovY, float aspect, float near, float far) {
        cout << "\n=== 基于FOV的透视投影矩阵 ===" << endl;
        
        float f = 1.0f / tan(fovY * M_PI / 360.0f);
        
        cout << "\n参数:" << endl;
        cout << "  FOV: " << fovY << " 度" << endl;
        cout << "  宽高比: " << aspect << endl;
        cout << "  近平面: " << near << endl;
        cout << "  远平面: " << far << endl;
        cout << "  f = 1/tan(FOV/2) = " << f << endl;
        
        cout << "\n透视投影矩阵:" << endl;
        cout << "  [ f/aspect    0         0              0    ]" << endl;
        cout << "  [    0        f         0              0    ]" << endl;
        cout << "  [    0        0    (f+n)/(n-f)   (2*f*n)/(n-f) ]" << endl;
        cout << "  [    0        0        -1              0    ]" << endl;
    }
    
    // 验证透视变换
    static void verifyPerspectiveTransform(float x, float y, float z, float n, float f) {
        cout << "\n=== 透视变换验证 ===" << endl;
        cout << "原始点: (" << x << ", " << y << ", " << z << ")" << endl;
        
        // 相似三角形方法
        float x_proj = (n / -z) * x;
        float y_proj = (n / -z) * y;
        
        cout << "\n相似三角形方法:" << endl;
        cout << "  x' = (n/-z) * x = (" << n << "/-" << z << ") * " << x << " = " << x_proj << endl;
        cout << "  y' = (n/-z) * y = (" << n << "/-" << z << ") * " << y << " = " << y_proj << endl;
        
        // 矩阵变换方法
        float z_prime = ((f + n) + (-f * n) / z);
        
        cout << "\n矩阵变换方法:" << endl;
        cout << "  z' = (f+n) + (-f*n)/z = (" << f << "+" << n << ") + (-" << f << "*" << n << ")/" << z << " = " << z_prime << endl;
        
        // 透视除法
        float w = z; // 齐次坐标的w分量
        cout << "\n透视除法:" << endl;
        cout << "  齐次坐标: [" << x_proj << ", " << y_proj << ", " << z_prime << ", " << w << "]" << endl;
        cout << "  除以w后: [" << x_proj/w << ", " << y_proj/w << ", " << z_prime/w << "]" << endl;
    }
};

int main() {
    // 推导透视投影矩阵
    PerspectiveProjection::derivePerspectiveMatrix();
    
    // 基于FOV计算透视投影矩阵
    PerspectiveProjection::perspectiveFromFOV(45.0f, 4.0f/3.0f, 0.1f, 100.0f);
    
    // 验证透视变换
    PerspectiveProjection::verifyPerspectiveTransform(2.0f, 1.0f, -5.0f, 0.1f, 100.0f);
    
    return 0;
}
```

### 8. 算法性能对比

```cpp
#include <chrono>
#include <random>

class AlgorithmBenchmark {
public:
    // 生成随机测试数据
    static vector<pair<int, int>> generateRandomLines(int count) {
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dis(0, 100);
        
        vector<pair<int, int>> lines;
        for (int i = 0; i < count; i++) {
            lines.push_back({dis(gen), dis(gen)});
            lines.push_back({dis(gen), dis(gen)});
        }
        return lines;
    }
    
    // DDA算法性能测试
    template<typename LineFunc>
    static double benchmarkDDA(const vector<pair<int, int>>& lines, LineFunc drawLine) {
        auto start = chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < lines.size(); i += 2) {
            int x1 = lines[i].first, y1 = lines[i].second;
            int x2 = lines[i+1].first, y2 = lines[i+1].second;
            drawLine(x1, y1, x2, y2);
        }
        
        auto end = chrono::high_resolution_clock::now();
        return chrono::duration<double, milli>(end - start).count();
    }
    
    // Bresenham算法性能测试
    template<typename LineFunc>
    static double benchmarkBresenham(const vector<pair<int, int>>& lines, LineFunc drawLine) {
        auto start = chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < lines.size(); i += 2) {
            int x1 = lines[i].first, y1 = lines[i].second;
            int x2 = lines[i+1].first, y2 = lines[i+1].second;
            drawLine(x1, y1, x2, y2);
        }
        
        auto end = chrono::high_resolution_clock::now();
        return chrono::duration<double, milli>(end - start).count();
    }
};

int main() {
    cout << "=== 算法性能对比测试 ===" << endl;
    
    // 生成测试数据
    auto lines = AlgorithmBenchmark::generateRandomLines(1000);
    
    // 空绘制函数用于性能测试
    auto emptyDraw = [](int x1, int y1, int x2, int y2) {
        // 空操作，仅用于测试算法开销
    };
    
    // DDA性能测试
    cout << "\nDDA算法性能测试:" << endl;
    double ddaTime = AlgorithmBenchmark::benchmarkDDA(lines, emptyDraw);
    cout << "  绘制1000条直线耗时: " << ddaTime << " ms" << endl;
    
    // Bresenham性能测试
    cout << "\nBresenham算法性能测试:" << endl;
    double bresenhamTime = AlgorithmBenchmark::benchmarkBresenham(lines, emptyDraw);
    cout << "  绘制1000条直线耗时: " << bresenhamTime << " ms" << endl;
    
    // 性能对比
    cout << "\n性能对比:" << endl;
    if (bresenhamTime < ddaTime) {
        cout << "  Bresenham比DDA快 " << (ddaTime/bresenhamTime) << " 倍" << endl;
    } else {
        cout << "  DDA比Bresenham快 " << (bresenhamTime/ddaTime) << " 倍" << endl;
    }
    
    return 0;
}
```

---

## 参考文献

[^1]: 如何理解 OpenGL 中着色器、渲染管线、光栅化. https://cloud.tencent.com/developer/article/2330048
[^2]: WebGPU入门(二):着色器、图元装配与光栅化. https://juejin.cn/post/7231430726432079933
[^3]: GPU渲染管线中的MVP变换矩阵. https://www.yumefx.com/?p=3889
[^4]: 【3】现代计算机图形学(正交投影,透视投影,MVP变换). https://blog.csdn.net/qq_43149051/article/details/105925787
[^5]: 深入理解透视矩阵. https://www.zhyingkun.com/perspective/perspective/
[^6]: 什么是图形变换管线:图形变换管线定义 | Unity. https://unity.com/cn/glossary/graphics-transformation-pipeline
[^7]: 二维光栅图形的扫描:直线的DDA、Bresenham算法. https://zhuanlan.zhihu.com/p/120955585
[^8]: 计算机图形学的奠基-2万字说清DDA直线光栅化算法. https://zhuanlan.zhihu.com/p/1960423688957560055
[^9]: [计算机图形学]光栅化算法:DDA和Bresenham算法. https://www.codeleading.com/article/54895068335/
[^10]: 【图形学】直线光栅化算法(DDA,Bresenham,中点). https://blog.csdn.net/m0_72895175/article/details/135623887
[^11]: 计算机图形学 - 多边形填充算法. https://tutorialspoint.org.cn/computer_graphics/polygon_filling_algorithm.htm
[^12]: 一文读懂:计算机图形学基础之“纹理映射”. https://zhuanlan.zhihu.com/p/646544508
[^13]: 第十四章 纹理映(北大VCI课程讲义). https://vcl.pku.edu.cn/course/vci/notes/14-texture-notes.pdf
[^14]: 计算机图形学12:纹理映射. https://forliage.github.io/_posts/2025-08-27-cg12.html
[^15]: 重心坐标与插值、纹理映射 - Tim's Note. https://zouchanglin.cn/post/11-10-barycentric-coordinates-interpolation-texture-mapping/
[^16]: GAMES101学习笔记(五):Texture 纹理(纹理映射). https://jishuzhan.net/article/1886012145007595521
[^17]: Z-Buffer与深度测试详解. https://www.yumefx.com/?p=4017
[^18]: 深度缓存器算法(Z-buffer)简介 - 哔哩哔哩. https://www.bilibili.com/opus/924961025886781473
[^19]: 计算机图形学 学习笔记(六):消隐算法:Z-buffer,区间扫描线. https://blog.csdn.net/jurbo/article/details/75007260
[^20]: OpenGL基础——渲染管线 - 简书. https://www.jianshu.com/p/a5c7e5585275
[^21]: OpenGL图形渲染管线(Pipeline)学习 - CSDN. https://blog.csdn.net/u012169524/article/details/113344328
[^22]: 渲染管线 | ShaderFans. https://www.shaderfans.com/post/xuan-ran-guan-xian/index.html