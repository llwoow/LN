#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建系统调用流程图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    import warnings
    import matplotlib.pyplot as plt
    
    # Ensure warnings are printed
    warnings.filterwarnings('default')  # Show all warnings
    
    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")
    
    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def create_system_call_flowchart():
    """创建系统调用流程图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    plt.title('系统调用实现机制与流程\n(System Call Implementation Mechanism)', 
              fontsize=18, fontweight='bold', pad=20)
    
    # 定义颜色
    colors = {
        'user_space': '#FFE5B4',     # 浅橙色 - 用户空间
        'kernel_space': '#E6F3FF',   # 浅蓝色 - 内核空间
        'transition': '#FFB6C1',     # 浅粉色 - 转换过程
        'process': '#DDA0DD',        # 紫色 - 进程
        'hardware': '#F0E68C'        # 浅黄色 - 硬件
    }
    
    # 用户空间区域
    user_space = FancyBboxPatch(
        (0.5, 6), 6, 3,
        boxstyle="round,pad=0.1",
        facecolor=colors['user_space'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax.add_patch(user_space)
    ax.text(3.5, 8.7, '用户空间 (User Space)', 
            fontsize=14, fontweight='bold', ha='center', va='center')
    
    # 内核空间区域
    kernel_space = FancyBboxPatch(
        (7.5, 6), 6, 3,
        boxstyle="round,pad=0.1",
        facecolor=colors['kernel_space'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax.add_patch(kernel_space)
    ax.text(10.5, 8.7, '内核空间 (Kernel Space)', 
            fontsize=14, fontweight='bold', ha='center', va='center')
    
    # 硬件层区域
    hardware_space = FancyBboxPatch(
        (3, 1), 8, 2,
        boxstyle="round,pad=0.1",
        facecolor=colors['hardware'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax.add_patch(hardware_space)
    ax.text(7, 2.7, '硬件层 (Hardware Layer)', 
            fontsize=14, fontweight='bold', ha='center', va='center')
    
    # 用户空间组件
    # 应用程序
    app_box = FancyBboxPatch(
        (1, 7.5), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(app_box)
    ax.text(2, 7.9, '应用程序\n(Application)', 
            fontsize=10, ha='center', va='center')
    
    # 库函数 (libc)
    libc_box = FancyBboxPatch(
        (1, 6.5), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(libc_box)
    ax.text(2, 6.9, '库函数\n(libc)', 
            fontsize=10, ha='center', va='center')
    
    # 系统调用接口
    syscall_box = FancyBboxPatch(
        (4, 7.5), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor=colors['transition'],
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(syscall_box)
    ax.text(5, 7.9, '系统调用接口\n(System Call Interface)', 
            fontsize=10, ha='center', va='center')
    
    # 内核空间组件
    # 系统调用处理器
    handler_box = FancyBboxPatch(
        (8, 7.5), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(handler_box)
    ax.text(9, 7.9, '系统调用处理器\n(System Call Handler)', 
            fontsize=10, ha='center', va='center')
    
    # 系统调用表
    table_box = FancyBboxPatch(
        (8, 6.5), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(table_box)
    ax.text(9, 6.9, '系统调用表\n(System Call Table)', 
            fontsize=10, ha='center', va='center')
    
    # 内核服务
    service_box = FancyBboxPatch(
        (11, 7.5), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(service_box)
    ax.text(12, 7.9, '内核服务\n(Kernel Services)', 
            fontsize=10, ha='center', va='center')
    
    # 硬件组件
    cpu_box = FancyBboxPatch(
        (4, 2), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(cpu_box)
    ax.text(5, 2.4, 'CPU\n(特权模式)', 
            fontsize=10, ha='center', va='center')
    
    memory_box = FancyBboxPatch(
        (8, 2), 2, 0.8,
        boxstyle="round,pad=0.05",
        facecolor='white',
        edgecolor='black',
        linewidth=1
    )
    ax.add_patch(memory_box)
    ax.text(9, 2.4, '内存管理\n(Memory Management)', 
            fontsize=10, ha='center', va='center')
    
    # 绘制箭头和流程
    # 1. 应用程序调用库函数
    arrow1 = FancyArrowPatch((2, 7.5), (2, 7.3),
                            connectionstyle="arc3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='blue')
    ax.add_patch(arrow1)
    
    # 2. 库函数调用系统调用
    arrow2 = FancyArrowPatch((3, 7.3), (4, 7.3),
                            connectionstyle="arc3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='red')
    ax.add_patch(arrow2)
    ax.text(3.5, 7.1, '1. 系统调用号\n参数传递', 
            fontsize=9, ha='center', va='center', color='red')
    
    # 3. 系统调用触发中断
    arrow3 = FancyArrowPatch((6, 7.9), (8, 7.9),
                            connectionstyle="arc3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='orange')
    ax.add_patch(arrow3)
    ax.text(7, 8.1, '2. 触发中断\n(int 0x80/syscall)', 
            fontsize=9, ha='center', va='center', color='orange')
    
    # 4. 处理器查找系统调用表
    arrow4 = FancyArrowPatch((9, 7.5), (9, 7.3),
                            connectionstyle="arc3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='green')
    ax.add_patch(arrow4)
    ax.text(9.5, 7.4, '3. 查找系统调用表', 
            fontsize=9, ha='center', va='center', color='green')
    
    # 5. 执行内核服务
    arrow5 = FancyArrowPatch((10, 7.3), (11, 7.3),
                            connectionstyle="arc3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='purple')
    ax.add_patch(arrow5)
    ax.text(10.5, 7.1, '4. 执行内核服务', 
            fontsize=9, ha='center', va='center', color='purple')
    
    # 6. 内核访问硬件
    arrow6 = FancyArrowPatch((12, 7.5), (9, 3),
                            connectionstyle="arc3,rad=0.3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='brown')
    ax.add_patch(arrow6)
    ax.text(11, 5, '5. 访问硬件资源', 
            fontsize=9, ha='center', va='center', color='brown')
    
    # 7. 返回用户空间
    arrow7 = FancyArrowPatch((8, 6.5), (6, 6.5),
                            connectionstyle="arc3", 
                            arrowstyle='->', 
                            mutation_scale=20, 
                            color='red')
    ax.add_patch(arrow7)
    ax.text(7, 6.3, '6. 返回结果\n(用户空间)', 
            fontsize=9, ha='center', va='center', color='red')
    
    # 添加详细说明
    details = [
        "系统调用参数传递机制:",
        "• 寄存器传递: 系统调用号放入EAX, 参数放入EBX, ECX, EDX等",
        "• 栈传递: 复杂参数通过用户栈传递",
        "• 结构体传递: 大型数据结构通过指针传递",
        "",
        "特权级转换过程:",
        "• 用户态(ring 3) → 内核态(ring 0)",
        "• CPU模式切换和上下文保存",
        "• 权限检查和安全验证",
        "• 执行完成后恢复用户态"
    ]
    
    ax.text(0.5, 4.5, '\n'.join(details), 
            fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle="round,pad=0.5", 
                     facecolor='lightyellow', 
                     edgecolor='black', 
                     alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/system_call_flowchart.png', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("系统调用流程图已创建: /workspace/docs/system_call_flowchart.png")

if __name__ == "__main__":
    create_system_call_flowchart()