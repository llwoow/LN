#!/usr/bin/env python3
"""
提取NIST SP 800-125A PDF文档的虚拟化安全相关内容
"""

import pdfplumber
import json
import re
from pathlib import Path

def extract_virtualization_security_content(pdf_path):
    """提取PDF中虚拟化安全相关的内容"""
    
    # 虚拟化安全相关的关键词
    virtualization_keywords = [
        'hypervisor', 'hyper-v', 'vmware', 'esxi', 'kvm', 'qemu', 'xen',
        'virtualization', 'virtual machine', 'vm', 'guest', 'host',
        'virtualization security', 'vm isolation', 'virtual network',
        'virtualization attack', 'vm escape', 'hypervisor security',
        'virtualization threat', 'vm security', 'virtualization best practice',
        'hypervisor hardening', 'vm hardening', 'virtualization configuration'
    ]
    
    extracted_content = {
        'title': '',
        'document_info': {},
        'hypervisor_security': [],
        'vm_isolation': [],
        'virtualization_attack_surface': [],
        'security_recommendations': [],
        'threats_and_mitigations': [],
        'platform_specific_guidance': [],
        'all_relevant_text': []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 提取文档信息
            extracted_content['document_info'] = {
                'total_pages': len(pdf.pages),
                'title': pdf.metadata.get('Title', ''),
                'author': pdf.metadata.get('Author', ''),
                'subject': pdf.metadata.get('Subject', ''),
                'creator': pdf.metadata.get('Creator', '')
            }
            
            all_text = ""
            
            # 逐页提取文本
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    all_text += f"\n=== 第 {page_num} 页 ===\n"
                    all_text += page_text
                    
                    # 检查页面是否包含虚拟化相关内容
                    page_lower = page_text.lower()
                    relevant_keywords_found = [kw for kw in virtualization_keywords if kw in page_lower]
                    
                    if relevant_keywords_found:
                        extracted_content['all_relevant_text'].append({
                            'page': page_num,
                            'keywords_found': relevant_keywords_found,
                            'text': page_text
                        })
            
            # 分析和分类内容
            analyze_content(all_text, extracted_content)
            
    except Exception as e:
        extracted_content['error'] = str(e)
    
    return extracted_content

def analyze_content(text, content_dict):
    """分析文本内容并分类"""
    
    text_lower = text.lower()
    
    # 分类虚拟化安全相关内容
    sections = {
        'hypervisor_security': ['hypervisor security', 'hypervisor hardening', 'hypervisor configuration'],
        'vm_isolation': ['vm isolation', 'virtual machine isolation', 'guest isolation'],
        'virtualization_attack_surface': ['attack surface', 'virtualization attack', 'vm escape'],
        'security_recommendations': ['recommendation', 'best practice', 'configuration guidance'],
        'threats_and_mitigations': ['threat', 'mitigation', 'vulnerability', 'risk'],
        'platform_specific_guidance': ['vmware', 'hyper-v', 'kvm', 'xen', 'esxi']
    }
    
    # 提取相关内容段落
    paragraphs = text.split('\n\n')
    
    for category, keywords in sections.items():
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            if any(keyword in paragraph_lower for keyword in keywords):
                if len(paragraph.strip()) > 50:  # 过滤掉太短的段落
                    content_dict[category].append(paragraph.strip())

def main():
    pdf_path = "/workspace/downloads/NIST_SP_800-125A.pdf"
    
    print("开始提取NIST SP 800-125A PDF文档内容...")
    content = extract_virtualization_security_content(pdf_path)
    
    # 保存提取的内容
    output_path = "/workspace/extract/nist_sp_800-125a_extracted_content.json"
    Path("/workspace/extract").mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"内容已提取并保存到: {output_path}")
    
    # 显示摘要信息
    if 'error' not in content:
        print(f"\n文档信息:")
        print(f"标题: {content['document_info'].get('title', 'N/A')}")
        print(f"总页数: {content['document_info'].get('total_pages', 'N/A')}")
        print(f"找到的相关页面数: {len(content['all_relevant_text'])}")
        
        print(f"\n分类内容统计:")
        for category in ['hypervisor_security', 'vm_isolation', 'virtualization_attack_surface', 
                        'security_recommendations', 'threats_and_mitigations', 'platform_specific_guidance']:
            print(f"{category}: {len(content[category])} 个段落")
    else:
        print(f"提取过程中出现错误: {content['error']}")

if __name__ == "__main__":
    main()