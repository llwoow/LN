#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内存管理机制图表生成脚本
生成内存管理相关的示意图和性能对比图
"""

import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
import numpy as np
import seaborn as sns
from matplotlib.sankey import Sankey

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    warnings.filterwarnings('default')  # Show all warnings

    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")

    # Set chart style
    plt.style.use("seaborn-v0_8")
    sns.set_palette("husl")

    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def create_memory_management_architecture():
    """创建内存管理架构图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 定义颜色
    colors = {
        'cpu': '#FF6B6B',
        'mmu': '#4ECDC4', 
        'memory': '#45B7D1',
        'disk': '#96CEB4',
        'cache': '#FFEAA7',
        'process': '#DDA0DD'
    }
    
    # CPU
    cpu_rect = FancyBboxPatch((1, 8), 2.5, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['cpu'], 
                             edgecolor='black', linewidth=2)
    ax.add_patch(cpu_rect)
    ax.text(2.25, 8.75, 'CPU\n寄存器/缓存', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # MMU
    mmu_rect = FancyBboxPatch((1, 6), 2.5, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['mmu'], 
                             edgecolor='black', linewidth=2)
    ax.add_patch(mmu_rect)
    ax.text(2.25, 6.75, 'MMU\n内存管理单元', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # TLB
    tlb_rect = FancyBboxPatch((4.5, 6), 2, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['cache'], 
                             edgecolor='black', linewidth=2)
    ax.add_patch(tlb_rect)
    ax.text(5.5, 6.75, 'TLB\n快表', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 物理内存
    memory_rect = FancyBboxPatch((1, 3.5), 2.5, 2, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['memory'], 
                                edgecolor='black', linewidth=2)
    ax.add_patch(memory_rect)
    ax.text(2.25, 4.5, '物理内存\n(主存)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 页表
    pagetable_rect = FancyBboxPatch((4.5, 3.5), 2, 2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=colors['memory'], 
                                   edgecolor='black', linewidth=2)
    ax.add_patch(pagetable_rect)
    ax.text(5.5, 4.5, '页表\n映射表', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 虚拟内存
    virtual_rect = FancyBboxPatch((7.5, 6), 2.5, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['process'], 
                                 edgecolor='black', linewidth=2)
    ax.add_patch(virtual_rect)
    ax.text(8.75, 6.75, '虚拟地址空间\n进程地址空间', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 磁盘
    disk_rect = FancyBboxPatch((1, 0.5), 2.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['disk'], 
                              edgecolor='black', linewidth=2)
    ax.add_patch(disk_rect)
    ax.text(2.25, 1.25, '磁盘\n交换空间', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 添加箭头连接
    # CPU -> MMU
    ax.annotate('', xy=(2.25, 6), xytext=(2.25, 8), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax.text(2.5, 7, '地址请求', ha='left', va='center', fontsize=8)
    
    # MMU -> TLB
    ax.annotate('', xy=(4.5, 6.75), xytext=(3.5, 6.75), 
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    ax.text(4, 7.2, 'TLB查找', ha='center', va='center', fontsize=8)
    
    # MMU -> 页表
    ax.annotate('', xy=(4.5, 4.5), xytext=(3.5, 6.75), 
                arrowprops=dict(arrowstyle='->', lw=2, color='green'))
    ax.text(3.8, 5.5, '页表查询', ha='center', va='center', fontsize=8)
    
    # MMU -> 物理内存
    ax.annotate('', xy=(3.5, 4.5), xytext=(3.5, 6), 
                arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
    ax.text(3.8, 5.2, '内存访问', ha='center', va='center', fontsize=8)
    
    # 物理内存 -> 磁盘
    ax.annotate('', xy=(2.25, 2), xytext=(2.25, 3.5), 
                arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
    ax.text(2.8, 2.75, '页面置换', ha='center', va='center', fontsize=8)
    
    # 虚拟内存 -> MMU
    ax.annotate('', xy=(4, 6.75), xytext=(7.5, 6.75), 
                arrowprops=dict(arrowstyle='->', lw=2, color='brown'))
    ax.text(5.75, 7.2, '虚拟地址', ha='center', va='center', fontsize=8)
    
    # 设置坐标轴
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('内存管理架构图', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/workspace/charts/memory_management_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_address_translation_diagram():
    """创建分页地址转换示意图"""
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左侧：虚拟地址结构
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 8)
    ax1.axis('off')
    
    # 虚拟地址框
    va_rect = FancyBboxPatch((1, 5), 8, 2, 
                            boxstyle="round,pad=0.2", 
                            facecolor='lightblue', 
                            edgecolor='black', linewidth=2)
    ax1.add_patch(va_rect)
    ax1.text(5, 6, '虚拟地址 (32位)', ha='center', va='center', fontsize=14, fontweight='bold')
    
    # 虚拟页号
    vpn_rect = FancyBboxPatch((1, 2.5), 4, 2, 
                             boxstyle="round,pad=0.1", 
                             facecolor='lightgreen', 
                             edgecolor='black', linewidth=1)
    ax1.add_patch(vpn_rect)
    ax1.text(3, 3.5, '虚拟页号 (VPN)\n20位', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 页内偏移
    offset_rect = FancyBboxPatch((5, 2.5), 4, 2, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightyellow', 
                                edgecolor='black', linewidth=1)
    ax1.add_patch(offset_rect)
    ax1.text(7, 3.5, '页内偏移\n12位', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 箭头
    ax1.annotate('', xy=(3, 5), xytext=(3, 4.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax1.annotate('', xy=(7, 5), xytext=(7, 4.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    ax1.set_title('虚拟地址结构 (32位, 4KB页)', fontsize=14, fontweight='bold')
    
    # 右侧：物理地址结构
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 8)
    ax2.axis('off')
    
    # 物理地址框
    pa_rect = FancyBboxPatch((1, 5), 8, 2, 
                            boxstyle="round,pad=0.2", 
                            facecolor='lightcoral', 
                            edgecolor='black', linewidth=2)
    ax2.add_patch(pa_rect)
    ax2.text(5, 6, '物理地址 (32位)', ha='center', va='center', fontsize=14, fontweight='bold')
    
    # 物理页框号
    pfn_rect = FancyBboxPatch((1, 2.5), 4, 2, 
                             boxstyle="round,pad=0.1", 
                             facecolor='lightpink', 
                             edgecolor='black', linewidth=1)
    ax2.add_patch(pfn_rect)
    ax2.text(3, 3.5, '物理页框号 (PFN)\n20位', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 页内偏移
    offset_rect2 = FancyBboxPatch((5, 2.5), 4, 2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightyellow', 
                                 edgecolor='black', linewidth=1)
    ax2.add_patch(offset_rect2)
    ax2.text(7, 3.5, '页内偏移\n12位', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 箭头
    ax2.annotate('', xy=(3, 5), xytext=(3, 4.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax2.annotate('', xy=(7, 5), xytext=(7, 4.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    ax2.set_title('物理地址结构 (32位, 4KB页)', fontsize=14, fontweight='bold')
    
    # 添加转换公式
    fig.text(0.5, 0.15, '地址转换公式: 物理地址 = PFN × 页面大小 + 偏移量', 
             ha='center', va='center', fontsize=16, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/address_translation_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_page_replacement_flowchart():
    """创建页面置换算法流程图"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # FIFO算法流程图
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 12)
    ax1.axis('off')
    ax1.set_title('FIFO算法流程', fontsize=14, fontweight='bold')
    
    # 流程框
    boxes_fifo = [
        (5, 11, '开始'),
        (5, 9.5, '页面访问'),
        (5, 8, '页面已在内存?'),
        (2, 6.5, '是\n更新访问时间'),
        (8, 6.5, '否\n检查是否有空页框'),
        (5, 5, '有空闲页框?'),
        (2, 3.5, '是\n装入页面'),
        (8, 3.5, '否\n淘汰队首页面'),
        (5, 2, '装入新页面'),
        (5, 0.5, '结束')
    ]
    
    for x, y, text in boxes_fifo:
        if text in ['开始', '结束']:
            color = 'lightgreen'
        elif text in ['页面访问']:
            color = 'lightblue'
        elif text in ['页面已在内存?']:
            color = 'orange'
        else:
            color = 'white'
        
        box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                           boxstyle="round,pad=0.1", 
                           facecolor=color, 
                           edgecolor='black', linewidth=1)
        ax1.add_patch(box)
        ax1.text(x, y, text, ha='center', va='center', fontsize=9)
    
    # 添加箭头
    arrows_fifo = [
        (5, 10.7, 5, 9.8),
        (5, 9.2, 5, 8.3),
        (3.5, 8, 2.8, 6.8),
        (6.5, 8, 7.2, 6.8),
        (5, 6.2, 5, 5.3),
        (3.5, 5, 2.8, 3.8),
        (6.5, 5, 7.2, 3.8),
        (5, 3.2, 5, 2.3),
        (5, 1.7, 5, 0.8)
    ]
    
    for x1, y1, x2, y2 in arrows_fifo:
        ax1.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # LRU算法流程图
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 12)
    ax2.axis('off')
    ax2.set_title('LRU算法流程', fontsize=14, fontweight='bold')
    
    boxes_lru = [
        (5, 11, '开始'),
        (5, 9.5, '页面访问'),
        (5, 8, '页面已在内存?'),
        (2, 6.5, '是\n更新LRU时间'),
        (8, 6.5, '否\n检查是否有空页框'),
        (5, 5, '有空闲页框?'),
        (2, 3.5, '是\n装入页面'),
        (8, 3.5, '否\n淘汰最久未用页面'),
        (5, 2, '装入新页面'),
        (5, 0.5, '结束')
    ]
    
    for x, y, text in boxes_lru:
        if text in ['开始', '结束']:
            color = 'lightgreen'
        elif text in ['页面访问']:
            color = 'lightblue'
        elif text in ['页面已在内存?']:
            color = 'orange'
        else:
            color = 'white'
        
        box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                           boxstyle="round,pad=0.1", 
                           facecolor=color, 
                           edgecolor='black', linewidth=1)
        ax2.add_patch(box)
        ax2.text(x, y, text, ha='center', va='center', fontsize=9)
    
    # 添加箭头
    for x1, y1, x2, y2 in arrows_fifo:
        ax2.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # OPT算法流程图
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 12)
    ax3.axis('off')
    ax3.set_title('OPT算法流程', fontsize=14, fontweight='bold')
    
    boxes_opt = [
        (5, 11, '开始'),
        (5, 9.5, '页面访问'),
        (5, 8, '页面已在内存?'),
        (2, 6.5, '是\n命中'),
        (8, 6.5, '否\n检查是否有空页框'),
        (5, 5, '有空闲页框?'),
        (2, 3.5, '是\n装入页面'),
        (8, 3.5, '否\n预测未来访问\n淘汰最晚使用页面'),
        (5, 2, '装入新页面'),
        (5, 0.5, '结束')
    ]
    
    for x, y, text in boxes_opt:
        if text in ['开始', '结束']:
            color = 'lightgreen'
        elif text in ['页面访问']:
            color = 'lightblue'
        elif text in ['页面已在内存?']:
            color = 'orange'
        else:
            color = 'white'
        
        box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                           boxstyle="round,pad=0.1", 
                           facecolor=color, 
                           edgecolor='black', linewidth=1)
        ax3.add_patch(box)
        ax3.text(x, y, text, ha='center', va='center', fontsize=9)
    
    # 添加箭头
    for x1, y1, x2, y2 in arrows_fifo:
        ax3.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # Clock算法流程图
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 12)
    ax4.axis('off')
    ax4.set_title('Clock算法流程', fontsize=14, fontweight='bold')
    
    boxes_clock = [
        (5, 11, '开始'),
        (5, 9.5, '页面访问'),
        (5, 8, '页面已在内存?'),
        (2, 6.5, '是\n设置访问位=1'),
        (8, 6.5, '否\n检查是否有空页框'),
        (5, 5, '有空闲页框?'),
        (2, 3.5, '是\n装入页面'),
        (8, 3.5, '否\n循环扫描\n检查访问位'),
        (5, 2, '装入新页面'),
        (5, 0.5, '结束')
    ]
    
    for x, y, text in boxes_clock:
        if text in ['开始', '结束']:
            color = 'lightgreen'
        elif text in ['页面访问']:
            color = 'lightblue'
        elif text in ['页面已在内存?']:
            color = 'orange'
        else:
            color = 'white'
        
        box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                           boxstyle="round,pad=0.1", 
                           facecolor=color, 
                           edgecolor='black', linewidth=1)
        ax4.add_patch(box)
        ax4.text(x, y, text, ha='center', va='center', fontsize=9)
    
    # 添加箭头
    for x1, y1, x2, y2 in arrows_fifo:
        ax4.annotate('', xy=(x2, y2), xytext=(x1, y1), 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/page_replacement_flowchart.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_comparison():
    """创建页面置换算法性能对比图"""
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 缺页率对比
    algorithms = ['FIFO', 'LRU', 'OPT', 'Clock', 'LFU']
    page_fault_rates = [76.9, 53.8, 46.2, 61.5, 65.4]  # 示例数据
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    bars = ax1.bar(algorithms, page_fault_rates, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('缺页率 (%)', fontsize=12)
    ax1.set_title('页面置换算法缺页率对比', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 100)
    
    # 在柱状图上添加数值
    for bar, rate in zip(bars, page_fault_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 性能比较雷达图
    categories = ['实现复杂度', '性能表现', '内存开销', '时间局部性适应性', '空间局部性适应性']
    
    # 各算法在不同维度的评分 (1-5分)
    fifo_scores = [1, 2, 1, 2, 3]
    lru_scores = [4, 4, 3, 5, 4]
    opt_scores = [5, 5, 5, 5, 5]
    clock_scores = [3, 3, 2, 4, 3]
    
    # 计算角度
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形
    
    # 添加数据
    fifo_scores += fifo_scores[:1]
    lru_scores += lru_scores[:1]
    opt_scores += opt_scores[:1]
    clock_scores += clock_scores[:1]
    
    ax2 = plt.subplot(122, projection='polar')
    ax2.plot(angles, fifo_scores, 'o-', linewidth=2, label='FIFO', color='#FF6B6B')
    ax2.fill(angles, fifo_scores, alpha=0.25, color='#FF6B6B')
    ax2.plot(angles, lru_scores, 'o-', linewidth=2, label='LRU', color='#4ECDC4')
    ax2.fill(angles, lru_scores, alpha=0.25, color='#4ECDC4')
    ax2.plot(angles, opt_scores, 'o-', linewidth=2, label='OPT', color='#45B7D1')
    ax2.fill(angles, opt_scores, alpha=0.25, color='#45B7D1')
    ax2.plot(angles, clock_scores, 'o-', linewidth=2, label='Clock', color='#96CEB4')
    ax2.fill(angles, clock_scores, alpha=0.25, color='#96CEB4')
    
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories, fontsize=10)
    ax2.set_ylim(0, 5)
    ax2.set_yticks([1, 2, 3, 4, 5])
    ax2.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
    ax2.set_title('页面置换算法综合性能对比', fontsize=14, fontweight='bold', pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_belady_anomaly_demo():
    """创建Belady异常现象演示图"""
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 访问序列
    access_sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    
    # FIFO with 3 frames
    ax1.set_xlim(0, len(access_sequence) + 1)
    ax1.set_ylim(0, 5)
    ax1.set_title('FIFO算法 (3个页框)', fontsize=14, fontweight='bold')
    
    # 绘制访问序列
    for i, page in enumerate(access_sequence):
        color = 'lightcoral' if i % 2 == 0 else 'lightblue'
        rect = Rectangle((i+0.5, 3), 0.8, 1, facecolor=color, edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(i+0.9, 3.5, str(page), ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 绘制页框状态
    for i in range(3):
        rect = Rectangle((0.5, i), 11, 0.8, facecolor='lightgray', edgecolor='black', alpha=0.5)
        ax1.add_patch(rect)
        ax1.text(0.2, i+0.4, f'页框{i+1}', ha='center', va='center', fontsize=10)
    
    ax1.set_xlabel('访问序列', fontsize=12)
    ax1.set_ylabel('页框状态', fontsize=12)
    
    # FIFO with 4 frames
    ax2.set_xlim(0, len(access_sequence) + 1)
    ax2.set_ylim(0, 6)
    ax2.set_title('FIFO算法 (4个页框) - Belady异常', fontsize=14, fontweight='bold')
    
    # 绘制访问序列
    for i, page in enumerate(access_sequence):
        color = 'lightcoral' if i % 2 == 0 else 'lightblue'
        rect = Rectangle((i+0.5, 4), 0.8, 1, facecolor=color, edgecolor='black')
        ax2.add_patch(rect)
        ax2.text(i+0.9, 4.5, str(page), ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 绘制页框状态
    for i in range(4):
        rect = Rectangle((0.5, i), 11, 0.8, facecolor='lightgray', edgecolor='black', alpha=0.5)
        ax2.add_patch(rect)
        ax2.text(0.2, i+0.4, f'页框{i+1}', ha='center', va='center', fontsize=10)
    
    ax2.set_xlabel('访问序列', fontsize=12)
    ax2.set_ylabel('页框状态', fontsize=12)
    
    # 添加说明文字
    fig.text(0.5, 0.02, 'Belady异常：增加页框数量反而导致更多缺页中断', 
             ha='center', va='center', fontsize=14, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/belady_anomaly_demo.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_tlb_structure_diagram():
    """创建TLB结构示意图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # TLB标题
    ax.text(6, 11, 'TLB (Translation Lookaside Buffer) 结构', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # TLB条目
    tlb_entries = [
        ('VPN', 'PFN', 'Valid', 'Access', 'Dirty', 'ASID'),
        ('0x123', '0x456', '1', 'R/W', '0', '5'),
        ('0x789', '0xABC', '1', 'R', '1', '3'),
        ('0xDEF', '0x123', '1', 'R/W', '0', '1'),
        ('0x456', '0x789', '0', '-', '-', '2'),
        ('...', '...', '...', '...', '...', '...')
    ]
    
    # 绘制TLB表格
    for i, entry in enumerate(tlb_entries):
        y_pos = 9.5 - i * 1.5
        if i == 0:  # 表头
            color = 'lightblue'
            fontweight = 'bold'
        else:
            color = 'white'
            fontweight = 'normal'
        
        # 绘制表格行
        for j, cell in enumerate(entry):
            x_pos = 2 + j * 1.5
            rect = Rectangle((x_pos, y_pos), 1.4, 1, facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            ax.text(x_pos + 0.7, y_pos + 0.5, cell, ha='center', va='center', 
                   fontsize=10, fontweight=fontweight)
    
    # 添加说明
    explanations = [
        (6, 6.5, 'VPN: 虚拟页号 (Virtual Page Number)'),
        (6, 5.8, 'PFN: 物理页框号 (Physical Frame Number)'),
        (6, 5.1, 'Valid: 有效位'),
        (6, 4.4, 'Access: 访问权限 (R/W/X)'),
        (6, 3.7, 'Dirty: 脏位'),
        (6, 3.0, 'ASID: 地址空间标识符')
    ]
    
    for x, y, text in explanations:
        ax.text(x, y, text, ha='center', va='center', fontsize=12)
    
    # 添加工作流程
    workflow_steps = [
        (1, 1.5, '1. CPU发送虚拟地址'),
        (3.5, 1.5, '2. TLB查找匹配'),
        (6, 1.5, '3. 命中→返回PFN'),
        (8.5, 1.5, '4. 未命中→查页表'),
        (1, 0.5, '5. 更新TLB')
    ]
    
    for x, y, text in workflow_steps:
        circle = Circle((x, y), 0.3, facecolor='yellow', edgecolor='black')
        ax.add_patch(circle)
        ax.text(x, y, text.split('.')[0], ha='center', va='center', fontsize=8, fontweight='bold')
        ax.text(x, y-0.7, text[2:], ha='center', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/tlb_structure_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """主函数：生成所有图表"""
    print("开始生成内存管理图表...")
    
    print("1. 生成内存管理架构图...")
    create_memory_management_architecture()
    
    print("2. 生成分页地址转换示意图...")
    create_address_translation_diagram()
    
    print("3. 生成页面置换算法流程图...")
    create_page_replacement_flowchart()
    
    print("4. 生成性能对比图...")
    create_performance_comparison()
    
    print("5. 生成Belady异常演示图...")
    create_belady_anomaly_demo()
    
    print("6. 生成TLB结构示意图...")
    create_tlb_structure_diagram()
    
    print("所有图表生成完成！")

if __name__ == "__main__":
    main()
