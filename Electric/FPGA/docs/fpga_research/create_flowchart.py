#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FPGA设计流程图生成脚本
"""

import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    # Ensure warnings are printed
    warnings.filterwarnings('default')  # Show all warnings

    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")

    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def create_fpga_flowchart():
    """创建FPGA设计流程图"""
    setup_matplotlib_for_plotting()
    
    # 创建图形和坐标轴
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 定义流程步骤
    steps = [
        {"name": "设计需求分析", "pos": (5, 11), "color": "#e3f2fd"},
        {"name": "系统架构设计", "pos": (5, 10), "color": "#e8f5e8"},
        {"name": "RTL设计输入\n(Verilog/VHDL/SystemVerilog)", "pos": (5, 9), "color": "#f3e5f5"},
        {"name": "功能仿真验证\n(Behavioral Simulation)", "pos": (5, 8), "color": "#fff3e0"},
        {"name": "逻辑综合\n(Synthesis)", "pos": (5, 7), "color": "#e8f5e8"},
        {"name": "综合后验证\n(Post-Synthesis Simulation)", "pos": (5, 6), "color": "#fff3e0"},
        {"name": "时序约束\n(SDC/XDC)", "pos": (2, 5), "color": "#fce4ec"},
        {"name": "逻辑映射\n(Mapping)", "pos": (5, 5), "color": "#fff3e0"},
        {"name": "布局\n(Placement)", "pos": (5, 4), "color": "#fff3e0"},
        {"name": "布线\n(Routing)", "pos": (5, 3), "color": "#fff3e0"},
        {"name": "时序分析\n(STA)", "pos": (5, 2), "color": "#fce4ec"},
        {"name": "比特流生成\n(Bitstream Generation)", "pos": (5, 1), "color": "#f1f8e9"}
    ]
    
    # 绘制流程框
    for step in steps:
        x, y = step["pos"]
        # 创建圆角矩形
        bbox = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                            boxstyle="round,pad=0.1",
                            facecolor=step["color"], 
                            edgecolor='black',
                            linewidth=1)
        ax.add_patch(bbox)
        
        # 添加文本
        ax.text(x, y, step["name"], ha='center', va='center', 
               fontsize=10, fontweight='bold')
    
    # 绘制箭头连接
    arrows = [
        (5, 10.7, 5, 10.3),  # 设计需求 -> 系统架构
        (5, 9.7, 5, 9.3),   # 系统架构 -> RTL设计
        (5, 8.7, 5, 8.3),   # RTL设计 -> 功能仿真
        (5, 7.7, 5, 7.3),   # 功能仿真 -> 逻辑综合
        (5, 6.7, 5, 6.3),   # 逻辑综合 -> 综合后验证
        (5, 5.7, 5, 5.3),   # 综合后验证 -> 逻辑映射
        (5, 4.7, 5, 4.3),   # 逻辑映射 -> 布局
        (5, 3.7, 5, 3.3),   # 布局 -> 布线
        (5, 2.7, 5, 2.3),   # 布线 -> 时序分析
        (5, 1.7, 5, 1.3),   # 时序分析 -> 比特流生成
    ]
    
    for arrow in arrows:
        ax.annotate('', xy=(arrow[2], arrow[3]), xytext=(arrow[0], arrow[1]),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # 添加时序约束连接线
    ax.annotate('', xy=(2.8, 5), xytext=(4.2, 5),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='red', linestyle='--'))
    ax.text(3.5, 5.3, '时序约束', ha='center', va='center', 
           fontsize=8, color='red', fontweight='bold')
    
    # 添加反馈循环箭头
    ax.annotate('', xy=(5.8, 6), xytext=(5.8, 2),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='orange', 
                             connectionstyle="arc3,rad=0.3"))
    ax.text(7.5, 4, '时序优化\n反馈循环', ha='center', va='center', 
           fontsize=8, color='orange', fontweight='bold')
    
    # 添加标题
    plt.title('FPGA完整设计流程图', fontsize=16, fontweight='bold', pad=20)
    
    # 保存图片
    plt.tight_layout()
    plt.savefig('/workspace/docs/fpga_research/fpga_design_flow.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("FPGA设计流程图已生成: fpga_design_flow.png")

def create_implementation_details():
    """创建实现过程详细流程图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 实现过程步骤
    impl_steps = [
        {"name": "1. 翻译 (Translate)\n• NGDBuild\n• 合并约束文件\n• 生成.ngd文件", "pos": (2, 7), "color": "#e3f2fd"},
        {"name": "2. 映射 (Map)\n• 逻辑映射到LUT\n• 资源分配\n• 生成.ncd文件", "pos": (5, 7), "color": "#e8f5e8"},
        {"name": "3. 布局 (Place)\n• 位置分配\n• 时钟树优化\n• 资源约束", "pos": (8, 7), "color": "#fff3e0"},
        {"name": "4. 布线 (Route)\n• 互连优化\n• 时序驱动\n• 生成布线文件", "pos": (5, 5), "color": "#fce4ec"},
        {"name": "5. 时序分析\n• STA分析\n• 时序闭合检查\n• 报告生成", "pos": (2, 5), "color": "#f1f8e9"},
        {"name": "6. 比特流生成\n• BitGen\n• 配置数据\n• 编程文件", "pos": (5, 3), "color": "#f9fbe7"}
    ]
    
    # 绘制实现步骤框
    for step in impl_steps:
        x, y = step["pos"]
        bbox = FancyBboxPatch((x-0.9, y-0.6), 1.8, 1.2, 
                            boxstyle="round,pad=0.1",
                            facecolor=step["color"], 
                            edgecolor='black',
                            linewidth=1)
        ax.add_patch(bbox)
        
        ax.text(x, y, step["name"], ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # 绘制连接箭头
    connections = [
        (2.9, 7, 4.1, 7),      # 翻译 -> 映射
        (5.9, 7, 7.1, 7),      # 映射 -> 布局
        (8, 6.4, 5.9, 5.6),    # 布局 -> 布线
        (5, 4.4, 4.1, 5),      # 布线 -> 时序分析
        (2, 4.4, 4.1, 3.6),    # 时序分析 -> 比特流
        (5.9, 3, 2.9, 5),      # 比特流 -> 翻译 (反馈)
    ]
    
    for conn in connections:
        ax.annotate('', xy=(conn[2], conn[3]), xytext=(conn[0], conn[1]),
                   arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # 添加反馈箭头
    ax.annotate('', xy=(2, 6.4), xytext=(4.1, 3),
               arrowprops=dict(arrowstyle='->', lw=2, color='red',
                             connectionstyle="arc3,rad=-0.3"))
    ax.text(1, 4.5, '时序不闭合\n需要重新优化', ha='center', va='center', 
           fontsize=8, color='red', fontweight='bold')
    
    plt.title('FPGA实现过程详细流程', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/workspace/docs/fpga_research/fpga_implementation_flow.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("FPGA实现流程图已生成: fpga_implementation_flow.png")

def create_tool_comparison():
    """创建工具对比表格图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.axis('off')
    
    # 工具对比数据
    tools_data = {
        '特性': ['综合工具', '布局布线', '时序分析', '仿真工具', 'IP集成', 
               '约束文件', 'GUI界面', '命令行支持', '增量编译', '调试工具'],
        'Xilinx Vivado': ['Vivado Synthesis', 'Vivado Implementation', 
                         'Vivado Timing Analysis', 'Vivado Simulator',
                         'IP Integrator', 'XDC', '现代化GUI', 
                         'Tcl/批处理', '支持', 'ILA/逻辑分析'],
        'Intel Quartus': ['Intel Synthesis', 'Quartus Fitter',
                        'Timing Analyzer', 'QuestaSim',
                        'IP Catalog', 'SDC', '传统GUI',
                        'Tcl/批处理', '支持', 'SignalTap'],
        'Lattice Diamond': ['LSE/Synplify Pro', 'Diamond Place&Route',
                          'Timing Analyzer', 'Active-HDL',
                          'IPexpress', 'SDC', '简洁GUI',
                          'Tcl/批处理', '有限', 'Identify'],
        'Microchip Libero': ['Synplify Pro', 'Designer',
                           'SmartTime', 'ModelSim',
                           'IP Catalog', 'SDC', '企业GUI',
                           'Tcl/批处理', '支持', 'SmartDebug']
    }
    
    # 创建表格
    rows = len(tools_data['特性']) + 1
    cols = len(tools_data.keys())
    
    # 设置表格位置
    cell_width = 2.5
    cell_height = 0.5
    start_x = 1
    start_y = 8
    
    # 绘制表头
    headers = list(tools_data.keys())
    for i, header in enumerate(headers):
        x = start_x + i * cell_width
        bbox = FancyBboxPatch((x, start_y), cell_width, cell_height,
                            boxstyle="round,pad=0.05",
                            facecolor='#4CAF50', edgecolor='black')
        ax.add_patch(bbox)
        ax.text(x + cell_width/2, start_y + cell_height/2, header,
               ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # 绘制数据行
    for row_idx, feature in enumerate(tools_data['特性']):
        y = start_y - (row_idx + 1) * cell_height
        
        # 特性列
        x = start_x
        bbox = FancyBboxPatch((x, y), cell_width, cell_height,
                            boxstyle="round,pad=0.05",
                            facecolor='#E3F2FD', edgecolor='black')
        ax.add_patch(bbox)
        ax.text(x + cell_width/2, y + cell_height/2, feature,
               ha='center', va='center', fontsize=9, fontweight='bold')
        
        # 工具列
        tool_colors = ['#FFF3E0', '#E8F5E8', '#F3E5F5', '#FCE4EC']
        for col_idx, tool in enumerate(['Xilinx Vivado', 'Intel Quartus', 'Lattice Diamond', 'Microchip Libero']):
            x = start_x + (col_idx + 1) * cell_width
            bbox = FancyBboxPatch((x, y), cell_width, cell_height,
                                boxstyle="round,pad=0.05",
                                facecolor=tool_colors[col_idx], edgecolor='black')
            ax.add_patch(bbox)
            ax.text(x + cell_width/2, y + cell_height/2, tools_data[tool][row_idx],
                   ha='center', va='center', fontsize=8)
    
    plt.title('FPGA开发工具对比表', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/workspace/docs/fpga_research/fpga_tools_comparison.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("FPGA工具对比图已生成: fpga_tools_comparison.png")

if __name__ == "__main__":
    create_fpga_flowchart()
    create_implementation_details()
    create_tool_comparison()
    print("所有流程图和对比图已生成完成！")
