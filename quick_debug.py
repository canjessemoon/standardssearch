import requests
import json

def test_document_structure():
    """Test what's actually in the document index"""
    try:
        # Get document list
        response = requests.get("http://localhost:5000/api/documents")
        docs = response.json()
        print(f"Available documents: {len(docs['documents'])}")
        
        # Search for accidental activation to see what sections we get
        search_data = {
            "query": '"accidental activation"',
            "documents": ["MIL-STD-1472H.pdf"]
        }
        
        response = requests.post("http://localhost:5000/api/search", json=search_data)
        results = response.json()
        
        print(f"\nSearch results: {results['total_matches']} matches")
        
        # Look at first 10 results to see page/section distribution
        unique_pages = set()
        unique_sections = set()
        
        for i, result in enumerate(results['results'][:10]):
            print(f"\nResult {i+1}:")
            print(f"  Page: {result['page']}")
            print(f"  Section: {result['section_number']} - {result['section_title']}")
            print(f"  Context preview: {result['context'][:100]}...")
            
            unique_pages.add(result['page'])
            unique_sections.add((result['section_number'], result['section_title']))
        
        print(f"\nUnique pages in first 10 results: {sorted(unique_pages)}")
        print(f"Unique sections in first 10 results: {len(unique_sections)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_document_structure()
