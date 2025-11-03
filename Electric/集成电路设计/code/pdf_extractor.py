#!/usr/bin/env python3
"""
PDF技术文档内容提取器
专门用于提取故障模型和ATPG测试生成相关的技术内容
"""

import PyPDF2
import json
import re
from typing import Dict, List, Any

def extract_pdf_content(pdf_path: str) -> Dict[str, Any]:
    """提取PDF文档内容"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # 获取文档信息
            doc_info = pdf_reader.metadata if pdf_reader.metadata else {}
            
            # 提取所有页面文本
            all_text = ""
            page_count = len(pdf_reader.pages)
            
            for page_num in range(page_count):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                all_text += f"\n--- 第{page_num + 1}页 ---\n"
                all_text += page_text
            
            return {
                "document_info": {
                    "title": doc_info.get('/Title', 'Unknown'),
                    "author": doc_info.get('/Author', 'Unknown'),
                    "subject": doc_info.get('/Subject', 'Unknown'),
                    "page_count": page_count
                },
                "full_text": all_text,
                "page_count": page_count
            }
    except Exception as e:
        return {"error": f"PDF解析错误: {str(e)}"}

def analyze_fault_models_and_atpg(content: str) -> Dict[str, Any]:
    """分析故障模型和ATPG相关内容"""
    
    # 故障模型相关关键词
    fault_model_keywords = [
        "fault model", "stuck-at", "bridging fault", "open fault", 
        "delay fault", "transient fault", "fault classification",
        "single stuck-at", "multiple stuck-at", "bridging", "open",
        "delay", "transient", "coupling fault", "memory fault"
    ]
    
    # ATPG相关关键词
    atpg_keywords = [
        "ATPG", "test pattern generation", "test vector", "test generation",
        "automatic test pattern", "test generation algorithm", "D-algorithm",
        "PODEM", "FAN", "test generation", "pattern generation",
        "test pattern", "test vector generation"
    ]
    
    # 覆盖率相关关键词
    coverage_keywords = [
        "coverage", "fault coverage", "test coverage", "detection rate",
        "coverage calculation", "coverage formula", "coverage metric"
    ]
    
    # 分割内容为段落
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    
    # 提取相关段落
    fault_model_sections = []
    atpg_sections = []
    coverage_sections = []
    formulas = []
    
    for paragraph in paragraphs:
        # 检查故障模型相关内容
        if any(keyword.lower() in paragraph.lower() for keyword in fault_model_keywords):
            fault_model_sections.append(paragraph)
        
        # 检查ATPG相关内容
        if any(keyword.lower() in paragraph.lower() for keyword in atpg_keywords):
            atpg_sections.append(paragraph)
        
        # 检查覆盖率相关内容
        if any(keyword.lower() in paragraph.lower() for keyword in coverage_keywords):
            coverage_sections.append(paragraph)
        
        # 提取公式（包含等号、数学符号等）
        if '=' in paragraph and any(char in paragraph for char in ['∑', '∏', '∫', '√', 'α', 'β', 'γ', 'δ', 'λ', 'μ']):
            formulas.append(paragraph)
    
    return {
        "fault_model_content": fault_model_sections,
        "atpg_content": atpg_sections,
        "coverage_content": coverage_sections,
        "formulas": formulas,
        "total_paragraphs": len(paragraphs)
    }

def main():
    """主函数"""
    pdf_path = "/workspace/notes4.pdf"
    
    print("正在提取PDF内容...")
    pdf_data = extract_pdf_content(pdf_path)
    
    if "error" in pdf_data:
        print(f"错误: {pdf_data['error']}")
        return
    
    print(f"成功提取PDF内容，共{pdf_data['page_count']}页")
    
    # 分析技术内容
    print("正在分析故障模型和ATPG相关内容...")
    analysis = analyze_fault_models_and_atpg(pdf_data['full_text'])
    
    # 整理结果
    result = {
        "document_info": pdf_data["document_info"],
        "extraction_summary": {
            "total_pages": pdf_data["page_count"],
            "fault_model_sections": len(analysis["fault_model_content"]),
            "atpg_sections": len(analysis["atpg_content"]),
            "coverage_sections": len(analysis["coverage_content"]),
            "formulas_found": len(analysis["formulas"])
        },
        "technical_content": {
            "fault_models": analysis["fault_model_content"],
            "atpg_methods": analysis["atpg_content"],
            "coverage_calculation": analysis["coverage_content"],
            "formulas": analysis["formulas"]
        },
        "full_text": pdf_data["full_text"]
    }
    
    # 保存结果
    output_path = "/workspace/data/fault_model_atpg_extraction.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"提取结果已保存到: {output_path}")
    
    # 输出摘要
    print("\n=== 提取摘要 ===")
    print(f"文档标题: {pdf_data['document_info']['title']}")
    print(f"总页数: {pdf_data['page_count']}")
    print(f"故障模型相关段落: {len(analysis['fault_model_content'])}")
    print(f"ATPG相关段落: {len(analysis['atpg_content'])}")
    print(f"覆盖率相关段落: {len(analysis['coverage_content'])}")
    print(f"发现公式: {len(analysis['formulas'])}")
    
    return result

if __name__ == "__main__":
    main()