#!/usr/bin/env python3
"""
提取Sony IMX477数据手册PDF的完整技术规格信息
"""

import pdfplumber
import json
import re
from pathlib import Path

def extract_imx477_specs(pdf_path):
    """提取IMX477数据手册的技术规格"""
    
    specs = {
        "基本信息": {},
        "图像规格": {},
        "电气特性": {},
        "性能参数": {},
        "接口类型": {},
        "应用场景": {},
        "对比信息": {}
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            print(f"提取的总文本长度: {len(full_text)} 字符")
            
            # 提取基本信息
            extract_basic_info(full_text, specs)
            
            # 提取图像规格
            extract_image_specs(full_text, specs)
            
            # 提取电气特性
            extract_electrical_specs(full_text, specs)
            
            # 提取性能参数
            extract_performance_specs(full_text, specs)
            
            # 提取接口类型
            extract_interface_info(full_text, specs)
            
            # 提取应用场景
            extract_applications(full_text, specs)
            
            # 提取对比信息
            extract_comparison_info(full_text, specs)
            
            # 保存完整文本用于分析
            with open('/workspace/data/imx477_full_text.txt', 'w', encoding='utf-8') as f:
                f.write(full_text)
                
    except Exception as e:
        print(f"提取PDF内容时出错: {e}")
        
    return specs

def extract_basic_info(text, specs):
    """提取基本信息"""
    patterns = {
        "产品型号": r"IMX477",
        "制造商": r"(Sony|索尼)",
        "传感器类型": r"(CMOS|图像传感器)",
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["基本信息"][key] = match.group(0)

def extract_image_specs(text, specs):
    """提取图像规格"""
    # 分辨率
    resolution_patterns = [
        r"(\d+)\s*[x×]\s*(\d+)\s*像素",
        r"(\d+)\s*[x×]\s*(\d+)\s*pixels?",
        r"(\d+)\s*[x×]\s*(\d+)\s*resolution"
    ]
    
    for pattern in resolution_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["图像规格"]["分辨率"] = f"{match.group(1)} x {match.group(2)} 像素"
            break
    
    # 像素尺寸
    pixel_size_patterns = [
        r"(\d+\.?\d*)\s*(μm|micron|微米)\s*像素",
        r"(\d+\.?\d*)\s*(μm|micron|微米)\s*pixel"
    ]
    
    for pattern in pixel_size_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["图像规格"]["像素尺寸"] = f"{match.group(1)} {match.group(2)}"
            break
    
    # 传感器尺寸
    sensor_size_patterns = [
        r"(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)\s*(mm|毫米)",
        r"(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)\s*mm"
    ]
    
    for pattern in sensor_size_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["图像规格"]["传感器尺寸"] = f"{match.group(1)} x {match.group(2)} {match.group(3)}"
            break

def extract_electrical_specs(text, specs):
    """提取电气特性"""
    # 供电电压
    voltage_patterns = [
        r"(\d+\.?\d*)\s*[vV]",
        r"(\d+\.?\d*)\s*V\s*供电",
        r"(\d+\.?\d*)\s*V\s*supply"
    ]
    
    for pattern in voltage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["电气特性"]["供电电压"] = match.group(0)
            break
    
    # 功耗
    power_patterns = [
        r"(\d+\.?\d*)\s*(mW|W|毫瓦|瓦)",
        r"功耗.*?(\d+\.?\d*)\s*(mW|W|毫瓦|瓦)",
        r"power.*?(\d+\.?\d*)\s*(mW|W)"
    ]
    
    for pattern in power_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["电气特性"]["功耗"] = match.group(0)
            break

def extract_performance_specs(text, specs):
    """提取性能参数"""
    # 帧率
    framerate_patterns = [
        r"(\d+\.?\d*)\s*(fps|帧/秒)",
        r"(\d+\.?\d*)\s*fps"
    ]
    
    for pattern in framerate_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["性能参数"]["帧率"] = match.group(0)
            break
    
    # 曝光时间
    exposure_patterns = [
        r"曝光.*?(\d+\.?\d*)\s*(ms|μs|毫秒|微秒)",
        r"exposure.*?(\d+\.?\d*)\s*(ms|μs)"
    ]
    
    for pattern in exposure_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["性能参数"]["曝光时间"] = match.group(0)
            break
    
    # 灵敏度
    sensitivity_patterns = [
        r"灵敏度.*?(\d+\.?\d*)\s*(V/lx·s|mV/lux·sec)",
        r"sensitivity.*?(\d+\.?\d*)\s*(V/lx·s|mV/lux·sec)"
    ]
    
    for pattern in sensitivity_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            specs["性能参数"]["灵敏度"] = match.group(0)
            break

def extract_interface_info(text, specs):
    """提取接口类型"""
    interface_patterns = [
        r"MIPI",
        r"CSI",
        r"Serial",
        r"Parallel",
        r"接口",
        r"interface"
    ]
    
    interfaces = []
    for pattern in interface_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            interfaces.append(pattern)
    
    if interfaces:
        specs["接口类型"]["可用接口"] = list(set(interfaces))

def extract_applications(text, specs):
    """提取应用场景"""
    app_keywords = [
        "数码相机", "digital camera", 
        "监控", "surveillance",
        "机器视觉", "machine vision",
        "汽车", "automotive",
        "工业", "industrial",
        "医疗", "medical"
    ]
    
    applications = []
    for keyword in app_keywords:
        if re.search(keyword, text, re.IGNORECASE):
            applications.append(keyword)
    
    if applications:
        specs["应用场景"]["相关应用"] = list(set(applications))

def extract_comparison_info(text, specs):
    """提取对比信息"""
    comparison_keywords = [
        "IMX586", "OV9281", 
        "对比", "comparison",
        "优势", "advantage",
        "性能", "performance"
    ]
    
    comparisons = []
    for keyword in comparison_keywords:
        if re.search(keyword, text, re.IGNORECASE):
            comparisons.append(keyword)
    
    if comparisons:
        specs["对比信息"]["提及的传感器"] = list(set(comparisons))

if __name__ == "__main__":
    # 创建数据目录
    Path("/workspace/data").mkdir(exist_ok=True)
    
    pdf_path = "/workspace/downloads/IMX477-DS.pdf"
    
    print("开始提取Sony IMX477数据手册技术规格...")
    specs = extract_imx477_specs(pdf_path)
    
    # 保存提取的规格
    with open('/workspace/data/imx477_specs.json', 'w', encoding='utf-8') as f:
        json.dump(specs, f, ensure_ascii=False, indent=2)
    
    print("技术规格提取完成！")
    print("\n提取的规格摘要:")
    for category, items in specs.items():
        if items:
            print(f"\n{category}:")
            for key, value in items.items():
                print(f"  {key}: {value}")