#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互连寄生参数提取PDF内容提取脚本
重点提取电容、电阻和电感计算方法
"""

import PyPDF2
import json
import re
from pathlib import Path

def extract_interconnect_parasitic_content(pdf_path):
    """提取互连寄生参数相关内容"""
    
    content_data = {
        "title": "互连寄生参数提取技术文档",
        "source": "https://cseweb.ucsd.edu/classes/fa12/cse291-c/slides/L5extract.pdf",
        "extraction_date": "2025-11-02",
        "total_pages": 0,
        "chapters": [],
        "capacitance_content": [],
        "resistance_content": [],
        "inductance_content": [],
        "extraction_methods": [],
        "full_text": "",
        "key_formulas": [],
        "calculation_examples": []
    }
    
    # 关键词列表用于筛选相关内容
    capacitance_keywords = [
        "capacitance", "capacitor", "capacitive", "电容", "c", "capacitance calculation",
        "coupling capacitance", "fringe capacitance", "ground capacitance", "lateral capacitance",
        "parallel plate", "边缘电容", "耦合电容", "接地电容"
    ]
    
    resistance_keywords = [
        "resistance", "resistive", "电阻", "r", "resistance calculation", "sheet resistance",
        "spreading resistance", "contact resistance", "via resistance", "metal resistance",
        "电阻率", "薄层电阻", "扩散电阻", "接触电阻"
    ]
    
    inductance_keywords = [
        "inductance", "inductive", "电感", "l", "mutual inductance", "self inductance",
        "partial inductance", "loop inductance", "skin effect", "proximity effect",
        "电感计算", "互感", "自感", "部分电感", "环路电感"
    ]
    
    extraction_keywords = [
        "extraction", "parasitic", "parameter extraction", "rc extraction", "rcl extraction",
        "field solver", "boundary element method", "finite element method", "fastcap", "fasthenry",
        "提取", "寄生参数", "场求解器", "边界元法", "有限元法"
    ]
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content_data["total_pages"] = len(pdf_reader.pages)
            
            print(f"PDF总页数: {content_data['total_pages']}")
            
            # 提取每一页的内容
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text.strip():
                        content_data["full_text"] += f"\n--- 第 {page_num} 页 ---\n"
                        content_data["full_text"] += text + "\n"
                        
                        # 检查是否包含电容相关内容
                        for keyword in capacitance_keywords:
                            if keyword.lower() in text.lower():
                                content_data["capacitance_content"].append({
                                    "page": page_num,
                                    "keyword": keyword,
                                    "content": text[:500] + "..." if len(text) > 500 else text
                                })
                                break
                        
                        # 检查是否包含电阻相关内容
                        for keyword in resistance_keywords:
                            if keyword.lower() in text.lower():
                                content_data["resistance_content"].append({
                                    "page": page_num,
                                    "keyword": keyword,
                                    "content": text[:500] + "..." if len(text) > 500 else text
                                })
                                break
                        
                        # 检查是否包含电感相关内容
                        for keyword in inductance_keywords:
                            if keyword.lower() in text.lower():
                                content_data["inductance_content"].append({
                                    "page": page_num,
                                    "keyword": keyword,
                                    "content": text[:500] + "..." if len(text) > 500 else text
                                })
                                break
                        
                        # 检查是否包含提取方法相关内容
                        for keyword in extraction_keywords:
                            if keyword.lower() in text.lower():
                                content_data["extraction_methods"].append({
                                    "page": page_num,
                                    "keyword": keyword,
                                    "content": text[:500] + "..." if len(text) > 500 else text
                                })
                                break
                        
                        # 识别章节标题
                        if re.search(r'chapter|chapter\s+\d+|第\s*\d+\s*章|lecture\s*\d+', text, re.IGNORECASE):
                            content_data["chapters"].append({
                                "page": page_num,
                                "title": text[:100] + "..." if len(text) > 100 else text
                            })
                        
                        # 识别公式
                        formula_patterns = [
                            r'[A-Za-z]\s*=\s*[^=]+',
                            r'[A-Za-z]\s*∝\s*[^∝]+',
                            r'[A-Za-z]\s*~\s*[^~]+',
                            r'ε\s*.*?F/m',
                            r'ρ\s*.*?Ω·m',
                            r'μ\s*.*?H/m'
                        ]
                        
                        for pattern in formula_patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches:
                                content_data["key_formulas"].append({
                                    "page": page_num,
                                    "formula": match.strip()
                                })
                        
                        # 识别计算示例
                        if any(keyword in text.lower() for keyword in ["example", "计算", "example:", "example of"]):
                            content_data["calculation_examples"].append({
                                "page": page_num,
                                "content": text[:300] + "..." if len(text) > 300 else text
                            })
                
                except Exception as e:
                    print(f"处理第{page_num}页时出错: {e}")
                    continue
            
            print(f"提取完成！")
            print(f"电容相关内容: {len(content_data['capacitance_content'])}处")
            print(f"电阻相关内容: {len(content_data['resistance_content'])}处")
            print(f"电感相关内容: {len(content_data['inductance_content'])}处")
            print(f"提取方法: {len(content_data['extraction_methods'])}处")
            print(f"识别章节: {len(content_data['chapters'])}个")
            print(f"关键公式: {len(content_data['key_formulas'])}个")
            print(f"计算示例: {len(content_data['calculation_examples'])}个")
            
    except Exception as e:
        print(f"PDF处理错误: {e}")
        return None
    
    return content_data

def save_extracted_content(content_data, output_dir="/workspace"):
    """保存提取的内容"""
    
    # 保存完整文本
    with open(f"{output_dir}/interconnect_parasitic_full_text.txt", "w", encoding="utf-8") as f:
        f.write(content_data["full_text"])
    
    # 保存结构化数据
    with open(f"{output_dir}/interconnect_parasitic_extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)
    
    print(f"内容已保存到: {output_dir}/interconnect_parasitic_full_text.txt")
    print(f"结构化数据已保存到: {output_dir}/interconnect_parasitic_extracted_data.json")

if __name__ == "__main__":
    pdf_path = "/workspace/interconnect_parasitic_extraction.pdf"
    
    print("开始提取互连寄生参数提取PDF内容...")
    content_data = extract_interconnect_parasitic_content(pdf_path)
    
    if content_data:
        save_extracted_content(content_data)
        print("PDF内容提取完成！")
    else:
        print("PDF内容提取失败！")