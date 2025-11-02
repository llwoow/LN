#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Bosch BMI088技术规格并生成详细报告
"""

import json
import re
from pathlib import Path

def analyze_bmi088_specs():
    """分析BMI088技术规格"""
    
    # 读取提取的PDF内容
    with open('/workspace/extract/bosch_bmi088_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 合并所有页面文本
    all_text = ""
    for page in data['pages']:
        all_text += page['text'] + "\n"
    
    # 分析技术规格
    specs = {
        "device_overview": {
            "name": "Bosch BMI088",
            "type": "6轴惯性测量单元(IMU)",
            "description": "结合3轴陀螺仪和3轴加速度计的高性能传感器",
            "package": "LGA 3.0mm x 4.5mm x 0.95mm"
        },
        
        "accelerometer_specs": extract_accelerometer_specs(all_text),
        "gyroscope_specs": extract_gyroscope_specs(all_text),
        "power_specs": extract_power_specs(all_text),
        "interface_specs": extract_interface_specs(all_text),
        "environmental_specs": extract_environmental_specs(all_text),
        "calibration_features": extract_calibration_features(all_text),
        "applications": extract_applications(all_text)
    }
    
    return specs

def extract_accelerometer_specs(text):
    """提取加速度计规格"""
    specs = {}
    
    # 量程
    range_match = re.search(r'Acceleration Range.*?gFS3g.*?±3 g.*?gFS6g.*?±6 g.*?gFS12g.*?±12 g.*?gFS24g.*?±24 g', text, re.DOTALL)
    if range_match:
        specs["量程"] = "±3g, ±6g, ±12g, ±24g (可选择)"
    
    # 灵敏度
    sens_matches = re.findall(r'S(\d+g).*?(\d+).*?LSB/g', text)
    if sens_matches:
        specs["灵敏度"] = {}
        for range_val, lsb in sens_matches:
            specs["灵敏度"][range_val] = f"{lsb} LSB/g"
    
    # 温度系数
    tcs_match = re.search(r'Sensitivity TCS.*?(\d+\.?\d*).*?%/K', text)
    if tcs_match:
        specs["灵敏度温度系数"] = f"{tcs_match.group(1)} %/K"
    
    # 零偏稳定性
    offset_match = re.search(r'Zero-g Offset.*?(\d+).*?mg', text)
    if offset_match:
        specs["零偏稳定性"] = f"{offset_match.group(1)} mg"
    
    # 噪声密度
    noise_match = re.search(r'Output Noise.*?(\d+).*?µg/√Hz', text)
    if noise_match:
        specs["噪声密度"] = f"{noise_match.group(1)} µg/√Hz"
    
    # 输出数据率
    odr_match = re.search(r'Output Data Rate.*?ODR.*?(\d+\.?\d*).*?(\d+\.?\d*).*?Hz', text)
    if odr_match:
        specs["输出数据率"] = f"{odr_match.group(1)} - {odr_match.group(2)} Hz"
    
    # 非线性度
    nl_match = re.search(r'Nonlinearity.*?(\d+\.?\d*).*?%FS', text)
    if nl_match:
        specs["非线性度"] = f"{nl_match.group(1)} %FS"
    
    return specs

def extract_gyroscope_specs(text):
    """提取陀螺仪规格"""
    specs = {}
    
    # 量程
    range_matches = re.findall(r'RFS(\d+).*?(\d+).*?°/s', text)
    if range_matches:
        ranges = [f"±{range_val}°/s" for range_val, _ in range_matches]
        specs["量程"] = ", ".join(ranges) + " (可选择)"
    
    # 灵敏度
    sens_matches = re.findall(r'Ta=25°C, RFS(\d+).*?(\d+\.?\d*).*?LSB/°/s', text)
    if sens_matches:
        specs["灵敏度"] = {}
        for range_val, lsb in sens_matches:
            specs["灵敏度"][f"±{range_val}°/s"] = f"{lsb} LSB/°/s"
    
    # 温度系数
    tcs_match = re.search(r'Sensitivity.*?TCS.*?(\d+\.?\d*).*?%/K', text)
    if tcs_match:
        specs["灵敏度温度系数"] = f"{tcs_match.group(1)} %/K"
    
    # 零偏稳定性
    offset_match = re.search(r'Offset.*?TCO.*?(\d+\.?\d*).*?°/s/K', text)
    if offset_match:
        specs["零偏温度系数"] = f"{offset_match.group(1)} °/s/K"
    
    # 噪声密度
    noise_match = re.search(r'Rate Noise.*?Density.*?(\d+\.?\d*).*?°/s/√Hz', text)
    if noise_match:
        specs["噪声密度"] = f"{noise_match.group(1)} °/s/√Hz"
    
    # 数据率
    odr_match = re.search(r'Data rate.*?(\d+).*?Hz.*?(\d+).*?Hz.*?(\d+).*?Hz', text)
    if odr_match:
        specs["数据率"] = f"{odr_match.group(1)}, {odr_match.group(2)}, {odr_match.group(3)} Hz"
    
    return specs

def extract_power_specs(text):
    """提取电源规格"""
    specs = {}
    
    # 主电源电压
    vdd_match = re.search(r'Supply Voltage VDD.*?(\d+\.?\d*).*?(\d+\.?\d*).*?V', text)
    if vdd_match:
        specs["主电源电压(VDD)"] = f"{vdd_match.group(1)} - {vdd_match.group(2)} V"
    
    # I/O电源电压
    vddio_match = re.search(r'Supply Voltage VDDIO.*?(\d+\.?\d*).*?(\d+\.?\d*).*?V', text)
    if vddio_match:
        specs["I/O电源电压(VDDIO)"] = f"{vddio_match.group(1)} - {vddio_match.group(2)} V"
    
    # 加速度计功耗
    accel_current_match = re.search(r'Total Supply.*?Current.*?Normal mode.*?(\d+).*?µA', text)
    if accel_current_match:
        specs["加速度计正常模式功耗"] = f"{accel_current_match.group(1)} µA"
    
    accel_suspend_match = re.search(r'Total Supply.*?Current.*?Suspend Mode.*?(\d+).*?µA', text)
    if accel_suspend_match:
        specs["加速度计挂起模式功耗"] = f"{accel_suspend_match.group(1)} µA"
    
    # 陀螺仪功耗
    gyro_normal_match = re.search(r'Supply Current.*?Normal Mode.*?(\d+\.?\d*).*?mA', text)
    if gyro_normal_match:
        specs["陀螺仪正常模式功耗"] = f"{gyro_normal_match.group(1)} mA"
    
    gyro_suspend_match = re.search(r'Supply Current.*?Suspend Mode.*?(\d+\.?\d*).*?µA', text)
    if gyro_suspend_match:
        specs["陀螺仪挂起模式功耗"] = f"{gyro_suspend_match.group(1)} µA"
    
    gyro_deep_match = re.search(r'Supply Current.*?Deep Suspend.*?(\d+\.?\d*).*?µA', text)
    if gyro_deep_match:
        specs["陀螺仪深度挂起模式功耗"] = f"<{gyro_deep_match.group(1)} µA"
    
    return specs

def extract_interface_specs(text):
    """提取接口规格"""
    specs = {}
    
    # 接口类型
    if "SPI" in text:
        specs["接口类型"] = "SPI, I²C"
    
    # SPI规格
    spi_freq_match = re.search(r'Clock Frequency.*?fSPI.*?(\d+).*?MHz', text)
    if spi_freq_match:
        specs["SPI时钟频率"] = f"最大 {spi_freq_match.group(1)} MHz"
    
    # I²C规格
    i2c_freq_match = re.search(r'Clock Frequency.*?fSCL.*?(\d+).*?kHz', text)
    if i2c_freq_match:
        specs["I²C时钟频率"] = f"最大 {i2c_freq_match.group(1)} kHz"
    
    # 协议选择
    ps_match = re.search(r'PS.*?´VDDIO´.*?selects.*?I²C.*?PS.*?´GND´.*?selects.*?SPI', text, re.DOTALL)
    if ps_match:
        specs["协议选择"] = "PS引脚：VDDIO=I²C, GND=SPI"
    
    return specs

def extract_environmental_specs(text):
    """提取环境规格"""
    specs = {}
    
    # 工作温度
    temp_match = re.search(r'Operating.*?Temperature.*?(-?\d+).*?(-?\d+).*?°C', text)
    if temp_match:
        specs["工作温度范围"] = f"{temp_match.group(1)}°C 到 {temp_match.group(2)}°C"
    
    # 存储温度
    storage_match = re.search(r'Passive Storage Temp\. Range.*?(-?\d+).*?(-?\d+).*?°C', text)
    if storage_match:
        specs["存储温度范围"] = f"{storage_match.group(1)}°C 到 {storage_match.group(2)}°C"
    
    # 机械冲击
    shock_match = re.search(r'Mechanical Shock.*?Duration.*?≤.*?(\d+).*?µs.*?(\d+).*?g', text)
    if shock_match:
        specs["机械冲击"] = f"≤{shock_match.group(1)}µs: {shock_match.group(2)}g"
    
    # ESD保护
    esd_match = re.search(r'ESD.*?HBM.*?(\d+).*?kV', text)
    if esd_match:
        specs["ESD保护(HBM)"] = f"{esd_match.group(1)} kV"
    
    return specs

def extract_calibration_features(text):
    """提取校准和补偿功能"""
    features = []
    
    # 自检功能
    if "self-test" in text.lower():
        features.append("内置自检功能")
    
    # 温度补偿
    if "temperature" in text.lower() and "compensation" in text.lower():
        features.append("温度补偿")
    
    # 工厂校准
    if "calibrated" in text.lower():
        features.append("工厂校准")
    
    # FIFO功能
    if "FIFO" in text:
        features.append("FIFO缓冲区")
    
    # 中断功能
    if "interrupt" in text.lower():
        features.append("中断控制")
    
    return features

def extract_applications(text):
    """提取应用信息"""
    apps = []
    
    # 无人机
    if "drone" in text.lower():
        apps.append("无人机")
    
    # 机器人
    if "robotics" in text.lower():
        apps.append("机器人")
    
    # 图像稳定
    if "stabilization" in text.lower():
        apps.append("图像/视频稳定")
    
    # 汽车
    if "automotive" in text.lower():
        apps.append("汽车应用")
    
    # 工业
    if "industrial" in text.lower():
        apps.append("工业应用")
    
    # 消费电子
    if "consumer" in text.lower():
        apps.append("消费电子")
    
    return apps

def generate_report(specs):
    """生成技术规格报告"""
    
    report = f"""# Bosch BMI088 6轴惯性测量单元技术规格报告

## 设备概述
- **器件名称**: {specs['device_overview']['name']}
- **器件类型**: {specs['device_overview']['type']}
- **描述**: {specs['device_overview']['description']}
- **封装**: {specs['device_overview']['package']}

## 1. 加速度计技术规格

"""
    
    for key, value in specs['accelerometer_specs'].items():
        if isinstance(value, dict):
            report += f"**{key}**:\n"
            for sub_key, sub_value in value.items():
                report += f"- {sub_key}: {sub_value}\n"
        else:
            report += f"**{key}**: {value}\n"
        report += "\n"
    
    report += "## 2. 陀螺仪技术规格\n\n"
    
    for key, value in specs['gyroscope_specs'].items():
        if isinstance(value, dict):
            report += f"**{key}**:\n"
            for sub_key, sub_value in value.items():
                report += f"- {sub_key}: {sub_value}\n"
        else:
            report += f"**{key}**: {value}\n"
        report += "\n"
    
    report += "## 3. 电源规格\n\n"
    
    for key, value in specs['power_specs'].items():
        report += f"**{key}**: {value}\n\n"
    
    report += "## 4. 接口规格\n\n"
    
    for key, value in specs['interface_specs'].items():
        report += f"**{key}**: {value}\n\n"
    
    report += "## 5. 环境规格\n\n"
    
    for key, value in specs['environmental_specs'].items():
        report += f"**{key}**: {value}\n\n"
    
    report += "## 6. 校准和补偿功能\n\n"
    
    for feature in specs['calibration_features']:
        report += f"- {feature}\n"
    
    report += "\n## 7. 推荐应用\n\n"
    
    for app in specs['applications']:
        report += f"- {app}\n"
    
    report += "\n## 8. 关键特性总结\n\n"
    report += "### 优势特性:\n"
    report += "- 高精度6轴惯性测量\n"
    report += "- 宽量程范围选择\n"
    report += "- 低功耗设计\n"
    report += "- 多种数字接口支持\n"
    report += "- 内置温度补偿\n"
    report += "- 工厂校准，即用即配\n"
    report += "- 强大的抗振动能力\n"
    report += "- 工业级温度范围\n\n"
    
    report += "### 适用场景:\n"
    report += "- 无人机飞行控制\n"
    report += "- 机器人导航\n"
    report += "- 图像稳定系统\n"
    report += "- 汽车安全系统\n"
    report += "- 工业运动控制\n"
    report += "- 消费电子产品\n\n"
    
    report += "---\n"
    report += "*报告生成时间: 2025-11-02 14:17:50*\n"
    report += "*数据来源: Bosch BMI088官方数据手册 v1.9*\n"
    
    return report

def main():
    """主函数"""
    print("开始分析Bosch BMI088技术规格...")
    
    # 分析技术规格
    specs = analyze_bmi088_specs()
    
    # 生成报告
    report = generate_report(specs)
    
    # 保存报告
    report_path = "/workspace/docs/bosch_bmi088_technical_report.md"
    Path("/workspace/docs").mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"技术规格报告已保存到: {report_path}")
    
    # 保存结构化数据
    specs_path = "/workspace/extract/bosch_bmi088_specs_structured.json"
    with open(specs_path, 'w', encoding='utf-8') as f:
        json.dump(specs, f, ensure_ascii=False, indent=2)
    
    print(f"结构化数据已保存到: {specs_path}")
    
    return specs

if __name__ == "__main__":
    main()