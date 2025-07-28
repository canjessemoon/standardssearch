# LLM Setup Script for Document Search Tool
# This script installs the required packages for AI-powered search

Write-Host "=== Setting up LLM capabilities for Document Search Tool ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "❌ Error: Please run this script from the project root directory (c:\dev\Standards-Search)" -ForegroundColor Red
    exit 1
}

Write-Host "1. Installing LLM dependencies..." -ForegroundColor Yellow

# Navigate to backend directory
cd backend

try {
    # Install the LLM packages
    Write-Host "   Installing OpenAI package..." -ForegroundColor Gray
    pip install openai>=1.0.0
    
    Write-Host "   Installing tiktoken for token counting..." -ForegroundColor Gray  
    pip install tiktoken>=0.5.0
    
    Write-Host "   Installing scikit-learn for similarity calculations..." -ForegroundColor Gray
    pip install scikit-learn>=1.3.0
    
    Write-Host "✅ All LLM dependencies installed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error installing packages: $($_.Exception.Message)" -ForegroundColor Red
    cd ..
    exit 1
}

# Go back to project root
cd ..

Write-Host "`n2. Setting up OpenAI API Key..." -ForegroundColor Yellow
Write-Host "   You'll need an OpenAI API key to use the AI features." -ForegroundColor Gray
Write-Host "   Get your API key from: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host ""

$apiKey = Read-Host "   Enter your OpenAI API key (or press Enter to skip)"

if ($apiKey) {
    # Set environment variable for current session
    $env:OPENAI_API_KEY = $apiKey
    
    # Also set it persistently for the user
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $apiKey, "User")
    
    Write-Host "✅ API key configured!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Skipped API key setup. You can set it later with:" -ForegroundColor Yellow
    Write-Host "   set OPENAI_API_KEY=your_key_here" -ForegroundColor Gray
}

Write-Host "`n3. Testing LLM setup..." -ForegroundColor Yellow

# Test if we can import the required modules
try {
    $testScript = @"
import sys
sys.path.append('backend')
try:
    from app.llm_search import LLMSearchEngine
    print("✅ LLM modules imported successfully")
    
    # Test API key if provided
    if '$apiKey':
        try:
            engine = LLMSearchEngine()
            print("✅ LLM engine initialized successfully")
        except Exception as e:
            print(f"⚠️  LLM engine test failed: {e}")
    else:
        print("⚠️  API key not provided - LLM engine not tested")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"@

    $testScript | python
    
} catch {
    Write-Host "❌ Error testing setup: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. Start the backend server: cd backend && python -m app.main" -ForegroundColor White
Write-Host "2. Start the frontend: npm run dev" -ForegroundColor White
Write-Host "3. Click the '🤖 AI Assistant' tab in the web interface" -ForegroundColor White
Write-Host ""
Write-Host "💡 The AI assistant can:" -ForegroundColor Cyan
Write-Host "   • Answer questions in natural language" -ForegroundColor White
Write-Host "   • Find relevant document sections automatically" -ForegroundColor White
Write-Host "   • Provide summaries and explanations" -ForegroundColor White
Write-Host "   • Work with technical documents in context" -ForegroundColor White
Write-Host ""
Write-Host "📝 Example questions to try:" -ForegroundColor Cyan
Write-Host "   'What are the safety requirements for head clearance?'" -ForegroundColor Gray
Write-Host "   'Explain the procedures for accidental activation prevention'" -ForegroundColor Gray
Write-Host "   'What are the noise level standards for equipment?'" -ForegroundColor Gray
