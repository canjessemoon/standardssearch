# Test script for the improved exact phrase search functionality

Write-Host "Testing Backend API Search Functionality" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Test 1: Health check
Write-Host "`n1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET
    Write-Host "✓ Backend is healthy with $($health.documents_indexed) documents indexed" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Simple search (individual words)
Write-Host "`n2. Testing simple search for 'whole body vibration'..." -ForegroundColor Yellow
try {
    $simpleSearch = @{
        query = "whole body vibration"
        language = "en"
    } | ConvertTo-Json
    
    $result1 = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $simpleSearch
    Write-Host "✓ Simple search returned $($result1.total_matches) matches" -ForegroundColor Green
} catch {
    Write-Host "✗ Simple search failed: $_" -ForegroundColor Red
}

# Test 3: Exact phrase search (with quotes)
Write-Host "`n3. Testing exact phrase search for '\"whole body vibration\"'..." -ForegroundColor Yellow
try {
    $exactSearch = @{
        query = '"whole body vibration"'
        language = "en"
    } | ConvertTo-Json
    
    $result2 = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $exactSearch
    Write-Host "✓ Exact phrase search returned $($result2.total_matches) matches" -ForegroundColor Green
    
    # Show the difference
    if ($result1.total_matches -gt $result2.total_matches) {
        Write-Host "✓ Exact phrase search is working correctly (fewer matches than individual words)" -ForegroundColor Green
        Write-Host "  Individual words: $($result1.total_matches) matches" -ForegroundColor Cyan
        Write-Host "  Exact phrase: $($result2.total_matches) matches" -ForegroundColor Cyan
    } else {
        Write-Host "⚠ Exact phrase search may not be working as expected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Exact phrase search failed: $_" -ForegroundColor Red
}

# Test 4: Show some sample results
Write-Host "`n4. Sample exact phrase matches:" -ForegroundColor Yellow
if ($result2.results.Count -gt 0) {
    $result2.results | Select-Object -First 3 | ForEach-Object {
        Write-Host "  Document: $($_.document)" -ForegroundColor Cyan
        Write-Host "  Section: $($_.section_title)" -ForegroundColor Cyan
        Write-Host "  Match: $($_.matched_term)" -ForegroundColor Cyan
        Write-Host "  Context: $($_.context.Substring(0, [Math]::Min(100, $_.context.Length)))..." -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Host "  No exact phrase matches found" -ForegroundColor Yellow
}

Write-Host "`nSearch functionality test completed!" -ForegroundColor Green
