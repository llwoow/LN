#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取MIT运放教材PDF内容
重点关注：运算放大器理想模型、传递函数推导、反馈系统分析、频率响应
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 下载PDF
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 保存PDF
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
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

def extract_opamp_information(text: str) -> Dict[str, Any]:
    """从文本中提取运放相关信息"""
    
    # 定义关键词
    keywords = {
        "ideal_model": ["ideal op-amp", "理想运放", "ideal operational amplifier", "infinite gain", "infinite input impedance", "zero output impedance"],
        "transfer_function": ["transfer function", "传递函数", "gain", "amplification", "闭环增益", "open-loop gain"],
        "feedback": ["feedback", "反馈", "negative feedback", "负反馈", "positive feedback", "正反馈", "feedback loop"],
        "frequency_response": ["frequency response", "频率响应", "bandwidth", "带宽", "cutoff frequency", "截止频率", "stability", "稳定性"],
        "analysis": ["analysis", "分析", "derivation", "推导", "bode plot", "bode图", "pole", "zero", "极点", "零点"]
    }
    
    # 查找相关内容
    extracted_info = {
        "ideal_model": [],
        "transfer_function": [],
        "feedback": [],
        "frequency_response": [],
        "analysis": []
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

def generate_summary_report(opamp_info: Dict[str, Any]) -> str:
    """生成总结报告"""
    
    report = """# MIT运放教材第1章总结报告
## Electronic Feedback Systems - Operational Amplifiers

## 文档概述
本文档提取了MIT开放课程运放教材第1章的核心内容，重点关注：
- 运算放大器理想模型
- 传递函数推导
- 反馈系统分析
- 频率响应特性

## 各类内容详细信息

"""
    
    category_names = {
        "ideal_model": "运算放大器理想模型 (Ideal Op-Amp Model)",
        "transfer_function": "传递函数推导 (Transfer Function Derivation)",
        "feedback": "反馈系统分析 (Feedback System Analysis)",
        "frequency_response": "频率响应 (Frequency Response)",
        "analysis": "分析方法 (Analysis Methods)"
    }
    
    for category, info in opamp_info["categories"].items():
        if info:  # 只显示有信息的类别
            report += f"### {category_names.get(category, category)}\n\n"
            
            # 显示相关段落
            for i, paragraph in enumerate(info[:8], 1):  # 最多显示8个段落
                report += f"**段落 {i}:**\n{paragraph}\n\n"
            
            report += "---\n\n"
    
    # 添加公式部分
    if opamp_info["formulas"]:
        report += "## 发现的数学公式和表达式\n\n"
        for i, formula in enumerate(opamp_info["formulas"][:30], 1):  # 最多显示30个公式
            report += f"{i}. `{formula}`\n"
        report += "\n"
    
    # 添加统计信息
    report += f"## 文档统计信息\n\n"
    report += f"- 总页数: {opamp_info['total_pages']}\n"
    report += f"- 发现的公式数量: {len(opamp_info['formulas'])}\n"
    
    for category, info in opamp_info["categories"].items():
        if info:
            report += f"- {category_names.get(category, category)}相关内容: {len(info)} 段落\n"
    
    return report

def main():
    pdf_url = "https://ocw.mit.edu/courses/res-6-010-electronic-feedback-systems-spring-2013/432fa8464521d3998a5f815bd57e42c9_MITRES_6-010S13_chap01.pdf"
    pdf_path = "/workspace/mit_opamp_chapter1.pdf"
    
    print("开始下载和提取MIT运放教材内容...")
    text = download_and_extract_pdf(pdf_url, pdf_path)
    
    if not text:
        print("无法提取PDF内容")
        return
    
    print(f"提取的文本长度: {len(text)} 字符")
    
    # 保存完整文本
    with open("/workspace/docs/mit_opamp_full_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("提取运放相关信息...")
    opamp_info = extract_opamp_information(text)
    
    # 保存提取的信息
    with open("/workspace/docs/mit_opamp_analysis.json", "w", encoding="utf-8") as f:
        json.dump(opamp_info, f, ensure_ascii=False, indent=2)
    
    # 生成总结报告
    report = generate_summary_report(opamp_info)
    with open("/workspace/docs/mit_opamp_summary.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("提取完成！")
    print(f"- 完整文本保存至: /workspace/docs/mit_opamp_full_text.txt")
    print(f"- 运放信息保存至: /workspace/docs/mit_opamp_analysis.json")
    print(f"- 总结报告保存至: /workspace/docs/mit_opamp_summary.md")
    
    return opamp_info

if __name__ == "__main__":
    main()