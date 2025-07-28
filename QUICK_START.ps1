# Quick Start Script for Resuming Work
# Run this when you return to immediately test the fixes

Write-Host "=== BILINGUAL DOCUMENT SEARCH - QUICK START ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Check if backend is running
Write-Host "1. Checking backend server status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 5
    Write-Host "✅ Backend is running - $($health.documents_indexed) documents indexed" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding - need to start it" -ForegroundColor Red
    Write-Host "Run: cd c:\dev\Standards-Search\backend && .\start_backend.bat" -ForegroundColor Yellow
    exit
}

# Test the critical "accidental activation" fix
Write-Host "`n2. Testing the critical 'accidental activation' fix..." -ForegroundColor Yellow
try {
    $testQuery = '{"query":"\"accidental activation\"","documents":[],"language":"en"}'
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $testQuery
    
    Write-Host "✅ Search successful!" -ForegroundColor Green
    Write-Host "   Total matches: $($response.total_matches)" -ForegroundColor White
    
    if ($response.total_matches -lt 100) {
        Write-Host "✅ GOOD: Match count is reasonable (was 3726 before fix)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: Match count seems high - may need further tuning" -ForegroundColor Yellow
    }
    
    # Show sample results
    if ($response.results.Count -gt 0) {
        Write-Host "`n   Sample result:" -ForegroundColor Gray
        $first = $response.results[0]
        Write-Host "   Document: $($first.document)" -ForegroundColor White
        Write-Host "   Page: $($first.page)" -ForegroundColor White
        Write-Host "   Context: $($first.context.Substring(0, [Math]::Min(100, $first.context.Length)))..." -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Search test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test page attribution fix
Write-Host "`n3. Testing page attribution fix..." -ForegroundColor Yellow
try {
    $testQuery = '{"query":"clearance","documents":[],"language":"en"}'
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $testQuery
    
    $pages = $response.results | ForEach-Object { $_.page } | Sort-Object -Unique
    Write-Host "✅ Search returned results from pages: $($pages -join ', ')" -ForegroundColor Green
    
    if ($pages.Count -gt 1) {
        Write-Host "✅ GOOD: Results span multiple pages (page attribution fix working)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: All results from same page - check page attribution" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Page attribution test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "✓ Run comprehensive tests: .\test_search_comprehensive.ps1" -ForegroundColor White
Write-Host "✓ Start frontend: npm run dev" -ForegroundColor White
Write-Host "✓ Test frontend-backend integration" -ForegroundColor White
Write-Host "✓ Review PROJECT_STATUS_SUMMARY.md for details" -ForegroundColor White

Write-Host "`n🚀 Ready to continue development!" -ForegroundColor Green
