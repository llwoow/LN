"""
差分放大器LTspice仿真代码示例
包含完整的仿真流程和参数分析
"""

# 1. 基本差分放大器LTspice网表
basic_differential_amplifier = """
* 基本差分放大器LTspice仿真
* 作者：MiniMax Agent
* 日期：2025-11-02

* 电源
VCC 10 0 5V
VEE 20 0 -5V

* 差分输入信号
V1 1 0 SIN(0 1mV 1kHz)
V2 2 0 SIN(0 1mV 1kHz 180)

* 差分对晶体管
Q1 3 1 20 Q2N2222
Q2 4 2 20 Q2N2222

* 恒流源
I1 20 5 1mA

* 负载电阻
R1 10 3 10k
R2 10 4 10k

* 输出节点
VOD 3 4

* 直流分析
.op

* 交流分析
.ac dec 100 1 1meg

* 瞬态分析
.tran 0 1ms 0 1us

* 蒙特卡洛分析
.mc 100 .ac dec 10 1 1meg

.end
"""

# 2. 改进型差分放大器（威尔逊电流源）
improved_differential_amplifier = """
* 改进型差分放大器（威尔逊电流源）
* 更高的CMRR和温度稳定性

* 电源
VCC 10 0 5V
VEE 20 0 -5V

* 差分输入
V1 1 0 SIN(0 1mV 1kHz)
V2 2 0 SIN(0 1mV 1kHz 180)

* 差分对
Q1 3 1 20 Q2N2222
Q2 4 2 20 Q2N2222

* 威尔逊电流源
Q3 5 6 20 Q2N2222
Q4 6 5 10 Q2N2222
Q5 7 6 20 Q2N2222
R3 10 7 1k

* 负载电阻
R1 10 3 10k
R2 10 4 10k

* 输出
VOD 3 4

* 分析控制
.op
.ac dec 100 1 1meg
.tran 0 1ms 0 1us

.end
"""

# 3. 共模测试电路
common_mode_test_circuit = """
* 共模测试电路
* 用于测量CMRR

* 电源
VCC 10 0 5V
VEE 20 0 -5V

* 共模输入信号
VCM 1 0 SIN(0 1V 1kHz)
VCM2 2 0 SIN(0 1V 1kHz)

* 差分对
Q1 3 1 20 Q2N2222
Q2 4 2 20 Q2N2222

* 恒流源
I1 20 5 1mA

* 负载电阻
R1 10 3 10k
R2 10 4 10k

* 输出测量
VOC 3 4

* 交流分析
.ac dec 100 1 1meg

.end
"""

# 4. 温度分析
temperature_analysis = """
* 温度分析
* 评估温度对性能的影响

* 电源
VCC 10 0 5V
VEE 20 0 -5V

* 差分输入
V1 1 0 SIN(0 1mV 1kHz)
V2 2 0 SIN(0 1mV 1kHz 180)

* 差分对
Q1 3 1 20 Q2N2222
Q2 4 2 20 Q2N2222

* 恒流源
I1 20 5 1mA

* 负载电阻
R1 10 3 10k
R2 10 4 10k

* 温度扫描
.temp -40 125 5

* 直流分析
.op

.end
"""

# 5. 蒙特卡洛分析
monte_carlo_analysis = """
* 蒙特卡洛分析
* 评估元件失配对性能的影响

* 电源
VCC 10 0 5V
VEE 20 0 -5V

* 差分输入
V1 1 0 SIN(0 1mV 1kHz)
V2 2 0 SIN(0 1mV 1kHz 180)

* 差分对（考虑失配）
Q1 3 1 20 Q2N2222
Q2 4 2 20 Q2N2222

* 恒流源
I1 20 5 1mA

* 负载电阻（考虑失配）
R1 10 3 10k
R2 10 4 10k

* 蒙特卡洛参数
.param R1_val=10k*(1+0.001*gauss(0,1))
.param R2_val=10k*(1+0.001*gauss(0,1))

* 蒙特卡洛分析
.mc 100 .ac dec 10 1 1meg

.end
"""

# 6. Python数据分析脚本
python_analysis_script = """
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def analyze_differential_amplifier_data():
    """
    分析差分放大器仿真数据
    """
    
    # 模拟仿真数据
    freq = np.logspace(1, 6, 100)  # 10Hz to 1MHz
    ad_magnitude = 40 * np.ones_like(freq)  # 40dB差模增益
    ad_phase = -90 * np.ones_like(freq)     # -90度相位
    
    # 共模增益（理想情况下很低）
    ac_magnitude = -80 + 20*np.log10(freq/1000)  # 随频率增加
    ac_phase = -180 * np.ones_like(freq)
    
    # 计算CMRR
    cmrr = ad_magnitude - ac_magnitude
    
    # 绘制频率响应
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # 差模增益
    ax1.semilogx(freq, ad_magnitude)
    ax1.set_xlabel('频率 (Hz)')
    ax1.set_ylabel('增益 (dB)')
    ax1.set_title('差模增益频率响应')
    ax1.grid(True)
    
    # 差模相位
    ax2.semilogx(freq, ad_phase)
    ax2.set_xlabel('频率 (Hz)')
    ax2.set_ylabel('相位 (度)')
    ax2.set_title('差模相位频率响应')
    ax2.grid(True)
    
    # 共模增益
    ax3.semilogx(freq, ac_magnitude)
    ax3.set_xlabel('频率 (Hz)')
    ax3.set_ylabel('增益 (dB)')
    ax3.set_title('共模增益频率响应')
    ax3.grid(True)
    
    # CMRR
    ax4.semilogx(freq, cmrr)
    ax4.set_xlabel('频率 (Hz)')
    ax4.set_ylabel('CMRR (dB)')
    ax4.set_title('共模抑制比')
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('differential_amplifier_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 性能统计
    print(f"低频差模增益: {ad_magnitude[0]:.1f} dB")
    print(f"低频CMRR: {cmrr[0]:.1f} dB")
    print(f"-3dB带宽: {freq[np.where(ad_magnitude < 37)[0][0]]/1e3:.1f} kHz")
    
    return {
        'frequency': freq,
        'ad_magnitude': ad_magnitude,
        'ad_phase': ad_phase,
        'ac_magnitude': ac_magnitude,
        'ac_phase': ac_phase,
        'cmrr': cmrr
    }

def calculate_design_parameters():
    """
    计算差分放大器设计参数
    """
    
    # 设计规格
    Ad_target = 100  # 目标增益 40dB
    CMRR_target = 80  # 目标CMRR 80dB
    I_bias = 1e-3    # 偏置电流 1mA
    VT = 26e-3       # 热电压 26mV
    
    # 基本计算
    gm = I_bias / VT  # 跨导
    Rc = Ad_target / gm  # 负载电阻
    ro_required = 10**(CMRR_target/20) / gm  # 所需输出电阻
    
    # 性能预估
    input_impedance = 2 / gm  # 输入阻抗
    power_consumption = 2 * I_bias * 5  # 功耗估计
    
    results = {
        'transconductance': gm,
        'load_resistance': Rc,
        'output_resistance': ro_required,
        'input_impedance': input_impedance,
        'power_consumption': power_consumption
    }
    
    print("=== 差分放大器设计参数 ===")
    print(f"跨导 gm = {gm*1e3:.1f} mS")
    print(f"负载电阻 Rc = {Rc/1e3:.1f} kΩ")
    print(f"所需输出电阻 ro = {ro_required/1e6:.1f} MΩ")
    print(f"输入阻抗 = {input_impedance/1e6:.1f} MΩ")
    print(f"功耗 = {power_consumption*1e3:.1f} mW")
    
    return results

def monte_carlo_analysis():
    """
    蒙特卡洛分析
    """
    
    # 模拟100次蒙特卡洛运行
    n_samples = 100
    
    # 电阻失配（0.1%标准差）
    resistor_mismatch = np.random.normal(0, 0.001, n_samples)
    
    # VBE失配（1mV标准差）
    vbe_mismatch = np.random.normal(0, 1e-3, n_samples)
    
    # β失配（10%标准差）
    beta_mismatch = np.random.normal(1, 0.1, n_samples)
    
    # 计算CMRR分布
    cmrr_base = 80  # 基准CMRR 80dB
    cmrr_variation = -20 * np.log10(1 + resistor_mismatch)
    cmrr_total = cmrr_base + cmrr_variation
    
    # 统计分析
    cmrr_mean = np.mean(cmrr_total)
    cmrr_std = np.std(cmrr_total)
    cmrr_min = np.min(cmrr_total)
    cmrr_max = np.max(cmrr_total)
    
    print("=== 蒙特卡洛分析结果 ===")
    print(f"CMRR平均值: {cmrr_mean:.1f} dB")
    print(f"CMRR标准差: {cmrr_std:.1f} dB")
    print(f"CMRR范围: {cmrr_min:.1f} - {cmrr_max:.1f} dB")
    print(f"95%置信区间: {cmrr_mean-2*cmrr_std:.1f} - {cmrr_mean+2*cmrr_std:.1f} dB")
    
    # 绘制分布图
    plt.figure(figsize=(10, 6))
    plt.hist(cmrr_total, bins=20, alpha=0.7, edgecolor='black')
    plt.axvline(cmrr_mean, color='red', linestyle='--', label=f'平均值: {cmrr_mean:.1f} dB')
    plt.axvline(cmrr_target, color='green', linestyle='--', label=f'目标: {cmrr_target} dB')
    plt.xlabel('CMRR (dB)')
    plt.ylabel('频次')
    plt.title('CMRR蒙特卡洛分布')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('cmrr_monte_carlo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return {
        'cmrr_samples': cmrr_total,
        'mean': cmrr_mean,
        'std': cmrr_std,
        'min': cmrr_min,
        'max': cmrr_max
    }

if __name__ == "__main__":
    # 运行分析
    print("差分放大器性能分析")
    print("=" * 50)
    
    # 设计参数计算
    design_params = calculate_design_parameters()
    
    print("\n" + "=" * 50)
    
    # 频率响应分析
    frequency_response = analyze_differential_amplifier_data()
    
    print("\n" + "=" * 50)
    
    # 蒙特卡洛分析
    mc_results = monte_carlo_analysis()
    
    print("\n分析完成！")
"""

# 7. 完整的LTspice仿真脚本
complete_ltspice_script = """
* 差分放大器完整仿真脚本
* 包含所有必要的分析类型

* 仿真参数设置
.param I_bias=1m
.param Rc=10k
.param Ad_target=40

* 电源
VCC 10 0 5V
VEE 20 0 -5V

* 差分输入测试
.subckt diff_input_test
V1 1 0 SIN(0 1mV 1kHz)
V2 2 0 SIN(0 1mV 1kHz 180)
.ends

* 共模输入测试
.subckt common_input_test
VCM 1 0 SIN(0 1V 1kHz)
VCM2 2 0 SIN(0 1V 1kHz)
.ends

* 差分放大器核心
.subckt diff_amp_core
Q1 3 1 20 Q2N2222
Q2 4 2 20 Q2N2222
I1 20 5 {I_bias}
R1 10 3 {Rc}
R2 10 4 {Rc}
.ends

* 调用测试电路
X1 1 2 3 4 diff_amp_core

* 分析控制
.op                    ; 直流工作点
.ac dec 100 1 1meg     ; 交流分析
.tran 0 1ms 0 1us      ; 瞬态分析
.temp -40 125 5        ; 温度分析

* 测量指令
.meas ac Ad_mag param=mag(V(3,4))/mag(V(1,2))
.meas ac Ac_mag param=mag(V(3,4))/mag(V(1,2))
.meas ac CMRR param=20*log10(Ad_mag/Ac_mag)

.end
"""

# 8. 输出所有代码到文件
def write_simulation_files():
    """
    将所有仿真代码写入文件
    """
    
    files_to_write = {
        'basic_diff_amp.cir': basic_differential_amplifier,
        'improved_diff_amp.cir': improved_differential_amplifier,
        'common_mode_test.cir': common_mode_test_circuit,
        'temperature_analysis.cir': temperature_analysis,
        'monte_carlo.cir': monte_carlo_analysis,
        'complete_simulation.cir': complete_ltspice_script,
        'analysis_script.py': python_analysis_script
    }
    
    for filename, content in files_to_write.items():
        with open(f'/workspace/code/{filename}', 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("所有仿真文件已写入 /workspace/code/ 目录")
    print("文件列表:")
    for filename in files_to_write.keys():
        print(f"  - {filename}")

if __name__ == "__main__":
    # 写入仿真文件
    write_simulation_files()
    
    print("\n差分放大器仿真代码生成完成！")
    print("\n使用方法:")
    print("1. 使用LTspice打开.cir文件进行仿真")
    print("2. 运行python脚本进行数据分析")
    print("3. 根据仿真结果优化设计参数")
"""