#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取u-blox ZED-F9P数据手册PDF内容的脚本
"""

import pdfplumber
import json
import re
from pathlib import Path

def extract_zed_f9p_content(pdf_path):
    """提取ZED-F9P PDF内容并整理为结构化数据"""
    
    content = {
        "title": "u-blox ZED-F9P-04B Data Sheet",
        "url": "https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf",
        "pages": [],
        "technical_specs": {
            "rtk_positioning": {},
            "satellite_systems": {},
            "power_consumption": {},
            "interfaces": {},
            "electrical_characteristics": {},
            "operating_conditions": {},
            "environmental_specifications": {},
            "rtk_performance": {},
            "configuration": {},
            "applications": {},
            "integration_recommendations": {}
        },
        "key_features": [],
        "performance_parameters": [],
        "integration_guidelines": []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"PDF总页数: {len(pdf.pages)}")
            
            # 提取所有页面的文本
            all_text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    content["pages"].append({
                        "page_number": i + 1,
                        "text": page_text[:800] + "..." if len(page_text) > 800 else page_text
                    })
                    all_text += f"\n=== 第{i+1}页 ===\n{page_text}\n"
            
            # 保存完整文本
            Path("/workspace/extract").mkdir(exist_ok=True)
            with open('/workspace/extract/zed_f9p_full_content.txt', 'w', encoding='utf-8') as f:
                f.write(all_text)
            
            # 提取技术规格
            extract_rtk_specs(all_text, content)
            
            # 提取关键特性
            extract_key_features(all_text, content)
            
            # 提取性能参数
            extract_performance_params(all_text, content)
            
            # 提取应用信息
            extract_applications(all_text, content)
            
            # 提取集成指南
            extract_integration_guidelines(all_text, content)
            
    except Exception as e:
        print(f"提取PDF内容时出错: {e}")
        content["error"] = str(e)
    
    return content

def extract_rtk_specs(text, content):
    """提取RTK定位相关规格"""
    
    # RTK定位精度
    rtk_accuracy_patterns = [
        r"RTK.*?horizontal.*?(\d+\.?\d*)\s*(mm|cm|m)",
        r"horizontal.*?accuracy.*?(\d+\.?\d*)\s*(mm|cm|m)",
        r"positioning.*?accuracy.*?(\d+\.?\d*)\s*(mm|cm|m)",
        r"(\d+\.?\d*)\s*(mm|cm|m).*?horizontal",
        r"(\d+\.?\d*)\s*(mm|cm|m).*?positioning"
    ]
    
    for pattern in rtk_accuracy_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["rtk_positioning"]["horizontal_accuracy"] = f"{match.group(1)} {match.group(2)}"
            break
    
    # 垂直精度
    vertical_patterns = [
        r"RTK.*?vertical.*?(\d+\.?\d*)\s*(mm|cm|m)",
        r"vertical.*?accuracy.*?(\d+\.?\d*)\s*(mm|cm|m)",
        r"(\d+\.?\d*)\s*(mm|cm|m).*?vertical"
    ]
    
    for pattern in vertical_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["rtk_positioning"]["vertical_accuracy"] = f"{match.group(1)} {match.group(2)}"
            break
    
    # 卫星系统支持
    satellite_systems = {
        "GPS": ["L1", "L2", "L5"],
        "GLONASS": ["L1", "L2"],
        "Galileo": ["E1", "E5a", "E5b"],
        "BeiDou": ["B1", "B2"],
        "QZSS": ["L1", "L2", "L5", "L6"],
        "SBAS": ["L1", "L5"]
    }
    
    for system, frequencies in satellite_systems.items():
        for freq in frequencies:
            if re.search(f"{system}.*{freq}", text, re.IGNORECASE) or re.search(f"{freq}.*{system}", text, re.IGNORECASE):
                if system not in content["technical_specs"]["satellite_systems"]:
                    content["technical_specs"]["satellite_systems"][system] = []
                if freq not in content["technical_specs"]["satellite_systems"][system]:
                    content["technical_specs"]["satellite_systems"][system].append(freq)
    
    # 功耗信息
    power_patterns = [
        r"power.*?consumption.*?(\d+\.?\d*)\s*(mA|mW)",
        r"(\d+\.?\d*)\s*(mA|mW).*?power",
        r"current.*?(\d+\.?\d*)\s*(mA|mA@3\.3V)",
        r"supply.*?current.*?(\d+\.?\d*)\s*mA"
    ]
    
    for pattern in power_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["power_consumption"]["consumption"] = f"{match.group(1)} {match.group(2)}"
            break
    
    # 电源电压
    voltage_patterns = [
        r"supply.*?voltage.*?(\d+\.?\d*)\s*V.*?(\d+\.?\d*)\s*V",
        r"operating.*?voltage.*?(\d+\.?\d*)\s*V.*?(\d+\.?\d*)\s*V",
        r"voltage.*?(\d+\.?\d*)\s*V.*?(\d+\.?\d*)\s*V",
        r"(\d+\.?\d*)\s*V.*?supply"
    ]
    
    for pattern in voltage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["electrical_characteristics"]["supply_voltage"] = f"{match.group(1)}V to {match.group(2)}V"
            break
    
    # 接口类型
    interfaces = {}
    
    # UART接口
    uart_match = re.search(r"UART.*?(\d+).*?(\d+).*?(\d+).*?(\d+)", text, re.IGNORECASE)
    if uart_match:
        interfaces["UART"] = f"{uart_match.group(1)}-{uart_match.group(2)}-{uart_match.group(3)}-{uart_match.group(4)}"
    
    # USB接口
    usb_match = re.search(r"USB.*?(2\.0|3\.0|3\.1)", text, re.IGNORECASE)
    if usb_match:
        interfaces["USB"] = usb_match.group(1)
    
    # SPI接口
    if re.search(r"SPI", text, re.IGNORECASE):
        interfaces["SPI"] = "Supported"
    
    # I2C接口
    if re.search(r"I2C", text, re.IGNORECASE):
        interfaces["I2C"] = "Supported"
    
    # GPIO
    gpio_match = re.search(r"GPIO.*?(\d+)", text, re.IGNORECASE)
    if gpio_match:
        interfaces["GPIO"] = f"{gpio_match.group(1)} pins"
    
    content["technical_specs"]["interfaces"] = interfaces
    
    # 工作温度范围
    temp_patterns = [
        r"operating.*?temperature.*?(-?\d+).*?°C.*?(-?\d+).*?°C",
        r"temperature.*?range.*?(-?\d+).*?°C.*?(-?\d+).*?°C",
        r"(-?\d+).*?°C.*?(-?\d+).*?°C.*?temperature"
    ]
    
    for pattern in temp_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["operating_conditions"]["temperature_range"] = f"{match.group(1)}°C to {match.group(2)}°C"
            break
    
    # 存储温度
    storage_patterns = [
        r"storage.*?temperature.*?(-?\d+).*?°C.*?(-?\d+).*?°C",
        r"(-?\d+).*?°C.*?(-?\d+).*?°C.*?storage"
    ]
    
    for pattern in storage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["environmental_specifications"]["storage_temperature"] = f"{match.group(1)}°C to {match.group(2)}°C"
            break

def extract_key_features(text, content):
    """提取关键特性"""
    
    feature_keywords = [
        "multi-band", "multi-constellation", "RTK", "real-time kinematic",
        "high precision", "centimeter level", "multi-frequency",
        "advanced jamming mitigation", "spoofing detection", "GNSS",
        "precision agriculture", "surveying", "robotics", "UAV"
    ]
    
    lines = text.split('\n')
    for line in lines:
        line_clean = line.strip()
        if len(line_clean) > 15:  # 过滤太短的行
            for keyword in feature_keywords:
                if keyword.lower() in line_clean.lower():
                    content["key_features"].append(line_clean)
                    break
    
    # 去重并限制数量
    content["key_features"] = list(set(content["key_features"]))[:15]

def extract_performance_params(text, content):
    """提取性能参数"""
    
    param_patterns = [
        r"time.*?to.*?first.*?fix.*?(\d+).*?(s|sec|seconds)",
        r"TTFF.*?(\d+).*?(s|sec|seconds)",
        r"sensitivity.*?(\d+).*?(dBm|dB)",
        r"update.*?rate.*?(\d+).*?(Hz|hz)",
        r"(\d+).*?(Hz|hz).*?update"
    ]
    
    for pattern in param_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["performance_parameters"].append(f"{match.group(1)} {match.group(2)}")
    
    # RTK性能参数
    rtk_params = [
        r"convergence.*?time.*?(\d+).*?(s|sec|minutes)",
        r"(\d+).*?(s|sec|minutes).*?convergence",
        r"initialization.*?time.*?(\d+).*?(s|sec|minutes)"
    ]
    
    for pattern in rtk_params:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content["technical_specs"]["rtk_performance"]["convergence_time"] = f"{match.group(1)} {match.group(2)}"

def extract_applications(text, content):
    """提取应用信息"""
    
    app_keywords = [
        "precision agriculture", "surveying", "mapping", "robotics",
        "UAV", "drone", "autonomous vehicle", "GIS", "geodetic",
        "construction", "mining", "marine", "aviation"
    ]
    
    lines = text.split('\n')
    for line in lines:
        line_clean = line.strip()
        if len(line_clean) > 15:
            for keyword in app_keywords:
                if keyword.lower() in line_clean.lower():
                    content["technical_specs"]["applications"][keyword] = line_clean
                    break

def extract_integration_guidelines(text, content):
    """提取集成建议"""
    
    integration_keywords = [
        "antenna", "ground plane", "cable", "connector",
        "layout", "PCB", "design", "integration",
        "calibration", "configuration"
    ]
    
    lines = text.split('\n')
    for line in lines:
        line_clean = line.strip()
        if len(line_clean) > 20:
            for keyword in integration_keywords:
                if keyword.lower() in line_clean.lower():
                    content["integration_guidelines"].append(line_clean)
                    break
    
    # 去重并限制数量
    content["integration_guidelines"] = list(set(content["integration_guidelines"]))[:10]

def main():
    """主函数"""
    pdf_path = "/workspace/downloads/ZED-F9P-04B_DataSheet.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print("开始提取ZED-F9P PDF内容...")
    content = extract_zed_f9p_content(pdf_path)
    
    # 保存提取的内容
    output_path = "/workspace/extract/zed_f9p_specifications.json"
    Path("/workspace/extract").mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"内容已保存到: {output_path}")
    
    # 打印关键信息摘要
    print("\n=== ZED-F9P 技术规格摘要 ===")
    print(f"PDF总页数: {len(content['pages'])}")
    print(f"关键特性: {len(content['key_features'])} 个")
    print(f"性能参数: {len(content['performance_parameters'])} 个")
    print(f"应用领域: {len(content['technical_specs']['applications'])} 个")
    print(f"集成建议: {len(content['integration_guidelines'])} 个")
    
    # 打印主要技术规格
    print("\n=== 主要技术规格 ===")
    specs = content["technical_specs"]
    
    if specs["rtk_positioning"]:
        print("RTK定位精度:")
        for key, value in specs["rtk_positioning"].items():
            print(f"  {key}: {value}")
    
    if specs["satellite_systems"]:
        print("支持的卫星系统:")
        for system, freqs in specs["satellite_systems"].items():
            print(f"  {system}: {', '.join(freqs)}")
    
    if specs["power_consumption"]:
        print("功耗:")
        for key, value in specs["power_consumption"].items():
            print(f"  {key}: {value}")
    
    if specs["interfaces"]:
        print("接口类型:")
        for interface, desc in specs["interfaces"].items():
            print(f"  {interface}: {desc}")
    
    if specs["operating_conditions"]:
        print("工作条件:")
        for key, value in specs["operating_conditions"].items():
            print(f"  {key}: {value}")
    
    return content

if __name__ == "__main__":
    main()