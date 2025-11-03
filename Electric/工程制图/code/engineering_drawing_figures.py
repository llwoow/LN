#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程制图核心概念示意图生成器
创建工程制图课程的关键概念配图
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import warnings

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    warnings.filterwarnings('default')  # Show all warnings

    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")

    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12

def create_three_view_projection():
    """创建三视图形成与投影面展开示意图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('三视图形成与投影面展开', fontsize=16, fontweight='bold')
    
    # 1. 立体图
    ax = fig.add_subplot(2, 3, 1, projection='3d')
    
    # 创建立体物体（长方体）
    u = np.array([[0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
                  [0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
                  [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]])
    
    ax.scatter(u[0], u[1], u[2], c='lightblue', s=100)
    
    # 绘制投影面
    ax.plot([0, 4], [0, 0], [0, 0], 'k-', linewidth=2, label='V面（正面）')
    ax.plot([0, 0], [0, 4], [0, 0], 'k-', linewidth=2, label='H面（水平面）')
    ax.plot([0, 0], [0, 0], [0, 4], 'k-', linewidth=2, label='W面（侧面）')
    
    # 绘制投影线
    ax.plot([2, 2], [2, 2], [0, 0], 'r--', linewidth=1, label='投影线')
    ax.plot([2, 2], [0, 2], [0, 0], 'r--', linewidth=1)
    ax.plot([0, 2], [2, 2], [0, 0], 'r--', linewidth=1)
    
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')
    ax.set_zlabel('Z轴')
    ax.set_title('立体图与投影面')
    ax.legend()
    
    # 2. 主视图
    ax = fig.add_subplot(2, 3, 2)
    ax.add_patch(patches.Rectangle((1, 1), 2, 2, fill=False, edgecolor='black', linewidth=2))
    ax.add_patch(patches.Rectangle((1.5, 1.5), 1, 1, fill=True, facecolor='lightblue', alpha=0.7))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('主视图（Front View）')
    ax.set_xlabel('长度')
    ax.set_ylabel('高度')
    
    # 3. 俯视图
    ax = fig.add_subplot(2, 3, 3)
    ax.add_patch(patches.Rectangle((1, 1), 2, 2, fill=False, edgecolor='black', linewidth=2))
    ax.add_patch(patches.Rectangle((1.5, 1.5), 1, 1, fill=True, facecolor='lightblue', alpha=0.7))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('俯视图（Top View）')
    ax.set_xlabel('长度')
    ax.set_ylabel('宽度')
    
    # 4. 左视图
    ax = fig.add_subplot(2, 3, 4)
    ax.add_patch(patches.Rectangle((1, 1), 2, 2, fill=False, edgecolor='black', linewidth=2))
    ax.add_patch(patches.Rectangle((1.5, 1.5), 1, 1, fill=True, facecolor='lightblue', alpha=0.7))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('左视图（Left View）')
    ax.set_xlabel('宽度')
    ax.set_ylabel('高度')
    
    # 5. 投影关系示意图
    ax = fig.add_subplot(2, 3, 5)
    # 绘制三个视图的投影关系
    ax.plot([1, 3], [3, 3], 'k-', linewidth=2)  # 主视图底边
    ax.plot([1, 3], [1, 1], 'k-', linewidth=2)  # 俯视图顶边
    ax.plot([1, 1], [1, 3], 'k-', linewidth=2)  # 左视图右边
    
    # 标注投影关系
    ax.text(2, 3.3, '长对正', ha='center', fontsize=12, fontweight='bold')
    ax.text(0.7, 2, '高平齐', ha='center', va='center', rotation=90, fontsize=12, fontweight='bold')
    ax.text(2, 0.7, '宽相等', ha='center', fontsize=12, fontweight='bold')
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('三视图投影关系')
    ax.axis('off')
    
    # 6. 投影面展开图
    ax = fig.add_subplot(2, 3, 6)
    # 绘制展开的投影面
    ax.add_patch(patches.Rectangle((1, 3), 2, 2, fill=False, edgecolor='black', linewidth=2, label='V面'))
    ax.add_patch(patches.Rectangle((1, 1), 2, 2, fill=False, edgecolor='black', linewidth=2, label='H面'))
    ax.add_patch(patches.Rectangle((3, 1), 2, 2, fill=False, edgecolor='black', linewidth=2, label='W面'))
    
    # 添加箭头表示展开方向
    ax.annotate('', xy=(2, 0.5), xytext=(2, 1.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax.annotate('', xy=(0.5, 2), xytext=(1.5, 2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal')
    ax.set_title('投影面展开图')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/three_view_projection.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 三视图形成与投影面展开图已创建")

def create_projection_types_comparison():
    """创建投影类型对比图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('工程制图投影类型对比', fontsize=16, fontweight='bold')
    
    # 1. 正投影
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    
    # 创建立体
    u = np.array([[0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
                  [0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
                  [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0]])
    
    ax.scatter(u[0], u[1], u[2], c='blue', s=100)
    ax.set_title('正投影（Orthographic Projection）\n投射线垂直于投影面')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # 2. 斜投影
    ax = fig.add_subplot(2, 2, 2, projection='3d')
    
    # 斜投影变换
    shear_matrix = np.array([[1, 0.5, 0],
                            [0, 1, 0],
                            [0, 0, 1]])
    u_sheared = shear_matrix @ u
    
    ax.scatter(u_sheared[0], u_sheared[1], u_sheared[2], c='green', s=100)
    ax.set_title('斜投影（Oblique Projection）\n投射线与投影面倾斜')
    ax.set_xlabel('X\'')
    ax.set_ylabel('Y\'')
    ax.set_zlabel('Z\'')
    
    # 3. 轴测投影
    ax = fig.add_subplot(2, 2, 3, projection='3d')
    
    # 轴测投影变换（正等轴测）
    isometric_matrix = np.array([[1, 0, 0.5],
                                [0, 1, 0.5],
                                [0, 0, 0]])
    u_isometric = isometric_matrix @ u
    
    ax.scatter(u_isometric[0], u_isometric[1], u_isometric[2], c='red', s=100)
    ax.set_title('轴测投影（Axonometric Projection）\n单面投影显示三坐标面')
    ax.set_xlabel('X\'\' ')
    ax.set_ylabel('Y\'\' ')
    ax.set_zlabel('Z\'\' ')
    
    # 4. 透视投影
    ax = fig.add_subplot(2, 2, 4, projection='3d')
    
    # 透视投影变换（简化版）
    # 使用简单的透视变换
    u_perspective = u.copy()
    # 模拟透视效果
    scale_factor = 1 / (1 + 0.3 * u[2])  # Z越大，缩放越小
    u_perspective[0] = u[0] * scale_factor
    u_perspective[1] = u[1] * scale_factor
    u_perspective[2] = u[2] * scale_factor
    
    ax.scatter(u_perspective[0], u_perspective[1], u_perspective[2], c='orange', s=100)
    ax.set_title('透视投影（Perspective Projection）\n中心投影，近大远小')
    ax.set_xlabel('X\'\'\' ')
    ax.set_ylabel('Y\'\'\' ')
    ax.set_zlabel('Z\'\'\' ')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/projection_types_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 投影类型对比图已创建")

def create_cylinder_cone_intersection():
    """创建圆柱/圆锥截交线投影图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('基本几何体截交线投影', fontsize=16, fontweight='bold')
    
    # 1. 圆柱截交线 - 水平截平面
    ax = fig.add_subplot(2, 3, 1)
    
    # 绘制圆柱的俯视图
    circle = patches.Circle((2, 2), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # 绘制截交线（圆）
    intersection_circle = patches.Circle((2, 2), 0.7, fill=False, edgecolor='red', linewidth=2)
    ax.add_patch(intersection_circle)
    
    # 标注
    ax.text(2, 3.2, '圆柱截交线\n（水平截平面）', ha='center', fontsize=12, fontweight='bold')
    ax.text(2, 0.8, '截交线为圆', ha='center', fontsize=10)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('圆柱俯视图')
    ax.grid(True, alpha=0.3)
    
    # 2. 圆柱截交线 - 倾斜截平面
    ax = fig.add_subplot(2, 3, 2)
    
    # 绘制圆柱的俯视图
    circle = patches.Circle((2, 2), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # 绘制截交线（椭圆）
    ellipse = patches.Ellipse((2, 2), 1.4, 0.7, fill=False, edgecolor='red', linewidth=2)
    ax.add_patch(ellipse)
    
    # 标注
    ax.text(2, 3.2, '圆柱截交线\n（倾斜截平面）', ha='center', fontsize=12, fontweight='bold')
    ax.text(2, 0.8, '截交线为椭圆', ha='center', fontsize=10)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('圆柱俯视图')
    ax.grid(True, alpha=0.3)
    
    # 3. 圆锥截交线 - 水平截平面
    ax = fig.add_subplot(2, 3, 3)
    
    # 绘制圆锥的俯视图
    circle = patches.Circle((2, 2), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # 绘制截交线（圆）
    intersection_circle = patches.Circle((2, 2), 0.5, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(intersection_circle)
    
    # 标注
    ax.text(2, 3.2, '圆锥截交线\n（水平截平面）', ha='center', fontsize=12, fontweight='bold')
    ax.text(2, 0.8, '截交线为圆', ha='center', fontsize=10)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('圆锥俯视图')
    ax.grid(True, alpha=0.3)
    
    # 4. 圆锥截交线 - 通过锥顶
    ax = fig.add_subplot(2, 3, 4)
    
    # 绘制圆锥的俯视图
    circle = patches.Circle((2, 2), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # 绘制截交线（直线）
    ax.plot([1, 3], [2, 2], 'b-', linewidth=3, label='截交线')
    
    # 标注
    ax.text(2, 3.2, '圆锥截交线\n（通过锥顶）', ha='center', fontsize=12, fontweight='bold')
    ax.text(2, 0.8, '截交线为直线', ha='center', fontsize=10)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('圆锥俯视图')
    ax.grid(True, alpha=0.3)
    
    # 5. 球体截交线
    ax = fig.add_subplot(2, 3, 5)
    
    # 绘制球的俯视图
    circle = patches.Circle((2, 2), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # 绘制截交线（圆）
    intersection_circle = patches.Circle((2, 2), 0.8, fill=False, edgecolor='green', linewidth=2)
    ax.add_patch(intersection_circle)
    
    # 标注
    ax.text(2, 3.2, '球体截交线\n（任意截平面）', ha='center', fontsize=12, fontweight='bold')
    ax.text(2, 0.8, '截交线总为圆', ha='center', fontsize=10)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('球体俯视图')
    ax.grid(True, alpha=0.3)
    
    # 6. 截交线类型总结
    ax = fig.add_subplot(2, 3, 6)
    ax.axis('off')
    
    # 创建表格
    table_data = [
        ['几何体', '截平面位置', '截交线形状'],
        ['圆柱', '水平', '圆'],
        ['', '倾斜', '椭圆'],
        ['', '垂直', '矩形'],
        ['圆锥', '水平', '圆'],
        ['', '通过锥顶', '直线'],
        ['', '一般倾斜', '椭圆/抛物线/双曲线'],
        ['球体', '任意', '圆']
    ]
    
    table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # 设置表格样式
    for i in range(len(table_data)):
        for j in range(len(table_data[0])):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
    
    ax.set_title('截交线类型总结', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/cylinder_cone_intersection.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 圆柱/圆锥截交线投影图已创建")

def create_cylinder_intersection():
    """创建两圆柱相贯线图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('两圆柱正交相贯线', fontsize=16, fontweight='bold')
    
    # 1. 主视图 - 相贯线为曲线
    ax = fig.add_subplot(2, 2, 1)
    
    # 绘制大圆柱轮廓
    rect1 = patches.Rectangle((1, 1), 2, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    
    # 绘制小圆柱轮廓
    rect2 = patches.Rectangle((2, 1), 1, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    
    # 绘制相贯线
    x = np.linspace(2, 3, 50)
    y1 = 1 + np.sqrt(0.25 - (x - 2.5)**2) + 0.5  # 上半部分
    y2 = 1 - np.sqrt(0.25 - (x - 2.5)**2) + 0.5  # 下半部分
    
    ax.plot(x, y1, 'r-', linewidth=3, label='相贯线')
    ax.plot(x, y2, 'r-', linewidth=3)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('主视图')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. 俯视图 - 相贯线为圆弧
    ax = fig.add_subplot(2, 2, 2)
    
    # 绘制大圆柱俯视图
    circle1 = patches.Circle((2, 2), 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle1)
    
    # 绘制小圆柱俯视图
    circle2 = patches.Circle((2, 2), 0.5, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle2)
    
    # 绘制相贯线（圆弧）
    theta = np.linspace(-np.pi/3, np.pi/3, 50)
    x_arc = 2 + 0.5 * np.cos(theta)
    y_arc = 2 + 0.5 * np.sin(theta)
    
    ax.plot(x_arc, y_arc, 'r-', linewidth=3, label='相贯线')
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('俯视图')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 左视图 - 相贯线为曲线
    ax = fig.add_subplot(2, 2, 3)
    
    # 绘制大圆柱左视图
    rect1 = patches.Rectangle((1, 1), 2, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    
    # 绘制小圆柱左视图
    rect2 = patches.Rectangle((1, 2), 2, 1, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    
    # 绘制相贯线
    x = np.linspace(1.5, 2.5, 50)  # 限制范围避免虚数
    y1 = 2 + np.sqrt(0.25 - (x - 2)**2) + 0.5  # 上半部分
    y2 = 2 - np.sqrt(0.25 - (x - 2)**2) + 0.5  # 下半部分
    
    ax.plot(x, y1, 'r-', linewidth=3, label='相贯线')
    ax.plot(x, y2, 'r-', linewidth=3)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('左视图')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. 相贯线特性说明
    ax = fig.add_subplot(2, 2, 4)
    ax.axis('off')
    
    # 创建说明文字
    properties = [
        "两圆柱正交相贯线特性：",
        "",
        "1. 相贯线性质：",
        "   • 是两立体表面的共有线",
        "   • 具有封闭性",
        "   • 是空间曲线",
        "",
        "2. 投影特性：",
        "   • 在反映圆柱形状的视图上为圆弧",
        "   • 在其他视图上为曲线",
        "   • 向大圆柱轴线方向凸起",
        "",
        "3. 作图方法：",
        "   • 利用积聚性投影",
        "   • 辅助平面法求共有点",
        "   • 依次连线并判断可见性"
    ]
    
    for i, text in enumerate(properties):
        if i == 0:  # 标题
            ax.text(0.05, 0.95 - i*0.06, text, fontsize=14, fontweight='bold', 
                   transform=ax.transAxes)
        elif text == "":
            continue
        else:
            ax.text(0.05, 0.95 - i*0.06, text, fontsize=11, 
                   transform=ax.transAxes)
    
    ax.set_title('相贯线特性说明', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/cylinder_intersection.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 两圆柱相贯线图已创建")

def create_dimensioning_rules():
    """创建尺寸标注规则示意图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('尺寸标注规则示意', fontsize=16, fontweight='bold')
    
    # 1. 尺寸标注基本要素
    ax = fig.add_subplot(2, 2, 1)
    
    # 绘制零件轮廓
    rect = patches.Rectangle((1, 1), 3, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    # 绘制尺寸线
    ax.plot([1.5, 1.5], [0.5, 1], 'k-', linewidth=1)  # 尺寸界线
    ax.plot([1.5, 1.5], [3, 3.5], 'k-', linewidth=1)  # 尺寸界线
    ax.plot([1.5, 1.5], [1, 3], 'k-', linewidth=1)    # 尺寸线
    ax.arrow(1.5, 1.5, 0, -0.3, head_width=0.1, head_length=0.1, fc='k', ec='k')  # 箭头
    ax.arrow(1.5, 2.5, 0, 0.3, head_width=0.1, head_length=0.1, fc='k', ec='k')  # 箭头
    
    # 添加尺寸数字
    ax.text(1.2, 2, '30', fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 标注要素
    ax.text(0.8, 0.8, '尺寸界线', fontsize=10, ha='center')
    ax.text(0.8, 2.2, '尺寸线', fontsize=10, ha='center')
    ax.text(0.5, 2, '尺寸数字', fontsize=10, ha='center')
    ax.text(0.5, 1.5, '箭头', fontsize=10, ha='center')
    
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('尺寸标注基本要素')
    ax.grid(True, alpha=0.3)
    
    # 2. 尺寸标注规则
    ax = fig.add_subplot(2, 2, 2)
    
    # 绘制零件
    rect = patches.Rectangle((1, 1), 3, 2, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    # 正确标注
    ax.plot([2, 2], [0.5, 1], 'k-', linewidth=1)  # 尺寸界线
    ax.plot([2, 2], [3, 3.5], 'k-', linewidth=1)  # 尺寸界线
    ax.plot([2, 2], [1, 3], 'k-', linewidth=1)    # 尺寸线
    ax.arrow(2, 1.5, 0, -0.3, head_width=0.1, head_length=0.1, fc='k', ec='k')
    ax.arrow(2, 2.5, 0, 0.3, head_width=0.1, head_length=0.1, fc='k', ec='k')
    ax.text(1.7, 2, '✓', fontsize=16, color='green', fontweight='bold', ha='center', va='center')
    
    # 错误标注示例
    ax.plot([3, 3], [0.2, 1], 'r--', linewidth=1)  # 错误的尺寸界线
    ax.plot([3, 3], [3, 3.8], 'r--', linewidth=1)  # 错误的尺寸界线
    ax.plot([3, 3], [1, 3], 'r-', linewidth=1)     # 错误的尺寸线
    ax.text(2.7, 2, '✗', fontsize=16, color='red', fontweight='bold', ha='center', va='center')
    
    ax.text(1.5, 0.2, '正确', fontsize=10, ha='center', color='green', fontweight='bold')
    ax.text(2.5, 0.1, '错误', fontsize=10, ha='center', color='red', fontweight='bold')
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.set_title('尺寸标注正确与错误对比')
    ax.grid(True, alpha=0.3)
    
    # 3. 角度标注
    ax = fig.add_subplot(2, 2, 3)
    
    # 绘制角度
    theta = np.linspace(0, np.pi/3, 100)
    x = 2 + 1 * np.cos(theta)
    y = 2 + 1 * np.sin(theta)
    ax.plot(x, y, 'k-', linewidth=2)
    ax.plot([2, 3], [2, 2], 'k-', linewidth=2)
    
    # 标注角度
    arc = patches.Arc((2, 2), 0.8, 0.8, angle=0, theta1=0, theta2=60, 
                     color='red', linewidth=2)
    ax.add_patch(arc)
    ax.text(2.6, 2.3, '60°', fontsize=12, fontweight='bold', color='red')
    
    ax.set_xlim(1, 4)
    ax.set_ylim(1, 4)
    ax.set_aspect('equal')
    ax.set_title('角度标注')
    ax.grid(True, alpha=0.3)
    
    # 4. 标注规则总结
    ax = fig.add_subplot(2, 2, 4)
    ax.axis('off')
    
    # 创建规则列表
    rules = [
        "尺寸标注基本规则：",
        "",
        "1. 尺寸线与尺寸界线：",
        "   • 均用细实线绘制",
        "   • 尺寸界线垂直于尺寸线",
        "   • 可用轮廓线延长线作尺寸界线",
        "",
        "2. 尺寸线终端：",
        "   • 箭头或斜线",
        "   • 同一图样只能用一种形式",
        "",
        "3. 尺寸数字：",
        "   • 位置应便于读数",
        "   • 不得被图线穿过",
        "   • 避免在30°阴影区内标注",
        "",
        "4. 尺寸数字方向：",
        "   • 水平方向或沿尺寸线方向",
        "   • 角度尺寸数字水平放置"
    ]
    
    for i, text in enumerate(rules):
        if i == 0:  # 标题
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=12, fontweight='bold', 
                   transform=ax.transAxes)
        elif text == "":
            continue
        else:
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=10, 
                   transform=ax.transAxes)
    
    ax.set_title('尺寸标注规则总结', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/dimensioning_rules.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 尺寸标注规则示意图已创建")

def create_right_angle_projection_theorem():
    """创建直角投影定理示意图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('直角投影定理', fontsize=16, fontweight='bold')
    
    # 1. 空间直角与投影
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    
    # 绘制空间直角
    ax.quiver(0, 0, 0, 2, 0, 0, color='red', arrow_length_ratio=0.1, linewidth=2, label='X轴')
    ax.quiver(0, 0, 0, 0, 2, 0, color='green', arrow_length_ratio=0.1, linewidth=2, label='Y轴')
    ax.quiver(0, 0, 0, 0, 0, 2, color='blue', arrow_length_ratio=0.1, linewidth=2, label='Z轴')
    
    # 绘制垂直线段
    ax.plot([1, 1], [0, 1.5], [0, 0], 'k-', linewidth=3, label='AB⊥BC')
    ax.plot([1, 1], [1.5, 1.5], [0, 0], 'k-', linewidth=3)
    
    # 标注
    ax.text(1, 0, 0.2, 'A', fontsize=12, fontweight='bold')
    ax.text(1, 1.5, 0.2, 'B', fontsize=12, fontweight='bold')
    ax.text(1, 1.5, 0.2, 'C', fontsize=12, fontweight='bold', 
           bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('空间垂直两直线')
    ax.legend()
    
    # 2. H面投影
    ax = fig.add_subplot(2, 2, 2)
    
    # 绘制H面投影
    ax.plot([1, 1], [0, 1.5], 'k-', linewidth=3, label='ab')
    ax.plot([1, 1], [1.5, 1.5], 'k-', linewidth=3, label='bc')
    
    # 标注投影
    ax.text(0.8, 0, 'a', fontsize=12, fontweight='bold')
    ax.text(0.8, 1.5, 'b', fontsize=12, fontweight='bold')
    ax.text(1.2, 1.5, 'c', fontsize=12, fontweight='bold')
    
    # 添加直角标记
    ax.plot([0.9, 1.1], [1.4, 1.4], 'k-', linewidth=1)
    ax.plot([0.9, 0.9], [1.4, 1.6], 'k-', linewidth=1)
    ax.plot([1.1, 1.1], [1.4, 1.6], 'k-', linewidth=1)
    
    ax.text(0.7, 1.5, '90°', fontsize=12, fontweight='bold', color='red')
    
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_aspect('equal')
    ax.set_title('H面投影 ab⊥bc')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 直角三角形法求实长
    ax = fig.add_subplot(2, 2, 3)
    
    # 绘制直角三角形
    ax.plot([1, 3], [1, 1], 'b-', linewidth=2, label='水平投影长度')
    ax.plot([3, 3], [1, 2], 'r-', linewidth=2, label='高度差')
    ax.plot([1, 3], [1, 2], 'g-', linewidth=2, label='实长')
    
    # 标注长度
    ax.text(2, 0.8, 'L₁', fontsize=12, fontweight='bold', ha='center')
    ax.text(3.2, 1.5, 'ΔH', fontsize=12, fontweight='bold', va='center')
    ax.text(2, 1.7, 'L', fontsize=12, fontweight='bold', ha='center')
    
    # 添加直角标记
    ax.plot([2.9, 3.1], [1.1, 1.1], 'k-', linewidth=1)
    ax.plot([2.9, 2.9], [1.1, 1.3], 'k-', linewidth=1)
    ax.plot([3.1, 3.1], [1.1, 1.3], 'k-', linewidth=1)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 3)
    ax.set_aspect('equal')
    ax.set_title('直角三角形法求实长')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. 公式与计算
    ax = fig.add_subplot(2, 2, 4)
    ax.axis('off')
    
    # 创建公式说明
    formulas = [
        "直角投影定理与实长计算：",
        "",
        "1. 直角投影定理：",
        "   若两直线在空间垂直，且其中一条",
        "   平行于投影面，则它们在该投影",
        "   面上的投影仍保持垂直。",
        "",
        "2. 实长计算公式：",
        "   L = √(L₁² + ΔH²)",
        "   其中：",
        "   L  - 线段实长",
        "   L₁ - 水平投影长度",
        "   ΔH - 两端点高度差",
        "",
        "3. 倾角计算：",
        "   cosα = L₁/L",
        "   sinα = ΔH/L",
        "   其中α为线段与投影面夹角"
    ]
    
    for i, text in enumerate(formulas):
        if i == 0:  # 标题
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=12, fontweight='bold', 
                   transform=ax.transAxes)
        elif text == "":
            continue
        elif "L = " in text or "cosα = " in text or "sinα = " in text:
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=11, fontweight='bold', 
                   transform=ax.transAxes, color='blue')
        else:
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=10, 
                   transform=ax.transAxes)
    
    ax.set_title('公式与计算', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/right_angle_projection_theorem.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 直角投影定理示意图已创建")

def create_axonometric_projection_coefficients():
    """创建轴测投影轴向伸缩系数图"""
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('轴测投影轴向伸缩系数', fontsize=16, fontweight='bold')
    
    # 1. 正方体轴测投影
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    
    # 正方体顶点
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # 底面
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # 顶面
    ])
    
    # 绘制正方体
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # 底面
        [4, 5], [5, 6], [6, 7], [7, 4],  # 顶面
        [0, 4], [1, 5], [2, 6], [3, 7]   # 侧棱
    ]
    
    for edge in edges:
        points = vertices[edge]
        ax.plot3D(*points.T, 'b-', linewidth=2)
    
    # 标注轴测轴
    ax.text(1.2, 0, 0, 'X₁', fontsize=12, fontweight='bold')
    ax.text(0, 1.2, 0, 'Y₁', fontsize=12, fontweight='bold')
    ax.text(0, 0, 1.2, 'Z₁', fontsize=12, fontweight='bold')
    
    ax.set_xlabel('X₁')
    ax.set_ylabel('Y₁')
    ax.set_zlabel('Z₁')
    ax.set_title('正方体正等轴测投影')
    
    # 2. 轴向伸缩系数推导
    ax = fig.add_subplot(2, 2, 2)
    
    # 绘制几何关系图
    ax.plot([0, 2], [0, 0], 'k-', linewidth=2, label='投影轴')
    ax.plot([0, 0], [0, 2], 'k-', linewidth=2)
    ax.plot([0, 0], [0, 0], [0, 2], 'k-', linewidth=2)
    
    # 绘制空间线段投影
    ax.plot([0, 1.64], [0, 0.82], 'r-', linewidth=3, label='X轴投影')
    ax.plot([0, 0.82], [0, 1.64], 'g-', linewidth=3, label='Y轴投影')
    ax.plot([0, 0.82], [0, 0.82], 'b-', linewidth=3, label='Z轴投影')
    
    # 标注长度
    ax.text(0.8, -0.1, '0.82L', fontsize=10, ha='center', fontweight='bold')
    ax.text(-0.1, 0.8, '0.82L', fontsize=10, ha='center', fontweight='bold', rotation=90)
    ax.text(0.4, 0.4, '0.82L', fontsize=10, ha='center', fontweight='bold')
    
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_aspect('equal')
    ax.set_title('轴向伸缩系数推导')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 系数计算公式
    ax = fig.add_subplot(2, 2, 3)
    ax.axis('off')
    
    # 创建公式说明
    formulas = [
        "轴向伸缩系数推导：",
        "",
        "1. 几何关系：",
        "   设正方体对角线垂直于投影面，",
        "   则各坐标轴与投影面夹角相等",
        "   约为35°16′",
        "",
        "2. 系数计算：",
        "   cosα = √6/3 ≈ 0.82",
        "   其中α为坐标轴与投影面夹角",
        "",
        "3. 简化系数：",
        "   实际绘图常采用简化系数1.0",
        "   图形放大倍数为1/0.82 ≈ 1.22",
        "",
        "4. 正等轴测特点：",
        "   • 三个轴向伸缩系数相等",
        "   • 轴间角均为120°",
        "   • 图形具有立体感"
    ]
    
    for i, text in enumerate(formulas):
        if i == 0:  # 标题
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=12, fontweight='bold', 
                   transform=ax.transAxes)
        elif text == "":
            continue
        elif "cosα = " in text:
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=11, fontweight='bold', 
                   transform=ax.transAxes, color='blue')
        else:
            ax.text(0.05, 0.95 - i*0.05, text, fontsize=10, 
                   transform=ax.transAxes)
    
    ax.set_title('系数推导与特点', fontsize=12, fontweight='bold')
    
    # 4. 斜二测投影对比
    ax = fig.add_subplot(2, 2, 4)
    
    # 绘制斜二测投影
    ax.plot([0, 1], [0, 0], 'k-', linewidth=2, label='X轴')
    ax.plot([0, 0.5], [0, 1], 'k-', linewidth=2, label='Y轴')
    ax.plot([0, 0], [0, 1], 'k-', linewidth=2, label='Z轴')
    
    # 标注系数
    ax.text(0.5, -0.1, '1.0', fontsize=10, ha='center', fontweight='bold')
    ax.text(0.2, 0.5, '0.5', fontsize=10, ha='center', fontweight='bold', rotation=45)
    ax.text(-0.1, 0.5, '1.0', fontsize=10, ha='center', fontweight='bold')
    
    # 添加轴间角标注
    ax.text(0.3, 0.2, '90°', fontsize=10, ha='center', color='red')
    ax.text(0.2, 0.7, '135°', fontsize=10, ha='center', color='red')
    ax.text(-0.2, 0.7, '135°', fontsize=10, ha='center', color='red')
    
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_aspect('equal')
    ax.set_title('斜二测投影系数')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/engineering_drawing_research/figures/axonometric_projection_coefficients.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ 轴测投影轴向伸缩系数图已创建")

def main():
    """主函数：创建所有配图"""
    import os
    
    # 创建图片目录
    os.makedirs('/workspace/docs/engineering_drawing_research/figures', exist_ok=True)
    
    print("开始创建工程制图核心概念配图...")
    
    # 创建所有配图
    create_three_view_projection()
    create_projection_types_comparison()
    create_cylinder_cone_intersection()
    create_cylinder_intersection()
    create_dimensioning_rules()
    create_right_angle_projection_theorem()
    create_axonometric_projection_coefficients()
    
    print("\n✅ 所有配图创建完成！")
    print("图片保存位置：/workspace/docs/engineering_drawing_research/figures/")

if __name__ == "__main__":
    main()
