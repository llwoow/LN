#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多旋翼飞行器气动力学性能分析图表生成
创建关键的性能分析图表以支持研究报告
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

def create_propeller_performance_curves():
    """创建螺旋桨性能曲线图"""
    setup_matplotlib_for_plotting()
    
    # 转速范围 (RPM)
    rpm = np.linspace(2000, 12000, 100)
    
    # 螺旋桨直径 (英寸)
    diameters = [8, 9, 11, 12]
    
    # 推力计算公式: T = CT × ρ × n² × D⁴
    # 其中 CT ≈ 0.08 (典型值), ρ = 1.225 kg/m³
    CT = 0.08
    rho = 1.225
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 推力-转速曲线
    for d in diameters:
        # 将直径转换为米
        D = d * 0.0254  # 1英寸 = 0.0254米
        # 转速转换为转/秒
        n = rpm / 60
        # 计算推力 (牛顿)
        T = CT * rho * n**2 * D**4
        ax1.plot(rpm, T, label=f'{d}"螺旋桨', linewidth=2)
    
    ax1.set_xlabel('转速 (RPM)')
    ax1.set_ylabel('推力 (N)')
    ax1.set_title('螺旋桨直径对推力的影响')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 功率-转速曲线
    # 功率公式: P = CP × ρ × n³ × D⁵
    # CP ≈ 0.02 (典型值)
    CP = 0.02
    
    for d in diameters:
        D = d * 0.0254
        n = rpm / 60
        P = CP * rho * n**3 * D**5
        ax2.plot(rpm, P, label=f'{d}"螺旋桨', linewidth=2)
    
    ax2.set_xlabel('转速 (RPM)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('螺旋桨直径对功率的影响')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 效率曲线
    for d in diameters:
        D = d * 0.0254
        n = rpm / 60
        T = CT * rho * n**2 * D**4
        P = CP * rho * n**3 * D**5
        # 效率 = 推力功率 / 输入功率
        efficiency = (T * n * 2 * np.pi * D/2) / P  # 简化计算
        efficiency = np.clip(efficiency, 0, 1)  # 限制在0-1之间
        ax3.plot(rpm, efficiency * 100, label=f'{d}"螺旋桨', linewidth=2)
    
    ax3.set_xlabel('转速 (RPM)')
    ax3.set_ylabel('效率 (%)')
    ax3.set_title('螺旋桨效率随转速变化')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 推力系数CT随转速变化
    for d in diameters:
        D = d * 0.0254
        n = rpm / 60
        T = CT * rho * n**2 * D**4
        # 重新计算CT
        CT_calculated = T / (rho * n**2 * D**4)
        ax4.plot(rpm, CT_calculated, label=f'{d}"螺旋桨', linewidth=2)
    
    ax4.set_xlabel('转速 (RPM)')
    ax4.set_ylabel('推力系数 CT')
    ax4.set_title('推力系数随转速变化')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/propeller_performance_curves.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_environmental_effects():
    """创建环境因素影响分析图"""
    setup_matplotlib_for_plotting()
    
    # 海拔高度 (米)
    altitude = np.linspace(0, 4000, 100)
    
    # 空气密度随海拔变化 (标准大气模型)
    # ρ = ρ0 * (1 - 0.0065 * h / T0)^(g * M / (R * 0.0065)) - 1
    # 简化版本: ρ = ρ0 * (1 - 0.0065 * h / 288.15)^(5.256)
    rho0 = 1.225  # 海平面密度 kg/m³
    rho = rho0 * (1 - 0.0065 * altitude / 288.15)**5.256
    
    # 温度随海拔变化
    T = 288.15 - 0.0065 * altitude
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 空气密度随海拔变化
    ax1.plot(altitude, rho, linewidth=3, color='blue')
    ax1.set_xlabel('海拔高度 (m)')
    ax1.set_ylabel('空气密度 (kg/m³)')
    ax1.set_title('空气密度随海拔变化')
    ax1.grid(True, alpha=0.3)
    
    # 2. 温度随海拔变化
    ax2.plot(altitude, T, linewidth=3, color='red')
    ax2.set_xlabel('海拔高度 (m)')
    ax2.set_ylabel('温度 (K)')
    ax2.set_title('温度随海拔变化')
    ax2.grid(True, alpha=0.3)
    
    # 3. 推力损失随海拔变化 (假设转速恒定)
    D = 0.25  # 0.25米直径螺旋桨
    CT = 0.08
    n = 6000 / 60  # 6000 RPM = 100 rps
    T0 = CT * rho0 * n**2 * D**4  # 海平面推力
    T_altitude = CT * rho * n**2 * D**4
    thrust_loss = (T0 - T_altitude) / T0 * 100
    
    ax3.plot(altitude, thrust_loss, linewidth=3, color='orange')
    ax3.set_xlabel('海拔高度 (m)')
    ax3.set_ylabel('推力损失 (%)')
    ax3.set_title('推力损失随海拔变化')
    ax3.grid(True, alpha=0.3)
    
    # 4. 效率损失随海拔变化
    CP = 0.02
    P0 = CP * rho0 * n**3 * D**5  # 海平面功率
    P_altitude = CP * rho * n**3 * D**5
    efficiency_loss = (P0 - P_altitude) / P0 * 100
    
    ax4.plot(altitude, efficiency_loss, linewidth=3, color='green')
    ax4.set_xlabel('海拔高度 (m)')
    ax4.set_ylabel('功率损失 (%)')
    ax4.set_title('功率损失随海拔变化')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/environmental_effects.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_flight_performance_analysis():
    """创建飞行性能分析图"""
    setup_matplotlib_for_plotting()
    
    # 飞行速度 (m/s)
    flight_speed = np.linspace(0, 30, 100)
    
    # 螺旋桨参数
    D = 0.25  # 直径 0.25m
    CT = 0.08
    CP = 0.02
    rho = 1.225
    
    # 悬停状态 (V=0)
    n_hover = 100  # rps
    T_hover = CT * rho * n_hover**2 * D**4
    P_hover = CP * rho * n_hover**3 * D**5
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 所需推力随飞行速度变化
    # 简化模型: T = T_hover + 0.5 * ρ * Cd * A * V²
    mass = 2.0  # 2kg质量
    g = 9.81
    T_weight = mass * g
    CdA = 0.02  # 阻力系数×面积
    
    T_required = T_weight + 0.5 * rho * CdA * flight_speed**2
    ax1.plot(flight_speed, T_required, linewidth=3, label='所需推力')
    ax1.axhline(y=T_hover, color='red', linestyle='--', label='悬停推力')
    ax1.set_xlabel('飞行速度 (m/s)')
    ax1.set_ylabel('所需推力 (N)')
    ax1.set_title('所需推力随飞行速度变化')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 所需功率随飞行速度变化
    # 考虑前飞时的功率增加
    P_required = P_hover + 0.5 * rho * CdA * flight_speed**3
    ax2.plot(flight_speed, P_required, linewidth=3, color='blue')
    ax2.axhline(y=P_hover, color='red', linestyle='--', label='悬停功率')
    ax2.set_xlabel('飞行速度 (m/s)')
    ax2.set_ylabel('所需功率 (W)')
    ax2.set_title('所需功率随飞行速度变化')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 飞行效率随速度变化
    efficiency = (T_required * flight_speed) / P_required
    efficiency = np.clip(efficiency, 0, 1)
    ax3.plot(flight_speed, efficiency * 100, linewidth=3, color='green')
    ax3.set_xlabel('飞行速度 (m/s)')
    ax3.set_ylabel('飞行效率 (%)')
    ax3.set_title('飞行效率随速度变化')
    ax3.grid(True, alpha=0.3)
    
    # 4. 续航时间分析 (假设电池容量100Wh)
    battery_capacity = 100  # Wh
    endurance = battery_capacity / P_required * 3600  # 秒转换为小时
    endurance = np.clip(endurance, 0, 10)  # 限制显示范围
    
    ax4.plot(flight_speed, endurance, linewidth=3, color='purple')
    ax4.set_xlabel('飞行速度 (m/s)')
    ax4.set_ylabel('续航时间 (小时)')
    ax4.set_title('续航时间随飞行速度变化')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/flight_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_payload_capacity_analysis():
    """创建载荷能力分析图"""
    setup_matplotlib_for_plotting()
    
    # 螺旋桨数量
    num_rotors = np.array([3, 4, 6, 8])
    
    # 螺旋桨参数
    D = 0.25  # 直径 0.25m
    CT = 0.08
    CP = 0.02
    rho = 1.225
    n = 100  # rps
    
    # 单个螺旋桨推力
    T_single = CT * rho * n**2 * D**4
    
    # 总推力
    T_total = T_single * num_rotors
    
    # 系统重量估算 (包括机体、电池等)
    system_weight = 0.5 + 0.3 * num_rotors  # 基础重量 + 每个螺旋桨0.3kg
    
    # 有效载荷
    payload_capacity = T_total - system_weight * 9.81
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 推力随螺旋桨数量变化
    ax1.bar(num_rotors, T_total, alpha=0.7, color='skyblue')
    ax1.set_xlabel('螺旋桨数量')
    ax1.set_ylabel('总推力 (N)')
    ax1.set_title('总推力随螺旋桨数量变化')
    ax1.grid(True, alpha=0.3)
    
    # 2. 系统重量随螺旋桨数量变化
    ax2.bar(num_rotors, system_weight, alpha=0.7, color='lightcoral')
    ax2.set_xlabel('螺旋桨数量')
    ax2.set_ylabel('系统重量 (kg)')
    ax2.set_title('系统重量随螺旋桨数量变化')
    ax2.grid(True, alpha=0.3)
    
    # 3. 载荷能力分析
    ax3.bar(num_rotors, payload_capacity, alpha=0.7, color='lightgreen')
    ax3.axhline(y=0, color='red', linestyle='--', label='零载荷线')
    ax3.set_xlabel('螺旋桨数量')
    ax3.set_ylabel('载荷能力 (N)')
    ax3.set_title('载荷能力随螺旋桨数量变化')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 推重比分析
    thrust_to_weight_ratio = T_total / (system_weight * 9.81)
    ax4.bar(num_rotors, thrust_to_weight_ratio, alpha=0.7, color='gold')
    ax4.axhline(y=1.0, color='red', linestyle='--', label='1:1推重比')
    ax4.set_xlabel('螺旋桨数量')
    ax4.set_ylabel('推重比')
    ax4.set_title('推重比随螺旋桨数量变化')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/payload_capacity_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_optimization_analysis():
    """创建性能优化分析图"""
    setup_matplotlib_for_plotting()
    
    # 螺旋桨直径 (英寸)
    diameters = np.linspace(6, 16, 50)
    
    # 转速 (RPM)
    rpm = np.linspace(3000, 12000, 50)
    D_mesh, RPM_mesh = np.meshgrid(diameters, rpm)
    
    # 参数设置
    CT = 0.08
    CP = 0.02
    rho = 1.225
    
    # 计算性能指标
    D_mesh_m = D_mesh * 0.0254  # 转换为米
    n_mesh = RPM_mesh / 60  # 转换为转/秒
    
    # 推力
    T = CT * rho * n_mesh**2 * D_mesh_m**4
    
    # 功率
    P = CP * rho * n_mesh**3 * D_mesh_m**5
    
    # 效率
    efficiency = (T * n_mesh * 2 * np.pi * D_mesh_m/2) / P
    efficiency = np.clip(efficiency, 0, 1)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 推力等高线图
    contour1 = ax1.contourf(D_mesh, RPM_mesh, T, levels=20, cmap='viridis')
    ax1.set_xlabel('螺旋桨直径 (英寸)')
    ax1.set_ylabel('转速 (RPM)')
    ax1.set_title('推力等高线图 (N)')
    plt.colorbar(contour1, ax=ax1)
    
    # 2. 功率等高线图
    contour2 = ax2.contourf(D_mesh, RPM_mesh, P, levels=20, cmap='plasma')
    ax2.set_xlabel('螺旋桨直径 (英寸)')
    ax2.set_ylabel('转速 (RPM)')
    ax2.set_title('功率等高线图 (W)')
    plt.colorbar(contour2, ax=ax2)
    
    # 3. 效率等高线图
    contour3 = ax3.contourf(D_mesh, RPM_mesh, efficiency*100, levels=20, cmap='RdYlGn')
    ax3.set_xlabel('螺旋桨直径 (英寸)')
    ax3.set_ylabel('转速 (RPM)')
    ax3.set_title('效率等高线图 (%)')
    plt.colorbar(contour3, ax=ax3)
    
    # 4. 推力-功率权衡分析
    ax4.scatter(P.flatten(), T.flatten(), c=efficiency.flatten(), 
               cmap='RdYlGn', alpha=0.6, s=10)
    ax4.set_xlabel('功率 (W)')
    ax4.set_ylabel('推力 (N)')
    ax4.set_title('推力-功率权衡分析')
    cbar = plt.colorbar(ax4.collections[0], ax=ax4)
    cbar.set_label('效率 (%)')
    
    plt.tight_layout()
    plt.savefig('/workspace/charts/optimization_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """主函数 - 创建所有分析图表"""
    print("开始创建多旋翼飞行器气动力学分析图表...")
    
    # 创建图表目录
    import os
    os.makedirs('/workspace/charts', exist_ok=True)
    
    # 创建各类分析图表
    print("1. 创建螺旋桨性能曲线...")
    create_propeller_performance_curves()
    
    print("2. 创建环境因素影响分析...")
    create_environmental_effects()
    
    print("3. 创建飞行性能分析...")
    create_flight_performance_analysis()
    
    print("4. 创建载荷能力分析...")
    create_payload_capacity_analysis()
    
    print("5. 创建性能优化分析...")
    create_optimization_analysis()
    
    print("所有分析图表创建完成！")

if __name__ == "__main__":
    main()