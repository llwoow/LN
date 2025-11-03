#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取TI噪声分析PDF文档中的噪声类型信息
重点关注：热噪声、闪烁噪声、散粒噪声、爆裂噪声、产生-复合噪声
"""

import PyPDF2
import pdfplumber
import json
import re
from typing import List, Dict, Any

def extract_pdf_content(pdf_path: str) -> str:
    """提取PDF文档的文本内容"""
    try:
        # 使用pdfplumber提取文本（处理表格和公式更好）
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"处理第 {page_num} 页...")
                page_text = page.extract_text()
                if page_text:
                    full_text += f"\n=== 第 {page_num} 页 ===\n"
                    full_text += page_text
                    full_text += "\n"
        return full_text
    except Exception as e:
        print(f"pdfplumber提取失败: {e}")
        # 备用方法：使用PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    print(f"PyPDF2处理第 {page_num} 页...")
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n=== 第 {page_num} 页 ===\n"
                        full_text += page_text
                        full_text += "\n"
            return full_text
        except Exception as e2:
            print(f"PyPDF2也提取失败: {e2}")
            return ""

def extract_noise_information(text: str) -> Dict[str, Any]:
    """从文本中提取噪声相关信息"""
    
    # 定义噪声类型的关键词
    noise_types = {
        "thermal_noise": ["thermal noise", "热噪声", "约翰逊噪声", "johnson noise"],
        "flicker_noise": ["flicker noise", "1/f noise", "闪烁噪声", "粉红噪声"],
        "shot_noise": ["shot noise", "散粒噪声", "泊松噪声"],
        "burst_noise": ["burst noise", "爆裂噪声", "随机电报噪声", "popcorn noise"],
        "gr_noise": ["generation-recombination noise", "g-r noise", "产生-复合噪声", "产生复合噪声"]
    }
    
    # 查找包含噪声类型的段落
    noise_info = {
        "thermal_noise": [],
        "flicker_noise": [],
        "shot_noise": [],
        "burst_noise": [],
        "gr_noise": []
    }
    
    # 查找公式（包含数学符号的行）
    formulas = []
    formula_patterns = [
        r'[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^=]+',  # 基本公式模式
        r'[A-Za-z_][A-Za-z0-9_]*\s*∝\s*[^∝]+',  # 比例关系
        r'\d+.*[×·].*\d+',  # 包含乘号的表达式
        r'kT',  # 热噪声相关
        r'qI',  # 散粒噪声相关
        r'1/f',  # 闪烁噪声相关
        r'√[A-Za-z]',  # 平方根表达式
        r'[A-Za-z]²',  # 平方项
        r'10\s*log',  # dB计算
        r'RMS',  # 有效值
        r'[μnmkMGT]V',  # 电压单位
        r'[μnmkMGT]A',  # 电流单位
        r'[μnmkMGT]W',  # 功率单位
        r'[μnmkMGT]Hz'  # 频率单位
    ]
    
    # 分割文本为段落
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    for paragraph in paragraphs:
        # 检查是否包含噪声类型关键词
        for noise_type, keywords in noise_types.items():
            for keyword in keywords:
                if keyword.lower() in paragraph.lower():
                    noise_info[noise_type].append(paragraph)
                    break
        
        # 检查是否包含公式
        for pattern in formula_patterns:
            matches = re.findall(pattern, paragraph, re.IGNORECASE)
            if matches:
                formulas.extend(matches)
    
    # 查找分析方法
    analysis_methods = []
    method_keywords = ["measurement", "measurement method", "测试方法", "分析方法", "calculation", "计算", "simulation", "仿真"]
    
    for paragraph in paragraphs:
        for keyword in method_keywords:
            if keyword.lower() in paragraph.lower() and len(paragraph) > 50:
                analysis_methods.append(paragraph)
                break
    
    return {
        "noise_types": noise_info,
        "formulas": list(set(formulas)),  # 去重
        "analysis_methods": analysis_methods[:20]  # 限制数量
    }

def main():
    pdf_path = "/workspace/ti_noise_analysis.pdf"
    
    print("开始提取PDF内容...")
    text = extract_pdf_content(pdf_path)
    
    if not text:
        print("无法提取PDF内容")
        return
    
    print(f"提取的文本长度: {len(text)} 字符")
    
    # 保存完整文本
    with open("/workspace/docs/full_pdf_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("提取噪声相关信息...")
    noise_info = extract_noise_information(text)
    
    # 保存提取的信息
    with open("/workspace/docs/noise_analysis.json", "w", encoding="utf-8") as f:
        json.dump(noise_info, f, ensure_ascii=False, indent=2)
    
    # 生成总结报告
    report = generate_summary_report(noise_info)
    with open("/workspace/docs/noise_summary.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("提取完成！")
    print(f"- 完整文本保存至: /workspace/docs/full_pdf_text.txt")
    print(f"- 噪声信息保存至: /workspace/docs/noise_analysis.json")
    print(f"- 总结报告保存至: /workspace/docs/noise_summary.md")
    
    return noise_info

def generate_summary_report(noise_info: Dict[str, Any]) -> str:
    """生成总结报告"""
    
    report = """# TI噪声分析文档总结报告

## 文档概述
本文档提取了TI噪声分析PDF中关于集成电路噪声类型的关键信息，重点关注：
- 热噪声 (Thermal Noise)
- 闪烁噪声 (Flicker Noise/1/f Noise)  
- 散粒噪声 (Shot Noise)
- 爆裂噪声 (Burst Noise)
- 产生-复合噪声 (Generation-Recombination Noise)

## 各类噪声详细信息

"""
    
    noise_type_names = {
        "thermal_noise": "热噪声 (Thermal Noise)",
        "flicker_noise": "闪烁噪声 (Flicker Noise/1/f Noise)",
        "shot_noise": "散粒噪声 (Shot Noise)",
        "burst_noise": "爆裂噪声 (Burst Noise)",
        "gr_noise": "产生-复合噪声 (Generation-Recombination Noise)"
    }
    
    for noise_type, info in noise_info["noise_types"].items():
        if info:  # 只显示有信息的噪声类型
            report += f"### {noise_type_names.get(noise_type, noise_type)}\n\n"
            
            # 显示相关段落
            for i, paragraph in enumerate(info[:5], 1):  # 最多显示5个段落
                report += f"**段落 {i}:**\n{paragraph}\n\n"
            
            report += "---\n\n"
    
    # 添加公式部分
    if noise_info["formulas"]:
        report += "## 发现的数学公式和表达式\n\n"
        for i, formula in enumerate(noise_info["formulas"][:20], 1):  # 最多显示20个公式
            report += f"{i}. `{formula}`\n"
        report += "\n"
    
    # 添加分析方法
    if noise_info["analysis_methods"]:
        report += "## 分析方法\n\n"
        for i, method in enumerate(noise_info["analysis_methods"][:10], 1):  # 最多显示10个方法
            report += f"**方法 {i}:**\n{method}\n\n"
    
    return report

if __name__ == "__main__":
    main()