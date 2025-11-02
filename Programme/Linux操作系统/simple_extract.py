#!/usr/bin/env python3
"""
简单提取Linux内核设备驱动文档内容
"""

import re
import json

def extract_text_from_html(file_path):
    """从HTML文件中提取纯文本内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', ' ', content)
        
        # 清理空白字符
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # 查找标题
        title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        return {
            'title': title,
            'content': text[:2000],  # 限制长度
            'full_length': len(text)
        }
    except Exception as e:
        return {
            'title': f"Error: {file_path}",
            'content': str(e),
            'full_length': 0
        }

def extract_code_blocks(file_path):
    """提取代码块"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找<code>和<pre>标签中的内容
        code_pattern = r'<(?:code|pre)[^>]*>([^<]+)</(?:code|pre)>'
        code_matches = re.findall(code_pattern, content, re.IGNORECASE)
        
        # 过滤和清理代码块
        cleaned_codes = []
        for code in code_matches:
            code = code.strip()
            if len(code) > 10 and len(code) < 500:  # 过滤太短或太长的代码
                cleaned_codes.append(code)
        
        return cleaned_codes[:10]  # 限制数量
    except Exception as e:
        return [f"Error extracting code: {e}"]

def extract_headings(file_path):
    """提取标题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找标题
        heading_pattern = r'<(h[1-6])[^>]*>([^<]+)</\1>'
        heading_matches = re.findall(heading_pattern, content, re.IGNORECASE)
        
        headings = []
        for tag, text in heading_matches:
            text = text.strip()
            if text:
                headings.append(f"{tag.upper()}: {text}")
        
        return headings[:20]  # 限制数量
    except Exception as e:
        return [f"Error extracting headings: {e}"]

def main():
    """主函数"""
    files = [
        ('/workspace/kernel_driver_api_index.html', '设备驱动API索引'),
        ('/workspace/driver_model.html', '设备驱动模型'),
        ('/workspace/pci_driver.html', 'PCI驱动框架'),
        ('/workspace/character_device.html', '字符设备驱动')
    ]
    
    results = {}
    
    print("开始提取Linux内核设备驱动文档内容...")
    print("=" * 60)
    
    for file_path, description in files:
        print(f"\n处理文件: {description}")
        print("-" * 40)
        
        # 提取基本内容
        content_info = extract_text_from_html(file_path)
        
        # 提取代码块
        code_blocks = extract_code_blocks(file_path)
        
        # 提取标题
        headings = extract_headings(file_path)
        
        results[description] = {
            'file_path': file_path,
            'title': content_info['title'],
            'content_preview': content_info['content'],
            'full_length': content_info['full_length'],
            'code_blocks': code_blocks,
            'headings': headings
        }
        
        print(f"标题: {content_info['title']}")
        print(f"内容长度: {content_info['full_length']} 字符")
        print(f"代码块数量: {len(code_blocks)}")
        print(f"标题数量: {len(headings)}")
        
        # 显示前几个标题
        if headings:
            print("主要章节:")
            for i, heading in enumerate(headings[:5]):
                print(f"  {i+1}. {heading}")
    
    # 保存结果
    output_file = '/workspace/kernel_docs_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"分析完成！结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    main()