#!/usr/bin/env python3
"""
Extract text from PDF files for requirements analysis
"""

import PyPDF2
import sys

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

def main():
    """Extract text from all PDF files"""
    pdf_files = ['HLD.pdf', 'LDL.pdf', 'PRM.pdf']
    
    for pdf_file in pdf_files:
        print(f"\n{'='*50}")
        print(f"EXTRACTING TEXT FROM: {pdf_file}")
        print(f"{'='*50}")
        
        text = extract_pdf_text(pdf_file)
        print(text[:2000])  # First 2000 characters
        print(f"\n[... truncated for brevity ...]")

if __name__ == "__main__":
    main()
