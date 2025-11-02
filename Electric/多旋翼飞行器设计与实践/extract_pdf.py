#!/usr/bin/env python3
import PyPDF2
import sys

def extract_pdf_content(pdf_path, output_path):
    """提取PDF内容并保存为文本文件"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"PDF总页数: {len(pdf_reader.pages)}")
            
            content = []
            content.append("=== MS5611-01BA03 数据手册内容 ===\n")
            
            for page_num, page in enumerate(pdf_reader.pages):
                print(f"正在处理第 {page_num + 1} 页...")
                page_text = page.extract_text()
                if page_text.strip():
                    content.append(f"\n--- 第 {page_num + 1} 页 ---\n")
                    content.append(page_text)
                    content.append("\n")
            
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(''.join(content))
            
            print(f"内容已保存到: {output_path}")
            return True
            
    except Exception as e:
        print(f"提取PDF内容时出错: {e}")
        return False

if __name__ == "__main__":
    pdf_path = "/workspace/ms5611_datasheet.pdf"
    output_path = "/workspace/ms5611_content.txt"
    
    success = extract_pdf_content(pdf_path, output_path)
    if success:
        print("PDF内容提取完成！")
    else:
        print("PDF内容提取失败！")