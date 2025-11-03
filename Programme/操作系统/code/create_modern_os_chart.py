#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建现代操作系统架构图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
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

def create_modern_os_architecture():
    """创建现代操作系统架构图"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('现代操作系统架构特性\n(Modern Operating System Architecture Features)', 
                 fontsize=18, fontweight='bold')
    
    # 定义颜色
    colors = {
        'application': '#FFE5B4',     # 浅橙色 - 应用程序层
        'middleware': '#E6F3FF',      # 浅蓝色 - 中间件层
        'kernel': '#FFB6C1',          # 浅粉色 - 内核层
        'hardware': '#DDA0DD',        # 紫色 - 硬件层
        'security': '#F0E68C',        # 浅黄色 - 安全机制
        'network': '#98FB98',         # 浅绿色 - 网络功能
        'distributed': '#FFA07A'      # 浅橙色 - 分布式功能
    }
    
    # 1. 多处理机系统架构 (左上)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('多处理机系统架构\n(Multiprocessor Systems)', fontsize=14, fontweight='bold')
    
    # 应用程序层
    app_layer = FancyBboxPatch(
        (1, 8), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['application'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax1.add_patch(app_layer)
    ax1.text(5, 8.75, '应用程序层 (Application Layer)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 内核层 - 对称多处理
    kernel_layer = FancyBboxPatch(
        (1, 5.5), 8, 2,
        boxstyle="round,pad=0.1",
        facecolor=colors['kernel'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax1.add_patch(kernel_layer)
    ax1.text(5, 6.8, '对称多处理内核 (SMP Kernel)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 多核CPU
    cpu1 = Circle((2.5, 6), 0.8, facecolor='white', edgecolor='black', linewidth=2)
    cpu2 = Circle((5, 6), 0.8, facecolor='white', edgecolor='black', linewidth=2)
    cpu3 = Circle((7.5, 6), 0.8, facecolor='white', edgecolor='black', linewidth=2)
    ax1.add_patch(cpu1)
    ax1.add_patch(cpu2)
    ax1.add_patch(cpu3)
    ax1.text(2.5, 6, 'CPU1', fontsize=10, ha='center', va='center')
    ax1.text(5, 6, 'CPU2', fontsize=10, ha='center', va='center')
    ax1.text(7.5, 6, 'CPU3', fontsize=10, ha='center', va='center')
    
    # 共享内存
    memory = FancyBboxPatch(
        (1, 4), 8, 1,
        boxstyle="round,pad=0.1",
        facecolor=colors['hardware'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax1.add_patch(memory)
    ax1.text(5, 4.5, '共享内存 (Shared Memory)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 安全特性
    security_box = FancyBboxPatch(
        (0.5, 2), 9, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['security'],
        edgecolor='red',
        linewidth=2,
        alpha=0.7
    )
    ax1.add_patch(security_box)
    ax1.text(5, 2.75, '安全机制: 内存保护、进程隔离、特权级控制', 
             fontsize=11, fontweight='bold', ha='center', va='center')
    
    # 2. 分布式系统架构 (右上)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('分布式系统架构\n(Distributed Systems)', fontsize=14, fontweight='bold')
    
    # 分布式节点
    nodes = [
        (2, 8, '节点1\n(Node 1)'),
        (5, 8, '节点2\n(Node 2)'),
        (8, 8, '节点3\n(Node 3)'),
        (2, 5, '节点4\n(Node 4)'),
        (5, 5, '节点5\n(Node 5)'),
        (8, 5, '节点6\n(Node 6)')
    ]
    
    for x, y, label in nodes:
        node = Circle((x, y), 0.8, facecolor=colors['distributed'], 
                     edgecolor='black', linewidth=2, alpha=0.7)
        ax2.add_patch(node)
        ax2.text(x, y, label, fontsize=9, ha='center', va='center')
    
    # 网络连接
    connections = [
        ((2, 8), (5, 8)), ((5, 8), (8, 8)),  # 水平连接
        ((2, 8), (2, 5)), ((5, 5), (5, 8)),  # 垂直连接
        ((2, 5), (5, 5)), ((5, 5), (8, 5)),  # 底部水平
        ((8, 8), (8, 5))  # 右侧垂直
    ]
    
    for (x1, y1), (x2, y2) in connections:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               connectionstyle="arc3", 
                               arrowstyle='<->', 
                               mutation_scale=15, 
                               color='blue',
                               alpha=0.6)
        ax2.add_patch(arrow)
    
    # 分布式安全
    security_dist = FancyBboxPatch(
        (1, 2), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['security'],
        edgecolor='red',
        linewidth=2,
        alpha=0.7
    )
    ax2.add_patch(security_dist)
    ax2.text(5, 2.75, '分布式安全: 身份认证、访问控制、加密通信', 
             fontsize=11, fontweight='bold', ha='center', va='center')
    
    # 3. 实时操作系统架构 (左下)
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.axis('off')
    ax3.set_title('实时操作系统架构\n(Real-Time Operating Systems)', fontsize=14, fontweight='bold')
    
    # 实时任务层
    rt_tasks = FancyBboxPatch(
        (1, 7.5), 8, 2,
        boxstyle="round,pad=0.1",
        facecolor=colors['application'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax3.add_patch(rt_tasks)
    ax3.text(5, 8.5, '实时任务层 (Real-Time Tasks)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    ax3.text(5, 8, '• 硬实时任务  • 软实时任务  • 周期性任务', 
             fontsize=10, ha='center', va='center')
    
    # 实时内核
    rt_kernel = FancyBboxPatch(
        (1, 5), 8, 2,
        boxstyle="round,pad=0.1",
        facecolor=colors['kernel'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax3.add_patch(rt_kernel)
    ax3.text(5, 6.2, '实时内核 (RT Kernel)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    ax3.text(5, 5.8, '• 优先级调度  • 中断处理  • 任务同步', 
             fontsize=10, ha='center', va='center')
    ax3.text(5, 5.4, '• 内存管理  • 定时器服务', 
             fontsize=10, ha='center', va='center')
    
    # 硬件抽象层
    hal = FancyBboxPatch(
        (1, 2.5), 8, 2,
        boxstyle="round,pad=0.1",
        facecolor=colors['hardware'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax3.add_patch(hal)
    ax3.text(5, 3.7, '硬件抽象层 (Hardware Abstraction Layer)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    ax3.text(5, 3.3, '• 中断控制器  • 定时器  • I/O设备', 
             fontsize=10, ha='center', va='center')
    
    # 实时安全
    rt_security = FancyBboxPatch(
        (1, 0.5), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['security'],
        edgecolor='red',
        linewidth=2,
        alpha=0.7
    )
    ax3.add_patch(rt_security)
    ax3.text(5, 1.25, '实时安全: 任务隔离、时间确定性、资源保护', 
             fontsize=11, fontweight='bold', ha='center', va='center')
    
    # 4. 移动操作系统架构 (右下)
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    ax4.axis('off')
    ax4.set_title('移动操作系统架构\n(Mobile Operating Systems)', fontsize=14, fontweight='bold')
    
    # 应用层
    mobile_apps = FancyBboxPatch(
        (1, 8), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['application'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax4.add_patch(mobile_apps)
    ax4.text(5, 8.75, '移动应用层 (Mobile Apps)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 运行时环境
    runtime = FancyBboxPatch(
        (1, 6), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['middleware'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax4.add_patch(runtime)
    ax4.text(5, 6.75, '运行时环境 (Runtime Environment)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    ax4.text(5, 6.35, '• Android Runtime (ART)  • iOS Runtime', 
             fontsize=10, ha='center', va='center')
    
    # 移动内核
    mobile_kernel = FancyBboxPatch(
        (1, 4), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['kernel'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax4.add_patch(mobile_kernel)
    ax4.text(5, 4.75, '移动内核 (Mobile Kernel)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    ax4.text(5, 4.35, '• Linux Kernel (Android)  • XNU Kernel (iOS)', 
             fontsize=10, ha='center', va='center')
    
    # 硬件抽象层
    mobile_hal = FancyBboxPatch(
        (1, 2), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['hardware'],
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax4.add_patch(mobile_hal)
    ax4.text(5, 2.75, '硬件抽象层 (Hardware Abstraction Layer)', 
             fontsize=12, fontweight='bold', ha='center', va='center')
    ax4.text(5, 2.35, '• 传感器驱动  • 通信模块  • 多媒体', 
             fontsize=10, ha='center', va='center')
    
    # 移动安全
    mobile_security = FancyBboxPatch(
        (1, 0.2), 8, 1.5,
        boxstyle="round,pad=0.1",
        facecolor=colors['security'],
        edgecolor='red',
        linewidth=2,
        alpha=0.7
    )
    ax4.add_patch(mobile_security)
    ax4.text(5, 0.95, '移动安全: 应用沙箱、权限管理、代码签名', 
             fontsize=11, fontweight='bold', ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/modern_os_architecture.png', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("现代操作系统架构图已创建: /workspace/docs/modern_os_architecture.png")

if __name__ == "__main__":
    create_modern_os_architecture()