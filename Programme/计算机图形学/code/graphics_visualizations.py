#!/usr/bin/env python3
"""
计算机图形学算法可视化脚本
用于生成技术文档中的图表和可视化内容
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from typing import List, Tuple, Optional
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
    sns.set_palette("husl")

    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def plot_bezier_curve_de_casteljau():
    """
    绘制Bezier曲线的de Casteljau算法可视化
    """
    setup_matplotlib_for_plotting()
    
    # 控制点
    control_points = np.array([[0, 0], [1, 3], [2, 1], [3, 3]])
    
    # 参数t的取值
    t_values = np.linspace(0, 1, 50)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Bezier曲线的de Casteljau算法可视化', fontsize=16, fontweight='bold')
    
    # 不同的t值展示算法过程
    t_examples = [0.25, 0.5, 0.75]
    
    for idx, t in enumerate(t_examples):
        ax = axes[idx // 2, idx % 2]
        
        # 绘制控制多边形
        ax.plot(control_points[:, 0], control_points[:, 1], 'o-', 
                color='gray', linewidth=2, markersize=8, label='控制多边形')
        
        # de Casteljau算法第一步：线性插值
        Q1_01 = (1-t) * control_points[0] + t * control_points[1]
        Q1_12 = (1-t) * control_points[1] + t * control_points[2]
        Q1_23 = (1-t) * control_points[2] + t * control_points[3]
        
        # 绘制第一步插值点
        ax.plot([Q1_01[0], Q1_12[0], Q1_23[0]], 
                [Q1_01[1], Q1_12[1], Q1_23[1]], 'ro', markersize=6)
        
        # de Casteljau算法第二步
        Q2_012 = (1-t) * Q1_01 + t * Q1_12
        Q2_123 = (1-t) * Q1_12 + t * Q1_23
        
        # 绘制第二步插值点
        ax.plot([Q2_012[0], Q2_123[0]], [Q2_012[1], Q2_123[1]], 'go', markersize=8)
        
        # 最终点
        final_point = (1-t) * Q2_012 + t * Q2_123
        ax.plot(final_point[0], final_point[1], 'bo', markersize=10, 
                label=f'Bezier点 (t={t:.2f})')
        
        # 绘制连线
        ax.plot([Q1_01[0], Q1_12[0], Q1_23[0]], 
                [Q1_01[1], Q1_12[1], Q1_23[1]], 'r--', alpha=0.7)
        ax.plot([Q2_012[0], Q2_123[0]], [Q2_012[1], Q2_123[1]], 'g--', alpha=0.7)
        
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(-0.5, 3.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_title(f'de Casteljau算法 - t = {t}')
    
    # 绘制完整的Bezier曲线
    ax = axes[1, 1]
    ax.plot(control_points[:, 0], control_points[:, 1], 'o-', 
            color='gray', linewidth=2, markersize=8, label='控制多边形')
    
    # 计算完整曲线
    curve_points = []
    for t in t_values:
        # 使用de Casteljau算法
        Q1_01 = (1-t) * control_points[0] + t * control_points[1]
        Q1_12 = (1-t) * control_points[1] + t * control_points[2]
        Q1_23 = (1-t) * control_points[2] + t * control_points[3]
        
        Q2_012 = (1-t) * Q1_01 + t * Q1_12
        Q2_123 = (1-t) * Q1_12 + t * Q1_23
        
        final_point = (1-t) * Q2_012 + t * Q2_123
        curve_points.append(final_point)
    
    curve_points = np.array(curve_points)
    ax.plot(curve_points[:, 0], curve_points[:, 1], 'b-', linewidth=3, 
            label='Bezier曲线')
    
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title('完整Bezier曲线')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/bezier_de_casteljau.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_bspline_basis_functions():
    """
    绘制B样条基函数
    """
    setup_matplotlib_for_plotting()
    
    # 节点矢量
    knots = np.array([0, 0, 0, 0, 1, 2, 3, 4, 5, 5, 5, 5])
    degree = 3
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('B样条基函数可视化', fontsize=16, fontweight='bold')
    
    t_range = np.linspace(0, 5, 1000)
    
    # 计算基函数
    def bspline_basis(i, p, t, knots):
        """递归计算B样条基函数"""
        if p == 0:
            if knots[i] <= t < knots[i + 1]:
                return 1.0
            else:
                return 0.0
        else:
            left = 0.0
            right = 0.0
            
            # 左项
            if knots[i + p] - knots[i] != 0:
                left = (t - knots[i]) / (knots[i + p] - knots[i]) * bspline_basis(i, p - 1, t, knots)
            
            # 右项
            if knots[i + p + 1] - knots[i + 1] != 0:
                right = (knots[i + p + 1] - t) / (knots[i + p + 1] - knots[i + 1]) * bspline_basis(i + 1, p - 1, t, knots)
            
            return left + right
    
    # 绘制不同次数的基函数
    for p, ax in zip([0, 1, 2, 3], axes.flat):
        ax.set_title(f'{p}次B样条基函数')
        
        # 绘制每个基函数
        for i in range(len(knots) - p - 1):
            basis_values = [bspline_basis(i, p, t, knots) for t in t_range]
            ax.plot(t_range, basis_values, label=f'N_{i},{p}(t)', linewidth=2)
        
        # 绘制节点
        unique_knots = np.unique(knots)
        for knot in unique_knots:
            ax.axvline(x=knot, color='gray', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('参数t')
        ax.set_ylabel('基函数值')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xlim(0, 5)
        ax.set_ylim(-0.1, 1.1)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/bspline_basis_functions.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_illumination_models():
    """
    绘制光照模型对比图
    """
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('光照模型对比', fontsize=16, fontweight='bold')
    
    # 角度范围
    angles = np.linspace(0, np.pi/2, 100)
    
    # Phong模型
    n_values = [1, 5, 10, 50]
    ax = axes[0, 0]
    for n in n_values:
        phong_specular = np.cos(angles) ** n
        ax.plot(angles * 180 / np.pi, phong_specular, 
                label=f'Phong (n={n})', linewidth=2)
    ax.set_title('Phong镜面反射模型')
    ax.set_xlabel('观察角度 (度)')
    ax.set_ylabel('反射强度')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Blinn-Phong模型
    ax = axes[0, 1]
    for n in n_values:
        blinn_phong_specular = np.cos(angles) ** n
        ax.plot(angles * 180 / np.pi, blinn_phong_specular, 
                label=f'Blinn-Phong (n={n})', linewidth=2)
    ax.set_title('Blinn-Phong镜面反射模型')
    ax.set_xlabel('观察角度 (度)')
    ax.set_ylabel('反射强度')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Cook-Torrance模型 - GGX分布
    ax = axes[1, 0]
    alpha_values = [0.1, 0.3, 0.5, 0.8]
    for alpha in alpha_values:
        # GGX分布
        cos_theta_m = np.cos(angles)
        D_ggx = alpha**2 / (np.pi * cos_theta_m**4 * (alpha**2 + np.tan(angles)**2)**2)
        # 归一化
        D_ggx = D_ggx / np.max(D_ggx)
        ax.plot(angles * 180 / np.pi, D_ggx, 
                label=f'GGX (α={alpha})', linewidth=2)
    ax.set_title('Cook-Torrance - GGX法线分布')
    ax.set_xlabel('微面元法线角度 (度)')
    ax.set_ylabel('分布密度')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 菲涅尔反射
    ax = axes[1, 1]
    F0_values = [0.04, 0.2, 0.5, 0.8]  # 绝缘体到金属
    for F0 in F0_values:
        cos_theta = np.cos(angles)
        F_schlick = F0 + (1 - F0) * (1 - cos_theta)**5
        ax.plot(angles * 180 / np.pi, F_schlick, 
                label=f'F₀={F0}', linewidth=2)
    ax.set_title('Schlick菲涅尔近似')
    ax.set_xlabel('入射角度 (度)')
    ax.set_ylabel('反射率')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/illumination_models.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_shadow_mapping_algorithm():
    """
    绘制阴影映射算法流程图
    """
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 定义流程步骤
    steps = [
        "1. 光源视角渲染",
        "2. 深度缓冲写入",
        "3. 阴影贴图生成",
        "4. 相机视角渲染", 
        "5. 深度比较测试",
        "6. 阴影因子计算"
    ]
    
    # 绘制流程图
    y_positions = np.linspace(0.9, 0.1, len(steps))
    box_width = 0.3
    box_height = 0.08
    
    for i, (step, y) in enumerate(zip(steps, y_positions)):
        # 绘制矩形框
        rect = patches.Rectangle((0.35, y - box_height/2), box_width, box_height,
                               linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.7)
        ax.add_patch(rect)
        
        # 添加文本
        ax.text(0.5, y, step, ha='center', va='center', fontsize=12, fontweight='bold')
        
        # 绘制箭头
        if i < len(steps) - 1:
            ax.arrow(0.5, y - box_height/2 - 0.02, 0, -0.06, 
                    head_width=0.02, head_length=0.01, fc='black', ec='black')
    
    # 添加阴影贴图可视化
    shadow_map = np.random.rand(20, 20) * 0.5 + 0.3  # 模拟深度值
    im = ax.imshow(shadow_map, extent=[0.05, 0.3, 0.1, 0.9], cmap='gray', alpha=0.8)
    ax.text(0.175, 0.05, '阴影贴图\n(深度纹理)', ha='center', va='center', fontsize=10)
    
    # 添加标题和设置
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('阴影映射算法流程图', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/shadow_mapping_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_subdivision_surface_masks():
    """
    绘制细分曲面掩码
    """
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('细分曲面掩码', fontsize=16, fontweight='bold')
    
    # Catmull-Clark掩码
    ax = axes[0]
    ax.set_title('Catmull-Clark细分掩码')
    
    # 绘制四边形网格示意
    square = patches.Rectangle((0.2, 0.2), 0.6, 0.6, linewidth=2, 
                             edgecolor='blue', facecolor='lightblue', alpha=0.3)
    ax.add_patch(square)
    
    # 中心点
    ax.plot(0.5, 0.5, 'ro', markersize=12, label='面点 (1/4)')
    
    # 边点
    ax.plot([0.3, 0.7, 0.5, 0.5], [0.5, 0.5, 0.3, 0.7], 'go', 
            markersize=10, label='边点 (1/8)')
    
    # 顶点更新权重标注
    ax.text(0.1, 0.9, '顶点更新: 1/2', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    ax.text(0.1, 0.8, '面点: 1/4', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    ax.text(0.1, 0.7, '边点: 1/8', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Loop细分掩码
    ax = axes[1]
    ax.set_title('Loop细分掩码')
    
    # 绘制三角形网格示意
    triangle = patches.Polygon([(0.3, 0.2), (0.7, 0.2), (0.5, 0.7)], 
                             linewidth=2, edgecolor='green', facecolor='lightgreen', alpha=0.3)
    ax.add_patch(triangle)
    
    # 顶点更新权重
    ax.text(0.1, 0.9, '顶点更新:', fontsize=12, fontweight='bold')
    ax.text(0.1, 0.8, '自身: β', fontsize=12)
    ax.text(0.1, 0.7, '邻居: (1-β)/n', fontsize=12)
    ax.text(0.1, 0.6, 'β = 1 - (5/8 + (3/8 + 1/4*cos(2π/n))²)', fontsize=10)
    
    # 边点权重
    ax.text(0.1, 0.4, '边点权重:', fontsize=12, fontweight='bold')
    ax.text(0.1, 0.3, '相邻顶点: 3/8', fontsize=12)
    ax.text(0.1, 0.2, '对边顶点: 1/8', fontsize=12)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/subdivision_masks.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_clipping_algorithms():
    """
    绘制裁剪算法示意图
    """
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('裁剪算法示意图', fontsize=16, fontweight='bold')
    
    # Cohen-Sutherland算法
    ax = axes[0]
    ax.set_title('Cohen-Sutherland线段裁剪')
    
    # 绘制裁剪窗口
    window = patches.Rectangle((0.2, 0.2), 0.6, 0.6, linewidth=2, 
                             edgecolor='black', facecolor='none')
    ax.add_patch(window)
    
    # 绘制9个区域编码
    regions = [
        (0.05, 0.85, '1001'), (0.35, 0.85, '1000'), (0.65, 0.85, '1010'),
        (0.05, 0.55, '0001'), (0.35, 0.55, '0000'), (0.65, 0.55, '0010'),
        (0.05, 0.25, '0101'), (0.35, 0.25, '0100'), (0.65, 0.25, '0110')
    ]
    
    for x, y, code in regions:
        ax.text(x, y, code, ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray", alpha=0.7))
    
    # 绘制示例线段
    # 完全可见
    ax.plot([0.3, 0.7], [0.3, 0.7], 'g-', linewidth=3, label='完全可见')
    # 完全不可见
    ax.plot([0.1, 0.9], [0.1, 0.9], 'r-', linewidth=3, label='完全不可见')
    # 部分可见
    ax.plot([0.1, 0.7], [0.3, 0.9], 'b-', linewidth=3, label='部分可见')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Sutherland-Hodgman算法
    ax = axes[1]
    ax.set_title('Sutherland-Hodgman多边形裁剪')
    
    # 绘制裁剪窗口
    window = patches.Rectangle((0.3, 0.3), 0.4, 0.4, linewidth=2, 
                             edgecolor='black', facecolor='none')
    ax.add_patch(window)
    
    # 原始多边形
    polygon = np.array([[0.1, 0.2], [0.5, 0.1], [0.9, 0.3], [0.8, 0.8], [0.2, 0.7]])
    ax.plot(np.append(polygon[:, 0], polygon[0, 0]), 
            np.append(polygon[:, 1], polygon[0, 1]), 'b-', linewidth=2, label='原始多边形')
    
    # 裁剪后的多边形
    clipped_polygon = np.array([[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6]])
    ax.plot(np.append(clipped_polygon[:, 0], clipped_polygon[0, 0]), 
            np.append(clipped_polygon[:, 1], clipped_polygon[0, 1]), 'r-', linewidth=3, label='裁剪后多边形')
    
    # 交点
    ax.plot([0.4, 0.6, 0.6, 0.4], [0.4, 0.4, 0.6, 0.6], 'ro', markersize=8, label='交点')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/clipping_algorithms.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_texture_mapping():
    """
    绘制纹理映射示意图
    """
    setup_matplotlib_for_plotting()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('纹理映射技术', fontsize=16, fontweight='bold')
    
    # 法线贴图
    ax = axes[0, 0]
    ax.set_title('法线贴图')
    
    # 创建简单的法线贴图示例
    x = np.linspace(0, 1, 50)
    y = np.linspace(0, 1, 50)
    X, Y = np.meshgrid(x, y)
    
    # 模拟法线贴图的法线扰动
    normal_x = np.sin(10 * np.pi * X) * np.cos(10 * np.pi * Y)
    normal_y = np.cos(10 * np.pi * X) * np.sin(10 * np.pi * Y)
    normal_z = np.sqrt(1 - normal_x**2 - normal_y**2)
    
    # 归一化
    magnitude = np.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
    normal_x /= magnitude
    normal_y /= magnitude
    normal_z /= magnitude
    
    # 显示法线贴图
    normal_map = np.zeros((50, 50, 3))
    normal_map[:, :, 0] = (normal_x + 1) / 2  # R通道
    normal_map[:, :, 1] = (normal_y + 1) / 2  # G通道
    normal_map[:, :, 2] = (normal_z + 1) / 2  # B通道
    
    ax.imshow(normal_map)
    ax.text(0.5, -0.1, '切线空间法线贴图', ha='center', transform=ax.transAxes, fontsize=10)
    
    # 位移贴图
    ax = axes[0, 1]
    ax.set_title('位移贴图')
    
    # 创建位移贴图示例
    height_map = np.sin(5 * np.pi * X) * np.cos(5 * np.pi * Y)
    im = ax.imshow(height_map, cmap='terrain')
    plt.colorbar(im, ax=ax)
    ax.text(0.5, -0.1, '高度场位移贴图', ha='center', transform=ax.transAxes, fontsize=10)
    
    # 环境贴图 - 立方体映射
    ax = axes[1, 0]
    ax.set_title('立方体环境贴图')
    
    # 创建一个简单的环境贴图示例
    cube_faces = []
    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
    
    for i, color in enumerate(colors):
        face = np.ones((20, 20, 3))
        if color == 'red':
            face[:, :, 0] = 0.8
        elif color == 'green':
            face[:, :, 1] = 0.8
        elif color == 'blue':
            face[:, :, 2] = 0.8
        elif color == 'yellow':
            face[:, :, :2] = 0.8
        elif color == 'purple':
            face[:, :, [0, 2]] = 0.8
        else:  # orange
            face[:, :, 0] = 0.8
            face[:, :, 1] = 0.5
        
        cube_faces.append(face)
    
    # 排列立方体贴图
    positions = [(0, 1), (1, 1), (2, 1), (0, 0), (1, 0), (2, 0)]
    face_names = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
    
    for i, (face, (x, y), name) in enumerate(zip(cube_faces, positions, face_names)):
        ax.imshow(face, extent=[x*0.3, (x+1)*0.3, y*0.3, (y+1)*0.3])
        ax.text(x*0.3 + 0.15, y*0.3 + 0.15, name, ha='center', va='center', 
                fontsize=8, fontweight='bold', color='white',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.7))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    
    # IBL效果
    ax = axes[1, 1]
    ax.set_title('基于图像的光照(IBL)')
    
    # 模拟IBL光照效果
    theta = np.linspace(0, 2*np.pi, 100)
    phi = np.linspace(0, np.pi, 50)
    THETA, PHI = np.meshgrid(theta, phi)
    
    # 环境光照强度分布
    env_light = np.sin(PHI) * (1 + 0.5 * np.cos(3 * THETA))
    
    # 转换为笛卡尔坐标
    X_env = env_light * np.sin(PHI) * np.cos(THETA)
    Y_env = env_light * np.sin(PHI) * np.sin(THETA)
    Z_env = env_light * np.cos(PHI)
    
    # 绘制球面环境光照
    ax = fig.add_subplot(2, 2, 4, projection='3d')
    surf = ax.plot_surface(X_env, Y_env, Z_env, cmap='viridis', alpha=0.8)
    ax.set_title('环境光照球面表示')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/texture_mapping.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_brdf_visualization():
    """
    绘制BRDF可视化
    """
    setup_matplotlib_for_plotting()
    
    fig = plt.figure(figsize=(16, 12))
    
    # 3D BRDF可视化
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.set_title('Lambert BRDF (漫反射)')
    
    # 球坐标网格
    theta = np.linspace(0, np.pi/2, 30)  # 极角
    phi = np.linspace(0, 2*np.pi, 60)    # 方位角
    THETA, PHI = np.meshgrid(theta, phi)
    
    # Lambert BRDF (常数)
    R_lambert = np.ones_like(THETA)
    
    # 转换为笛卡尔坐标
    X = R_lambert * np.sin(THETA) * np.cos(PHI)
    Y = R_lambert * np.sin(THETA) * np.sin(PHI)
    Z = R_lambert * np.cos(THETA)
    
    surf1 = ax1.plot_surface(X, Y, Z, cmap='Blues', alpha=0.8)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    
    # Phong BRDF
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    ax2.set_title('Phong BRDF (镜面反射)')
    
    n = 10  # 镜面指数
    R_phong = np.cos(THETA) ** n
    
    X2 = R_phong * np.sin(THETA) * np.cos(PHI)
    Y2 = R_phong * np.sin(THETA) * np.sin(PHI)
    Z2 = R_phong * np.cos(THETA)
    
    surf2 = ax2.plot_surface(X2, Y2, Z2, cmap='Reds', alpha=0.8)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    
    # Cook-Torrance BRDF
    ax3 = fig.add_subplot(2, 2, 3, projection='3d')
    ax3.set_title('Cook-Torrance BRDF (微表面)')
    
    alpha = 0.3  # 粗糙度
    cos_theta_m = np.cos(THETA)
    D_ggx = alpha**2 / (np.pi * cos_theta_m**4 * (alpha**2 + np.tan(THETA)**2)**2)
    D_ggx = D_ggx / np.max(D_ggx)  # 归一化
    
    X3 = D_ggx * np.sin(THETA) * np.cos(PHI)
    Y3 = D_ggx * np.sin(THETA) * np.sin(PHI)
    Z3 = D_ggx * np.cos(THETA)
    
    surf3 = ax3.plot_surface(X3, Y3, Z3, cmap='Greens', alpha=0.8)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_zlabel('Z')
    
    # BRDF参数对比
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_title('BRDF模型参数对比')
    
    # 不同粗糙度的Cook-Torrance
    alpha_values = [0.1, 0.3, 0.5, 0.8]
    angles = np.linspace(0, np.pi/2, 100)
    
    for alpha in alpha_values:
        cos_theta_m = np.cos(angles)
        D_ggx = alpha**2 / (np.pi * cos_theta_m**4 * (alpha**2 + np.tan(angles)**2)**2)
        D_ggx = D_ggx / np.max(D_ggx)
        ax4.plot(angles * 180 / np.pi, D_ggx, label=f'α={alpha}', linewidth=2)
    
    ax4.set_xlabel('角度 (度)')
    ax4.set_ylabel('归一化反射率')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/imgs/brdf_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """
    主函数：生成所有可视化图表
    """
    print("开始生成计算机图形学算法可视化图表...")
    
    # 确保输出目录存在
    import os
    os.makedirs('/workspace/imgs', exist_ok=True)
    
    # 生成所有图表
    plot_bezier_curve_de_casteljau()
    print("✓ Bezier曲线de Casteljau算法可视化完成")
    
    plot_bspline_basis_functions()
    print("✓ B样条基函数可视化完成")
    
    plot_illumination_models()
    print("✓ 光照模型对比图完成")
    
    plot_shadow_mapping_algorithm()
    print("✓ 阴影映射算法流程图完成")
    
    plot_subdivision_surface_masks()
    print("✓ 细分曲面掩码图完成")
    
    plot_clipping_algorithms()
    print("✓ 裁剪算法示意图完成")
    
    plot_texture_mapping()
    print("✓ 纹理映射技术图完成")
    
    plot_brdf_visualization()
    print("✓ BRDF可视化图完成")
    
    print("\n所有可视化图表生成完成！")
    print("图表保存在 /workspace/imgs/ 目录下")

if __name__ == "__main__":
    main()
