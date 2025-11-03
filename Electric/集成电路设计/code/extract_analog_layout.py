#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟版图设计PDF内容提取脚本
重点提取器件匹配和精度计算相关内容
"""

import PyPDF2
import json
import re
from pathlib import Path

def extract_pdf_content(pdf_path):
    """提取PDF内容并重点关注器件匹配和精度计算"""
    
    content_data = {
        "title": "模拟版图设计技术文档",
        "source": "https://picture.iczhiku.com/resource/eetop/WHIfpIKOkSZFpmcC.pdf",
        "extraction_date": "2025-11-02",
        "total_pages": 0,
        "chapters": [],
        "matching_content": [],
        "precision_content": [],
        "full_text": "",
        "key_topics": []
    }
    
    # 关键词列表用于筛选相关内容
    matching_keywords = [
        "matching", "匹配", "device matching", "器件匹配", "matching issues",
        "matching capacitors", "匹配电容", "matching resistors", "匹配电阻",
        "symmetry", "对称", "common centroid", "共质心", "interdigitated", "交叉指状",
        "guard ring", "保护环", "dummy", "虚拟器件"
    ]
    
    precision_keywords = [
        "precision", "精度", "accuracy", "准确度", "offset", "偏置", "drift", "漂移",
        "mismatch", "失配", "variation", "变化", "tolerance", "容差",
        "low offset", "低偏置", "design for low offset", "低偏置设计",
        "statistical", "统计", "monte carlo", "蒙特卡洛", "corner", "角落分析"
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
                        
                        # 检查是否包含匹配相关内容
                        for keyword in matching_keywords:
                            if keyword.lower() in text.lower():
                                content_data["matching_content"].append({
                                    "page": page_num,
                                    "keyword": keyword,
                                    "content": text[:500] + "..." if len(text) > 500 else text
                                })
                                break
                        
                        # 检查是否包含精度相关内容
                        for keyword in precision_keywords:
                            if keyword.lower() in text.lower():
                                content_data["precision_content"].append({
                                    "page": page_num,
                                    "keyword": keyword,
                                    "content": text[:500] + "..." if len(text) > 500 else text
                                })
                                break
                        
                        # 识别章节标题
                        if re.search(r'chapter|chapter\s+\d+|第\s*\d+\s*章', text, re.IGNORECASE):
                            content_data["chapters"].append({
                                "page": page_num,
                                "title": text[:100] + "..." if len(text) > 100 else text
                            })
                        
                        # 识别关键话题
                        if any(topic in text.lower() for topic in ["analog layout", "layout consideration", "版图设计"]):
                            content_data["key_topics"].append({
                                "page": page_num,
                                "content": text[:200] + "..." if len(text) > 200 else text
                            })
                
                except Exception as e:
                    print(f"处理第{page_num}页时出错: {e}")
                    continue
            
            print(f"提取完成！")
            print(f"匹配相关内容: {len(content_data['matching_content'])}处")
            print(f"精度相关内容: {len(content_data['precision_content'])}处")
            print(f"识别章节: {len(content_data['chapters'])}个")
            print(f"关键话题: {len(content_data['key_topics'])}处")
            
    except Exception as e:
        print(f"PDF处理错误: {e}")
        return None
    
    return content_data

def save_extracted_content(content_data, output_dir="/workspace"):
    """保存提取的内容"""
    
    # 保存完整文本
    with open(f"{output_dir}/analog_layout_full_text.txt", "w", encoding="utf-8") as f:
        f.write(content_data["full_text"])
    
    # 保存结构化数据
    with open(f"{output_dir}/analog_layout_extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)
    
    print(f"内容已保存到: {output_dir}/analog_layout_full_text.txt")
    print(f"结构化数据已保存到: {output_dir}/analog_layout_extracted_data.json")

if __name__ == "__main__":
    pdf_path = "/workspace/analog_layout_design.pdf"
    
    print("开始提取模拟版图设计PDF内容...")
    content_data = extract_pdf_content(pdf_path)
    
    if content_data:
        save_extracted_content(content_data)
        print("PDF内容提取完成！")
    else:
        print("PDF内容提取失败！")