# Start backend server with LLM capabilities
$env:OPENAI_API_KEY="***REPLACED***"

Write-Host "Starting backend server with LLM capabilities..."
Write-Host "API Key configured: $($env:OPENAI_API_KEY.Substring(0,20))..."

# Change to correct directory and start server
Set-Location "c:\dev\Standards-Search"
& "C:\dev\Standards-Search\.venv\Scripts\python.exe" "backend\app\main.py"
