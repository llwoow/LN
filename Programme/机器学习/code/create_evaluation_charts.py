#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习模型评估指标和优化方法 - 图表生成脚本
创建所有报告中引用的可视化图表
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
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
    # Must be set after style.use, otherwise will be overridden by style configuration
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def create_bias_variance_tradeoff():
    """创建偏差-方差权衡图"""
    setup_matplotlib_for_plotting()
    
    # 生成模拟数据
    np.random.seed(42)
    complexity = np.linspace(1, 10, 100)
    bias = 10 / complexity
    variance = complexity / 10
    noise = np.ones_like(complexity) * 2
    total_error = bias**2 + variance + noise
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(complexity, bias**2, 'b-', label='偏差² (Bias²)', linewidth=2)
    ax.plot(complexity, variance, 'r-', label='方差 (Variance)', linewidth=2)
    ax.plot(complexity, noise, 'g--', label='噪声 (Noise)', linewidth=2)
    ax.plot(complexity, total_error, 'k-', label='总误差 (Total Error)', linewidth=3)
    
    # 标记最优点
    optimal_idx = np.argmin(total_error)
    ax.plot(complexity[optimal_idx], total_error[optimal_idx], 'ro', markersize=10, 
            label=f'最优点 (Complexity={complexity[optimal_idx]:.1f})')
    
    ax.set_xlabel('模型复杂度 (Model Complexity)', fontsize=12)
    ax.set_ylabel('误差 (Error)', fontsize=12)
    ax.set_title('偏差-方差权衡 (Bias-Variance Tradeoff)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/bias_variance_tradeoff.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建偏差-方差权衡图")

def create_confusion_matrix_heatmap():
    """创建混淆矩阵热力图"""
    setup_matplotlib_for_plotting()
    
    # 生成模拟数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 训练模型
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # 计算混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['预测负例', '预测正例'],
                yticklabels=['真实负例', '真实正例'])
    ax.set_title('混淆矩阵 (Confusion Matrix)', fontsize=14, fontweight='bold')
    ax.set_xlabel('预测标签 (Predicted Label)', fontsize=12)
    ax.set_ylabel('真实标签 (True Label)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/confusion_matrix_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建混淆矩阵热力图")

def create_roc_curve():
    """创建ROC曲线"""
    setup_matplotlib_for_plotting()
    
    # 生成模拟数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 训练多个模型
    models = {
        '逻辑回归': LogisticRegression(random_state=42),
        '随机森林': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        ax.plot(fpr, tpr, linewidth=2, label=f'{name} (AUC = {roc_auc:.3f})')
    
    # 绘制随机分类器基线
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='随机分类器 (AUC = 0.500)')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('假正例率 (False Positive Rate)', fontsize=12)
    ax.set_ylabel('真正例率 (True Positive Rate)', fontsize=12)
    ax.set_title('ROC曲线 (Receiver Operating Characteristic)', fontsize=14, fontweight='bold')
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/roc_curve_example.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建ROC曲线图")

def create_precision_recall_curve():
    """创建精确率-召回率曲线"""
    setup_matplotlib_for_plotting()
    
    # 生成不平衡数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, weights=[0.9, 0.1], 
                               flip_y=0.05, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 训练多个模型
    models = {
        '逻辑回归': LogisticRegression(random_state=42),
        '随机森林': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        pr_auc = auc(recall, precision)
        
        ax.plot(recall, precision, linewidth=2, label=f'{name} (AUC = {pr_auc:.3f})')
    
    # 绘制随机分类器基线
    baseline = np.sum(y_test) / len(y_test)
    ax.axhline(y=baseline, color='k', linestyle='--', linewidth=1, 
               label=f'随机分类器 (AUC = {baseline:.3f})')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('召回率 (Recall)', fontsize=12)
    ax.set_ylabel('精确率 (Precision)', fontsize=12)
    ax.set_title('精确率-召回率曲线 (Precision-Recall Curve)', fontsize=14, fontweight='bold')
    ax.legend(loc="lower left", fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/precision_recall_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建精确率-召回率曲线图")

def create_regression_metrics_comparison():
    """创建回归指标对比图"""
    setup_matplotlib_for_plotting()
    
    # 生成回归数据
    np.random.seed(42)
    X, y = make_regression(n_samples=1000, n_features=10, noise=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 训练不同复杂度的模型
    models = {
        '简单模型 (3棵树)': RandomForestRegressor(n_estimators=3, max_depth=3, random_state=42),
        '中等模型 (50棵树)': RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42),
        '复杂模型 (200棵树)': RandomForestRegressor(n_estimators=200, max_depth=None, random_state=42)
    }
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # 计算指标
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # 绘制预测vs真实值
        ax1.scatter(y_test, y_pred, alpha=0.6, label=name)
        
        # 绘制残差分布
        residuals = y_test - y_pred
        ax2.hist(residuals, bins=30, alpha=0.7, label=name)
        
        # 绘制残差vs预测值
        ax3.scatter(y_pred, residuals, alpha=0.6, label=name)
        
        # 绘制指标对比
        metrics = ['MAE', 'RMSE', 'R²']
        values = [mae, rmse, r2]
        colors = ['skyblue', 'lightcoral', 'lightgreen']
        
        x_pos = np.arange(len(metrics))
        width = 0.25
        
        for i, (model_name, val) in enumerate(zip([name], values)):
            if i == 0:
                ax4.bar(x_pos + i*width, [mae, rmse, r2], width, 
                       label=model_name, color=colors[i], alpha=0.8)
    
    # 设置子图标题和标签
    ax1.set_xlabel('真实值 (True Values)', fontsize=10)
    ax1.set_ylabel('预测值 (Predicted Values)', fontsize=10)
    ax1.set_title('预测值 vs 真实值', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
    
    ax2.set_xlabel('残差 (Residuals)', fontsize=10)
    ax2.set_ylabel('频次 (Frequency)', fontsize=10)
    ax2.set_title('残差分布', fontsize=12, fontweight='bold')
    ax2.legend()
    
    ax3.set_xlabel('预测值 (Predicted Values)', fontsize=10)
    ax3.set_ylabel('残差 (Residuals)', fontsize=10)
    ax3.set_title('残差 vs 预测值', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.axhline(y=0, color='k', linestyle='--', linewidth=1)
    
    ax4.set_xlabel('指标 (Metrics)', fontsize=10)
    ax4.set_ylabel('值 (Value)', fontsize=10)
    ax4.set_title('模型性能指标对比', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(metrics)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('/workspace/images/regression_metrics_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建回归指标对比图")

def create_cross_validation_comparison():
    """创建交叉验证方法对比图"""
    setup_matplotlib_for_plotting()
    
    # 生成不平衡分类数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, weights=[0.8, 0.2], 
                               flip_y=0.05, random_state=42)
    
    # 不同的交叉验证策略
    cv_strategies = {
        '标准K折 (K=5)': 5,
        '分层K折 (K=5)': 'stratified',
        '标准K折 (K=10)': 10,
        '分层K折 (K=10)': 'stratified_10'
    }
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. 交叉验证得分分布
    cv_scores = []
    cv_labels = []
    
    for name, cv_type in cv_strategies.items():
        if cv_type == 'stratified':
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        elif cv_type == 'stratified_10':
            cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
        else:
            from sklearn.model_selection import KFold
            cv = KFold(n_splits=cv_type, shuffle=True, random_state=42)
        
        scores = cross_val_score(RandomForestClassifier(n_estimators=50, random_state=42), 
                                X, y, cv=cv, scoring='accuracy')
        cv_scores.append(scores)
        cv_labels.append(name)
    
    # 箱线图
    box_plot = ax1.boxplot(cv_scores, labels=cv_labels, patch_artist=True)
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
    
    ax1.set_ylabel('准确率 (Accuracy)', fontsize=12)
    ax1.set_title('交叉验证得分分布', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # 2. 不同折数下的性能稳定性
    fold_numbers = [3, 5, 7, 10, 15]
    mean_scores = []
    std_scores = []
    
    for k in fold_numbers:
        cv = KFold(n_splits=k, shuffle=True, random_state=42)
        scores = cross_val_score(RandomForestClassifier(n_estimators=50, random_state=42), 
                                X, y, cv=cv, scoring='accuracy')
        mean_scores.append(np.mean(scores))
        std_scores.append(np.std(scores))
    
    ax2.errorbar(fold_numbers, mean_scores, yerr=std_scores, 
                marker='o', capsize=5, capthick=2, linewidth=2, markersize=8)
    ax2.set_xlabel('折数 (Number of Folds)', fontsize=12)
    ax2.set_ylabel('平均准确率 (Mean Accuracy)', fontsize=12)
    ax2.set_title('K值对模型性能稳定性的影响', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/cross_validation_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建交叉验证对比图")

def create_hyperparameter_optimization_comparison():
    """创建超参数优化方法对比图"""
    setup_matplotlib_for_plotting()
    
    # 生成数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    
    from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
    from scipy.stats import randint, uniform
    
    # 定义参数空间
    param_dist = {
        'n_estimators': randint(10, 200),
        'max_depth': randint(3, 20),
        'min_samples_split': randint(2, 20),
        'min_samples_leaf': randint(1, 10),
        'max_features': ['sqrt', 'log2', None]
    }
    
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [5, 10, 15],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 5],
        'max_features': ['sqrt', 'log2']
    }
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 搜索效率对比
    iterations = range(1, 51)
    grid_scores = []
    random_scores = []
    
    # 模拟网格搜索的进展（简化版）
    for i in iterations:
        # 网格搜索：逐步评估所有组合
        total_combinations = 3**5  # 假设的组合数
        progress = min(i / total_combinations * 100, 100)
        grid_scores.append(progress)
        
        # 随机搜索：随机采样
        if i <= 20:
            random_scores.append(i * 5)  # 前20次快速提升
        else:
            random_scores.append(100 + np.random.normal(0, 2))  # 后续微调
    
    ax1.plot(iterations, grid_scores, 'b-', linewidth=2, label='网格搜索 (Grid Search)')
    ax1.plot(iterations, random_scores, 'r-', linewidth=2, label='随机搜索 (Random Search)')
    ax1.set_xlabel('评估次数 (Number of Evaluations)', fontsize=12)
    ax1.set_ylabel('完成进度 (%)', fontsize=12)
    ax1.set_title('搜索效率对比', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 搜索空间可视化（2D投影）
    n_estimators = np.linspace(10, 200, 50)
    max_depth = np.linspace(3, 20, 50)
    N, D = np.meshgrid(n_estimators, max_depth)
    
    # 模拟性能表面
    performance = -0.0001 * (N - 100)**2 - 0.1 * (D - 10)**2 + np.random.normal(0, 0.1, N.shape)
    
    contour = ax2.contourf(N, D, performance, levels=20, cmap='viridis', alpha=0.8)
    ax2.set_xlabel('估计器数量 (n_estimators)', fontsize=12)
    ax2.set_ylabel('最大深度 (max_depth)', fontsize=12)
    ax2.set_title('参数空间性能表面', fontsize=14, fontweight='bold')
    plt.colorbar(contour, ax=ax2, label='性能得分')
    
    # 3. 贝叶斯优化过程
    iterations_bayes = range(1, 31)
    exploration_exploitation = []
    
    # 模拟贝叶斯优化的探索-利用权衡
    for i in iterations_bayes:
        if i <= 10:
            # 前期探索
            score = 0.5 + 0.3 * (i/10) + np.random.normal(0, 0.05)
        elif i <= 20:
            # 中期平衡
            score = 0.8 + 0.15 * np.sin(i/2) + np.random.normal(0, 0.03)
        else:
            # 后期利用
            score = 0.95 + 0.03 * np.cos(i/3) + np.random.normal(0, 0.02)
        exploration_exploitation.append(score)
    
    ax3.plot(iterations_bayes, exploration_exploitation, 'g-', linewidth=3, marker='o', markersize=4)
    ax3.set_xlabel('迭代次数 (Iterations)', fontsize=12)
    ax3.set_ylabel('目标函数值 (Objective Value)', fontsize=12)
    ax3.set_title('贝叶斯优化：探索-利用权衡', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. 最终性能对比
    methods = ['网格搜索', '随机搜索', '贝叶斯优化']
    mean_scores = [0.85, 0.87, 0.91]
    std_scores = [0.02, 0.015, 0.01]
    
    bars = ax4.bar(methods, mean_scores, yerr=std_scores, capsize=5, 
                   color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8)
    ax4.set_ylabel('最佳性能得分 (Best Performance Score)', fontsize=12)
    ax4.set_title('超参数优化方法性能对比', fontsize=14, fontweight='bold')
    ax4.set_ylim(0.8, 0.95)
    
    # 添加数值标签
    for bar, score in zip(bars, mean_scores):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{score:.3f}', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/hyperparameter_optimization_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建超参数优化对比图")

def create_feature_selection_methods():
    """创建特征选择方法对比图"""
    setup_matplotlib_for_plotting()
    
    # 生成高维数据
    np.random.seed(42)
    n_samples, n_features = 500, 50
    X = np.random.randn(n_samples, n_features)
    
    # 创建真实相关特征
    true_features = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    y = np.sum(X[:, true_features], axis=1) + np.random.randn(n_samples) * 0.1
    
    from sklearn.feature_selection import SelectKBest, f_regression, RFE
    from sklearn.linear_model import Lasso
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Filter方法：相关性得分
    selector = SelectKBest(score_func=f_regression, k=10)
    X_selected = selector.fit_transform(X, y)
    scores = selector.scores_
    
    # 只显示前20个特征的得分
    feature_indices = range(min(20, len(scores)))
    ax1.bar(feature_indices, scores[:len(feature_indices)], color='skyblue', alpha=0.8)
    ax1.set_xlabel('特征索引 (Feature Index)', fontsize=12)
    ax1.set_ylabel('F统计量 (F-statistic)', fontsize=12)
    ax1.set_title('过滤法：特征相关性得分', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 标记真实相关特征
    true_indices = [i for i in true_features if i < 20]
    ax1.scatter(true_indices, [scores[i] for i in true_indices], 
               color='red', s=100, zorder=5, label='真实相关特征')
    ax1.legend()
    
    # 2. Wrapper方法：递归特征消除
    estimator = RandomForestRegressor(n_estimators=50, random_state=42)
    rfe = RFE(estimator=estimator, n_features_to_select=10)
    rfe.fit(X, y)
    rfe_scores = rfe.ranking_
    
    ax2.bar(range(len(rfe_scores)), rfe_scores, color='lightgreen', alpha=0.8)
    ax2.set_xlabel('特征索引 (Feature Index)', fontsize=12)
    ax2.set_ylabel('特征排名 (Feature Ranking)', fontsize=12)
    ax2.set_title('包装法：递归特征消除排名', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 标记选择的特征
    selected_features = np.where(rfe.support_)[0]
    ax2.scatter(selected_features, [rfe_scores[i] for i in selected_features], 
               color='red', s=100, zorder=5, label='选择的特征')
    ax2.legend()
    
    # 3. Embedded方法：Lasso系数
    alphas = np.logspace(-4, 1, 50)
    coefs = []
    
    for alpha in alphas:
        lasso = Lasso(alpha=alpha, random_state=42)
        lasso.fit(X, y)
        coefs.append(lasso.coef_)
    
    coefs = np.array(coefs)
    
    # 选择几个代表性特征进行可视化
    selected_features_lasso = [0, 5, 10, 15, 20]
    for feature in selected_features_lasso:
        if feature < coefs.shape[1]:
            ax3.plot(alphas, coefs[:, feature], linewidth=2, label=f'特征 {feature}')
    
    ax3.set_xscale('log')
    ax3.set_xlabel('正则化参数 α (Regularization Parameter)', fontsize=12)
    ax3.set_ylabel('系数值 (Coefficient Value)', fontsize=12)
    ax3.set_title('嵌入式：Lasso正则化路径', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 特征选择方法性能对比
    methods = ['原始特征', '过滤法', '包装法', '嵌入式']
    scores = [0.75, 0.82, 0.85, 0.88]  # 模拟性能得分
    colors = ['lightgray', 'skyblue', 'lightgreen', 'lightcoral']
    
    bars = ax4.bar(methods, scores, color=colors, alpha=0.8)
    ax4.set_ylabel('模型性能得分 (Model Performance)', fontsize=12)
    ax4.set_title('特征选择方法性能对比', fontsize=14, fontweight='bold')
    ax4.set_ylim(0.7, 0.9)
    
    # 添加数值标签
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{score:.3f}', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/feature_selection_methods.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建特征选择方法对比图")

def create_ensemble_methods_comparison():
    """创建集成方法对比图"""
    setup_matplotlib_for_plotting()
    
    # 生成数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier
    from sklearn.tree import DecisionTreeClassifier
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Bagging vs 单模型性能
    n_estimators_range = range(1, 51)
    bagging_scores = []
    single_scores = []
    
    for n_est in n_estimators_range:
        # Bagging
        bagging = RandomForestClassifier(n_estimators=n_est, random_state=42)
        bagging.fit(X_train, y_train)
        bagging_scores.append(bagging.score(X_test, y_test))
        
        # 单模型
        single = DecisionTreeClassifier(random_state=42)
        single.fit(X_train, y_train)
        single_scores.append(single.score(X_test, y_test))
    
    ax1.plot(n_estimators_range, bagging_scores, 'b-', linewidth=2, label='Bagging (随机森林)')
    ax1.axhline(y=single_scores[0], color='r', linestyle='--', linewidth=2, label='单决策树')
    ax1.set_xlabel('估计器数量 (Number of Estimators)', fontsize=12)
    ax1.set_ylabel('准确率 (Accuracy)', fontsize=12)
    ax1.set_title('Bagging：集成数量对性能的影响', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Boosting学习曲线
    n_estimators_boost = range(1, 101)
    ada_scores = []
    gb_scores = []
    
    for n_est in n_estimators_boost:
        # AdaBoost
        ada = AdaBoostClassifier(n_estimators=n_est, random_state=42)
        ada.fit(X_train, y_train)
        ada_scores.append(ada.score(X_test, y_test))
        
        # Gradient Boosting
        gb = GradientBoostingClassifier(n_estimators=n_est, random_state=42)
        gb.fit(X_train, y_train)
        gb_scores.append(gb.score(X_test, y_test))
    
    ax2.plot(n_estimators_boost, ada_scores, 'g-', linewidth=2, label='AdaBoost')
    ax2.plot(n_estimators_boost, gb_scores, 'orange', linewidth=2, label='Gradient Boosting')
    ax2.set_xlabel('迭代次数 (Number of Iterations)', fontsize=12)
    ax2.set_ylabel('准确率 (Accuracy)', fontsize=12)
    ax2.set_title('Boosting：迭代次数对性能的影响', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 集成方法方差对比
    methods = ['单决策树', 'Bagging\n(10棵树)', 'Bagging\n(50棵树)', 'AdaBoost', 'Gradient Boosting']
    variances = [0.15, 0.08, 0.06, 0.05, 0.04]  # 模拟方差
    biases = [0.25, 0.18, 0.15, 0.12, 0.10]     # 模拟偏差
    
    x_pos = np.arange(len(methods))
    width = 0.35
    
    bars1 = ax3.bar(x_pos - width/2, variances, width, label='方差 (Variance)', 
                    color='lightcoral', alpha=0.8)
    bars2 = ax3.bar(x_pos + width/2, biases, width, label='偏差 (Bias)', 
                    color='lightblue', alpha=0.8)
    
    ax3.set_xlabel('模型类型 (Model Type)', fontsize=12)
    ax3.set_ylabel('误差 (Error)', fontsize=12)
    ax3.set_title('集成方法的偏差-方差权衡', fontsize=14, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(methods, rotation=45, ha='right')
    ax3.legend()
    
    # 4. 最终性能对比
    methods_final = ['单模型', 'Bagging', 'Boosting', 'Stacking']
    accuracies = [0.78, 0.85, 0.87, 0.89]
    stds = [0.02, 0.015, 0.012, 0.01]
    
    bars = ax4.bar(methods_final, accuracies, yerr=stds, capsize=5,
                   color=['lightgray', 'skyblue', 'lightgreen', 'lightcoral'], alpha=0.8)
    ax4.set_ylabel('准确率 (Accuracy)', fontsize=12)
    ax4.set_title('集成方法最终性能对比', fontsize=14, fontweight='bold')
    ax4.set_ylim(0.7, 0.95)
    
    # 添加数值标签
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{acc:.3f}', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/ensemble_methods_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建集成方法对比图")

def create_regularization_comparison():
    """创建正则化方法对比图"""
    setup_matplotlib_for_plotting()
    
    # 生成高维数据
    np.random.seed(42)
    n_samples, n_features = 200, 100
    X = np.random.randn(n_samples, n_features)
    
    # 创建真实稀疏系数
    true_coefs = np.zeros(n_features)
    true_coefs[:10] = np.random.randn(10)  # 只有前10个特征有贡献
    y = X @ true_coefs + np.random.randn(n_samples) * 0.5
    
    from sklearn.linear_model import Ridge, Lasso, ElasticNet
    from sklearn.preprocessing import StandardScaler
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 正则化路径对比
    alphas = np.logspace(-3, 2, 50)
    
    ridge_coefs = []
    lasso_coefs = []
    elastic_coefs = []
    
    for alpha in alphas:
        # Ridge
        ridge = Ridge(alpha=alpha, random_state=42)
        ridge.fit(X_scaled, y)
        ridge_coefs.append(ridge.coef_[:20])  # 只显示前20个
        
        # Lasso
        lasso = Lasso(alpha=alpha, random_state=42, max_iter=2000)
        lasso.fit(X_scaled, y)
        lasso_coefs.append(lasso.coef_[:20])
        
        # Elastic Net
        elastic = ElasticNet(alpha=alpha, l1_ratio=0.5, random_state=42, max_iter=2000)
        elastic.fit(X_scaled, y)
        elastic_coefs.append(elastic.coef_[:20])
    
    ridge_coefs = np.array(ridge_coefs)
    lasso_coefs = np.array(lasso_coefs)
    elastic_coefs = np.array(elastic_coefs)
    
    # 绘制前5个特征的路径
    for i in range(5):
        ax1.plot(alphas, ridge_coefs[:, i], '--', linewidth=2, label=f'Ridge 特征{i}')
        ax1.plot(alphas, lasso_coefs[:, i], '-', linewidth=2, label=f'Lasso 特征{i}')
        ax1.plot(alphas, elastic_coefs[:, i], ':', linewidth=2, label=f'ElasticNet 特征{i}')
    
    ax1.set_xscale('log')
    ax1.set_xlabel('正则化参数 α (Regularization Parameter)', fontsize=12)
    ax1.set_ylabel('系数值 (Coefficient Value)', fontsize=12)
    ax1.set_title('正则化路径对比', fontsize=14, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. 稀疏性对比
    l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
    sparsity_counts = []
    
    for l1_ratio in l1_ratios:
        elastic = ElasticNet(alpha=0.1, l1_ratio=l1_ratio, random_state=42, max_iter=2000)
        elastic.fit(X_scaled, y)
        sparsity_counts.append(np.sum(np.abs(elastic.coef_) > 1e-5))
    
    ax2.bar(range(len(l1_ratios)), sparsity_counts, color='lightcoral', alpha=0.8)
    ax2.set_xlabel('L1/L2比例 (L1/L2 Ratio)', fontsize=12)
    ax2.set_ylabel('非零系数数量 (Number of Non-zero Coefficients)', fontsize=12)
    ax2.set_title('ElasticNet的稀疏性控制', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(l1_ratios)))
    ax2.set_xticklabels([f'{r:.1f}' for r in l1_ratios])
    ax2.grid(True, alpha=0.3)
    
    # 3. 偏差-方差权衡
    alphas_bias_variance = np.logspace(-2, 1, 20)
    biases = []
    variances = []
    
    for alpha in alphas_bias_variance:
        lasso = Lasso(alpha=alpha, random_state=42, max_iter=2000)
        lasso.fit(X_scaled, y)
        # 模拟偏差和方差
        bias = 1.0 / (1 + alpha * 10)  # 正则化增加偏差
        variance = alpha * 0.1         # 正则化减少方差
        biases.append(bias)
        variances.append(variance)
    
    ax3.plot(alphas_bias_variance, biases, 'b-', linewidth=2, label='偏差 (Bias)')
    ax3.plot(alphas_bias_variance, variances, 'r-', linewidth=2, label='方差 (Variance)')
    ax3.set_xscale('log')
    ax3.set_xlabel('正则化参数 α (Regularization Parameter)', fontsize=12)
    ax3.set_ylabel('误差 (Error)', fontsize=12)
    ax3.set_title('正则化的偏差-方差权衡', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 性能对比
    methods = ['无正则化', 'L2 (Ridge)', 'L1 (Lasso)', 'ElasticNet']
    r2_scores = [0.65, 0.72, 0.78, 0.80]  # 模拟R²得分
    
    bars = ax4.bar(methods, r2_scores, color=['lightgray', 'lightblue', 'lightgreen', 'lightcoral'], alpha=0.8)
    ax4.set_ylabel('R² 得分 (R² Score)', fontsize=12)
    ax4.set_title('正则化方法性能对比', fontsize=14, fontweight='bold')
    ax4.set_ylim(0.6, 0.85)
    
    # 添加数值标签
    for bar, score in zip(bars, r2_scores):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.3f}', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('/workspace/images/regularization_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建正则化方法对比图")

def create_end_to_end_pipeline():
    """创建端到端流程图"""
    setup_matplotlib_for_plotting()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 定义流程步骤
    steps = [
        "数据收集\n与预处理",
        "特征工程\n与选择",
        "模型选择\n与训练",
        "超参数\n优化",
        "模型评估\n与验证",
        "模型部署\n与监控"
    ]
    
    # 定义位置
    x_positions = np.linspace(1, 13, len(steps))
    y_position = 5
    
    # 绘制流程框
    for i, (x, step) in enumerate(zip(x_positions, steps)):
        # 绘制矩形框
        rect = plt.Rectangle((x-1, y_position-0.8), 2, 1.6, 
                           facecolor='lightblue', edgecolor='navy', linewidth=2)
        ax.add_patch(rect)
        
        # 添加文本
        ax.text(x, y_position, step, ha='center', va='center', 
                fontsize=11, fontweight='bold')
        
        # 添加箭头（除了最后一个）
        if i < len(steps) - 1:
            ax.annotate('', xy=(x_positions[i+1]-1, y_position), 
                       xytext=(x+1, y_position),
                       arrowprops=dict(arrowstyle='->', lw=2, color='navy'))
    
    # 添加反馈循环
    ax.annotate('模型重训练\n与改进', xy=(x_positions[0]+0.5, y_position-2), 
               xytext=(x_positions[-1]-0.5, y_position-2),
               arrowprops=dict(arrowstyle='->', lw=2, color='red', 
                             connectionstyle="arc3,rad=0.3"),
               fontsize=10, ha='center', color='red', fontweight='bold')
    
    # 添加侧边注释
    annotations = [
        "数据质量\n影响模型上限",
        "特征工程\n决定模型能力",
        "算法选择\n匹配问题类型",
        "调参优化\n提升性能",
        "评估指标\n指导决策",
        "持续监控\n保证效果"
    ]
    
    for i, (x, annotation) in enumerate(zip(x_positions, annotations)):
        ax.text(x, y_position+2.5, annotation, ha='center', va='center',
                fontsize=9, style='italic', color='darkgreen',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7))
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_title('机器学习项目端到端流程', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/images/end_to_end_pipeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 创建端到端流程图")

def main():
    """主函数：创建所有图表"""
    print("开始创建机器学习评估指标与优化方法图表...")
    
    # 确保images目录存在
    import os
    os.makedirs('/workspace/images', exist_ok=True)
    
    # 创建所有图表
    create_bias_variance_tradeoff()
    create_confusion_matrix_heatmap()
    create_roc_curve()
    create_precision_recall_curve()
    create_regression_metrics_comparison()
    create_cross_validation_comparison()
    create_hyperparameter_optimization_comparison()
    create_feature_selection_methods()
    create_ensemble_methods_comparison()
    create_regularization_comparison()
    create_end_to_end_pipeline()
    
    print("\n✅ 所有图表创建完成！")
    print("图表保存位置：/workspace/images/")

if __name__ == "__main__":
    main()