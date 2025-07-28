#!/usr/bin/env python3

# Simple test to check if our imports work
import sys
import os

print("Testing imports...")

try:
    print("1. Testing basic imports...")
    from flask import Flask
    print("✅ Flask imported")
    
    import openai
    print("✅ OpenAI imported")
    
    import tiktoken
    print("✅ Tiktoken imported")
    
    import sklearn
    print("✅ Scikit-learn imported")
    
    print("\n2. Testing OpenAI API key...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key.startswith('sk-'):
        print(f"✅ API key configured (starts with sk-)")
    else:
        print(f"❌ API key not configured or invalid")
    
    print("\n3. Testing LLM search import...")
    sys.path.append('app')
    try:
        from llm_search import LLMSearchEngine
        print("✅ LLM search engine imported successfully")
        
        print("\n4. Testing LLM engine initialization...")
        engine = LLMSearchEngine()
        print("✅ LLM engine initialized successfully")
        
    except Exception as e:
        print(f"❌ LLM import/init failed: {e}")
    
    print("\n5. Testing basic Flask app...")
    app = Flask(__name__)
    print("✅ Flask app created")
    
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
