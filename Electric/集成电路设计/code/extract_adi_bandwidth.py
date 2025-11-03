#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载并提取ADI带宽教程PDF内容
重点关注：运算放大器带宽特性、增益带宽积、频率响应分析、带宽平坦性
"""

import requests
import PyPDF2
import pdfplumber
import json
import re
from typing import List, Dict, Any

def download_and_extract_pdf(url: str, output_path: str) -> str:
    """下载PDF并提取文本内容"""
    try:
        print(f"正在下载PDF: {url}")
        
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 下载PDF
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        print(f"下载状态: {response.status_code}")
        print(f"内容类型: {response.headers.get('content-type', 'Unknown')}")
        print(f"内容长度: {len(response.content)} bytes")
        
        # 保存PDF
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"PDF已保存至: {output_path}")
        
        # 提取文本内容
        return extract_pdf_content(output_path)
        
    except Exception as e:
        print(f"下载或提取失败: {e}")
        return ""

def extract_pdf_content(pdf_path: str) -> str:
    """提取PDF文档的文本内容"""
    try:
        # 使用pdfplumber提取文本（处理表格和公式更好）
        print("使用pdfplumber提取文本...")
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
            print("使用PyPDF2提取文本...")
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

def extract_bandwidth_information(text: str) -> Dict[str, Any]:
    """从文本中提取带宽相关信息"""
    
    # 定义关键词
    keywords = {
        "bandwidth_characteristics": ["bandwidth", "带宽", "frequency response", "频率响应", "cutoff frequency", "截止频率"],
        "gain_bandwidth_product": ["gain bandwidth product", "增益带宽积", "GBW", "gain-bandwidth", "unity gain bandwidth", "单位增益带宽"],
        "frequency_analysis": ["frequency analysis", "频率分析", "bode plot", "bode图", "phase margin", "相位裕度", "stability", "稳定性"],
        "bandwidth_flatness": ["bandwidth flatness", "带宽平坦性", "flat response", "平坦响应", "passband ripple", "通带波纹"],
        "opamp_bandwidth": ["op amp bandwidth", "运放带宽", "operational amplifier", "运算放大器", "closed-loop bandwidth", "闭环带宽"]
    }
    
    # 查找相关内容
    extracted_info = {
        "bandwidth_characteristics": [],
        "gain_bandwidth_product": [],
        "frequency_analysis": [],
        "bandwidth_flatness": [],
        "opamp_bandwidth": []
    }
    
    # 查找公式（包含数学符号的行）
    formulas = []
    formula_patterns = [
        r'[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^=]+',  # 基本公式模式
        r'[A-Za-z_][A-Za-z0-9_]*\s*∝\s*[^∝]+',  # 比例关系
        r'[A-Za-z]\s*[+\-*/=]\s*[A-Za-z0-9]',  # 简单数学表达式
        r'[A-Za-z]\([sω]\)',  # 拉普拉斯/频域表达式
        r'[A-Za-z]\s*=\s*[A-Za-z0-9]+\s*[+\-*/]\s*[A-Za-z0-9]+',  # 复杂公式
        r'[A-Za-z]_\w+',  # 下标变量
        r'[A-Za-z]^\w+',  # 上标变量
        r'jω',  # 频域变量
        r'[A-Za-z]\s*>>\s*[A-Za-z]',  # 近似关系
        r'[A-Za-z]\s*<<\s*[A-Za-z]',  # 近似关系
        r'20\s*log',  # dB计算
        r'[μnmkMGT]Hz',  # 频率单位
        r'[μnmkMGT]V',  # 电压单位
        r'[μnmkMGT]A',  # 电流单位
        r'[μnmkMGT]Ω',  # 电阻单位
        r'[μnmkMGT]F',  # 电容单位
        r'[μnmkMGT]H',  # 电感单位
        r'[A-Za-z]*BW[A-Za-z]*',  # 带宽相关
        r'[A-Za-z]*GBW[A-Za-z]*',  # 增益带宽积
        r'[A-Za-z]*GB[A-Za-z]*',  # 增益带宽
    ]
    
    # 分割文本为段落
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    for paragraph in paragraphs:
        # 检查是否包含关键词
        for category, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in paragraph.lower() and len(paragraph) > 20:
                    extracted_info[category].append(paragraph)
                    break
        
        # 检查是否包含公式
        for pattern in formula_patterns:
            matches = re.findall(pattern, paragraph, re.IGNORECASE)
            if matches:
                formulas.extend(matches)
    
    return {
        "categories": extracted_info,
        "formulas": list(set(formulas)),  # 去重
        "total_pages": text.count("=== 第") if "=== 第" in text else 0
    }

def generate_summary_report(bandwidth_info: Dict[str, Any]) -> str:
    """生成总结报告"""
    
    report = """# ADI带宽教程总结报告
## Op-Amp Bandwidth and Frequency Response

## 文档概述
本文档提取了ADI带宽教程MT-045的核心内容，重点关注：
- 运算放大器带宽特性
- 增益带宽积分析
- 频率响应分析
- 带宽平坦性评估

## 各类内容详细信息

"""
    
    category_names = {
        "bandwidth_characteristics": "运算放大器带宽特性 (Op-Amp Bandwidth Characteristics)",
        "gain_bandwidth_product": "增益带宽积 (Gain Bandwidth Product)",
        "frequency_analysis": "频率响应分析 (Frequency Response Analysis)",
        "bandwidth_flatness": "带宽平坦性 (Bandwidth Flatness)",
        "opamp_bandwidth": "运放带宽分析 (Op-Amp Bandwidth Analysis)"
    }
    
    for category, info in bandwidth_info["categories"].items():
        if info:  # 只显示有信息的类别
            report += f"### {category_names.get(category, category)}\n\n"
            
            # 显示相关段落
            for i, paragraph in enumerate(info[:10], 1):  # 最多显示10个段落
                report += f"**段落 {i}:**\n{paragraph}\n\n"
            
            report += "---\n\n"
    
    # 添加公式部分
    if bandwidth_info["formulas"]:
        report += "## 发现的数学公式和表达式\n\n"
        for i, formula in enumerate(bandwidth_info["formulas"][:40], 1):  # 最多显示40个公式
            report += f"{i}. `{formula}`\n"
        report += "\n"
    
    # 添加统计信息
    report += f"## 文档统计信息\n\n"
    report += f"- 总页数: {bandwidth_info['total_pages']}\n"
    report += f"- 发现的公式数量: {len(bandwidth_info['formulas'])}\n"
    
    for category, info in bandwidth_info["categories"].items():
        if info:
            report += f"- {category_names.get(category, category)}相关内容: {len(info)} 段落\n"
    
    return report

def main():
    pdf_url = "https://www.analog.com/media/en/training-seminars/tutorials/MT-045.pdf"
    pdf_path = "/workspace/adi_bandwidth_tutorial.pdf"
    
    print("开始下载和提取ADI带宽教程内容...")
    text = download_and_extract_pdf(pdf_url, pdf_path)
    
    if not text:
        print("无法提取PDF内容")
        return
    
    print(f"提取的文本长度: {len(text)} 字符")
    
    # 保存完整文本
    with open("/workspace/docs/adi_bandwidth_full_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("提取带宽相关信息...")
    bandwidth_info = extract_bandwidth_information(text)
    
    # 保存提取的信息
    with open("/workspace/docs/adi_bandwidth_analysis.json", "w", encoding="utf-8") as f:
        json.dump(bandwidth_info, f, ensure_ascii=False, indent=2)
    
    # 生成总结报告
    report = generate_summary_report(bandwidth_info)
    with open("/workspace/docs/adi_bandwidth_summary.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("提取完成！")
    print(f"- 完整文本保存至: /workspace/docs/adi_bandwidth_full_text.txt")
    print(f"- 带宽信息保存至: /workspace/docs/adi_bandwidth_analysis.json")
    print(f"- 总结报告保存至: /workspace/docs/adi_bandwidth_summary.md")
    
    return bandwidth_info

if __name__ == "__main__":
    main()