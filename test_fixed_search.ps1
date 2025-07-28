# Test the fixed search functionality
Write-Host "=== TESTING FIXED SEARCH FUNCTIONALITY ===" -ForegroundColor Green

# Test 1: Individual words search
Write-Host "`n1. Testing individual words search (no quotes)..." -ForegroundColor Yellow
$body1 = @{
    query = "accidental activation"
    documents = @()
    language = "en"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $body1
    Write-Host "✓ Individual words: $($response1.total_matches) matches" -ForegroundColor Green
    
    if ($response1.results.Count -gt 0) {
        $sample = $response1.results[0]
        Write-Host "Sample match: $($sample.matched_term)" -ForegroundColor Cyan
        Write-Host "Context: $($sample.context.Substring(0, [Math]::Min(100, $sample.context.Length)))..." -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Individual words search failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Exact phrase search
Write-Host "`n2. Testing exact phrase search (with quotes)..." -ForegroundColor Yellow
$body2 = @{
    query = '"accidental activation"'
    documents = @()
    language = "en"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $body2
    Write-Host "✓ Exact phrase: $($response2.total_matches) matches" -ForegroundColor Green
    
    if ($response2.results.Count -gt 0) {
        Write-Host "First few exact phrase matches:" -ForegroundColor Cyan
        $response2.results | Select-Object -First 3 | ForEach-Object {
            Write-Host "  Page $($_.page): $($_.matched_term)" -ForegroundColor White
            Write-Host "  Context: $($_.context.Substring(0, [Math]::Min(150, $_.context.Length)))..." -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        Write-Host "No exact phrase matches found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Exact phrase search failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Analysis
Write-Host "`n=== ANALYSIS ===" -ForegroundColor Green
if ($response1.total_matches -gt $response2.total_matches) {
    Write-Host "✓ Good: Exact phrase search returns fewer matches than individual words" -ForegroundColor Green
    Write-Host "  Individual words: $($response1.total_matches)" -ForegroundColor White
    Write-Host "  Exact phrase: $($response2.total_matches)" -ForegroundColor White
} else {
    Write-Host "⚠ Issue: Exact phrase search should return fewer matches" -ForegroundColor Yellow
}
