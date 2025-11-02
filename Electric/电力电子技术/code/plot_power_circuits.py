#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电力变换电路图绘制程序
包含电路拓扑图和波形分析图
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
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
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10

def draw_single_phase_rectifier():
    """绘制单相整流电路拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 绘制交流电源
    ax.plot([-2, -2], [0, 2], 'k-', linewidth=2)
    ax.plot([-2, -2], [0, -2], 'k-', linewidth=2)
    ax.text(-2, 2.3, 'AC Input', ha='center', fontsize=12, weight='bold')
    
    # 绘制变压器
    rect = FancyBboxPatch((-1.5, -0.3), 1, 0.6, boxstyle="round,pad=0.1", 
                         facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(-1, 0, 'Transformer', ha='center', va='center', fontsize=10, weight='bold')
    
    # 绘制整流桥
    # 桥臂1 (上臂)
    ax.plot([0.5, 2], [1, 1], 'k-', linewidth=2)  # 上导线
    ax.plot([2, 2], [0.5, 1.5], 'k-', linewidth=2)  # 竖线
    ax.plot([1.8, 2.2], [1.2, 1.2], 'k-', linewidth=3)  # D1 (上二极管)
    ax.text(2, 1.6, 'D1', ha='center', fontsize=12, weight='bold')
    
    # 桥臂2 (下臂)
    ax.plot([0.5, 2], [-1, -1], 'k-', linewidth=2)  # 下导线
    ax.plot([2, 2], [-1.5, -0.5], 'k-', linewidth=2)  # 竖线
    ax.plot([1.8, 2.2], [-1.2, -1.2], 'k-', linewidth=3)  # D2 (下二极管)
    ax.text(2, -1.6, 'D2', ha='center', fontsize=12, weight='bold')
    
    # 桥臂3 (右上)
    ax.plot([2.5, 2.5], [1, 0.5], 'k-', linewidth=2)
    ax.plot([2.2, 2.8], [0.8, 0.8], 'k-', linewidth=3)  # D3
    ax.text(2.5, 1.3, 'D3', ha='center', fontsize=12, weight='bold')
    
    # 桥臂4 (右下)
    ax.plot([2.5, 2.5], [-1, -0.5], 'k-', linewidth=2)
    ax.plot([2.2, 2.8], [-0.8, -0.8], 'k-', linewidth=3)  # D4
    ax.text(2.5, -1.3, 'D4', ha='center', fontsize=12, weight='bold')
    
    # 绘制输出电容和负载
    # 输出电容
    ax.plot([3, 3], [0.5, -0.5], 'k-', linewidth=2)
    ax.text(3.3, 0, 'C', ha='center', fontsize=12, weight='bold')
    
    # 负载电阻
    rect = Rectangle((3.5, -0.2), 1, 0.4, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(4, 0, 'R', ha='center', va='center', fontsize=12, weight='bold')
    
    # 连接线
    ax.plot([-2, -1.5], [0, 0], 'k-', linewidth=2)
    ax.plot([0.5, 0.5], [0, 0], 'k-', linewidth=2)
    ax.plot([2.5, 3], [0, 0], 'k-', linewidth=2)
    ax.plot([4.5, 4.5], [0, 0], 'k-', linewidth=2)
    ax.plot([4.5, 5], [0, 0], 'k-', linewidth=2)
    
    # 标注
    ax.text(1, 2, '单相桥式整流电路', ha='center', fontsize=16, weight='bold')
    ax.text(4.5, 0.5, '+Vdc', ha='center', fontsize=10, weight='bold')
    ax.text(4.5, -0.5, '-Vdc', ha='center', fontsize=10, weight='bold')
    
    ax.set_xlim(-3, 6)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/single_phase_rectifier.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_three_phase_rectifier():
    """绘制三相整流电路拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # 绘制三相交流电源
    phases = ['A', 'B', 'C']
    colors = ['red', 'green', 'blue']
    for i, (phase, color) in enumerate(zip(phases, colors)):
        y_pos = 2 - i * 0.8
        ax.plot([-2, -2], [y_pos-0.2, y_pos+0.2], color=color, linewidth=3)
        ax.text(-2.5, y_pos, f'{phase}相', ha='center', fontsize=12, weight='bold', color=color)
    
    # 绘制三相变压器
    rect = FancyBboxPatch((-1.5, -1), 1, 2, boxstyle="round,pad=0.1", 
                         facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(-1, 0, '三相\n变压器', ha='center', va='center', fontsize=10, weight='bold')
    
    # 绘制六脉冲整流桥
    # 上桥臂
    for i in range(3):
        y_pos = 1.5 - i * 0.6
        ax.plot([0.5, 2], [y_pos, y_pos], 'k-', linewidth=2)
        ax.plot([2, 2], [y_pos-0.2, y_pos+0.2], 'k-', linewidth=2)
        ax.plot([1.8, 2.2], [y_pos, y_pos], 'k-', linewidth=3)
        ax.text(2.3, y_pos, f'D{i+1}', ha='center', fontsize=10, weight='bold')
    
    # 下桥臂
    for i in range(3):
        y_pos = -0.5 - i * 0.6
        ax.plot([0.5, 2], [y_pos, y_pos], 'k-', linewidth=2)
        ax.plot([2, 2], [y_pos-0.2, y_pos+0.2], 'k-', linewidth=2)
        ax.plot([1.8, 2.2], [y_pos, y_pos], 'k-', linewidth=3)
        ax.text(2.3, y_pos, f'D{i+4}', ha='center', fontsize=10, weight='bold')
    
    # 绘制输出电容和负载
    ax.plot([2.5, 2.5], [1, -1], 'k-', linewidth=2)
    ax.text(2.8, 0, 'C', ha='center', fontsize=12, weight='bold')
    
    rect = Rectangle((3, -0.3), 1, 0.6, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(3.5, 0, 'R', ha='center', va='center', fontsize=12, weight='bold')
    
    # 连接线
    for i in range(3):
        y_pos = 2 - i * 0.8
        ax.plot([-2, -1.5], [y_pos, 1.5 - i * 0.6], color=colors[i], linewidth=2)
        ax.plot([-2, -1.5], [y_pos, -0.5 - i * 0.6], color=colors[i], linewidth=2)
    
    ax.plot([2.5, 3], [0, 0], 'k-', linewidth=2)
    ax.plot([4, 4], [0, 0], 'k-', linewidth=2)
    ax.plot([4, 4.5], [0, 0], 'k-', linewidth=2)
    
    # 标注
    ax.text(1, 2.5, '三相六脉冲整流电路', ha='center', fontsize=16, weight='bold')
    ax.text(4.5, 0.5, '+Vdc', ha='center', fontsize=10, weight='bold')
    ax.text(4.5, -0.5, '-Vdc', ha='center', fontsize=10, weight='bold')
    
    ax.set_xlim(-3, 6)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/three_phase_rectifier.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_buck_converter():
    """绘制Buck变换器拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 绘制输入电源
    ax.plot([-2, -2], [0, 2], 'k-', linewidth=3)
    ax.text(-2.5, 1, 'Vin', ha='center', fontsize=12, weight='bold')
    
    # 绘制开关管Q
    rect = FancyBboxPatch((-1.5, 0.5), 1, 1, boxstyle="round,pad=0.1", 
                         facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(-1, 1, 'Q', ha='center', va='center', fontsize=14, weight='bold')
    
    # 绘制电感L
    ax.plot([0.5, 0.5], [0.5, 2], 'k-', linewidth=2)
    # 电感符号
    for i in range(4):
        x = 0.5 + 0.2 * np.cos(np.pi + i * np.pi/4)
        y = 1.5 + 0.2 * np.sin(np.pi + i * np.pi/4)
        ax.plot([0.5, x], [1.5, y], 'k-', linewidth=2)
    ax.text(0.8, 1.5, 'L', ha='center', fontsize=12, weight='bold')
    
    # 绘制二极管D
    ax.plot([2, 2], [0.5, 2], 'k-', linewidth=2)
    ax.plot([1.8, 2.2], [1.5, 1.5], 'k-', linewidth=3)
    ax.text(2.3, 1.5, 'D', ha='center', fontsize=12, weight='bold')
    
    # 绘制输出电容C
    ax.plot([2.5, 2.5], [0.5, 2], 'k-', linewidth=2)
    ax.text(2.8, 1.25, 'C', ha='center', fontsize=12, weight='bold')
    
    # 绘制负载电阻R
    rect = Rectangle((3, 0.7), 1, 1, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(3.5, 1.2, 'R', ha='center', va='center', fontsize=14, weight='bold')
    
    # 连接线
    ax.plot([-2, -1.5], [1, 1], 'k-', linewidth=3)
    ax.plot([-0.5, 0.5], [1, 1], 'k-', linewidth=3)
    ax.plot([1.5, 2], [1, 1], 'k-', linewidth=3)
    ax.plot([2, 2.5], [1, 1], 'k-', linewidth=3)
    ax.plot([3, 4], [1, 1], 'k-', linewidth=3)
    ax.plot([4, 4], [1, 0], 'k-', linewidth=3)
    ax.plot([4, 2], [0, 0], 'k-', linewidth=3)
    ax.plot([2, 2], [0, 0.5], 'k-', linewidth=3)
    ax.plot([2, 0.5], [0, 0], 'k-', linewidth=3)
    ax.plot([0.5, -2], [0, 0], 'k-', linewidth=3)
    
    # 标注
    ax.text(1, 2.5, 'Buck变换器 (降压电路)', ha='center', fontsize=16, weight='bold')
    ax.text(4.5, 1.5, 'Vo', ha='center', fontsize=12, weight='bold')
    ax.text(-2.5, 2.5, 'Vo = Vi × D', ha='center', fontsize=12, weight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax.set_xlim(-3, 5)
    ax.set_ylim(-0.5, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/buck_converter.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_boost_converter():
    """绘制Boost变换器拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 绘制输入电源
    ax.plot([-2, -2], [0, 2], 'k-', linewidth=3)
    ax.text(-2.5, 1, 'Vin', ha='center', fontsize=12, weight='bold')
    
    # 绘制电感L
    ax.plot([-1.5, -1.5], [0.5, 2], 'k-', linewidth=2)
    for i in range(4):
        x = -1.5 + 0.2 * np.cos(np.pi + i * np.pi/4)
        y = 1.5 + 0.2 * np.sin(np.pi + i * np.pi/4)
        ax.plot([-1.5, x], [1.5, y], 'k-', linewidth=2)
    ax.text(-1.2, 1.5, 'L', ha='center', fontsize=12, weight='bold')
    
    # 绘制开关管Q
    rect = FancyBboxPatch((-0.5, 0.5), 1, 1, boxstyle="round,pad=0.1", 
                         facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(0, 1, 'Q', ha='center', va='center', fontsize=14, weight='bold')
    
    # 绘制二极管D
    ax.plot([1.5, 1.5], [0.5, 2], 'k-', linewidth=2)
    ax.plot([1.3, 1.7], [1.5, 1.5], 'k-', linewidth=3)
    ax.text(1.8, 1.5, 'D', ha='center', fontsize=12, weight='bold')
    
    # 绘制输出电容C
    ax.plot([2.5, 2.5], [0.5, 2], 'k-', linewidth=2)
    ax.text(2.8, 1.25, 'C', ha='center', fontsize=12, weight='bold')
    
    # 绘制负载电阻R
    rect = Rectangle((3, 0.7), 1, 1, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(3.5, 1.2, 'R', ha='center', va='center', fontsize=14, weight='bold')
    
    # 连接线
    ax.plot([-2, -1.5], [1, 1], 'k-', linewidth=3)
    ax.plot([-0.5, 0.5], [1, 1], 'k-', linewidth=3)
    ax.plot([1.5, 2], [1, 1], 'k-', linewidth=3)
    ax.plot([3, 4], [1, 1], 'k-', linewidth=3)
    ax.plot([4, 4], [1, 0], 'k-', linewidth=3)
    ax.plot([4, 2.5], [0, 0], 'k-', linewidth=3)
    ax.plot([2.5, 1.5], [0, 0], 'k-', linewidth=3)
    ax.plot([1.5, 0.5], [0, 0], 'k-', linewidth=3)
    ax.plot([0.5, -1.5], [0, 0], 'k-', linewidth=3)
    ax.plot([-1.5, -2], [0, 0], 'k-', linewidth=3)
    
    # 标注
    ax.text(1, 2.5, 'Boost变换器 (升压电路)', ha='center', fontsize=16, weight='bold')
    ax.text(4.5, 1.5, 'Vo', ha='center', fontsize=12, weight='bold')
    ax.text(-2.5, 2.5, 'Vo = Vi / (1-D)', ha='center', fontsize=12, weight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax.set_xlim(-3, 5)
    ax.set_ylim(-0.5, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/boost_converter.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_buck_boost_converter():
    """绘制Buck-Boost变换器拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 绘制输入电源
    ax.plot([-2, -2], [0, 2], 'k-', linewidth=3)
    ax.text(-2.5, 1, 'Vin', ha='center', fontsize=12, weight='bold')
    
    # 绘制电感L
    ax.plot([-1.5, -1.5], [0.5, 2], 'k-', linewidth=2)
    for i in range(4):
        x = -1.5 + 0.2 * np.cos(np.pi + i * np.pi/4)
        y = 1.5 + 0.2 * np.sin(np.pi + i * np.pi/4)
        ax.plot([-1.5, x], [1.5, y], 'k-', linewidth=2)
    ax.text(-1.2, 1.5, 'L', ha='center', fontsize=12, weight='bold')
    
    # 绘制开关管Q
    rect = FancyBboxPatch((-0.5, 0.5), 1, 1, boxstyle="round,pad=0.1", 
                         facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(0, 1, 'Q', ha='center', va='center', fontsize=14, weight='bold')
    
    # 绘制二极管D
    ax.plot([1.5, 1.5], [-1, 0.5], 'k-', linewidth=2)
    ax.plot([1.3, 1.7], [-0.5, -0.5], 'k-', linewidth=3)
    ax.text(1.8, -0.5, 'D', ha='center', fontsize=12, weight='bold')
    
    # 绘制输出电容C
    ax.plot([2.5, 2.5], [-1, 0.5], 'k-', linewidth=2)
    ax.text(2.8, -0.25, 'C', ha='center', fontsize=12, weight='bold')
    
    # 绘制负载电阻R (注意极性反转)
    rect = Rectangle((3, -0.7), 1, 1, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(3.5, -0.2, 'R', ha='center', va='center', fontsize=14, weight='bold')
    
    # 连接线
    ax.plot([-2, -1.5], [1, 1], 'k-', linewidth=3)
    ax.plot([-0.5, 0.5], [1, 1], 'k-', linewidth=3)
    ax.plot([1.5, 2], [-0.5, -0.5], 'k-', linewidth=3)
    ax.plot([3, 4], [-0.2, -0.2], 'k-', linewidth=3)
    ax.plot([4, 4], [-0.2, -1], 'k-', linewidth=3)
    ax.plot([4, 2.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([2.5, 1.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([1.5, 0.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([0.5, -1.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([-1.5, -2], [-1, -1], 'k-', linewidth=3)
    ax.plot([-2, -2], [-1, 0], 'k-', linewidth=3)
    
    # 标注
    ax.text(1, 2.5, 'Buck-Boost变换器 (升降压电路)', ha='center', fontsize=16, weight='bold')
    ax.text(4.5, 0.5, 'Vo', ha='center', fontsize=12, weight='bold')
    ax.text(-2.5, 2.5, 'Vo = -Vi × D/(1-D)', ha='center', fontsize=12, weight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax.set_xlim(-3, 5)
    ax.set_ylim(-2, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/buck_boost_converter.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_flyback_converter():
    """绘制反激变换器拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # 绘制输入电源
    ax.plot([-2, -2], [0, 2], 'k-', linewidth=3)
    ax.text(-2.5, 1, 'Vin', ha='center', fontsize=12, weight='bold')
    
    # 绘制变压器
    # 初级绕组
    rect1 = FancyBboxPatch((-1.5, 0.5), 1, 1, boxstyle="round,pad=0.1", 
                          facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    ax.text(-1, 1, 'N1', ha='center', va='center', fontsize=12, weight='bold')
    
    # 磁芯
    rect_core = FancyBboxPatch((-1.3, 0.7), 0.6, 0.6, 
                              facecolor='gray', edgecolor='black', linewidth=2)
    ax.add_patch(rect_core)
    
    # 次级绕组
    rect2 = FancyBboxPatch((0.5, -1), 1, 1, boxstyle="round,pad=0.1", 
                          facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    ax.text(1, -0.5, 'N2', ha='center', va='center', fontsize=12, weight='bold')
    
    # 绘制开关管Q
    rect = FancyBboxPatch((-1.5, -1), 1, 1, boxstyle="round,pad=0.1", 
                         facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(-1, -0.5, 'Q', ha='center', va='center', fontsize=14, weight='bold')
    
    # 绘制二极管D
    ax.plot([2, 2], [-1, 0.5], 'k-', linewidth=2)
    ax.plot([1.8, 2.2], [-0.5, -0.5], 'k-', linewidth=3)
    ax.text(2.3, -0.5, 'D', ha='center', fontsize=12, weight='bold')
    
    # 绘制输出电容C
    ax.plot([2.5, 2.5], [-1, 0.5], 'k-', linewidth=2)
    ax.text(2.8, -0.25, 'C', ha='center', fontsize=12, weight='bold')
    
    # 绘制负载电阻R
    rect = Rectangle((3, -0.7), 1, 1, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(3.5, -0.2, 'R', ha='center', va='center', fontsize=14, weight='bold')
    
    # 连接线
    ax.plot([-2, -1.5], [1, 1], 'k-', linewidth=3)
    ax.plot([-0.5, -0.5], [1, 0], 'k-', linewidth=3)
    ax.plot([-0.5, 0.5], [0, 0], 'k-', linewidth=3)
    ax.plot([1.5, 2], [-0.5, -0.5], 'k-', linewidth=3)
    ax.plot([3, 4], [-0.2, -0.2], 'k-', linewidth=3)
    ax.plot([4, 4], [-0.2, -1], 'k-', linewidth=3)
    ax.plot([4, 2.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([2.5, 1.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([1.5, 0.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([0.5, -0.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([-0.5, -1.5], [-1, -1], 'k-', linewidth=3)
    ax.plot([-1.5, -2], [-1, -1], 'k-', linewidth=3)
    ax.plot([-2, -2], [-1, 0], 'k-', linewidth=3)
    
    # 标注
    ax.text(1, 2.5, '反激变换器 (隔离型Buck-Boost)', ha='center', fontsize=16, weight='bold')
    ax.text(4.5, 0.5, 'Vo', ha='center', fontsize=12, weight='bold')
    ax.text(-2.5, 2.5, 'Vo = (N2/N1) × Vi × D/(1-D)', ha='center', fontsize=12, weight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax.set_xlim(-3, 5)
    ax.set_ylim(-2, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/flyback_converter.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_single_phase_inverter():
    """绘制单相全桥逆变器拓扑图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 绘制直流电源
    ax.plot([-2, -2], [0, 2], 'k-', linewidth=3)
    ax.text(-2.5, 1, 'Ud', ha='center', fontsize=12, weight='bold')
    
    # 绘制直流侧电容
    ax.plot([-1.5, -1.5], [0.5, 1.5], 'k-', linewidth=2)
    ax.text(-1.2, 1, 'C', ha='center', fontsize=12, weight='bold')
    
    # 绘制全桥结构
    # 上桥臂1 (Q1)
    rect1 = FancyBboxPatch((-0.5, 1.5), 1, 0.8, boxstyle="round,pad=0.1", 
                          facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    ax.text(0, 1.9, 'Q1', ha='center', va='center', fontsize=12, weight='bold')
    
    # 下桥臂1 (Q4)
    rect4 = FancyBboxPatch((-0.5, -0.3), 1, 0.8, boxstyle="round,pad=0.1", 
                          facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect4)
    ax.text(0, 0.1, 'Q4', ha='center', va='center', fontsize=12, weight='bold')
    
    # 上桥臂2 (Q3)
    rect3 = FancyBboxPatch((1.5, 1.5), 1, 0.8, boxstyle="round,pad=0.1", 
                          facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect3)
    ax.text(2, 1.9, 'Q3', ha='center', va='center', fontsize=12, weight='bold')
    
    # 下桥臂2 (Q2)
    rect2 = FancyBboxPatch((1.5, -0.3), 1, 0.8, boxstyle="round,pad=0.1", 
                          facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    ax.text(2, 0.1, 'Q2', ha='center', va='center', fontsize=12, weight='bold')
    
    # 绘制反并联二极管
    # D1
    ax.plot([0.5, 0.5], [1.5, 1.8], 'k-', linewidth=2)
    ax.plot([0.3, 0.7], [1.65, 1.65], 'k-', linewidth=3)
    ax.text(0.8, 1.65, 'D1', ha='center', fontsize=10, weight='bold')
    
    # D4
    ax.plot([0.5, 0.5], [-0.3, -0.6], 'k-', linewidth=2)
    ax.plot([0.3, 0.7], [-0.45, -0.45], 'k-', linewidth=3)
    ax.text(0.8, -0.45, 'D4', ha='center', fontsize=10, weight='bold')
    
    # D3
    ax.plot([2.5, 2.5], [1.5, 1.8], 'k-', linewidth=2)
    ax.plot([2.3, 2.7], [1.65, 1.65], 'k-', linewidth=3)
    ax.text(2.8, 1.65, 'D3', ha='center', fontsize=10, weight='bold')
    
    # D2
    ax.plot([2.5, 2.5], [-0.3, -0.6], 'k-', linewidth=2)
    ax.plot([2.3, 2.7], [-0.45, -0.45], 'k-', linewidth=3)
    ax.text(2.8, -0.45, 'D2', ha='center', fontsize=10, weight='bold')
    
    # 绘制输出负载
    rect = Rectangle((3.5, -0.3), 1, 0.6, facecolor='yellow', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(4, 0, 'R', ha='center', va='center', fontsize=12, weight='bold')
    
    # 连接线
    ax.plot([-2, -1.5], [1, 1], 'k-', linewidth=3)
    ax.plot([-1.5, -0.5], [1, 1.9], 'k-', linewidth=3)
    ax.plot([-1.5, -0.5], [1, 0.1], 'k-', linewidth=3)
    
    # 桥臂连接
    ax.plot([0.5, 0.5], [1.5, 1.5], 'k-', linewidth=2)
    ax.plot([0.5, 0.5], [-0.3, -0.3], 'k-', linewidth=2)
    ax.plot([0.5, 1.5], [0.1, 0.1], 'k-', linewidth=2)
    ax.plot([0.5, 1.5], [1.9, 1.9], 'k-', linewidth=2)
    ax.plot([1.5, 2.5], [0.1, 0.1], 'k-', linewidth=2)
    ax.plot([1.5, 2.5], [1.9, 1.9], 'k-', linewidth=2)
    ax.plot([2.5, 2.5], [1.5, 1.5], 'k-', linewidth=2)
    ax.plot([2.5, 2.5], [-0.3, -0.3], 'k-', linewidth=2)
    
    # 输出连接
    ax.plot([3.5, 3.5], [0.1, 0.1], 'k-', linewidth=2)
    ax.plot([3.5, 3.5], [1.9, 1.9], 'k-', linewidth=2)
    ax.plot([4.5, 4.5], [0.1, 0.1], 'k-', linewidth=2)
    ax.plot([4.5, 4.5], [1.9, 1.9], 'k-', linewidth=2)
    ax.plot([4.5, 4.5], [0.1, 1.9], 'k-', linewidth=2)
    
    # 标注
    ax.text(2, 2.8, '单相全桥逆变器 (SPWM控制)', ha='center', fontsize=16, weight='bold')
    ax.text(5, 1.5, 'Uo', ha='center', fontsize=12, weight='bold')
    
    ax.set_xlim(-3, 6)
    ax.set_ylim(-1, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/single_phase_inverter.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_pwm_waveforms():
    """绘制PWM调制波形"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10))
    
    # 时间轴
    t = np.linspace(0, 4*np.pi, 1000)
    
    # 调制波 (正弦波)
    fs = 50  # 50Hz
    modulation = np.sin(fs * t * 0.01)
    
    # 载波 (三角波)
    fc = 1000  # 1kHz
    carrier = np.abs(np.mod(fc * t * 0.01, 2) - 1) * 2 - 1
    
    # PWM波形
    pwm = np.where(modulation > carrier, 1, 0)
    
    # 绘制调制波
    ax1.plot(t, modulation, 'b-', linewidth=2, label='调制波 (正弦波)')
    ax1.set_ylabel('幅度', fontsize=12)
    ax1.set_title('PWM调制过程波形', fontsize=16, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(-1.5, 1.5)
    
    # 绘制载波
    ax2.plot(t, carrier, 'r-', linewidth=2, label='载波 (三角波)')
    ax2.set_ylabel('幅度', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(-1.5, 1.5)
    
    # 绘制PWM波形
    ax3.plot(t, pwm, 'k-', linewidth=2, label='PWM输出')
    ax3.set_xlabel('时间', fontsize=12)
    ax3.set_ylabel('幅度', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_ylim(-0.2, 1.2)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/pwm_waveforms.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_spwm_output():
    """绘制SPWM输出波形和频谱"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 时间轴
    t = np.linspace(0, 0.1, 2000)
    
    # 基波 (50Hz正弦波)
    fundamental = np.sin(2*np.pi*50*t)
    
    # SPWM调制波 (基波 + 载波边频)
    # 简化模型：基波 + 3次谐波 + 5次谐波
    spwm = (0.8 * fundamental + 
            0.15 * np.sin(2*np.pi*150*t) + 
            0.05 * np.sin(2*np.pi*250*t))
    
    # 方波 (对比)
    square_wave = np.sign(fundamental)
    
    # 绘制时域波形
    ax1.plot(t*1000, fundamental, 'b-', linewidth=2, label='基波 (50Hz)')
    ax1.set_xlabel('时间 (ms)')
    ax1.set_ylabel('幅度')
    ax1.set_title('基波波形', fontsize=14, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(-1.2, 1.2)
    
    ax2.plot(t*1000, spwm, 'r-', linewidth=2, label='SPWM输出')
    ax2.set_xlabel('时间 (ms)')
    ax2.set_ylabel('幅度')
    ax2.set_title('SPWM输出波形', fontsize=14, weight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(-1.2, 1.2)
    
    # 计算频谱
    freq = np.fft.fftfreq(len(t), t[1]-t[0])
    fundamental_fft = np.abs(np.fft.fft(fundamental))
    spwm_fft = np.abs(np.fft.fft(spwm))
    
    # 只显示正频率部分
    positive_freq = freq[:len(freq)//2]
    fundamental_fft_pos = fundamental_fft[:len(freq)//2]
    spwm_fft_pos = spwm_fft[:len(freq)//2]
    
    # 绘制频谱
    ax3.plot(positive_freq, fundamental_fft_pos, 'b-', linewidth=2, label='基波频谱')
    ax3.set_xlabel('频率 (Hz)')
    ax3.set_ylabel('幅度')
    ax3.set_title('基波频谱', fontsize=14, weight='bold')
    ax3.set_xlim(0, 500)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    ax4.plot(positive_freq, spwm_fft_pos, 'r-', linewidth=2, label='SPWM频谱')
    ax4.set_xlabel('频率 (Hz)')
    ax4.set_ylabel('幅度')
    ax4.set_title('SPWM输出频谱', fontsize=14, weight='bold')
    ax4.set_xlim(0, 500)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/spwm_output.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_rectifier_output():
    """绘制整流输出波形"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
    
    # 时间轴
    t = np.linspace(0, 4*np.pi, 1000)
    
    # 输入交流电压
    input_voltage = np.sin(t)
    
    # 单相全波整流输出
    full_wave_rectified = np.abs(input_voltage)
    
    # 带电容滤波的整流输出 (简化模型)
    # 模拟电容充电和放电过程
    filtered_output = np.zeros_like(t)
    capacitor_voltage = 0
    
    for i in range(len(t)):
        if i == 0:
            capacitor_voltage = 0
        else:
            # 充电过程 (当输入电压 > 电容电压时)
            if input_voltage[i] > capacitor_voltage:
                capacitor_voltage = input_voltage[i] * 0.95 + capacitor_voltage * 0.05
            else:
                # 放电过程 (指数衰减)
                capacitor_voltage = capacitor_voltage * 0.995
        
        filtered_output[i] = capacitor_voltage
    
    # 绘制输入电压
    ax1.plot(t/np.pi, input_voltage, 'b-', linewidth=2, label='输入交流电压')
    ax1.set_ylabel('幅度')
    ax1.set_title('整流电路输入输出波形', fontsize=16, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(-1.5, 1.5)
    
    # 绘制全波整流输出
    ax2.plot(t/np.pi, full_wave_rectified, 'r-', linewidth=2, label='全波整流输出')
    ax2.set_ylabel('幅度')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(-0.1, 1.5)
    
    # 绘制滤波后输出
    ax3.plot(t/np.pi, filtered_output, 'g-', linewidth=2, label='滤波后输出 (带电容)')
    ax3.set_xlabel('时间 (π弧度)')
    ax3.set_ylabel('幅度')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_ylim(-0.1, 1.5)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/rectifier_output.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_dc_dc_waveforms():
    """绘制DC-DC变换器工作波形"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 时间轴
    t = np.linspace(0, 4*np.pi, 1000)
    
    # PWM控制信号 (开关管驱动)
    duty_cycle = 0.6  # 60%占空比
    pwm_signal = np.where(np.mod(t, 2*np.pi) < duty_cycle * 2*np.pi, 1, 0)
    
    # Buck变换器波形
    # 输入电压
    vin = np.ones_like(t) * 12  # 12V输入
    
    # Buck输出电压 (Vo = Vi × D)
    vout_buck = vin * duty_cycle
    
    # Buck电感电流 (CCM模式)
    il_buck = 2 + 0.5 * np.sin(20 * t)  # 基础电流 + 纹波
    
    # Boost变换器波形
    # Boost输出电压 (Vo = Vi / (1-D))
    vout_boost = vin / (1 - duty_cycle)
    
    # Boost电感电流
    il_boost = 1.5 + 0.3 * np.sin(15 * t)
    
    # 绘制Buck变换器波形
    ax1.plot(t/np.pi, vin, 'b-', linewidth=2, label='输入电压 (12V)')
    ax1.plot(t/np.pi, vout_buck, 'r-', linewidth=2, label=f'输出电压 ({12*0.6:.1f}V)')
    ax1.set_ylabel('电压 (V)')
    ax1.set_title('Buck变换器电压波形', fontsize=14, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(0, 15)
    
    ax2.plot(t/np.pi, pwm_signal, 'k-', linewidth=2, label='PWM控制信号')
    ax2.plot(t/np.pi, il_buck, 'g-', linewidth=2, label='电感电流')
    ax2.set_ylabel('幅度')
    ax2.set_xlabel('时间 (π弧度)')
    ax2.set_title('Buck变换器电流波形', fontsize=14, weight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 绘制Boost变换器波形
    ax3.plot(t/np.pi, vin, 'b-', linewidth=2, label='输入电压 (12V)')
    ax3.plot(t/np.pi, vout_boost, 'r-', linewidth=2, label=f'输出电压 ({12/(1-0.6):.1f}V)')
    ax3.set_ylabel('电压 (V)')
    ax3.set_title('Boost变换器电压波形', fontsize=14, weight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_ylim(0, 35)
    
    ax4.plot(t/np.pi, pwm_signal, 'k-', linewidth=2, label='PWM控制信号')
    ax4.plot(t/np.pi, il_boost, 'g-', linewidth=2, label='电感电流')
    ax4.set_ylabel('幅度')
    ax4.set_xlabel('时间 (π弧度)')
    ax4.set_title('Boost变换器电流波形', fontsize=14, weight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/dc_dc_waveforms.png', dpi=300, bbox_inches='tight')
    plt.close()

def draw_harmonic_spectrum():
    """绘制谐波频谱分析图"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # 谐波次数
    harmonics = np.arange(1, 21)
    
    # 理想正弦波谐波 (只有基波)
    ideal_spectrum = np.zeros_like(harmonics, dtype=float)
    ideal_spectrum[0] = 1.0  # 基波幅值
    
    # 方波谐波 (奇次谐波)
    square_spectrum = np.zeros_like(harmonics, dtype=float)
    for i, h in enumerate(harmonics):
        if h % 2 == 1:  # 奇次谐波
            square_spectrum[i] = 1.0 / h
    
    # PWM波形谐波 (包含载波边频)
    pwm_spectrum = np.zeros_like(harmonics, dtype=float)
    pwm_spectrum[0] = 0.8  # 基波
    pwm_spectrum[2] = 0.15  # 3次谐波
    pwm_spectrum[4] = 0.05  # 5次谐波
    
    # 绘制频谱
    ax1.bar(harmonics - 0.2, ideal_spectrum, 0.4, label='理想正弦波', alpha=0.7)
    ax1.bar(harmonics + 0.2, square_spectrum, 0.4, label='方波', alpha=0.7)
    ax1.set_xlabel('谐波次数')
    ax1.set_ylabel('相对幅值')
    ax1.set_title('不同波形的谐波频谱对比', fontsize=16, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xticks(harmonics)
    
    # 绘制PWM频谱
    ax2.bar(harmonics - 0.2, ideal_spectrum, 0.4, label='理想正弦波', alpha=0.7)
    ax2.bar(harmonics + 0.2, pwm_spectrum, 0.4, label='PWM波形', alpha=0.7)
    ax2.set_xlabel('谐波次数')
    ax2.set_ylabel('相对幅值')
    ax2.set_title('PWM波形谐波频谱', fontsize=16, weight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xticks(harmonics)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/harmonic_spectrum.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """主函数：生成所有电路图和波形图"""
    # 设置matplotlib
    setup_matplotlib_for_plotting()
    
    print("正在生成电路拓扑图...")
    
    # 生成电路拓扑图
    draw_single_phase_rectifier()
    print("✓ 单相整流电路图已生成")
    
    draw_three_phase_rectifier()
    print("✓ 三相整流电路图已生成")
    
    draw_buck_converter()
    print("✓ Buck变换器电路图已生成")
    
    draw_boost_converter()
    print("✓ Boost变换器电路图已生成")
    
    draw_buck_boost_converter()
    print("✓ Buck-Boost变换器电路图已生成")
    
    draw_flyback_converter()
    print("✓ 反激变换器电路图已生成")
    
    draw_single_phase_inverter()
    print("✓ 单相逆变器电路图已生成")
    
    print("\n正在生成波形分析图...")
    
    # 生成波形分析图
    draw_pwm_waveforms()
    print("✓ PWM调制波形已生成")
    
    draw_spwm_output()
    print("✓ SPWM输出波形和频谱已生成")
    
    draw_rectifier_output()
    print("✓ 整流输出波形已生成")
    
    draw_dc_dc_waveforms()
    print("✓ DC-DC变换器工作波形已生成")
    
    draw_harmonic_spectrum()
    print("✓ 谐波频谱分析图已生成")
    
    print("\n所有图表生成完成！")

if __name__ == "__main__":
    main()