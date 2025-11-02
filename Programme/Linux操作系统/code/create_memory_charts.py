#!/usr/bin/env python3
"""
Linux内存管理可视化图表生成器
创建关键概念的图表来增强报告理解
"""

import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
import os

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

def create_page_table_diagram():
    """创建多级页表结构图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 虚拟地址分解
    ax.text(0.02, 0.95, '虚拟地址分解', fontsize=16, fontweight='bold', transform=ax.transAxes)
    ax.text(0.02, 0.90, '虚拟页号(VPN) + 页内偏移(Offset)', fontsize=12, transform=ax.transAxes)
    
    # 页表层级结构
    levels = [
        {'name': '一级页表', 'y': 0.75, 'color': '#E3F2FD'},
        {'name': '二级页表', 'y': 0.55, 'color': '#E8F5E8'},
        {'name': '三级页表', 'y': 0.35, 'color': '#FFF3E0'},
        {'name': '物理内存', 'y': 0.15, 'color': '#F3E5F5'}
    ]
    
    for i, level in enumerate(levels):
        # 绘制页表框
        rect = FancyBboxPatch((0.1, level['y']), 0.8, 0.12, 
                             boxstyle="round,pad=0.02", 
                             facecolor=level['color'], 
                             edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(0.5, level['y'] + 0.06, level['name'], 
               ha='center', va='center', fontsize=14, fontweight='bold')
        
        # 绘制索引
        for j in range(4):
            x = 0.15 + j * 0.18
            ax.text(x, level['y'] + 0.03, f'[{j}]', ha='center', va='center', fontsize=10)
    
    # 绘制连接线
    for i in range(len(levels) - 1):
        y1 = levels[i]['y']
        y2 = levels[i + 1]['y']
        for j in range(4):
            x = 0.24 + j * 0.18
            ax.arrow(x, y1, 0, y2 - y1 - 0.02, head_width=0.01, head_length=0.01, 
                    fc='blue', ec='blue', alpha=0.7)
    
    # 添加说明
    ax.text(0.02, 0.05, '页表项包含：物理页帧号(PFN)、访问权限、脏位、存在位等', 
           fontsize=11, transform=ax.transAxes, style='italic')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/memory_management/multilevel_page_table.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("多级页表结构图已创建")

def create_tlb_performance_chart():
    """创建TLB性能分析图表"""
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # TLB命中率对EMAT的影响
    hit_rates = np.linspace(0.5, 0.99, 50)
    emat_1 = 1 + 100 * (1 - hit_rates)  # 单级TLB
    emat_2 = 1 + 50 * (1 - hit_rates)   # 两级TLB
    
    ax1.plot(hit_rates, emat_1, 'b-', linewidth=2, label='单级TLB')
    ax1.plot(hit_rates, emat_2, 'r-', linewidth=2, label='两级TLB')
    ax1.set_xlabel('TLB命中率')
    ax1.set_ylabel('平均内存访问时间 (ns)')
    ax1.set_title('TLB命中率对性能的影响')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 页大小对TLB效率的影响
    page_sizes = ['4KB', '2MB', '1GB']
    tlb_entries = [1024, 2048, 4096]  # 假设的TLB条目数
    coverage = [4*1024*1024, 4*1024*1024*512, 4*1024*1024*512*256]  # TLB覆盖的内存大小
    
    x = np.arange(len(page_sizes))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, [e/1024 for e in tlb_entries], width, 
                   label='TLB条目数(K)', color='skyblue')
    bars2 = ax2.bar(x + width/2, [c/1024/1024 for c in coverage], width, 
                   label='覆盖内存(MB)', color='lightcoral')
    
    ax2.set_xlabel('页大小')
    ax2.set_ylabel('数量')
    ax2.set_title('不同页大小下的TLB效率')
    ax2.set_xticks(x)
    ax2.set_xticklabels(page_sizes)
    ax2.legend()
    
    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.0f}K', ha='center', va='bottom')
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.0f}MB', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/memory_management/tlb_performance_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("TLB性能分析图表已创建")

def create_page_replacement_comparison():
    """创建页面置换算法性能比较图"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 命中率比较
    algorithms = ['OPT', 'LRU', 'LFU', 'Clock', 'FIFO']
    hit_rates = [0.85, 0.82, 0.80, 0.78, 0.75]
    colors = ['#2E8B57', '#4169E1', '#FF6347', '#FFD700', '#DDA0DD']
    
    bars = ax1.bar(algorithms, hit_rates, color=colors, alpha=0.8)
    ax1.set_ylabel('命中率')
    ax1.set_title('页面置换算法命中率比较')
    ax1.set_ylim(0, 1)
    
    # 添加数值标签
    for bar, rate in zip(bars, hit_rates):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{rate:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. 实现复杂度
    complexity = {'OPT': '不可实现', 'LRU': 'O(n)', 'LFU': 'O(log n)', 'Clock': 'O(1)', 'FIFO': 'O(1)'}
    complexity_values = {'不可实现': 5, 'O(n)': 4, 'O(log n)': 3, 'O(1)': 1}
    
    y_pos = np.arange(len(algorithms))
    values = [complexity_values[complexity[alg]] for alg in algorithms]
    
    bars2 = ax2.barh(y_pos, values, color=colors, alpha=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(algorithms)
    ax2.set_xlabel('实现复杂度 (1=简单, 5=复杂)')
    ax2.set_title('算法实现复杂度比较')
    
    # 3. Belady异常演示
    frame_sizes = [3, 4, 5, 6, 7]
    fifo_faults = [9, 10, 8, 7, 6]  # FIFO可能出现Belady异常
    lru_faults = [10, 8, 7, 6, 5]   # LRU正常
    
    ax3.plot(frame_sizes, fifo_faults, 'o-', color='red', linewidth=2, label='FIFO (Belady异常)')
    ax3.plot(frame_sizes, lru_faults, 's-', color='blue', linewidth=2, label='LRU (正常)')
    ax3.set_xlabel('页框数')
    ax3.set_ylabel('缺页次数')
    ax3.set_title('Belady异常现象演示')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 工作集大小对性能的影响
    working_set_sizes = np.linspace(10, 100, 20)
    lru_performance = 0.9 * np.exp(-working_set_sizes/50) + 0.1
    fifo_performance = 0.8 * np.exp(-working_set_sizes/40) + 0.15
    clock_performance = 0.85 * np.exp(-working_set_sizes/45) + 0.12
    
    ax4.plot(working_set_sizes, lru_performance, label='LRU', linewidth=2)
    ax4.plot(working_set_sizes, fifo_performance, label='FIFO', linewidth=2)
    ax4.plot(working_set_sizes, clock_performance, label='Clock', linewidth=2)
    ax4.set_xlabel('工作集大小')
    ax4.set_ylabel('相对性能')
    ax4.set_title('工作集大小对算法性能的影响')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/memory_management/page_replacement_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("页面置换算法比较图表已创建")

def create_memory_allocation_flowchart():
    """创建内存分配流程图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # 定义流程节点
    nodes = [
        {'name': '内存请求', 'pos': (0.5, 0.9), 'color': '#FFE082'},
        {'name': '请求大小判断', 'pos': (0.5, 0.8), 'color': '#81C784'},
        {'name': '小对象(<页)', 'pos': (0.2, 0.65), 'color': '#64B5F6'},
        {'name': '大对象(≥页)', 'pos': (0.8, 0.65), 'color': '#64B5F6'},
        {'name': 'Slab分配器', 'pos': (0.2, 0.5), 'color': '#FFB74D'},
        {'name': '伙伴系统', 'pos': (0.8, 0.5), 'color': '#FFB74D'},
        {'name': '分配成功', 'pos': (0.5, 0.35), 'color': '#A5D6A7'},
        {'name': '内存不足', 'pos': (0.5, 0.2), 'color': '#EF9A9A'}
    ]
    
    # 绘制节点
    for node in nodes:
        circle = plt.Circle(node['pos'], 0.06, facecolor=node['color'], 
                          edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        ax.text(node['pos'][0], node['pos'][1], node['name'], 
               ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 绘制连接线和箭头
    connections = [
        ((0.5, 0.84), (0.5, 0.86)),  # 请求到判断
        ((0.45, 0.76), (0.25, 0.71)),  # 判断到小对象
        ((0.55, 0.76), (0.75, 0.71)),  # 判断到大对象
        ((0.2, 0.59), (0.2, 0.56)),  # 小对象到Slab
        ((0.8, 0.59), (0.8, 0.56)),  # 大对象到伙伴
        ((0.2, 0.44), (0.45, 0.41)),  # Slab到成功
        ((0.8, 0.44), (0.55, 0.41)),  # 伙伴到成功
        ((0.5, 0.29), (0.5, 0.26))   # 成功到不足
    ]
    
    for start, end in connections:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Linux内存分配流程图', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/memory_management/memory_allocation_flowchart.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("内存分配流程图已创建")

def create_slab_allocator_structure():
    """创建Slab分配器结构图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 绘制内存层次结构
    # 物理内存
    physical_mem = patches.Rectangle((0.1, 0.1), 0.8, 0.15, 
                                   facecolor='#E1F5FE', edgecolor='black', linewidth=2)
    ax.add_patch(physical_mem)
    ax.text(0.5, 0.175, '物理内存 (4KB页)', ha='center', va='center', 
           fontsize=12, fontweight='bold')
    
    # 伙伴系统
    buddy_system = patches.Rectangle((0.1, 0.3), 0.8, 0.15, 
                                   facecolor='#E8F5E8', edgecolor='black', linewidth=2)
    ax.add_patch(buddy_system)
    ax.text(0.5, 0.375, '伙伴系统 (页级分配)', ha='center', va='center', 
           fontsize=12, fontweight='bold')
    
    # Slab缓存
    slab_caches = [
        {'name': 'kmalloc-32', 'x': 0.1, 'width': 0.15, 'color': '#FFF3E0'},
        {'name': 'kmalloc-64', 'x': 0.3, 'width': 0.15, 'color': '#FFF3E0'},
        {'name': 'kmalloc-128', 'x': 0.5, 'width': 0.15, 'color': '#FFF3E0'},
        {'name': 'kmalloc-256', 'x': 0.7, 'width': 0.15, 'color': '#FFF3E0'}
    ]
    
    for cache in slab_caches:
        slab = patches.Rectangle((cache['x'], 0.5), cache['width'], 0.2, 
                               facecolor=cache['color'], edgecolor='black', linewidth=1)
        ax.add_patch(slab)
        ax.text(cache['x'] + cache['width']/2, 0.6, cache['name'], 
               ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 对象分布
    objects = ['对象1', '对象2', '对象3', '对象4', '对象5', '对象6']
    for i, obj in enumerate(objects):
        x = 0.15 + (i % 3) * 0.1
        y = 0.52 + (i // 3) * 0.08
        circle = plt.Circle((x, y), 0.015, facecolor='#FFB74D', 
                          edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        ax.text(x, y-0.04, obj, ha='center', va='center', fontsize=8)
    
    # 状态标识
    states = [
        {'name': '满(Full)', 'x': 0.15, 'y': 0.8, 'color': '#FFCDD2'},
        {'name': '部分(Partial)', 'x': 0.5, 'y': 0.8, 'color': '#FFF9C4'},
        {'name': '空(Empty)', 'x': 0.85, 'y': 0.8, 'color': '#C8E6C9'}
    ]
    
    for state in states:
        circle = plt.Circle((state['x'], state['y']), 0.04, 
                          facecolor=state['color'], edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        ax.text(state['x'], state['y']-0.07, state['name'], 
               ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 添加说明文字
    ax.text(0.02, 0.95, 'Slab分配器结构', fontsize=16, fontweight='bold')
    ax.text(0.02, 0.92, '• 基于伙伴系统提供字节级分配', fontsize=11)
    ax.text(0.02, 0.89, '• 维护常用对象缓存减少碎片', fontsize=11)
    ax.text(0.02, 0.86, '• 支持CPU本地缓存优化', fontsize=11)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/memory_management/slab_allocator_structure.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Slab分配器结构图已创建")

def create_memory_fragmentation_analysis():
    """创建内存碎片分析图表"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 伙伴系统内部碎片分析
    request_sizes = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])  # KB
    allocated_sizes = 2**np.ceil(np.log2(request_sizes))  # 2的幂次分配
    fragmentation_rate = (allocated_sizes - request_sizes) / allocated_sizes * 100
    
    ax1.bar(range(len(request_sizes)), fragmentation_rate, color='lightcoral', alpha=0.8)
    ax1.set_xlabel('请求大小 (KB)')
    ax1.set_ylabel('内部碎片率 (%)')
    ax1.set_title('伙伴系统内部碎片分析')
    ax1.set_xticks(range(len(request_sizes)))
    ax1.set_xticklabels([f'{size}KB' for size in request_sizes], rotation=45)
    
    # 添加最坏情况标记
    max_frag_idx = np.argmax(fragmentation_rate)
    ax1.annotate(f'最坏情况: {fragmentation_rate[max_frag_idx]:.1f}%', 
                xy=(max_frag_idx, fragmentation_rate[max_frag_idx]),
                xytext=(max_frag_idx+1, fragmentation_rate[max_frag_idx]+5),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')
    
    # 2. 外部碎片演示
    # 模拟内存分配和释放过程
    memory_blocks = ['A(8KB)', 'B(16KB)', 'C(8KB)', 'D(32KB)', 'E(16KB)']
    time_steps = ['初始', '分配A,B,C', '释放A', '释放C', '分配D', '释放B,E']
    
    # 简化的外部碎片可视化
    fragmentation_levels = [0, 20, 35, 25, 40, 10]  # 外部碎片程度
    
    ax2.plot(range(len(time_steps)), fragmentation_levels, 'o-', 
            linewidth=2, markersize=8, color='orange')
    ax2.set_xlabel('时间步骤')
    ax2.set_ylabel('外部碎片程度 (%)')
    ax2.set_title('外部碎片演变过程')
    ax2.set_xticks(range(len(time_steps)))
    ax2.set_xticklabels(time_steps, rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # 3. 分配算法效率比较
    algorithms = ['伙伴系统', 'Slab', 'Slub', 'SLOB']
    allocation_speed = [85, 95, 98, 75]  # 相对分配速度
    memory_efficiency = [70, 90, 92, 80]  # 内存利用效率
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, allocation_speed, width, 
                   label='分配速度', color='skyblue')
    bars2 = ax3.bar(x + width/2, memory_efficiency, width, 
                   label='内存效率', color='lightgreen')
    
    ax3.set_xlabel('分配算法')
    ax3.set_ylabel('性能指标 (%)')
    ax3.set_title('分配算法性能比较')
    ax3.set_xticks(x)
    ax3.set_xticklabels(algorithms)
    ax3.legend()
    
    # 4. 内存压缩效果
    compression_ratios = np.linspace(0.1, 0.9, 20)
    available_memory = 1000 * (1 + compression_ratios)  # 基础内存1000MB
    access_overhead = 5 + 15 * compression_ratios  # 访问开销增加
    
    ax4_twin = ax4.twinx()
    
    line1 = ax4.plot(compression_ratios, available_memory, 'b-', linewidth=2, label='可用内存')
    line2 = ax4_twin.plot(compression_ratios, access_overhead, 'r-', linewidth=2, label='访问开销')
    
    ax4.set_xlabel('压缩比')
    ax4.set_ylabel('可用内存 (MB)', color='blue')
    ax4_twin.set_ylabel('访问开销 (%)', color='red')
    ax4.set_title('内存压缩的收益与代价')
    
    # 合并图例
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='center right')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/memory_management/memory_fragmentation_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("内存碎片分析图表已创建")

def main():
    """主函数：创建所有图表"""
    # 确保输出目录存在
    output_dir = '/workspace/docs/memory_management'
    os.makedirs(output_dir, exist_ok=True)
    
    print("开始创建Linux内存管理可视化图表...")
    
    # 创建各种图表
    create_page_table_diagram()
    create_tlb_performance_chart()
    create_page_replacement_comparison()
    create_memory_allocation_flowchart()
    create_slab_allocator_structure()
    create_memory_fragmentation_analysis()
    
    print("\n所有图表创建完成！")
    print(f"图表保存在: {output_dir}")

if __name__ == "__main__":
    main()
