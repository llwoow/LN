#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习模型评估指标与优化方法 - 完整代码示例
展示所有主要概念的完整实现
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, KFold
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, BaggingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (confusion_matrix, classification_report, roc_curve, auc, 
                           precision_recall_curve, mean_absolute_error, mean_squared_error, r2_score)
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def setup_matplotlib_for_plotting():
    """设置matplotlib绘图配置"""
    plt.switch_backend("Agg")
    plt.style.use("seaborn-v0_8")
    sns.set_palette("husl")
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

def example_1_evaluation_metrics():
    """示例1：分类评估指标计算"""
    print("=" * 60)
    print("示例1：分类评估指标计算")
    print("=" * 60)
    
    # 生成数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 训练模型
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # 计算评估指标
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    print(f"准确率 (Accuracy): {accuracy:.4f}")
    print(f"精确率 (Precision): {precision:.4f}")
    print(f"召回率 (Recall): {recall:.4f}")
    print(f"F1分数 (F1-score): {f1:.4f}")
    print(f"AUC分数: {auc_score:.4f}")
    
    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n混淆矩阵:")
    print(cm)
    
    # 详细分类报告
    print(f"\n详细分类报告:")
    print(classification_report(y_test, y_pred))
    
    return y_test, y_pred, y_pred_proba

def example_2_regression_metrics():
    """示例2：回归评估指标计算"""
    print("\n" + "=" * 60)
    print("示例2：回归评估指标计算")
    print("=" * 60)
    
    # 生成回归数据
    np.random.seed(42)
    X, y = make_regression(n_samples=1000, n_features=10, noise=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 训练模型
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # 计算回归指标
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"平均绝对误差 (MAE): {mae:.4f}")
    print(f"均方误差 (MSE): {mse:.4f}")
    print(f"均方根误差 (RMSE): {rmse:.4f}")
    print(f"决定系数 (R²): {r2:.4f}")
    
    # 计算MAPE (平均绝对百分比误差)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    print(f"平均绝对百分比误差 (MAPE): {mape:.2f}%")
    
    return y_test, y_pred

def example_3_cross_validation():
    """示例3：交叉验证方法"""
    print("\n" + "=" * 60)
    print("示例3：交叉验证方法")
    print("=" * 60)
    
    # 生成不平衡分类数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, weights=[0.8, 0.2], 
                               flip_y=0.05, random_state=42)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    
    # 1. 标准K折交叉验证
    kfold_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"标准K折交叉验证 (K=5):")
    print(f"  得分: {kfold_scores}")
    print(f"  平均: {kfold_scores.mean():.4f} ± {kfold_scores.std():.4f}")
    
    # 2. 分层K折交叉验证
    stratified_scores = cross_val_score(model, X, y, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42), 
                                       scoring='accuracy')
    print(f"\n分层K折交叉验证 (K=5):")
    print(f"  得分: {stratified_scores}")
    print(f"  平均: {stratified_scores.mean():.4f} ± {stratified_scores.std():.4f}")
    
    # 3. 不同K值的比较
    k_values = [3, 5, 7, 10]
    print(f"\n不同K值的交叉验证结果:")
    for k in k_values:
        scores = cross_val_score(model, X, y, cv=k, scoring='accuracy')
        print(f"  K={k}: {scores.mean():.4f} ± {scores.std():.4f}")
    
    return kfold_scores, stratified_scores

def example_4_hyperparameter_optimization():
    """示例4：超参数优化"""
    print("\n" + "=" * 60)
    print("示例4：超参数优化")
    print("=" * 60)
    
    # 生成数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 定义参数空间
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    param_dist = {
        'n_estimators': np.arange(50, 201, 10),
        'max_depth': np.arange(3, 21, 2),
        'min_samples_split': np.arange(2, 21, 2),
        'min_samples_leaf': np.arange(1, 11, 1)
    }
    
    model = RandomForestClassifier(random_state=42)
    
    # 1. 网格搜索
    print("网格搜索 (Grid Search):")
    grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print(f"  最佳参数: {grid_search.best_params_}")
    print(f"  最佳得分: {grid_search.best_score_:.4f}")
    
    # 2. 随机搜索
    print("\n随机搜索 (Random Search):")
    random_search = RandomizedSearchCV(model, param_dist, n_iter=20, cv=3, 
                                      scoring='accuracy', random_state=42, n_jobs=-1)
    random_search.fit(X_train, y_train)
    print(f"  最佳参数: {random_search.best_params_}")
    print(f"  最佳得分: {random_search.best_score_:.4f}")
    
    # 3. 分层随机搜索 (针对不平衡数据)
    print("\n分层随机搜索 (Stratified Random Search):")
    from sklearn.model_selection import StratifiedKFold
    stratified_random = RandomizedSearchCV(model, param_dist, n_iter=20, cv=3, 
                                          scoring='accuracy', random_state=42, n_jobs=-1)
    stratified_random.fit(X_train, y_train)
    print(f"  最佳参数: {stratified_random.best_params_}")
    print(f"  最佳得分: {stratified_random.best_score_:.4f}")
    
    return grid_search, random_search, stratified_random

def example_5_feature_selection():
    """示例5：特征选择方法"""
    print("\n" + "=" * 60)
    print("示例5：特征选择方法")
    print("=" * 60)
    
    # 生成高维数据
    np.random.seed(42)
    n_samples, n_features = 500, 50
    X = np.random.randn(n_samples, n_features)
    
    # 创建真实相关特征
    true_features = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    y = np.sum(X[:, true_features], axis=1) + np.random.randn(n_samples) * 0.1
    
    # 1. 过滤法 (Filter)
    print("过滤法 (Filter Method):")
    selector = SelectKBest(score_func=f_regression, k=10)
    X_selected = selector.fit_transform(X, y)
    selected_features = selector.get_support(indices=True)
    print(f"  选择的特征索引: {selected_features}")
    print(f"  真实相关特征: {true_features}")
    print(f"  选择准确率: {len(set(selected_features) & set(true_features)) / len(true_features):.2f}")
    
    # 2. 包装法 (Wrapper)
    print("\n包装法 (Wrapper Method):")
    estimator = RandomForestRegressor(n_estimators=50, random_state=42)
    rfe = RFE(estimator=estimator, n_features_to_select=10)
    rfe.fit(X, y)
    wrapper_features = np.where(rfe.support_)[0]
    print(f"  选择的特征索引: {wrapper_features}")
    print(f"  选择准确率: {len(set(wrapper_features) & set(true_features)) / len(true_features):.2f}")
    
    # 3. 嵌入式 (Embedded)
    print("\n嵌入式 (Embedded Method):")
    lasso = Lasso(alpha=0.1, random_state=42)
    lasso.fit(X, y)
    embedded_features = np.where(np.abs(lasso.coef_) > 1e-5)[0]
    print(f"  选择的特征索引: {embedded_features}")
    print(f"  选择准确率: {len(set(embedded_features) & set(true_features)) / len(true_features):.2f}")
    
    return selector, rfe, lasso

def example_6_regularization():
    """示例6：正则化方法"""
    print("\n" + "=" * 60)
    print("示例6：正则化方法")
    print("=" * 60)
    
    # 生成高维数据
    np.random.seed(42)
    n_samples, n_features = 200, 100
    X = np.random.randn(n_samples, n_features)
    
    # 创建真实稀疏系数
    true_coefs = np.zeros(n_features)
    true_coefs[:10] = np.random.randn(10)
    y = X @ true_coefs + np.random.randn(n_samples) * 0.5
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 不同正则化方法
    alphas = [0.01, 0.1, 1.0, 10.0]
    
    print("不同正则化参数的效果:")
    for alpha in alphas:
        # Ridge回归
        ridge = Ridge(alpha=alpha, random_state=42)
        ridge.fit(X_scaled, y)
        ridge_score = ridge.score(X_scaled, y)
        ridge_nonzero = np.sum(np.abs(ridge.coef_) > 1e-5)
        
        # Lasso回归
        lasso = Lasso(alpha=alpha, random_state=42, max_iter=2000)
        lasso.fit(X_scaled, y)
        lasso_score = lasso.score(X_scaled, y)
        lasso_nonzero = np.sum(np.abs(lasso.coef_) > 1e-5)
        
        # Elastic Net
        elastic = ElasticNet(alpha=alpha, l1_ratio=0.5, random_state=42, max_iter=2000)
        elastic.fit(X_scaled, y)
        elastic_score = elastic.score(X_scaled, y)
        elastic_nonzero = np.sum(np.abs(elastic.coef_) > 1e-5)
        
        print(f"\nα = {alpha}:")
        print(f"  Ridge: R² = {ridge_score:.4f}, 非零系数 = {ridge_nonzero}")
        print(f"  Lasso: R² = {lasso_score:.4f}, 非零系数 = {lasso_nonzero}")
        print(f"  ElasticNet: R² = {elastic_score:.4f}, 非零系数 = {elastic_nonzero}")
    
    return ridge, lasso, elastic

def example_7_ensemble_methods():
    """示例7：集成方法"""
    print("\n" + "=" * 60)
    print("示例7：集成方法")
    print("=" * 60)
    
    # 生成数据
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 1. Bagging
    print("Bagging方法:")
    bagging = BaggingClassifier(n_estimators=50, random_state=42)
    bagging.fit(X_train, y_train)
    bagging_score = bagging.score(X_test, y_test)
    print(f"  准确率: {bagging_score:.4f}")
    
    # 2. Boosting
    print("\nBoosting方法:")
    boosting = AdaBoostClassifier(n_estimators=50, random_state=42)
    boosting.fit(X_train, y_train)
    boosting_score = boosting.score(X_test, y_test)
    print(f"  准确率: {boosting_score:.4f}")
    
    # 3. 随机森林
    print("\n随机森林:")
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)
    rf_score = rf.score(X_test, y_test)
    print(f"  准确率: {rf_score:.4f}")
    
    # 4. 单个决策树作为对比
    print("\n单个决策树:")
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)
    dt_score = dt.score(X_test, y_test)
    print(f"  准确率: {dt_score:.4f}")
    
    return bagging, boosting, rf, dt

def example_8_complete_pipeline():
    """示例8：完整的机器学习管道"""
    print("\n" + "=" * 60)
    print("示例8：完整的机器学习管道")
    print("=" * 60)
    
    # 1. 数据生成和预处理
    print("步骤1：数据生成和预处理")
    np.random.seed(42)
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                               n_redundant=5, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 特征标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"  训练集大小: {X_train_scaled.shape}")
    print(f"  测试集大小: {X_test_scaled.shape}")
    
    # 2. 特征选择
    print("\n步骤2：特征选择")
    selector = SelectKBest(score_func=f_regression, k=15)
    X_train_selected = selector.fit_transform(X_train_scaled, y_train)
    X_test_selected = selector.transform(X_test_scaled)
    
    print(f"  选择的特征数量: {X_train_selected.shape[1]}")
    
    # 3. 模型训练和超参数优化
    print("\n步骤3：模型训练和超参数优化")
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [10, 15],
        'min_samples_split': [2, 5]
    }
    
    model = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train_selected, y_train)
    
    print(f"  最佳参数: {grid_search.best_params_}")
    print(f"  交叉验证得分: {grid_search.best_score_:.4f}")
    
    # 4. 模型评估
    print("\n步骤4：模型评估")
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test_selected)
    y_pred_proba = best_model.predict_proba(X_test_selected)[:, 1]
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    print(f"  测试集准确率: {accuracy:.4f}")
    print(f"  精确率: {precision:.4f}")
    print(f"  召回率: {recall:.4f}")
    print(f"  F1分数: {f1:.4f}")
    print(f"  AUC分数: {auc_score:.4f}")
    
    # 5. 特征重要性
    print("\n步骤5：特征重要性分析")
    feature_importance = best_model.feature_importances_
    top_features = np.argsort(feature_importance)[-10:][::-1]
    
    print("  前10个重要特征:")
    for i, feat_idx in enumerate(top_features):
        print(f"    特征 {feat_idx}: {feature_importance[feat_idx]:.4f}")
    
    return best_model, scaler, selector

def main():
    """主函数：运行所有示例"""
    print("机器学习模型评估指标与优化方法 - 完整代码示例")
    print("=" * 80)
    
    # 设置绘图
    setup_matplotlib_for_plotting()
    
    # 运行所有示例
    example_1_evaluation_metrics()
    example_2_regression_metrics()
    example_3_cross_validation()
    example_4_hyperparameter_optimization()
    example_5_feature_selection()
    example_6_regularization()
    example_7_ensemble_methods()
    model, scaler, selector = example_8_complete_pipeline()
    
    print("\n" + "=" * 80)
    print("✅ 所有示例运行完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()