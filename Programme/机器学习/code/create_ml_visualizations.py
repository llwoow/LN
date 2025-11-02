#!/usr/bin/env python3
"""
机器学习基础概念可视化图表生成器
生成用于机器学习基础概念报告的图表
"""

import warnings
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

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
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12

def create_bias_variance_tradeoff():
    """创建偏差-方差权衡曲线图"""
    setup_matplotlib_for_plotting()
    
    # 生成模型复杂度数据
    model_complexity = np.linspace(0.1, 10, 100)
    
    # 模拟偏差和方差曲线
    bias = 5 * np.exp(-0.5 * model_complexity) + 0.5
    variance = 0.2 * model_complexity**2
    irreducible_error = np.ones_like(model_complexity) * 1.0
    total_error = bias**2 + variance + irreducible_error
    
    # 找到最小总误差点
    min_idx = np.argmin(total_error)
    optimal_complexity = model_complexity[min_idx]
    
    plt.figure(figsize=(12, 8))
    
    # 绘制各部分
    plt.plot(model_complexity, bias**2, 'b-', linewidth=3, label='偏差² (Bias²)', alpha=0.8)
    plt.plot(model_complexity, variance, 'r-', linewidth=3, label='方差 (Variance)', alpha=0.8)
    plt.plot(model_complexity, irreducible_error, 'g--', linewidth=2, label='不可约误差 (Irreducible Error)', alpha=0.7)
    plt.plot(model_complexity, total_error, 'k-', linewidth=4, label='总误差 (Total Error)', alpha=0.9)
    
    # 标记最佳点
    plt.axvline(x=optimal_complexity, color='orange', linestyle=':', linewidth=3, alpha=0.8)
    plt.plot(optimal_complexity, total_error[min_idx], 'o', color='orange', markersize=15, 
             label=f'最佳权衡点 (复杂度={optimal_complexity:.1f})')
    
    # 标记欠拟合和过拟合区域
    plt.axvspan(0.1, optimal_complexity-1, alpha=0.2, color='blue', label='欠拟合区域')
    plt.axvspan(optimal_complexity+1, 10, alpha=0.2, color='red', label='过拟合区域')
    
    plt.xlabel('模型复杂度 (Model Complexity)', fontsize=14)
    plt.ylabel('误差 (Error)', fontsize=14)
    plt.title('偏差-方差权衡 (Bias-Variance Tradeoff)', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12, loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig('/workspace/docs/bias_variance_tradeoff.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 偏差-方差权衡曲线图已生成: docs/bias_variance_tradeoff.png")

def create_gradient_descent_visualization():
    """创建梯度下降过程示意图"""
    setup_matplotlib_for_plotting()
    
    # 创建损失函数 (二次函数)
    x = np.linspace(-4, 4, 1000)
    y = (x - 1)**2 + 0.5
    
    # 模拟梯度下降过程
    x_history = [-3, -2.2, -1.5, -0.9, -0.4, 0.1, 0.5, 0.8, 0.95, 0.99]
    y_history = [(xi - 1)**2 + 0.5 for xi in x_history]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左图：梯度下降路径
    ax1.plot(x, y, 'b-', linewidth=3, label='损失函数 J(θ)', alpha=0.8)
    ax1.plot(x_history, y_history, 'ro-', linewidth=2, markersize=8, 
             label='梯度下降路径', alpha=0.9)
    
    # 标记起始点和最优点
    ax1.plot(x_history[0], y_history[0], 'go', markersize=15, label='起始点')
    ax1.plot(1, 0.5, 'ro', markersize=15, label='最优点 θ*')
    
    # 添加箭头表示梯度方向
    for i in range(len(x_history)-1):
        dx = x_history[i+1] - x_history[i]
        dy = y_history[i+1] - y_history[i]
        ax1.arrow(x_history[i], y_history[i], dx*0.8, dy*0.8, 
                 head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.7)
    
    ax1.set_xlabel('参数 θ', fontsize=14)
    ax1.set_ylabel('损失 J(θ)', fontsize=14)
    ax1.set_title('梯度下降过程 (Gradient Descent)', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 右图：学习率影响
    learning_rates = [0.01, 0.1, 0.5, 1.2]
    colors = ['blue', 'green', 'orange', 'red']
    
    for lr, color in zip(learning_rates, colors):
        x_lr = [-3]
        for _ in range(10):
            grad = 2 * (x_lr[-1] - 1)  # 梯度
            x_lr.append(x_lr[-1] - lr * grad)
        
        y_lr = [(xi - 1)**2 + 0.5 for xi in x_lr]
        ax2.plot(range(len(x_lr)), y_lr, 'o-', color=color, linewidth=2, 
                label=f'学习率 η = {lr}', alpha=0.8)
    
    ax2.set_xlabel('迭代次数 (Iterations)', fontsize=14)
    ax2.set_ylabel('损失 J(θ)', fontsize=14)
    ax2.set_title('学习率对收敛的影响', fontsize=16, fontweight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/gradient_descent_process.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 梯度下降过程图已生成: docs/gradient_descent_process.png")

def create_pca_visualization():
    """创建PCA降维示意图"""
    setup_matplotlib_for_plotting()
    
    # 生成二维数据点
    np.random.seed(42)
    n_points = 200
    
    # 创建椭圆分布的数据
    theta = np.random.uniform(0, 2*np.pi, n_points)
    r1 = np.random.normal(3, 1, n_points)
    r2 = np.random.normal(1, 0.3, n_points)
    
    x = r1 * np.cos(theta) + np.random.normal(0, 0.2, n_points)
    y = r1 * np.sin(theta) + np.random.normal(0, 0.2, n_points)
    
    # 旋转数据
    angle = np.pi/6  # 30度旋转
    x_rot = x * np.cos(angle) - y * np.sin(angle)
    y_rot = x * np.sin(angle) + y * np.cos(angle)
    
    # 计算PCA
    data = np.column_stack([x_rot, y_rot])
    mean = np.mean(data, axis=0)
    data_centered = data - mean
    
    # 计算协方差矩阵
    cov_matrix = np.cov(data_centered.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # 排序特征值和特征向量
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左图：原始数据和主成分方向
    ax1.scatter(data[:, 0], data[:, 1], alpha=0.6, s=30, color='blue', label='原始数据点')
    
    # 绘制主成分方向
    scale1 = 3 * np.sqrt(eigenvalues[0])
    scale2 = 3 * np.sqrt(eigenvalues[1])
    
    ax1.arrow(mean[0], mean[1], eigenvectors[0, 0] * scale1, eigenvectors[1, 0] * scale1,
             head_width=0.3, head_length=0.3, fc='red', ec='red', linewidth=3, 
             label=f'PC1 (λ₁={eigenvalues[0]:.2f})')
    ax1.arrow(mean[0], mean[1], eigenvectors[0, 1] * scale2, eigenvectors[1, 1] * scale2,
             head_width=0.3, head_length=0.3, fc='green', ec='green', linewidth=3,
             label=f'PC2 (λ₂={eigenvalues[1]:.2f})')
    
    ax1.set_xlabel('特征 x₁', fontsize=14)
    ax1.set_ylabel('特征 x₂', fontsize=14)
    ax1.set_title('PCA: 主成分分析', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # 右图：降维结果
    # 投影到第一主成分
    pca_1d = data_centered @ eigenvectors[:, 0]
    
    # 重建数据
    reconstructed = np.outer(pca_1d, eigenvectors[:, 0]) + mean
    
    ax2.scatter(data[:, 0], data[:, 1], alpha=0.3, s=20, color='blue', label='原始数据')
    ax2.scatter(reconstructed[:, 0], reconstructed[:, 1], alpha=0.6, s=30, color='red', 
               label='PC1重建数据')
    
    # 绘制从原始点到重建点的连线
    for i in range(0, len(data), 10):  # 每10个点画一条线
        ax2.plot([data[i, 0], reconstructed[i, 0]], [data[i, 1], reconstructed[i, 1]], 
                'k-', alpha=0.3, linewidth=1)
    
    ax2.set_xlabel('特征 x₁', fontsize=14)
    ax2.set_ylabel('特征 x₂', fontsize=14)
    ax2.set_title('PCA降维: 投影到第一主成分', fontsize=16, fontweight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/pca_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ PCA降维示意图已生成: docs/pca_visualization.png")

def create_learning_curves():
    """创建学习曲线图"""
    setup_matplotlib_for_plotting()
    
    # 生成样本大小数据
    training_sizes = np.array([50, 100, 200, 400, 800, 1600, 3200, 6400])
    
    # 模拟不同模型的学习曲线
    # 简单模型（欠拟合）
    train_error_simple = 0.8 - 0.4 * np.log(training_sizes/50) / np.log(128)
    val_error_simple = 0.9 - 0.3 * np.log(training_sizes/50) / np.log(128)
    
    # 复杂模型（过拟合）
    train_error_complex = 0.1 + 0.05 * np.exp(-training_sizes/500)
    val_error_complex = 0.3 + 0.4 * np.exp(-training_sizes/1000) + 0.1
    
    # 适中模型（良好拟合）
    train_error_good = 0.2 + 0.1 * np.exp(-training_sizes/300)
    val_error_good = 0.25 + 0.15 * np.exp(-training_sizes/400)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 欠拟合模型
    axes[0, 0].plot(training_sizes, train_error_simple, 'b-', linewidth=3, label='训练误差')
    axes[0, 0].plot(training_sizes, val_error_simple, 'r-', linewidth=3, label='验证误差')
    axes[0, 0].set_title('欠拟合模型 (High Bias)', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('训练样本数', fontsize=12)
    axes[0, 0].set_ylabel('误差', fontsize=12)
    axes[0, 0].legend(fontsize=12)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 过拟合模型
    axes[0, 1].plot(training_sizes, train_error_complex, 'b-', linewidth=3, label='训练误差')
    axes[0, 1].plot(training_sizes, val_error_complex, 'r-', linewidth=3, label='验证误差')
    axes[0, 1].set_title('过拟合模型 (High Variance)', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('训练样本数', fontsize=12)
    axes[0, 1].set_ylabel('误差', fontsize=12)
    axes[0, 1].legend(fontsize=12)
    axes[0, 1].grid(True, alpha=0.3)
    
    # 良好拟合模型
    axes[1, 0].plot(training_sizes, train_error_good, 'b-', linewidth=3, label='训练误差')
    axes[1, 0].plot(training_sizes, val_error_good, 'r-', linewidth=3, label='验证误差')
    axes[1, 0].set_title('良好拟合模型 (Good Fit)', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('训练样本数', fontsize=12)
    axes[1, 0].set_ylabel('误差', fontsize=12)
    axes[1, 0].legend(fontsize=12)
    axes[1, 0].grid(True, alpha=0.3)
    
    # 综合比较
    axes[1, 1].plot(training_sizes, val_error_simple, 'b--', linewidth=2, label='欠拟合验证误差')
    axes[1, 1].plot(training_sizes, val_error_complex, 'r--', linewidth=2, label='过拟合验证误差')
    axes[1, 1].plot(training_sizes, val_error_good, 'g-', linewidth=3, label='良好拟合验证误差')
    axes[1, 1].set_title('模型性能比较', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('训练样本数', fontsize=12)
    axes[1, 1].set_ylabel('验证误差', fontsize=12)
    axes[1, 1].legend(fontsize=12)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/learning_curves.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 学习曲线图已生成: docs/learning_curves.png")

def create_bayesian_theorem_visualization():
    """创建贝叶斯定理可视化"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 条件概率可视化
    x = np.linspace(0, 1, 1000)
    prior = np.ones_like(x)  # 均匀先验
    likelihood = 0.8 * x + 0.1  # 似然函数
    posterior = prior * likelihood
    posterior = posterior / np.trapz(posterior, x)  # 归一化
    
    ax1.plot(x, prior, 'b-', linewidth=3, label='先验 P(θ)', alpha=0.8)
    ax1.plot(x, likelihood, 'r-', linewidth=3, label='似然 P(X|θ)', alpha=0.8)
    ax1.plot(x, posterior, 'g-', linewidth=3, label='后验 P(θ|X)', alpha=0.8)
    ax1.set_xlabel('参数 θ', fontsize=12)
    ax1.set_ylabel('概率密度', fontsize=12)
    ax1.set_title('贝叶斯定理: 先验、似然、后验', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # 2. 垃圾邮件分类示例
    categories = ['垃圾邮件', '正常邮件']
    prior_probs = [0.3, 0.7]
    likelihood_spam = [0.9, 0.1]  # 包含"免费"词汇的概率
    likelihood_normal = [0.1, 0.9]
    
    x_pos = np.arange(len(categories))
    width = 0.35
    
    ax2.bar(x_pos - width/2, prior_probs, width, label='先验概率', alpha=0.8, color='skyblue')
    ax2.bar(x_pos + width/2, [likelihood_spam[0], likelihood_normal[0]], width, 
           label='P(包含"免费"|类别)', alpha=0.8, color='orange')
    
    ax2.set_xlabel('邮件类别', fontsize=12)
    ax2.set_ylabel('概率', fontsize=12)
    ax2.set_title('垃圾邮件分类示例', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(categories)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # 3. 后验更新过程
    iterations = np.arange(0, 11)
    posterior_means = []
    posterior_stds = []
    
    # 模拟贝叶斯更新过程
    for i in iterations:
        # 模拟每次观测后的后验分布
        mean = 0.5 + 0.3 * np.sin(i * 0.5) * np.exp(-i * 0.1)
        std = 0.3 * np.exp(-i * 0.15) + 0.1
        posterior_means.append(mean)
        posterior_stds.append(std)
    
    ax3.errorbar(iterations, posterior_means, yerr=posterior_stds, 
                fmt='o-', linewidth=2, markersize=8, capsize=5, capthick=2)
    ax3.set_xlabel('观测次数', fontsize=12)
    ax3.set_ylabel('后验均值', fontsize=12)
    ax3.set_title('贝叶斯后验更新过程', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. 贝叶斯 vs 频率派比较
    methods = ['频率派估计', '贝叶斯估计']
    estimates = [0.65, 0.67]
    uncertainties = [0.08, 0.05]
    
    bars = ax4.bar(methods, estimates, yerr=uncertainties, capsize=10, 
                  color=['lightcoral', 'lightblue'], alpha=0.8)
    ax4.set_ylabel('参数估计值', fontsize=12)
    ax4.set_title('频率派 vs 贝叶斯估计', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar, est, unc in zip(bars, estimates, uncertainties):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + unc + 0.01,
                f'{est:.2f}±{unc:.2f}', ha='center', va='bottom', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/bayesian_theorem.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 贝叶斯定理可视化图已生成: docs/bayesian_theorem.png")

def create_eigenvalue_eigenvector_visualization():
    """创建特征值和特征向量的几何直观图"""
    setup_matplotlib_for_plotting()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 特征向量的几何直观
    # 定义矩阵A
    A = np.array([[2, 1], [1, 2]])
    eigenvalues, eigenvectors = np.linalg.eig(A)
    
    # 生成单位圆上的点
    theta = np.linspace(0, 2*np.pi, 100)
    unit_circle = np.array([np.cos(theta), np.sin(theta)])
    
    # 应用线性变换
    transformed = A @ unit_circle
    
    ax1.plot(unit_circle[0, :], unit_circle[1, :], 'b-', linewidth=2, label='单位圆')
    ax1.plot(transformed[0, :], transformed[1, :], 'r-', linewidth=2, label='变换后的椭圆')
    
    # 绘制特征向量
    scale = 2
    for i in range(2):
        ax1.arrow(0, 0, eigenvectors[0, i]*scale, eigenvectors[1, i]*scale,
                 head_width=0.1, head_length=0.1, fc=f'C{i+2}', ec=f'C{i+2}', 
                 linewidth=3, label=f'特征向量 v{i+1} (λ={eigenvalues[i]:.1f})')
    
    ax1.set_xlim(-3, 3)
    ax1.set_ylim(-3, 3)
    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('y', fontsize=12)
    ax1.set_title('特征向量: 线性变换中的不变方向', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # 2. 不同特征值的影响
    matrices = [
        (np.array([[3, 0], [0, 1]]), 'λ₁=3, λ₂=1'),
        (np.array([[2, 0], [0, 0.5]]), 'λ₁=2, λ₂=0.5'),
        (np.array([[0.5, 0], [0, 3]]), 'λ₁=0.5, λ₂=3')
    ]
    
    colors = ['red', 'green', 'blue']
    
    for i, (mat, label) in enumerate(matrices):
        transformed = mat @ unit_circle
        ax2.plot(transformed[0, :], transformed[1, :], color=colors[i], 
                linewidth=2, label=label, alpha=0.8)
    
    ax2.plot(unit_circle[0, :], unit_circle[1, :], 'k--', linewidth=1, label='单位圆')
    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-3, 3)
    ax2.set_xlabel('x', fontsize=12)
    ax2.set_ylabel('y', fontsize=12)
    ax2.set_title('不同特征值对变换的影响', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    # 3. PCA中的特征值和方差
    # 生成相关数据
    np.random.seed(42)
    n_samples = 200
    
    # 创建具有不同方差的数据
    x = np.random.normal(0, 2, n_samples)
    y = 0.5 * x + np.random.normal(0, 0.8, n_samples)
    data = np.column_stack([x, y])
    
    # 计算PCA
    mean = np.mean(data, axis=0)
    data_centered = data - mean
    cov_matrix = np.cov(data_centered.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    ax3.scatter(data[:, 0], data[:, 1], alpha=0.6, s=30, color='blue', label='数据点')
    
    # 绘制主成分方向
    scale1 = 3 * np.sqrt(eigenvalues[0])
    scale2 = 3 * np.sqrt(eigenvalues[1])
    
    ax3.arrow(mean[0], mean[1], eigenvectors[0, 0] * scale1, eigenvectors[1, 0] * scale1,
             head_width=0.3, head_length=0.3, fc='red', ec='red', linewidth=3, 
             label=f'PC1 (方差={eigenvalues[0]:.2f})')
    ax3.arrow(mean[0], mean[1], eigenvectors[0, 1] * scale2, eigenvectors[1, 1] * scale2,
             head_width=0.3, head_length=0.3, fc='green', ec='green', linewidth=3,
             label=f'PC2 (方差={eigenvalues[1]:.2f})')
    
    ax3.set_xlabel('特征 x', fontsize=12)
    ax3.set_ylabel('特征 y', fontsize=12)
    ax3.set_title('PCA: 特征值表示方差', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')
    
    # 4. 特征值分解的数学表示
    # 创建对角矩阵示例
    diag_matrix = np.diag([3, 2, 1])
    eigenvalues_demo = np.array([3, 2, 1])
    
    # 创建简单的特征向量矩阵
    V = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # 单位矩阵作为特征向量
    
    # 重建矩阵
    reconstructed = V @ diag_matrix @ np.linalg.inv(V)
    
    # 可视化
    im = ax4.imshow(reconstructed, cmap='RdBu_r', aspect='auto')
    ax4.set_title('特征值分解: A = VΛV⁻¹', fontsize=14, fontweight='bold')
    ax4.set_xlabel('列索引', fontsize=12)
    ax4.set_ylabel('行索引', fontsize=12)
    
    # 添加数值标签
    for i in range(3):
        for j in range(3):
            ax4.text(j, i, f'{reconstructed[i, j]:.1f}', 
                    ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax4)
    cbar.set_label('矩阵元素值', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/eigenvalue_eigenvector.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 特征值和特征向量几何直观图已生成: docs/eigenvalue_eigenvector.png")

def create_neural_network_backpropagation():
    """创建神经网络反向传播示意图"""
    setup_matplotlib_for_plotting()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 1. 简单神经网络结构
    # 输入层
    input_x = [0, 1, 2]
    input_y = [0, 0, 0]
    ax1.scatter(input_x, input_y, s=200, c='lightblue', label='输入层', zorder=5)
    
    # 隐藏层
    hidden_x = [0.5, 1, 1.5]
    hidden_y = [1, 1, 1]
    ax1.scatter(hidden_x, hidden_y, s=200, c='lightgreen', label='隐藏层', zorder=5)
    
    # 输出层
    output_x = [1]
    output_y = [2]
    ax1.scatter(output_x, output_y, s=200, c='lightcoral', label='输出层', zorder=5)
    
    # 连接线（权重）
    # 输入到隐藏层
    for ix in input_x:
        for hx in hidden_x:
            ax1.plot([ix, hx], [0, 1], 'gray', alpha=0.5, linewidth=1)
    
    # 隐藏层到输出层
    for hx in hidden_x:
        ax1.plot([hx, output_x[0]], [1, 2], 'gray', alpha=0.5, linewidth=1)
    
    # 添加节点标签
    for i, x in enumerate(input_x):
        ax1.text(x, -0.2, f'x{i+1}', ha='center', fontsize=12, fontweight='bold')
    for i, x in enumerate(hidden_x):
        ax1.text(x, 1.2, f'h{i+1}', ha='center', fontsize=12, fontweight='bold')
    ax1.text(output_x[0], 2.2, 'y', ha='center', fontsize=12, fontweight='bold')
    
    ax1.set_xlim(-0.5, 2.5)
    ax1.set_ylim(-0.5, 2.5)
    ax1.set_title('神经网络结构示意图', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.axis('off')
    
    # 2. 反向传播过程
    # 模拟损失函数和梯度
    iterations = np.arange(1, 21)
    loss = 2.0 * np.exp(-0.2 * iterations) + 0.1 + 0.05 * np.random.randn(20)
    gradient = -0.4 * np.exp(-0.2 * iterations) + 0.01 + 0.02 * np.random.randn(20)
    
    ax2_twin = ax2.twinx()
    
    line1 = ax2.plot(iterations, loss, 'b-', linewidth=3, label='损失函数 L', marker='o')
    line2 = ax2_twin.plot(iterations, gradient, 'r-', linewidth=3, label='梯度 ∂L/∂w', marker='s')
    
    ax2.set_xlabel('迭代次数', fontsize=12)
    ax2.set_ylabel('损失函数值', fontsize=12, color='blue')
    ax2_twin.set_ylabel('梯度值', fontsize=12, color='red')
    ax2.set_title('反向传播: 损失函数与梯度变化', fontsize=16, fontweight='bold')
    
    # 合并图例
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, fontsize=12)
    
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    
    plt.tight_layout()
    plt.savefig('/workspace/docs/neural_network_backpropagation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 神经网络反向传播示意图已生成: docs/neural_network_backpropagation.png")

def main():
    """主函数：生成所有可视化图表"""
    print("🎨 开始生成机器学习基础概念可视化图表...")
    
    try:
        create_bias_variance_tradeoff()
        create_gradient_descent_visualization()
        create_pca_visualization()
        create_learning_curves()
        create_bayesian_theorem_visualization()
        create_eigenvalue_eigenvector_visualization()
        create_neural_network_backpropagation()
        
        print("\n🎉 所有可视化图表生成完成！")
        print("📊 生成的图表文件:")
        print("  - docs/bias_variance_tradeoff.png (偏差-方差权衡)")
        print("  - docs/gradient_descent_process.png (梯度下降过程)")
        print("  - docs/pca_visualization.png (PCA降维)")
        print("  - docs/learning_curves.png (学习曲线)")
        print("  - docs/bayesian_theorem.png (贝叶斯定理)")
        print("  - docs/eigenvalue_eigenvector.png (特征值和特征向量)")
        print("  - docs/neural_network_backpropagation.png (神经网络反向传播)")
        
    except Exception as e:
        print(f"❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
