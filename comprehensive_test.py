import requests
import json

# Test various search terms to verify page attribution
test_terms = ['accidental activation', 'safety', 'design', 'human factors', 'emergency']

print("=== COMPREHENSIVE SEARCH TESTING ===")
print("Testing page attribution fix across multiple search terms\n")

for term in test_terms:
    print(f'=== Testing: "{term}" ===')
    try:
        response = requests.get(f'http://localhost:5000/api/search?query={term}&limit=5')
        if response.status_code == 200:
            data = response.json()
            print(f'Total matches: {data["total_matches"]}')
            
            # Show page distribution for first few results
            page_counts = {}
            for result in data['results'][:10]:  # First 10 results
                page = result['page']
                page_counts[page] = page_counts.get(page, 0) + 1
            
            print('Page distribution (first 10 results):')
            for page in sorted(page_counts.keys()):
                print(f'  Page {page}: {page_counts[page]} matches')
                
            # Show a sample result with details
            if data['results']:
                sample = data['results'][0]
                print(f'Sample result: Page {sample["page"]}, Section {sample["section"]}')
                print(f'Context preview: {sample["context"][:100]}...')
        else:
            print(f'Error: HTTP {response.status_code}')
    except Exception as e:
        print(f'Error testing "{term}": {e}')
    print()

print("=== Test Complete ===")
