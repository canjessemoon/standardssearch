#!/usr/bin/env python3
"""Test script to verify LLM setup"""

import os
import sys

# Set the API key
# REMOVED OPENAI API KEY FOR SECURITY

print("🧪 Testing LLM Setup...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Test package imports
try:
    import openai
    print("✅ OpenAI package imported successfully")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")

try:
    import tiktoken
    print("✅ Tiktoken package imported successfully")
except ImportError as e:
    print(f"❌ Tiktoken import failed: {e}")

try:
    import sklearn
    print("✅ Scikit-learn package imported successfully")
except ImportError as e:
    print(f"❌ Scikit-learn import failed: {e}")

# Test API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ API key configured (starts with: {api_key[:10]}...)")
else:
    print("❌ No API key found")

# Test LLM search module
sys.path.append('backend')
try:
    from llm_search import LLMSearchEngine
    print("✅ LLM search module imported successfully")
    
    # Test engine creation
    try:
        engine = LLMSearchEngine()
        print("✅ LLM engine created successfully")
        print(f"   Model: {engine.model}")
        print(f"   Embedding model: {engine.embedding_model}")
    except Exception as e:
        print(f"❌ LLM engine creation failed: {e}")
        
except ImportError as e:
    print(f"❌ LLM search module import failed: {e}")

print("\n🚀 Setup test complete!")
