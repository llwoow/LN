// 节点对应现有正文；章内实线表示阅读顺序，跨节点虚线表示注明含义的知识联系。
window.LN_ELECTRICAL_MACHINES_MAP = {
  chapters: [
    { group: '第1章 磁路', description: '基础：从磁场定律到磁路模型' },
    { group: '第2章 变压器', description: '静止设备：建模、试验与运行' },
    { group: '第3章 直流电机', description: '旋转设备：机电转换与控制' }
  ],
  nodes: [
    { section: 'magnetic-sec11', title: '磁路基本定律', note: '安匝、磁通与磁阻' },
    { section: 'magnetic-sec12', title: '铁磁材料与饱和', note: '非线性、磁滞与损耗' },
    { section: 'magnetic-sec13', title: '磁路计算', note: '已知磁通求励磁，反向求解' },
    { section: 'magnetic-sec14', title: '磁链、电感与储能', note: '自感、互感与磁导' },
    { section: 'transformer-1', title: '交流量与磁路基础', note: '相量、功率与磁路方程' },
    { section: 'transformer-2', title: '理想变压器', note: '电磁感应与安匝平衡' },
    { section: 'transformer-3', title: '等效电路与折算', note: '励磁支路、漏抗与 T 型电路' },
    { section: 'transformer-4', title: '试验与参数辨识', note: '空载、短路试验和标幺值' },
    { section: 'transformer-5', title: '电压变化率与效率', note: '相量压降与损耗平衡' },
    { section: 'transformer-6', title: '三相联结与组别', note: '线相换算、相移与电流路径' },
    { section: 'transformer-7', title: '不对称运行与并联', note: '中性点、环流与负载分担' },
    { section: 'transformer-8', title: '暂态与调压', note: '合闸涌流、短路与分接' },
    { section: 'transformer-9', title: '特殊变压器', note: '自耦、三绕组与互感器' },
    { section: 'transformer-10', title: '综合计算', note: '从试验参数到功率守恒' },
    { section: 'transformer-homework', title: '第二章作业', note: '13 题，按题定位' },
    { section: 'dc-sec31', title: '结构与工作原理', note: '电动、发电与换向器' },
    { section: 'dc-sec32', title: '电枢绕组', note: '接线规则、线圈与并联支路' },
    { section: 'dc-sec33', title: '主磁场与电枢反应', note: '空载和负载磁场' },
    { section: 'dc-sec34', title: '感应电势与电磁转矩', note: '能量转换的两个关键关系' },
    { section: 'dc-sec35', title: '直流电机基本方程', note: '电压、功率与转矩平衡' },
    { section: 'dc-sec36', title: '发电机运行特性', note: '励磁连接与负载变化' },
    { section: 'dc-sec37', title: '电动机运行特性', note: '转矩、转速与机械特性' },
    { section: 'dc-sec38', title: '起动、调速与制动', note: '从电枢方程选择控制量' },
    { section: 'dc-sec39', title: '换向', note: '换向电流与火花问题' },
    { section: 'winding-model', title: '绕组交互模型', note: '接线、运动、电势与转矩' }
  ],
  links: [
    { from: 'magnetic-sec11', to: 'transformer-2', label: '电磁感应', description: '变化的磁通产生感应电压，是理解变压器电压关系的基础。' },
    { from: 'magnetic-sec12', to: 'transformer-8', label: '磁饱和与涌流', description: '合闸时磁通的暂态偏移可能使铁心进入饱和，产生较大的励磁电流。' },
    { from: 'magnetic-sec14', to: 'transformer-3', label: '自感、互感与等效电路', description: '用磁链和绕组电压方程区分主磁通、漏磁通及对应的电路支路。' },
    { from: 'magnetic-sec13', to: 'dc-sec33', label: '磁路与主磁场', description: '把磁路计算方法用于直流电机，理解主磁场及负载时电枢磁场的影响。' },
    { from: 'transformer-3', to: 'transformer-5', label: '电路参数决定运行特性', description: '由等效电路中的阻抗计算电压变化，由损耗和功率平衡计算效率。' },
    { from: 'transformer-6', to: 'transformer-7', label: '联结与并联条件', description: '联结组别影响相位关系；分析并联前需核对电压比、相位和阻抗。' },
    { from: 'transformer-3', to: 'dc-sec35', label: '绕组电压方程', description: '两类设备都需要分清感应电势和绕组压降，再在各自模型和参考方向下列方程。' },
    { from: 'dc-sec32', to: 'dc-sec34', label: '绕组与电势、转矩', description: '有效导体、极数和并联支路数进入直流电机的电势与转矩关系。' },
    { from: 'dc-sec35', to: 'dc-sec38', label: '基本方程与控制', description: '由电压和转矩方程分析零速起动电流、调速方式与制动工况。' },
    { from: 'dc-sec32', to: 'winding-model', label: '用模型检查绕组', description: '在交互模型中观察绕组接线、刷片接触和支路分区，再联系感应电势与转矩。' }
  ]
};
