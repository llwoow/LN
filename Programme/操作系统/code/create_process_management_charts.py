#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程管理和调度算法图表生成脚本
创建各种操作系统概念的可视化图表
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np
import warnings

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

    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def create_process_state_diagram():
    """创建进程状态转换图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 定义状态框的位置和大小
    states = {
        '新建': (2, 6, 'lightblue'),
        '就绪': (6, 6, 'lightgreen'),
        '运行': (10, 6, 'lightyellow'),
        '阻塞': (6, 2, 'lightcoral'),
        '终止': (10, 2, 'lightgray')
    }
    
    # 绘制状态框
    for state, (x, y, color) in states.items():
        rect = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, state, ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 定义转换关系和箭头
    transitions = [
        ('新建', '就绪', '创建'),
        ('就绪', '运行', '调度'),
        ('运行', '就绪', '时间片到'),
        ('运行', '阻塞', '等待I/O'),
        ('运行', '终止', '完成'),
        ('阻塞', '就绪', 'I/O完成'),
        ('就绪', '阻塞', '等待资源'),
        ('阻塞', '终止', '异常终止')
    ]
    
    # 绘制箭头
    state_positions = {state: (x, y) for state, (x, y, _) in states.items()}
    
    for from_state, to_state, label in transitions:
        x1, y1 = state_positions[from_state]
        x2, y2 = state_positions[to_state]
        
        # 计算箭头起点和终点
        if from_state == '新建' and to_state == '就绪':
            arrow = FancyArrowPatch((x1+0.8, y1), (x2-0.8, y2),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='blue', linewidth=2)
        elif from_state == '就绪' and to_state == '运行':
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='green', linewidth=2)
        elif from_state == '运行' and to_state == '就绪':
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='orange', linewidth=2)
        elif from_state == '运行' and to_state == '阻塞':
            arrow = FancyArrowPatch((x1, y1-0.4), (x2, y2+0.4),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='red', linewidth=2)
        elif from_state == '运行' and to_state == '终止':
            arrow = FancyArrowPatch((x1, y1-0.4), (x2, y2+0.4),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='purple', linewidth=2)
        elif from_state == '阻塞' and to_state == '就绪':
            arrow = FancyArrowPatch((x2, y2-0.4), (x1, y1+0.4),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='cyan', linewidth=2)
        elif from_state == '就绪' and to_state == '阻塞':
            arrow = FancyArrowPatch((x1, y1-0.4), (x2, y2+0.4),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='magenta', linewidth=2)
        elif from_state == '阻塞' and to_state == '终止':
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='brown', linewidth=2)
        
        ax.add_patch(arrow)
        
        # 添加标签
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                fontsize=9)
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('进程状态转换图', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/process_state_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("进程状态转换图已保存到: /workspace/docs/process_state_diagram.png")

def create_scheduling_algorithm_flowchart():
    """创建调度算法流程图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 定义流程框的位置和内容
    boxes = [
        (7, 9, '开始', 'lightblue'),
        (7, 8, '进程到达', 'lightgreen'),
        (5, 7, 'FCFS: 按到达时间排序', 'lightyellow'),
        (9, 7, 'SJF: 按执行时间排序', 'lightyellow'),
        (3, 6, 'RR: 时间片轮转', 'lightyellow'),
        (11, 6, '优先级: 按优先级排序', 'lightyellow'),
        (7, 5, '选择下一个进程', 'lightcoral'),
        (7, 4, '执行进程', 'lightgray'),
        (5, 3, '时间片用完?', 'lightpink'),
        (9, 3, '进程完成?', 'lightpink'),
        (3, 2, '重新排队', 'lightcyan'),
        (11, 2, '进程结束', 'lightcyan'),
        (7, 1, '结束', 'lightblue')
    ]
    
    # 绘制流程框
    for x, y, text, color in boxes:
        if text in ['开始', '结束']:
            # 圆形
            circle = Circle((x, y), 0.4, facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(circle)
        elif '?' in text:
            # 菱形
            diamond = patches.RegularPolygon((x, y), 4, radius=0.5, 
                                           orientation=np.pi/4, 
                                           facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(diamond)
        else:
            # 矩形
            rect = FancyBboxPatch((x-0.7, y-0.3), 1.4, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(rect)
        
        ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # 定义连接线
    arrows = [
        ((7, 8.6), (7, 8.4)),  # 开始 -> 进程到达
        ((7, 7.6), (7, 7.4)),  # 进程到达 -> 选择
        ((6.3, 7.4), (5.7, 7.1)),  # 选择 -> FCFS
        ((7.7, 7.4), (8.3, 7.1)),  # 选择 -> SJF
        ((5.7, 6.9), (3.7, 6.1)),  # FCFS -> RR
        ((8.3, 6.9), (10.3, 6.1)),  # SJF -> 优先级
        ((3.7, 5.9), (6.3, 5.1)),  # RR -> 选择
        ((10.3, 5.9), (7.7, 5.1)),  # 优先级 -> 选择
        ((7, 4.7), (7, 4.3)),  # 选择 -> 执行
        ((6.3, 3.7), (5.7, 3.3)),  # 执行 -> 时间片?
        ((7.7, 3.7), (8.3, 3.3)),  # 执行 -> 完成?
        ((4.3, 2.7), (3.7, 2.3)),  # 时间片? -> 重新排队
        ((8.3, 2.7), (10.3, 2.3)),  # 完成? -> 结束
        ((3, 1.7), (6.3, 1.3)),  # 重新排队 -> 结束
        ((7, 0.6), (7, 1.4))  # 结束 -> 开始
    ]
    
    # 绘制箭头
    for start, end in arrows:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', 
                              mutation_scale=15, color='black', linewidth=1.5)
        ax.add_patch(arrow)
    
    # 添加标签
    ax.text(1, 5, '调度算法选择:', fontsize=12, fontweight='bold')
    ax.text(1, 4.5, '• FCFS: 先来先服务', fontsize=10)
    ax.text(1, 4, '• SJF: 最短作业优先', fontsize=10)
    ax.text(1, 3.5, '• RR: 时间片轮转', fontsize=10)
    ax.text(1, 3, '• 优先级: 按优先级调度', fontsize=10)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('进程调度算法流程图', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/scheduling_algorithm_flowchart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("调度算法流程图已保存到: /workspace/docs/scheduling_algorithm_flowchart.png")

def create_deadlock_diagram():
    """创建死锁状态图"""
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左图：死锁产生条件
    ax1.set_title('死锁产生的四个必要条件', fontsize=14, fontweight='bold')
    
    conditions = [
        '互斥条件',
        '占有并等待',
        '非剥夺条件',
        '循环等待'
    ]
    
    colors = ['lightcoral', 'lightblue', 'lightgreen', 'lightyellow']
    
    for i, (condition, color) in enumerate(zip(conditions, colors)):
        y = 4 - i * 0.8
        rect = FancyBboxPatch((1, y-0.3), 6, 0.6, 
                             boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(4, y, condition, ha='center', va='center', fontsize=12, fontweight='bold')
        
        if i < 3:
            arrow = FancyArrowPatch((4, y-0.4), (4, y-0.8),
                                  arrowstyle='->', mutation_scale=20, 
                                  color='red', linewidth=2)
            ax1.add_patch(arrow)
    
    ax1.text(4, 0.5, '四个条件必须同时满足才会发生死锁', 
             ha='center', va='center', fontsize=11, 
             bbox=dict(boxstyle="round,pad=0.5", facecolor='pink', alpha=0.7))
    
    ax1.set_xlim(0, 8)
    ax1.set_ylim(0, 5)
    ax1.axis('off')
    
    # 右图：死锁示例
    ax2.set_title('死锁示例：进程资源分配图', fontsize=14, fontweight='bold')
    
    # 绘制进程圆圈
    processes = [(2, 3, 'P1'), (6, 3, 'P2')]
    for x, y, name in processes:
        circle = Circle((x, y), 0.5, facecolor='lightblue', edgecolor='black', linewidth=2)
        ax2.add_patch(circle)
        ax2.text(x, y, name, ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 绘制资源矩形
    resources = [(2, 1, 'R1'), (6, 1, 'R2')]
    for x, y, name in resources:
        rect = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                             boxstyle="round,pad=0.05", 
                             facecolor='lightgreen', edgecolor='black', linewidth=2)
        ax2.add_patch(rect)
        ax2.text(x, y, name, ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 绘制资源分配边
    # P1 -> R1 (已分配)
    arrow1 = FancyArrowPatch((2, 2.5), (2, 1.5),
                           arrowstyle='->', mutation_scale=20, 
                           color='green', linewidth=3)
    ax2.add_patch(arrow1)
    ax2.text(1.5, 2, '已分配', fontsize=9, color='green', fontweight='bold')
    
    # P2 -> R2 (已分配)
    arrow2 = FancyArrowPatch((6, 2.5), (6, 1.5),
                           arrowstyle='->', mutation_scale=20, 
                           color='green', linewidth=3)
    ax2.add_patch(arrow2)
    ax2.text(6.5, 2, '已分配', fontsize=9, color='green', fontweight='bold')
    
    # 绘制请求边 (形成循环)
    # P1 -> R2 (请求)
    arrow3 = FancyArrowPatch((2.5, 3), (5.5, 3),
                           arrowstyle='->', mutation_scale=20, 
                           color='red', linewidth=3)
    ax2.add_patch(arrow3)
    ax2.text(4, 3.3, '请求', fontsize=9, color='red', fontweight='bold')
    
    # P2 -> R1 (请求)
    arrow4 = FancyArrowPatch((5.5, 3), (2.5, 3),
                           arrowstyle='->', mutation_scale=20, 
                           color='red', linewidth=3)
    ax2.add_patch(arrow4)
    ax2.text(4, 2.7, '请求', fontsize=9, color='red', fontweight='bold')
    
    ax2.text(4, 0.3, 'P1等待R2，P2等待R1\n形成循环等待死锁', 
             ha='center', va='center', fontsize=11, 
             bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.7))
    
    ax2.set_xlim(0, 8)
    ax2.set_ylim(0, 4)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/deadlock_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("死锁状态图已保存到: /workspace/docs/deadlock_diagram.png")

def create_semaphore_working_principle():
    """创建信号量工作原理图"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 图1：信号量基本概念
    ax1.set_title('信号量基本概念', fontsize=14, fontweight='bold')
    
    # 绘制信号量结构
    rect = FancyBboxPatch((1, 3), 6, 2, 
                         boxstyle="round,pad=0.2", 
                         facecolor='lightblue', edgecolor='black', linewidth=2)
    ax1.add_patch(rect)
    ax1.text(4, 4, '信号量 S', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.text(4, 3.5, 'S ≥ 0: 可用资源数', ha='center', va='center', fontsize=11)
    ax1.text(4, 3.2, 'S < 0: |S| = 等待进程数', ha='center', va='center', fontsize=11)
    
    # 绘制等待队列
    for i in range(3):
        y = 2 - i * 0.5
        circle = Circle((2, y), 0.2, facecolor='lightyellow', edgecolor='black', linewidth=1)
        ax1.add_patch(circle)
        ax1.text(2, y, f'P{i+1}', ha='center', va='center', fontsize=8)
        
        if i < 2:
            arrow = FancyArrowPatch((2.2, y-0.1), (2.2, y-0.4),
                                  arrowstyle='->', mutation_scale=10, 
                                  color='gray', linewidth=1)
            ax1.add_patch(arrow)
    
    ax1.text(2, 0.5, '等待队列', ha='center', va='center', fontsize=10, fontweight='bold')
    
    ax1.set_xlim(0, 8)
    ax1.set_ylim(0, 6)
    ax1.axis('off')
    
    # 图2：P操作流程
    ax2.set_title('P操作（Wait）流程', fontsize=14, fontweight='bold')
    
    p_steps = [
        (4, 5, '开始'),
        (4, 4.3, 'S = S - 1'),
        (2, 3.5, 'S < 0?'),
        (6, 3.5, 'S ≥ 0'),
        (2, 2.5, '阻塞进程\n加入等待队列'),
        (4, 1.5, '进入临界区')
    ]
    
    for i, (x, y, text) in enumerate(p_steps):
        if i in [2]:  # 判断条件
            diamond = patches.RegularPolygon((x, y), 4, radius=0.4, 
                                           orientation=np.pi/4, 
                                           facecolor='lightyellow', edgecolor='black', linewidth=2)
            ax2.add_patch(diamond)
        else:
            rect = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightgreen' if i == 0 else 'lightblue', 
                                 edgecolor='black', linewidth=2)
            ax2.add_patch(rect)
        
        ax2.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 绘制连接线
    arrows_p = [
        ((4, 4.7), (4, 4.6)),
        ((4, 4), (4, 3.8)),
        ((3.4, 3.5), (2.4, 3.5)),
        ((4.6, 3.5), (5.4, 3.5)),
        ((1.6, 3.5), (1.6, 2.8)),
        ((2.4, 2.5), (3.4, 1.8)),
        ((5.4, 3.5), (4.6, 1.8))
    ]
    
    for start, end in arrows_p:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', 
                              mutation_scale=15, color='blue', linewidth=1.5)
        ax2.add_patch(arrow)
    
    # 添加标签
    ax2.text(1, 2, '是', fontsize=9, color='red', fontweight='bold')
    ax2.text(7, 3, '否', fontsize=9, color='green', fontweight='bold')
    
    ax2.set_xlim(0, 8)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    
    # 图3：V操作流程
    ax3.set_title('V操作（Signal）流程', fontsize=14, fontweight='bold')
    
    v_steps = [
        (4, 5, '开始'),
        (4, 4.3, 'S = S + 1'),
        (2, 3.5, 'S ≤ 0?'),
        (6, 3.5, 'S > 0'),
        (2, 2.5, '唤醒等待队列\n中第一个进程'),
        (4, 1.5, '退出临界区')
    ]
    
    for i, (x, y, text) in enumerate(v_steps):
        if i in [2]:  # 判断条件
            diamond = patches.RegularPolygon((x, y), 4, radius=0.4, 
                                           orientation=np.pi/4, 
                                           facecolor='lightyellow', edgecolor='black', linewidth=2)
            ax3.add_patch(diamond)
        else:
            rect = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightgreen' if i == 0 else 'lightblue', 
                                 edgecolor='black', linewidth=2)
            ax3.add_patch(rect)
        
        ax3.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 绘制连接线
    arrows_v = [
        ((4, 4.7), (4, 4.6)),
        ((4, 4), (4, 3.8)),
        ((3.4, 3.5), (2.4, 3.5)),
        ((4.6, 3.5), (5.4, 3.5)),
        ((1.6, 3.5), (1.6, 2.8)),
        ((2.4, 2.5), (3.4, 1.8)),
        ((5.4, 3.5), (4.6, 1.8))
    ]
    
    for start, end in arrows_v:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', 
                              mutation_scale=15, color='blue', linewidth=1.5)
        ax3.add_patch(arrow)
    
    # 添加标签
    ax3.text(1, 2, '是', fontsize=9, color='red', fontweight='bold')
    ax3.text(7, 3, '否', fontsize=9, color='green', fontweight='bold')
    
    ax3.set_xlim(0, 8)
    ax3.set_ylim(0, 6)
    ax3.axis('off')
    
    # 图4：信号量应用示例
    ax4.set_title('信号量应用：生产者-消费者问题', fontsize=14, fontweight='bold')
    
    # 绘制缓冲区
    buffer_rect = FancyBboxPatch((3, 2), 4, 2, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax4.add_patch(buffer_rect)
    ax4.text(5, 3, '共享缓冲区', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 绘制生产者
    prod_rect = FancyBboxPatch((1, 3.5), 1.5, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='lightblue', edgecolor='black', linewidth=2)
    ax4.add_patch(prod_rect)
    ax4.text(1.75, 4, '生产者', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 绘制消费者
    cons_rect = FancyBboxPatch((7.5, 3.5), 1.5, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax4.add_patch(cons_rect)
    ax4.text(8.25, 4, '消费者', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 绘制信号量
    sem_rect1 = FancyBboxPatch((0.5, 1.5), 1, 0.5, 
                              boxstyle="round,pad=0.05", 
                              facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax4.add_patch(sem_rect1)
    ax4.text(1, 1.75, 'empty', ha='center', va='center', fontsize=9, fontweight='bold')
    
    sem_rect2 = FancyBboxPatch((8.5, 1.5), 1, 0.5, 
                              boxstyle="round,pad=0.05", 
                              facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax4.add_patch(sem_rect2)
    ax4.text(9, 1.75, 'full', ha='center', va='center', fontsize=9, fontweight='bold')
    
    sem_rect3 = FancyBboxPatch((4.5, 0.5), 1, 0.5, 
                              boxstyle="round,pad=0.05", 
                              facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax4.add_patch(sem_rect3)
    ax4.text(5, 0.75, 'mutex', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # 绘制箭头
    # 生产者到缓冲区
    arrow_prod = FancyArrowPatch((2.5, 4), (3, 3.5),
                               arrowstyle='->', mutation_scale=15, 
                               color='blue', linewidth=2)
    ax4.add_patch(arrow_prod)
    
    # 缓冲区到消费者
    arrow_cons = FancyArrowPatch((7, 3.5), (7.5, 4),
                               arrowstyle='->', mutation_scale=15, 
                               color='red', linewidth=2)
    ax4.add_patch(arrow_cons)
    
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 6)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/semaphore_working_principle.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("信号量工作原理图已保存到: /workspace/docs/semaphore_working_principle.png")

def create_banker_algorithm_diagram():
    """创建银行家算法图解"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 图1：银行家算法数据结构
    ax1.set_title('银行家算法数据结构', fontsize=14, fontweight='bold')
    
    # 绘制矩阵表格
    matrices = [
        ('最大需求矩阵 Max', np.array([[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]])),
        ('已分配矩阵 Allocation', np.array([[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]])),
        ('需求矩阵 Need', np.array([[7, 4, 3], [1, 2, 2], [6, 0, 0], [0, 1, 1], [4, 3, 1]]))
    ]
    
    y_start = 4.5
    for i, (title, matrix) in enumerate(matrices):
        y = y_start - i * 1.5
        ax1.text(2, y + 0.5, title, fontsize=12, fontweight='bold')
        
        # 绘制矩阵
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                rect = FancyBboxPatch((3 + col * 0.8, y - row * 0.4), 0.7, 0.3, 
                                     boxstyle="round,pad=0.02", 
                                     facecolor='lightblue', edgecolor='black', linewidth=1)
                ax1.add_patch(rect)
                ax1.text(3.35 + col * 0.8, y - row * 0.4 + 0.15, str(matrix[row, col]), 
                        ha='center', va='center', fontsize=9)
    
    # 添加进程标签
    ax1.text(2.5, 4.8, 'P0', fontsize=10, fontweight='bold')
    ax1.text(2.5, 4.4, 'P1', fontsize=10, fontweight='bold')
    ax1.text(2.5, 4.0, 'P2', fontsize=10, fontweight='bold')
    ax1.text(2.5, 3.6, 'P3', fontsize=10, fontweight='bold')
    ax1.text(2.5, 3.2, 'P4', fontsize=10, fontweight='bold')
    
    ax1.text(3.35, 5.2, 'A', fontsize=10, fontweight='bold')
    ax1.text(4.15, 5.2, 'B', fontsize=10, fontweight='bold')
    ax1.text(4.95, 5.2, 'C', fontsize=10, fontweight='bold')
    
    ax1.set_xlim(0, 8)
    ax1.set_ylim(0, 6)
    ax1.axis('off')
    
    # 图2：安全性检测流程
    ax2.set_title('安全性检测流程', fontsize=14, fontweight='bold')
    
    safety_steps = [
        (4, 5, '初始化:\nWork = Available\nFinish[i] = false'),
        (4, 4, '寻找满足条件的进程:\nFinish[i]=false 且\nNeed[i] ≤ Work'),
        (6, 3, '执行进程:\nWork = Work + Allocation[i]\nFinish[i] = true'),
        (2, 3, '检查所有进程:\n是否所有Finish[i]=true?'),
        (4, 2, '安全状态:\n存在安全序列\n不安全状态:\n不存在安全序列')
    ]
    
    for i, (x, y, text) in enumerate(safety_steps):
        if i == 3:  # 判断条件
            diamond = patches.RegularPolygon((x, y), 4, radius=0.5, 
                                           orientation=np.pi/4, 
                                           facecolor='lightyellow', edgecolor='black', linewidth=2)
            ax2.add_patch(diamond)
        else:
            rect = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightgreen' if i == 0 else 'lightblue', 
                                 edgecolor='black', linewidth=2)
            ax2.add_patch(rect)
        
        ax2.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # 绘制连接线
    arrows_safety = [
        ((4, 4.6), (4, 4.4)),
        ((4.8, 4), (5.2, 3.2)),
        ((3.2, 3), (2.8, 3.2)),
        ((2, 2.6), (3.2, 2.2)),
        ((4.8, 2), (5.2, 2.2))
    ]
    
    for start, end in arrows_safety:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', 
                              mutation_scale=15, color='blue', linewidth=1.5)
        ax2.add_patch(arrow)
    
    ax2.text(1, 2.5, '否', fontsize=9, color='red', fontweight='bold')
    ax2.text(7, 2.5, '是', fontsize=9, color='green', fontweight='bold')
    
    ax2.set_xlim(0, 8)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    
    # 图3：安全序列示例
    ax3.set_title('安全序列示例', fontsize=14, fontweight='bold')
    
    # 绘制可用资源
    avail_rect = FancyBboxPatch((1, 4), 6, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax3.add_patch(avail_rect)
    ax3.text(4, 4.5, 'Available = [3, 3, 2]', ha='center', va='center', 
             fontsize=12, fontweight='bold')
    
    # 绘制安全序列步骤
    steps = [
        (1, 2.5, 'P1: Need=[1,2,2]\nAllocation=[2,0,0]\nWork=[5,3,2]'),
        (3, 2.5, 'P3: Need=[0,1,1]\nAllocation=[2,1,1]\nWork=[7,4,3]'),
        (5, 2.5, 'P4: Need=[4,3,1]\nAllocation=[0,0,2]\nWork=[7,4,5]'),
        (7, 2.5, 'P0: Need=[7,4,3]\nAllocation=[0,1,0]\nWork=[7,5,5]'),
        (9, 2.5, 'P2: Need=[6,0,0]\nAllocation=[3,0,2]\nWork=[10,5,7]')
    ]
    
    for i, (x, y, text) in enumerate(steps):
        color = ['lightgreen', 'lightblue', 'lightyellow', 'lightpink', 'lightcyan'][i]
        rect = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                             boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=2)
        ax3.add_patch(rect)
        ax3.text(x, y, text, ha='center', va='center', fontsize=8, fontweight='bold')
        
        if i < 4:
            arrow = FancyArrowPatch((x+0.8, y), (x+1.2, y),
                                  arrowstyle='->', mutation_scale=15, 
                                  color='blue', linewidth=2)
            ax3.add_patch(arrow)
    
    ax3.text(5, 1, '安全序列: <P1, P3, P4, P0, P2>', ha='center', va='center', 
             fontsize=12, fontweight='bold', 
             bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.7))
    
    ax3.set_xlim(0, 11)
    ax3.set_ylim(0, 6)
    ax3.axis('off')
    
    # 图4：银行家算法优缺点
    ax4.set_title('银行家算法优缺点分析', fontsize=14, fontweight='bold')
    
    pros_cons = [
        ('优点', ['避免死锁发生', '保证系统安全状态', '动态检测资源分配', '支持多进程多资源类型'], 'lightgreen'),
        ('缺点', ['实现复杂，开销大', '需要预先知道最大需求', '可能拒绝合理请求', '不适用于动态环境'], 'lightcoral')
    ]
    
    for i, (title, items, color) in enumerate(pros_cons):
        x = 2 + i * 4
        
        # 标题框
        title_rect = FancyBboxPatch((x-1, 4), 2, 0.8, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=color, edgecolor='black', linewidth=2)
        ax4.add_patch(title_rect)
        ax4.text(x, 4.4, title, ha='center', va='center', fontsize=14, fontweight='bold')
        
        # 内容框
        content_rect = FancyBboxPatch((x-1, 1), 2, 2.8, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor='white', edgecolor='black', linewidth=2)
        ax4.add_patch(content_rect)
        
        for j, item in enumerate(items):
            ax4.text(x, 3.4 - j * 0.4, f'• {item}', ha='center', va='center', fontsize=10)
    
    ax4.set_xlim(0, 8)
    ax4.set_ylim(0, 6)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/banker_algorithm_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("银行家算法图解已保存到: /workspace/docs/banker_algorithm_diagram.png")

def create_ipc_mechanisms_comparison():
    """创建IPC机制对比图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    ax.set_title('进程间通信(IPC)机制对比', fontsize=16, fontweight='bold', pad=20)
    
    # IPC机制数据
    ipc_data = [
        ('管道', '本地、父子进程', '字节流', '单向、半双工', '低', '简单', '不支持', '不支持'),
        ('命名管道', '本地、无亲缘关系', '字节流', '单向、半双工', '低', '简单', '不支持', '不支持'),
        ('消息队列', '本地进程', '结构化消息', '异步、双向', '中', '中等', '支持', '支持'),
        ('共享内存', '本地进程', '任意数据', '同步访问', '高', '复杂', '支持', '支持'),
        ('信号', '本地进程', '信号值', '异步', '高', '简单', '不支持', '不支持'),
        ('套接字', '本地/网络进程', '任意数据', '双向', '中', '复杂', '支持', '支持')
    ]
    
    # 绘制表格
    headers = ['机制', '适用范围', '数据类型', '通信模式', '速度', '复杂度', '同步控制', '网络支持']
    
    # 计算表格尺寸
    col_widths = [1.5, 1.8, 1.5, 1.8, 0.8, 1, 1.2, 1.2]
    row_height = 0.6
    
    # 绘制表头
    x_pos = 0.5
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        rect = FancyBboxPatch((x_pos, 8.5), width, 0.8, 
                             boxstyle="round,pad=0.05", 
                             facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x_pos + width/2, 8.9, header, ha='center', va='center', 
                fontsize=11, fontweight='bold')
        x_pos += width
    
    # 绘制数据行
    for row_idx, row_data in enumerate(ipc_data):
        y_pos = 7.5 - row_idx * row_height
        x_pos = 0.5
        
        for col_idx, (data, width) in enumerate(zip(row_data, col_widths)):
            color = ['lightgreen', 'lightyellow', 'lightcyan', 'lightpink', 
                    'lightgray', 'lightcoral'][row_idx]
            
            rect = FancyBboxPatch((x_pos, y_pos), width, row_height, 
                                 boxstyle="round,pad=0.02", 
                                 facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            ax.text(x_pos + width/2, y_pos + row_height/2, data, 
                   ha='center', va='center', fontsize=9)
            x_pos += width
    
    # 添加图例
    legend_y = 1.5
    ax.text(0.5, legend_y + 0.5, '速度等级:', fontsize=12, fontweight='bold')
    
    speed_levels = [('低', 'lightgreen'), ('中', 'lightyellow'), ('高', 'lightcoral')]
    for i, (level, color) in enumerate(speed_levels):
        x = 2.5 + i * 1.5
        rect = FancyBboxPatch((x, legend_y), 0.8, 0.4, 
                             boxstyle="round,pad=0.02", 
                             facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(x + 0.4, legend_y + 0.2, level, ha='center', va='center', fontsize=10)
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/ipc_mechanisms_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("IPC机制对比图已保存到: /workspace/docs/ipc_mechanisms_comparison.png")

if __name__ == "__main__":
    print("开始生成进程管理和调度算法图表...")
    
    create_process_state_diagram()
    create_scheduling_algorithm_flowchart()
    create_deadlock_diagram()
    create_semaphore_working_principle()
    create_banker_algorithm_diagram()
    create_ipc_mechanisms_comparison()
    
    print("\n所有图表生成完成！")
