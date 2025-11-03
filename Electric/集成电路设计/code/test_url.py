#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_url_access():
    """测试URL访问"""
    url = "https://ocw.mit.edu/courses/res-6-010-electronic-feedback-systems-spring-2013/432fa8464521d3998a5f815bd57e42c9_MITRES_6-010S13_chap01.pdf"
    
    try:
        print(f"测试访问URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"内容类型: {response.headers.get('content-type', 'Unknown')}")
        print(f"内容长度: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # 保存PDF文件
            with open('/workspace/test_download.pdf', 'wb') as f:
                f.write(response.content)
            print("PDF已保存为 test_download.pdf")
            
            # 尝试读取前几个字节
            print(f"前20字节: {response.content[:20]}")
            
        return response
        
    except Exception as e:
        print(f"访问失败: {e}")
        return None

if __name__ == "__main__":
    test_url_access()