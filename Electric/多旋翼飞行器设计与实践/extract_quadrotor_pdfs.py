#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四旋翼动力学PDF内容提取工具
"""

import PyPDF2
import os
import sys

def extract_pdf_text(pdf_path):
    """提取PDF文本内容"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n\n'
            return text
    except Exception as e:
        return f'提取PDF时出错: {e}'

def extract_mathematical_content(text):
    """提取数学内容"""
    import re
    
    # 查找数学公式的模式
    math_patterns = [
        r'\\$.*?\\$',  # LaTeX行内公式
        r'\\\\\[.*?\\\\\]',  # LaTeX显示公式
        r'\\begin\{equation\}.*?\\end\{equation\}',  # LaTeX equation环境
        r'\\begin\{align\}.*?\\end\{align\}',  # LaTeX align环境
        r'[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^\\n]+',  # 变量定义
        r'\\frac\{[^}]+\}\{[^}]+\}',  # 分数
        r'\\sum_\{[^}]+\}',  # 求和
        r'\\int_[^\\n]+',  # 积分
        r'\\omega\s*[=]',  # 角速度
        r'\\theta\s*[=]',  # 角度
        r'\\phi\s*[=]',    # 滚转角
        r'\\psi\s*[=]',    # 偏航角
        r'\\alpha\s*[=]',  # 攻角
        r'\\beta\s*[=]',   # 侧滑角
        r'\\rho\s*[=]',    # 密度
        r'\\mu\s*[=]',     # 摩擦系数
    ]
    
    math_content = []
    for pattern in math_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        math_content.extend(matches)
    
    return math_content

def main():
    """主函数"""
    pdf_files = [
        '/workspace/quadrotor_control_theory.pdf',
        '/workspace/quadrotor_paper.pdf'
    ]
    
    all_content = []
    
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            print(f"正在提取: {pdf_path}")
            text = extract_pdf_text(pdf_path)
            
            # 提取数学内容
            math_content = extract_mathematical_content(text)
            
            # 保存完整内容
            filename = os.path.basename(pdf_path).replace('.pdf', '_content.txt')
            output_path = f'/workspace/{filename}'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"=== {os.path.basename(pdf_path)} 完整内容 ===\n\n")
                f.write(text)
                f.write(f"\n\n=== 数学内容提取 ===\n\n")
                for i, math in enumerate(math_content, 1):
                    f.write(f"{i}. {math}\n")
            
            all_content.append({
                'file': pdf_path,
                'text': text,
                'math': math_content
            })
            
            print(f"已保存到: {output_path}")
        else:
            print(f"文件不存在: {pdf_path}")
    
    # 生成综合报告
    with open('/workspace/quadrotor_dynamics_summary.txt', 'w', encoding='utf-8') as f:
        f.write("=== 四旋翼动力学数学内容综合报告 ===\n\n")
        
        for content in all_content:
            f.write(f"=== {os.path.basename(content['file'])} ===\n\n")
            
            # 写入数学内容
            if content['math']:
                f.write("数学公式和方程:\n")
                for i, math in enumerate(content['math'], 1):
                    f.write(f"{i}. {math}\n")
                f.write("\n")
            
            # 写入关键技术细节
            f.write("关键技术内容:\n")
            lines = content['text'].split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in 
                       ['equation', 'dynamics', 'control', 'stability', 'motion', 'force', 'torque']):
                    if len(line) > 10:  # 过滤太短的内容
                        f.write(f"- {line}\n")
            f.write("\n" + "="*50 + "\n\n")
    
    print("所有PDF内容提取完成!")

if __name__ == "__main__":
    main()