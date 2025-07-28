import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from main import extract_text_from_pdf, clean_and_normalize_text
import re

# Extract text from MIL-STD-1472H
pdf_path = "backend/documents/MIL-STD-1472H.pdf"
print(f"Extracting text from {pdf_path}...")

document_data = extract_text_from_pdf(pdf_path)
print(f"Document title: {document_data['title']}")
print(f"Number of sections: {len(document_data['sections'])}")

# Search for sections that might contain "head clearance"
target_terms = ["head", "clearance", "5.6.2", "182"]

print("\n=== Searching for relevant sections ===")
for i, section in enumerate(document_data['sections']):
    section_text = ' '.join(section['content']).lower()
    section_title = section['title'].lower()
    
    # Check if this section might contain our target content
    if any(term in section_text or term in section_title for term in target_terms):
        print(f"\n--- Section {i+1}: {section['title']} (Page {section.get('page', 'Unknown')}) ---")
        print(f"Section number: {section['number']}")
        
        # Look for "head" and "clearance" in this section
        content = ' '.join(section['content'])
        if 'head' in content.lower() and 'clearance' in content.lower():
            print("*** FOUND BOTH 'head' AND 'clearance' ***")
            
            # Extract context around these words
            sentences = re.split(r'[.!?]+', content)
            for j, sentence in enumerate(sentences):
                if 'head' in sentence.lower() and 'clearance' in sentence.lower():
                    print(f"  Match sentence {j+1}: {sentence.strip()}")
                elif 'head' in sentence.lower() or 'clearance' in sentence.lower():
                    print(f"  Related sentence {j+1}: {sentence.strip()}")
        
        # Show first few lines of content for context
        content_lines = content.split('\n')[:5]
        for line in content_lines:
            if line.strip():
                print(f"  Content: {line.strip()[:100]}...")
                break

# Also search the full text directly
print("\n=== Searching full document text ===")
full_text = document_data['full_text'].lower()
if 'head clearance' in full_text:
    print("✓ Found 'head clearance' in full text")
    # Find all occurrences
    import re
    matches = list(re.finditer(r'[^.]*head clearance[^.]*', full_text, re.IGNORECASE))
    for i, match in enumerate(matches[:3]):  # Show first 3 matches
        print(f"  Match {i+1}: {match.group().strip()}")
else:
    print("✗ 'head clearance' not found in full text")
    
    # Check for variations
    variations = [
        'head-clearance', 'headclearance', 'head\sclearance', 'head\s+clearance',
        'head.*clearance', 'clearance.*head'
    ]
    
    for variation in variations:
        matches = re.findall(variation, full_text, re.IGNORECASE)
        if matches:
            print(f"  Found variation '{variation}': {matches[:3]}")

# Check if the words appear separately
head_count = full_text.count('head')
clearance_count = full_text.count('clearance')
print(f"\nWord frequency:")
print(f"  'head': {head_count} occurrences")
print(f"  'clearance': {clearance_count} occurrences")
