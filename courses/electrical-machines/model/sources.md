# 研究依据与实际查阅范围

核查日期：2026年10月26日。以下用于核对构造规则与模型边界；本模块代码、几何、区间接触算法和校核均为本次重构，不复制资料插图。

1. IIT Madras / NPTEL，Krishna Vasudevan、G. Sridhara Rao、P. Sasidhara Rao，*Electrical Machines I*, §4 Armature Windings：[官方PDF](https://archive.nptel.ac.in/content/storage2/courses/108106071/pdfs/2_4.pdf)。取得16页讲义，重点查阅印刷页29—38的双层鼓式、整距、单叠接片、支路与均压连接；波绕不属于本实现。
2. James L. Kirtley Jr., MIT 6.685，*DC (Commutator) and Permanent Magnet Machines*：[官方资源页](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/resources/mit6_685f13_chapter6/)。查阅运动电势、换向短接、换向极与补偿相关部分；用于区分原理模型和实际换向过程。
3. Altair FluxMotor，*DC winding*：[官方技术文档](https://help.altair.com/FluxMotor/topics/MC_winding_dc_winding.htm)。查阅线圈跨距、换向器节距、单叠叠进、并联支路及铜线长度／槽面积／电阻字段定义；未运行商业有限元软件或引用其仿真结果。
4. Mersen，*TDS-06 Setting the Neutral*，EN-2304：[官方9页PDF](https://www.mersen.com/sites/default/files/files_imported/ptt-tds-06-setting-the-neutral-en-2304.pdf)。查阅中性线及静态／运行中性位置差别；本页几何零位不代替负载下的实机刷位数据。
5. Mersen，*Carbon Brushes for Motors and Generators*，EN-2608：[官方手册](https://www.mersen.com/sites/default/files/medias/files/2026-08/ptt-carbon-brushes-for-motors-and-generators-mersen-EN-2608.pdf)。仅查阅前部接触、压降和机械条件相关内容，不声称完成整本材料选型或将某刷牌号用于本例。
6. U.S. Bureau of Standards，*Copper Wire Tables*, Circular No.31，第4版：[美国政府馆藏PDF](https://www.govinfo.gov/content/pkg/GOVPUB-C13-0623ad8ee79f1b1d92b7a3d7465714eb/pdf/GOVPUB-C13-0623ad8ee79f1b1d92b7a3d7465714eb.pdf)。取得PDF，查阅标准退火铜20°C电阻率0.017241 Ω·mm²/m与电阻温度系数0.00393/°C相关段落；作为参考材料值，不等于指定供应商铜线的实测值或现行产品认证。

本例的−半片距、接触区间、有限刷宽约束、支路提取及电势／转矩符号，均在上述构造规则上自行推导并独立测试。示例参数不是任何制造商产品数据；24组模型的扫角测试也不是制造商认证。

## 解析磁场与独立积分

为使参考场在均匀域中同时满足无散和无旋条件，设轴向矢势 Aₓ=(BₘR/p)(r/R)ᵖcos(pψ)，再取 Bᵣ=(1/r)∂Aₓ/∂ψ、Bθ=−∂Aₓ/∂r。这里只指定一个理想谐波基准，不求解铁心、槽、饱和或励磁边界。有效导体处的径向场随实际半径变化，几何显示位移不进入计算。测试另外用三维v×B积分和洛伦兹力叉乘核查电势与转矩，并用有限差分检查参考场的散度与旋度。

## 原附件的修正

原附件保留在工作区，没有覆盖。重构修正了槽／片相位、永久按线圈编号着色的支路、跨展开切口未裁剪的路径，以及拆解后换向片移动而引线端点不随动的问题。现在的投影、展开和电路视图均读取同一连接与路径记录。

## 尚需实机资料的项目

槽型、公差、绝缘与导线并绕数、逐匝端部排布、均压线、主磁场与换向极、负载电枢反应、刷牌号与接触压力、散热、转子强度和动平衡、换向电感与试验数据。已有输入字段可替换示例尺寸；尚未建模的量不能靠补一个数字自动变成已验证性能。
