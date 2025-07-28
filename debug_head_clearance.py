#!/usr/bin/env python3
"""
Debug script to find the exact location of "head clearance" in MIL-STD-1472H.pdf
"""

import os
import sys
import re
import pdfplumber
import fitz  # PyMuPDF

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))
from main import clean_and_normalize_text, create_flexible_phrase_pattern

def find_head_clearance_location():
    """Find the exact location of 'head clearance' in the PDF"""
    
    pdf_path = r"C:\dev\Standards-Search\backend\documents\MIL-STD-1472H.pdf"
    search_phrase = "head clearance"
    
    print(f"Searching for '{search_phrase}' in {os.path.basename(pdf_path)}")
    print("=" * 80)
    
    # Method 1: PDFPlumber page-by-page search
    print("\n1. PDFPlumber page-by-page search:")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")
            
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    cleaned_text = clean_and_normalize_text(page_text)
                    
                    # Check for exact phrase
                    if search_phrase.lower() in cleaned_text.lower():
                        print(f"\n*** FOUND on page {page_num + 1} ***")
                        
                        # Find the context around the match
                        lines = cleaned_text.split('\n')
                        for i, line in enumerate(lines):
                            if search_phrase.lower() in line.lower():
                                start_idx = max(0, i - 2)
                                end_idx = min(len(lines), i + 3)
                                context_lines = lines[start_idx:end_idx]
                                
                                print("Context:")
                                for j, context_line in enumerate(context_lines):
                                    marker = " >>> " if j == (i - start_idx) else "     "
                                    print(f"{marker}{context_line}")
                                print()
                        
                        # Also check for proximity matches
                        pattern = create_flexible_phrase_pattern(search_phrase)
                        matches = re.finditer(pattern, cleaned_text, re.IGNORECASE)
                        for match in matches:
                            start = max(0, match.start() - 100)
                            end = min(len(cleaned_text), match.end() + 100)
                            context = cleaned_text[start:end]
                            print(f"Regex match context: ...{context}...")
                            print()
    
    except Exception as e:
        print(f"PDFPlumber error: {e}")
    
    # Method 2: PyMuPDF search
    print("\n2. PyMuPDF search:")
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text:
                cleaned_text = clean_and_normalize_text(text)
                
                if search_phrase.lower() in cleaned_text.lower():
                    print(f"\n*** PyMuPDF FOUND on page {page_num + 1} ***")
                    
                    # Find the context
                    lines = cleaned_text.split('\n')
                    for i, line in enumerate(lines):
                        if search_phrase.lower() in line.lower():
                            start_idx = max(0, i - 2)
                            end_idx = min(len(lines), i + 3)
                            context_lines = lines[start_idx:end_idx]
                            
                            print("Context:")
                            for j, context_line in enumerate(context_lines):
                                marker = " >>> " if j == (i - start_idx) else "     "
                                print(f"{marker}{context_line}")
                            print()
        
        doc.close()
        
    except Exception as e:
        print(f"PyMuPDF error: {e}")
    
    # Method 3: Check what our current indexing system thinks
    print("\n3. Current indexing system results:")
    try:
        # Import the indexed data
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))
        from main import document_index, search_in_text, search_in_text_enhanced
        
        doc_filename = "MIL-STD-1472H.pdf"
        if doc_filename in document_index:
            doc_data = document_index[doc_filename]
            print(f"Indexed sections: {len(doc_data['sections'])}")
            
            search_terms = [{'text': search_phrase, 'is_exact': True}]
            
            for i, section in enumerate(doc_data['sections']):
                section_content = '\n'.join(section['content'])
                matches = search_in_text(section_content, search_terms)
                
                if not matches:
                    # Try enhanced search
                    matches = search_in_text_enhanced(section_content, search_terms, debug_mode=True)
                
                if matches:
                    print(f"\n*** INDEXED MATCH in section {i + 1} ***")
                    print(f"Section title: {section['title']}")
                    print(f"Section number: {section['number']}")
                    print(f"Section page: {section['page']}")
                    print(f"Matches found: {len(matches)}")
                    
                    for match in matches:
                        print(f"Match type: {match['matched_term']}")
                        print(f"Context: {match['context'][:200]}...")
                        print()
        else:
            print(f"Document {doc_filename} not found in index")
            
    except Exception as e:
        print(f"Indexing check error: {e}")

if __name__ == "__main__":
    find_head_clearance_location()
