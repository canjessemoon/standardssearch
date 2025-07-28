#!/usr/bin/env python3
"""
Simple test to check if we can import and run the backend code
"""

try:
    print("Testing import...")
    import sys
    import os
    
    # Add backend path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'app')
    print(f"Adding path: {backend_path}")
    sys.path.insert(0, backend_path)
    
    # Try to import
    print("Importing main module...")
    import main
    
    print("Import successful!")
    
    # Check if we can index
    print("Testing indexing...")
    main.index_documents()
    
    print(f"Documents indexed: {len(main.document_index)}")
    
    for doc_name in main.document_index:
        doc_data = main.document_index[doc_name]
        print(f"- {doc_name}: {len(doc_data['sections'])} sections")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
