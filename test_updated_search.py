#!/usr/bin/env python3
"""
Test the updated search functionality locally without running the server
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

def test_updated_search():
    print("Testing updated search functionality...")
    
    try:
        # Import the functions from main.py
        from main import index_documents, document_index, search_in_text, parse_search_query
        
        # Index documents
        print("Indexing documents...")
        index_documents()
        
        print(f"Documents indexed: {len(document_index)}")
        
        # Test search for "head clearance"
        if "MIL-STD-1472H.pdf" in document_index:
            doc_data = document_index["MIL-STD-1472H.pdf"]
            print(f"MIL-STD-1472H.pdf has {len(doc_data['sections'])} sections")
            
            # Parse the search query
            search_terms = parse_search_query('"head clearance"')
            print(f"Search terms: {search_terms}")
            
            # Search through each section and show page information
            matches_found = 0
            for i, section in enumerate(doc_data['sections']):
                section_content = '\n'.join(section['content'])
                matches = search_in_text(section_content, search_terms)
                
                if matches:
                    matches_found += len(matches)
                    print(f"\n*** MATCH FOUND in Section {i+1} ***")
                    print(f"Section title: {section['title']}")
                    print(f"Section number: {section['number']}")
                    print(f"Section page: {section['page']}")
                    print(f"Matches: {len(matches)}")
                    
                    for match in matches:
                        print(f"Match type: {match['matched_term']}")
                        print(f"Context (first 150 chars): {match['context'][:150]}...")
                        print()
                
                # Also check if the words appear separately
                if 'head' in section_content.lower() and 'clearance' in section_content.lower():
                    print(f"Section {i+1} (page {section['page']}) contains both 'head' and 'clearance' separately")
            
            print(f"\nTotal matches found: {matches_found}")
            
        else:
            print("MIL-STD-1472H.pdf not found in index")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_search()
