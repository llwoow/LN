#!/usr/bin/env python3
"""
PDF Content Extractor for Delay Fault Models
"""

import requests
import PyPDF2
import io
import sys
from urllib.parse import urlparse

def extract_pdf_content(url):
    """Extract content from PDF URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        print(f"Attempting to download PDF from: {url}")
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"Final URL: {response.url}")
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Check if content is actually a PDF
        if response.content.startswith(b'%PDF'):
            print("✓ Valid PDF file detected")
            
            # Extract text from PDF
            pdf_content = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_content)
            
            print(f"Number of pages: {len(pdf_reader.pages)}")
            
            # Extract all text
            full_text = ""
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n--- Page {i+1} ---\n"
                        full_text += page_text + "\n"
                except Exception as e:
                    print(f"Error extracting page {i+1}: {e}")
            
            return full_text
            
        else:
            print("✗ Not a PDF file")
            print(f"First 500 bytes of content:")
            print(response.content[:500].decode('utf-8', errors='ignore'))
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

def search_delay_fault_content(text):
    """Search for delay fault model content in the extracted text"""
    if not text:
        return "No text content available"
    
    # Keywords related to delay fault models
    keywords = [
        'delay fault', 'transition fault', 'gate delay', 'path delay', 
        'segment delay', 'transition delay', 'gate-level', 'timing fault',
        'transition fault model', 'gate delay fault', 'path delay fault',
        'segment delay fault', 'delay testing', 'timing verification'
    ]
    
    # Split text into lines for easier processing
    lines = text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for keyword in keywords:
            if keyword.lower() in line_lower:
                # Include context around the relevant line
                start_idx = max(0, i-2)
                end_idx = min(len(lines), i+3)
                context = '\n'.join(lines[start_idx:end_idx])
                relevant_lines.append(f"[Context around '{keyword}']:\n{context}\n")
                break
    
    return '\n'.join(relevant_lines) if relevant_lines else "No delay fault model content found"

if __name__ == "__main__":
    url = "https://link.springer.com/content/pdf/10.1007/978-1-4615-5597-1_3.pdf"
    
    print("=" * 60)
    print("PDF Content Extraction for Delay Fault Models")
    print("=" * 60)
    
    # Extract PDF content
    content = extract_pdf_content(url)
    
    if content:
        print("\n" + "=" * 60)
        print("EXTRACTED CONTENT")
        print("=" * 60)
        
        # Search for delay fault related content
        relevant_content = search_delay_fault_content(content)
        
        print(relevant_content)
        
        # Save full content to file
        with open('/workspace/extracted_pdf_content.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nFull content saved to: /workspace/extracted_pdf_content.txt")
        
    else:
        print("\nFailed to extract PDF content")
        print("This might be due to:")
        print("1. Access restrictions or paywall")
        print("2. Authentication required")
        print("3. Invalid URL or file format")
        print("4. Network issues")