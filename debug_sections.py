#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

try:
    from main import extract_text_from_pdf
    print("Successfully imported extract_text_from_pdf")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

def debug_sections():
    pdf_path = "backend/documents/MIL-STD-1472H.pdf"
    print(f"Debugging sections for: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    try:
        extracted_data = extract_text_from_pdf(pdf_path)
        print(f"Extraction completed successfully")
    except Exception as e:
        print(f"Extraction error: {e}")
        return
    
    print(f"\nTotal sections created: {len(extracted_data['sections'])}")
    print(f"Total text length: {len(extracted_data['full_text'])}")
    
    # Show first 5 sections with their page numbers
    for i, section in enumerate(extracted_data['sections'][:5]):
        print(f"\nSection {i+1}:")
        print(f"  Title: {section['title']}")
        print(f"  Number: {section['number']}")
        print(f"  Page: {section['page']}")
        print(f"  Content length: {len(section['content'][0]) if section['content'] else 0}")

if __name__ == "__main__":
    print("Starting debug script...")
    debug_sections()
    print("Debug script completed.")
