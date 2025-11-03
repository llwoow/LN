#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互连寄生参数提取PDF内容提取脚本 (简化版)
重点提取电容、电阻和电感计算方法
"""

import PyPDF2
import json
import re
from pathlib import Path

def extract_interconnect_content_simple(pdf_path):
    """简化版提取互连寄生参数内容"""
    
    content_data = {
        "title": "互连寄生参数提取技术文档",
        "source": "https://cseweb.ucsd.edu/classes/fa12/cse291-c/slides/L5extract.pdf",
        "extraction_date": "2025-11-02",
        "total_pages": 0,
        "content_sections": [],
        "full_text": "",
        "extraction_summary": ""
    }
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content_data["total_pages"] = len(pdf_reader.pages)
            
            print(f"PDF总页数: {content_data['total_pages']}")
            
            # 提取每一页的内容
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        content_data["full_text"] += f"\n--- 第 {page_num} 页 ---\n"
                        content_data["full_text"] += text + "\n"
                        
                        # 识别关键内容
                        key_terms = ["capacitance", "resistance", "inductance", "extraction", "parasitic", 
                                   "capacitor", "resistor", "inductor", "calculation", "method"]
                        
                        for term in key_terms:
                            if term.lower() in text.lower():
                                content_data["content_sections"].append({
                                    "page": page_num,
                                    "term": term,
                                    "content": text[:300] + "..." if len(text) > 300 else text
                                })
                                break
                        
                        print(f"已处理第 {page_num} 页")
                
                except Exception as e:
                    print(f"处理第{page_num}页时出错: {e}")
                    continue
            
            # 生成摘要
            content_data["extraction_summary"] = f"""
            成功提取了 {content_data['total_pages']} 页PDF内容
            识别了 {len(content_data['content_sections'])} 个相关内容段落
            重点关注电容、电阻、电感计算方法
            """
            
            print(f"提取完成！")
            print(f"识别内容段落: {len(content_data['content_sections'])}个")
            
    except Exception as e:
        print(f"PDF处理错误: {e}")
        return None
    
    return content_data

def save_content(content_data, output_dir="/workspace"):
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
    content_data = extract_interconnect_content_simple(pdf_path)
    
    if content_data:
        save_content(content_data)
        print("PDF内容提取完成！")
    else:
        print("PDF内容提取失败！")