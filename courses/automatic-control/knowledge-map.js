window.LN_AUTO_CONTROL_MAP={
  "chapters": [
    {
      "group": "第1章 自动控制系统的基本概念",
      "description": "教材原目录框架，正文尚待补全"
    },
    {
      "group": "第2章 自动控制系统的数学模型",
      "description": "教材原目录框架，正文尚待补全"
    },
    {
      "group": "第3章 自动控制系统的时域分析",
      "description": "时域性能、稳定性与稳态误差：有正文与已解作业"
    },
    {
      "group": "第4章 根轨迹法",
      "description": "根轨迹原理、完整法则、用户课堂题与实数增益交互验证"
    },
    {
      "group": "第5章 频率法",
      "description": "教材原目录框架，正文尚待补全"
    },
    {
      "group": "第6章 控制系统的校正及综合",
      "description": "教材原目录框架，正文尚待补全"
    },
    {
      "group": "第7章 非线性系统分析",
      "description": "教材原目录框架，正文尚待补全"
    },
    {
      "group": "第8章 线性离散系统的理论基础",
      "description": "教材原目录框架，正文尚待补全"
    }
  ],
  "nodes": [
    {
      "section": "ac-1-1",
      "title": "自动控制系统的基本概念",
      "note": "本章目录入口，正文待补全"
    },
    {
      "section": "ac-2-1",
      "title": "自动控制系统的数学模型",
      "note": "本章目录入口，正文待补全"
    },
    {
      "section": "ac-4-1",
      "title": "4.1 根轨迹的基础条件",
      "note": "相角、幅值条件及极点连续运动"
    },
    {
      "section": "ac-5-1",
      "title": "频率法",
      "note": "本章目录入口，正文待补全"
    },
    {
      "section": "ac-6-1",
      "title": "控制系统的校正及综合",
      "note": "本章目录入口，正文待补全"
    },
    {
      "section": "ac-7-1",
      "title": "非线性系统分析",
      "note": "本章目录入口，正文待补全"
    },
    {
      "section": "ac-8-1",
      "title": "线性离散系统的理论基础",
      "note": "本章目录入口，正文待补全"
    },
    {
      "section": "ac-3-1",
      "title": "3.1 自动控制系统的时域指标",
      "note": "典型输入与时域指标"
    },
    {
      "section": "ac-3-2",
      "title": "3.2 一阶系统的阶跃响应",
      "note": "时间常数与指数衰减"
    },
    {
      "section": "ac-3-3",
      "title": "3.3 二阶系统的阶跃响应",
      "note": "阻尼比、自然频率与超调"
    },
    {
      "section": "ac-3-4",
      "title": "3.4 高阶系统的动态响应",
      "note": "主导极点与暂态分量"
    },
    {
      "section": "ac-3-5",
      "title": "3.5 自动控制系统的代数稳定判据",
      "note": "特征方程、劳斯、特殊零行"
    },
    {
      "section": "ac-3-6",
      "title": "3.6 稳态误差",
      "note": "型别、给定与扰动误差"
    },
    {
      "section": "ac-3-7",
      "title": "3.7 用MATLAB进行系统时域分析",
      "note": "MATLAB验证与适用条件"
    },
    {
      "section": "ac-4-2",
      "title": "4.2 根轨迹绘制法则",
      "note": "绘图顺序与学习导航"
    },
    {
      "section": "ac-4-2-1",
      "title": "4.2.1 关键绘制公式",
      "note": "实轴、渐近线、分离点、出射到达角"
    },
    {
      "section": "ac-4-2-2",
      "title": "4.2.2 四阶例题与纠错",
      "note": "实时复平面轨迹、错误连接反证"
    },
    {
      "section": "ac-4-2-3",
      "title": "4.2.3 零度根轨迹",
      "note": "相角条件与实轴奇偶条件转变"
    },
    {
      "section": "ac-4-2-4",
      "title": "4.2.4 参数根轨迹",
      "note": "参数分离与等效开环模型"
    },
    {
      "section": "ac-4-3",
      "title": "4.3 动态性能",
      "note": "闭环极点、衰减振荡和稳定边界"
    },
    {
      "section": "ac-4-4",
      "title": "4.4 MATLAB求根轨迹",
      "note": "数值求根与rlocus复算"
    }
  ],
  "links": [
    {
      "from": "ac-3-1",
      "to": "ac-3-2",
      "label": "指标与一阶响应",
      "description": "时间常数影响调节时间"
    },
    {
      "from": "ac-3-2",
      "to": "ac-3-3",
      "label": "系统阶数与暂态",
      "description": "从单指数衰减推广到振荡和两个特征根"
    },
    {
      "from": "ac-3-3",
      "to": "ac-3-4",
      "label": "极点决定暂态",
      "description": "高阶系统的主导极点近似以二阶动态为基础"
    },
    {
      "from": "ac-3-4",
      "to": "ac-3-5",
      "label": "极点与稳定",
      "description": "所有内部模态的根位置决定渐近稳定性"
    },
    {
      "from": "ac-3-5",
      "to": "ac-3-6",
      "label": "先稳定再谈终值",
      "description": "使用静态误差系数与终值定理前需检验闭环稳定"
    },
    {
      "from": "ac-3-6",
      "to": "ac-3-7",
      "label": "计算与验证",
      "description": "用时域仿真与符号计算核查误差"
    },
    {
      "from": "ac-3-5",
      "to": "ac-4-1",
      "label": "稳定性到根轨迹",
      "description": "劳斯法判断区间，根轨迹展示随增益移动的闭环根"
    },
    {
      "from": "ac-4-1",
      "to": "ac-4-2",
      "label": "从条件到画法",
      "description": "利用相角和幅值条件推导几何法则"
    },
    {
      "from": "ac-4-2",
      "to": "ac-4-2-1",
      "label": "一般法则",
      "description": "建立完整公式及可检验的绘图顺序"
    },
    {
      "from": "ac-4-2-1",
      "to": "ac-4-2-2",
      "label": "公式代入本题",
      "description": "用四阶具体模型计算全部关键点与排除错误连接"
    },
    {
      "from": "ac-4-2-1",
      "to": "ac-4-2-3",
      "label": "增益符号变化",
      "description": "相角奇数周条件与零度条件对照"
    },
    {
      "from": "ac-4-2-3",
      "to": "ac-4-2-4",
      "label": "到一般参数",
      "description": "参数线性分离后形成等效轨迹问题"
    },
    {
      "from": "ac-4-2-2",
      "to": "ac-4-3",
      "label": "读出稳定性",
      "description": "用已求闭环极点解释稳定界和衰减"
    },
    {
      "from": "ac-4-3",
      "to": "ac-4-4",
      "label": "数值验证",
      "description": "用MATLAB检验极点连续性与临界增益"
    },
    {
      "from": "ac-3-3",
      "to": "ac-4-3",
      "label": "阻尼关系",
      "description": "由复根位置得到阻尼频率和二阶近似"
    }
  ]
};
