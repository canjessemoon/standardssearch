#!/usr/bin/env python3
"""
Simple debug script to find head clearance location
"""

import pdfplumber
import re

def find_head_clearance():
    pdf_path = r"C:\dev\Standards-Search\backend\documents\MIL-STD-1472H.pdf"
    search_phrase = "head clearance"
    
    print(f"Searching for '{search_phrase}' in MIL-STD-1472H.pdf")
    print("=" * 60)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")
            
            found_pages = []
            
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and search_phrase.lower() in page_text.lower():
                        found_pages.append(page_num + 1)
                        print(f"\nFOUND on page {page_num + 1}")
                        
                        # Find the specific line
                        lines = page_text.split('\n')
                        for i, line in enumerate(lines):
                            if search_phrase.lower() in line.lower():
                                print(f"Line {i + 1}: {line.strip()}")
                                
                                # Show context
                                start_idx = max(0, i - 2)
                                end_idx = min(len(lines), i + 3)
                                print("Context:")
                                for j in range(start_idx, end_idx):
                                    marker = " >>> " if j == i else "     "
                                    print(f"{marker}{lines[j].strip()}")
                                print()
                        
                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {e}")
            
            print(f"\nSummary: Found on pages: {found_pages}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_head_clearance()
