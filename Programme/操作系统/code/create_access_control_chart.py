#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建访问控制模型对比图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
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

def create_access_control_comparison():
    """创建访问控制模型对比图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    plt.title('访问控制模型对比分析\n(DAC vs MAC vs RBAC vs ABAC)', 
              fontsize=20, fontweight='bold', pad=20)
    
    # 定义颜色
    colors = {
        'DAC': '#FF6B6B',    # 红色
        'MAC': '#4ECDC4',    # 青色
        'RBAC': '#45B7D1',   # 蓝色
        'ABAC': '#96CEB4'    # 绿色
    }
    
    # 定义模型数据
    models = [
        {
            'name': 'DAC\n(自主访问控制)',
            'position': (1, 7),
            'color': colors['DAC'],
            'advantages': [
                '• 灵活性高',
                '• 用户自主管理',
                '• 实现简单',
                '• 常见于文件系统'
            ],
            'disadvantages': [
                '• 权限分散管理',
                '• 难以统一控制',
                '• 易受特洛伊木马攻击',
                '• 权限过大风险'
            ],
            'applications': [
                '• 文件系统',
                '• UNIX/Linux',
                '• Windows NT',
                '• 共享资源管理'
            ]
        },
        {
            'name': 'MAC\n(强制访问控制)',
            'position': (5.5, 7),
            'color': colors['MAC'],
            'advantages': [
                '• 安全性高',
                '• 权限集中管理',
                '• 适合机密机构',
                '• 防止信息泄漏'
            ],
            'disadvantages': [
                '• 管理不够灵活',
                '• 过重强调保密性',
                '• 配置复杂',
                '• 用户体验较差'
            ],
            'applications': [
                '• 机密机构',
                '• 军事系统',
                '• 政府机构',
                '• 高安全等级系统'
            ]
        },
        {
            'name': 'RBAC\n(基于角色访问控制)',
            'position': (1, 3.5),
            'color': colors['RBAC'],
            'advantages': [
                '• 角色权限稳定',
                '• 管理复杂性低',
                '• 灵活权限管理',
                '• 易于理解和维护'
            ],
            'disadvantages': [
                '• 需要预先规划',
                '• 动态适应性差',
                '• 角色爆炸问题',
                '• 细粒度控制有限'
            ],
            'applications': [
                '• 企业管理系统',
                '• 权限管理系统',
                '• 办公自动化',
                '• 数据库权限管理'
            ]
        },
        {
            'name': 'ABAC\n(基于属性访问控制)',
            'position': (5.5, 3.5),
            'color': colors['ABAC'],
            'advantages': [
                '• 细粒度控制',
                '• 灵活性最高',
                '• 动态权限管理',
                '• 支持复杂策略'
            ],
            'disadvantages': [
                '• 关系不直观',
                '• 维护复杂',
                '• 性能开销大',
                '• 管理困难'
            ],
            'applications': [
                '• 细粒度权限控制',
                '• 动态权限管理',
                '• 访问速率控制',
                '• 复杂业务场景'
            ]
        }
    ]
    
    # 绘制每个模型的框
    for model in models:
        x, y = model['position']
        
        # 主框
        main_box = FancyBboxPatch(
            (x-0.4, y-0.8), 0.8, 1.6,
            boxstyle="round,pad=0.1",
            facecolor=model['color'],
            edgecolor='black',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(main_box)
        
        # 模型名称
        ax.text(x, y+0.5, model['name'], 
                fontsize=12, fontweight='bold', 
                ha='center', va='center',
                color='white')
        
        # 优点
        ax.text(x-1.8, y+0.3, '优点:', 
                fontsize=10, fontweight='bold',
                ha='left', va='top')
        for i, adv in enumerate(model['advantages']):
            ax.text(x-1.8, y+0.1-i*0.15, adv, 
                    fontsize=9, ha='left', va='top')
        
        # 缺点
        ax.text(x-1.8, y-1.2, '缺点:', 
                fontsize=10, fontweight='bold',
                ha='left', va='top')
        for i, dis in enumerate(model['disadvantages']):
            ax.text(x-1.8, y-1.4-i*0.15, dis, 
                    fontsize=9, ha='left', va='top')
        
        # 应用场景
        ax.text(x+0.5, y+0.3, '应用场景:', 
                fontsize=10, fontweight='bold',
                ha='left', va='top')
        for i, app in enumerate(model['applications']):
            ax.text(x+0.5, y+0.1-i*0.15, app, 
                    fontsize=9, ha='left', va='top')
    
    # 添加比较表格
    table_data = [
        ['模型', '安全性', '灵活性', '管理复杂度', '适用场景'],
        ['DAC', '低', '高', '低', '文件系统'],
        ['MAC', '高', '低', '高', '机密机构'],
        ['RBAC', '中', '中', '中', '企业系统'],
        ['ABAC', '高', '最高', '最高', '复杂业务']
    ]
    
    # 绘制表格
    table_x, table_y = 1, 1.2
    table_width, table_height = 8, 0.8
    
    # 表格背景
    table_bg = FancyBboxPatch(
        (table_x-0.1, table_y-table_height/2), 
        table_width+0.2, table_height,
        boxstyle="round,pad=0.05",
        facecolor='lightgray',
        edgecolor='black',
        alpha=0.3
    )
    ax.add_patch(table_bg)
    
    # 表格内容
    for i, row in enumerate(table_data):
        for j, cell in enumerate(row):
            x_pos = table_x + j * (table_width / 4)
            y_pos = table_y + (0.3 - i * 0.15)
            
            if i == 0:  # 表头
                ax.text(x_pos, y_pos, cell, 
                        fontsize=10, fontweight='bold',
                        ha='center', va='center',
                        bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor='white', 
                                edgecolor='black'))
            else:
                ax.text(x_pos, y_pos, cell, 
                        fontsize=9,
                        ha='center', va='center')
    
    # 添加图例
    legend_elements = [
        patches.Patch(color=colors['DAC'], label='DAC - 自主访问控制'),
        patches.Patch(color=colors['MAC'], label='MAC - 强制访问控制'),
        patches.Patch(color=colors['RBAC'], label='RBAC - 基于角色访问控制'),
        patches.Patch(color=colors['ABAC'], label='ABAC - 基于属性访问控制')
    ]
    
    ax.legend(handles=legend_elements, 
              loc='upper right', 
              bbox_to_anchor=(0.98, 0.98),
              fontsize=10)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/access_control_models_comparison.png', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("访问控制模型对比图已创建: /workspace/docs/access_control_models_comparison.png")

if __name__ == "__main__":
    create_access_control_comparison()