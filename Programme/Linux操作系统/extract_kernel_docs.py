#!/usr/bin/env python3
"""
提取Linux内核设备驱动文档的关键内容
"""

import re
from bs4 import BeautifulSoup
import json

def extract_content_from_html(file_path):
    """从HTML文件中提取文本内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取标题
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Unknown Title"
        
        # 提取主要内容
        body = soup.find('body')
        if body:
            # 移除导航和侧边栏
            for nav in body.find_all(['div', 'span'], class_=re.compile(r'sphinxsidebar|sidebar|navigation')):
                nav.decompose()
            
            # 提取文本内容
            text_content = body.get_text()
            # 清理文本
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content.strip()
        else:
            text_content = "No content found"
        
        return {
            'title': title_text,
            'content': text_content,
            'length': len(text_content)
        }
    except Exception as e:
        return {
            'title': f"Error parsing {file_path}",
            'content': str(e),
            'length': 0
        }

def extract_structured_info(file_path):
    """提取结构化信息，如代码示例、API接口等"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找代码块
        code_blocks = []
        for code in soup.find_all(['code', 'pre']):
            code_text = code.get_text().strip()
            if code_text and len(code_text) > 10:  # 过滤掉太短的代码
                code_blocks.append(code_text)
        
        # 查找标题和章节
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                heading_text = heading.get_text().strip()
                if heading_text:
                    headings.append(f"H{i}: {heading_text}")
        
        # 查找链接
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().strip()
            link_url = link.get('href')
            if link_text and link_url:
                links.append({
                    'text': link_text,
                    'url': link_url
                })
        
        return {
            'code_blocks': code_blocks[:10],  # 限制数量
            'headings': headings[:20],  # 限制数量
            'links': links[:15]  # 限制数量
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def main():
    """主函数"""
    files = [
        ('/workspace/kernel_driver_api_index.html', '设备驱动API索引'),
        ('/workspace/driver_model.html', '设备驱动模型'),
        ('/workspace/pci_driver.html', 'PCI驱动框架'),
        ('/workspace/character_device.html', '字符设备驱动')
    ]
    
    results = {}
    
    for file_path, description in files:
        print(f"处理文件: {description} ({file_path})")
        
        # 提取基本内容
        content_info = extract_content_from_html(file_path)
        
        # 提取结构化信息
        structured_info = extract_structured_info(file_path)
        
        results[description] = {
            'file_path': file_path,
            'content_info': content_info,
            'structured_info': structured_info
        }
        
        print(f"  - 标题: {content_info['title']}")
        print(f"  - 内容长度: {content_info['length']} 字符")
        print(f"  - 代码块数量: {len(structured_info.get('code_blocks', []))}")
        print(f"  - 标题数量: {len(structured_info.get('headings', []))}")
        print()
    
    # 保存结果
    with open('/workspace/kernel_docs_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("结果已保存到 kernel_docs_extracted.json")
    return results

if __name__ == "__main__":
    main()