#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF内容提取脚本 - 用于提取OV9281数据手册的技术规格信息
"""

import pdfplumber
import json
import re

def extract_pdf_content(pdf_path):
    """提取PDF文本内容"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            pages_info = []
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text += f"\n=== 第 {i+1} 页 ===\n"
                    all_text += page_text
                    pages_info.append({
                        'page_number': i+1,
                        'text': page_text
                    })
                
                # 提取表格数据
                tables = page.extract_tables()
                if tables:
                    all_text += f"\n=== 第 {i+1} 页 表格 ===\n"
                    for j, table in enumerate(tables):
                        all_text += f"表格 {j+1}:\n"
                        for row in table:
                            if row:
                                all_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
                        all_text += "\n"
            
            return all_text, pages_info
    except Exception as e:
        print(f"提取PDF内容时出错: {e}")
        return None, None

def extract_key_specs(text):
    """提取关键技术规格"""
    specs = {
        "resolution": [],
        "pixel_size": [],
        "sensor_size": [],
        "global_shutter": [],
        "frame_rate": [],
        "power_consumption": [],
        "interface": [],
        "voltage": [],
        "temperature": [],
        "applications": [],
        "advantages": []
    }
    
    # 搜索分辨率信息
    resolution_patterns = [
        r'(\d+)\s*[x×]\s*(\d+)',
        r'Resolution[:\s]*(\d+)\s*[x×]\s*(\d+)',
        r'(\d+)\s*[x×]\s*(\d+)\s*pixel'
    ]
    
    for pattern in resolution_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        specs["resolution"].extend(matches)
    
    # 搜索像素尺寸
    pixel_patterns = [
        r'(\d+\.?\d*)\s*[µu]m\s*[x×]\s*(\d+\.?\d*)\s*[µu]m',
        r'Pixel\s*Size[:\s]*(\d+\.?\d*)\s*[µu]m',
        r'Pixel\s*Size[:\s]*(\d+\.?\d*)\s*[µu]m\s*[x×]\s*(\d+\.?\d*)\s*[µu]m'
    ]
    
    for pattern in pixel_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        specs["pixel_size"].extend(matches)
    
    # 搜索帧率信息
    fps_patterns = [
        r'(\d+)\s*fps',
        r'Frame\s*Rate[:\s]*(\d+)',
        r'Up\s*to\s*(\d+)\s*fps'
    ]
    
    for pattern in fps_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        specs["frame_rate"].extend(matches)
    
    # 搜索功耗信息
    power_patterns = [
        r'(\d+\.?\d*)\s*mW',
        r'Power\s*Consumption[:\s]*(\d+\.?\d*)\s*mW',
        r'(\d+\.?\d*)\s*µW'
    ]
    
    for pattern in power_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        specs["power_consumption"].extend(matches)
    
    # 搜索接口信息
    interface_keywords = ['MIPI', 'CSI', 'DVP', 'I2C', 'SCCB', 'LVDS']
    for keyword in interface_keywords:
        if keyword.lower() in text.lower():
            specs["interface"].append(keyword)
    
    # 搜索电压信息
    voltage_patterns = [
        r'(\d+\.?\d*)\s*V',
        r'(\d+\.?\d*)\s*volts?'
    ]
    
    for pattern in voltage_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        specs["voltage"].extend(matches)
    
    # 搜索温度信息
    temp_patterns = [
        r'(-?\d+)\s*[°cC]\s*to\s*(-?\d+)\s*[°cC]',
        r'Operating\s*Temperature[:\s]*(-?\d+)\s*[°cC]\s*to\s*(-?\d+)\s*[°cC]'
    ]
    
    for pattern in temp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        specs["temperature"].extend(matches)
    
    # 搜索应用信息
    application_keywords = ['machine vision', 'AR', 'VR', 'robotics', 'drone', 'barcode', 'tracking', 'automotive', 'industrial']
    for keyword in application_keywords:
        if keyword.lower() in text.lower():
            specs["applications"].append(keyword)
    
    # 搜索优势特性
    advantage_keywords = ['global shutter', 'low power', 'high speed', 'high sensitivity', 'wide dynamic range', 'compact']
    for keyword in advantage_keywords:
        if keyword.lower() in text.lower():
            specs["advantages"].append(keyword)
    
    return specs

def main():
    pdf_path = "/workspace/ov9281_datasheet.pdf"
    
    print("正在提取OV9281数据手册内容...")
    content, pages_info = extract_pdf_content(pdf_path)
    
    if content:
        # 保存完整内容
        with open("/workspace/extract/ov9281_full_content.txt", "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"完整内容已保存到: /workspace/extract/ov9281_full_content.txt")
        
        # 提取关键规格
        specs = extract_key_specs(content)
        
        # 保存规格信息
        with open("/workspace/extract/ov9281_specs.json", "w", encoding="utf-8") as f:
            json.dump(specs, f, ensure_ascii=False, indent=2)
        
        print(f"关键规格已保存到: /workspace/extract/ov9281_specs.json")
        
        # 输出关键信息摘要
        print("\n=== OV9281 关键技术规格摘要 ===")
        print(f"分辨率: {specs['resolution']}")
        print(f"像素尺寸: {specs['pixel_size']}")
        print(f"帧率: {specs['frame_rate']}")
        print(f"功耗: {specs['power_consumption']}")
        print(f"接口: {specs['interface']}")
        print(f"电压: {specs['voltage']}")
        print(f"工作温度: {specs['temperature']}")
        print(f"应用领域: {specs['applications']}")
        print(f"核心优势: {specs['advantages']}")
        
    else:
        print("无法提取PDF内容")

if __name__ == "__main__":
    main()