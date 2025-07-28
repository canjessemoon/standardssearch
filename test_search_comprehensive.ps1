# Comprehensive Search Testing Script
Write-Host "=== COMPREHENSIVE SEARCH TESTING ===" -ForegroundColor Green
Write-Host "Testing page attribution fix across multiple search terms" -ForegroundColor Yellow
Write-Host ""

# Test terms
$testTerms = @(
    "accidental activation",
    "safety",
    "design", 
    "human factors",
    "emergency"
)

foreach ($term in $testTerms) {
    Write-Host "=== Testing: '$term' ===" -ForegroundColor Cyan
    
    # Create JSON payload
    $body = @{
        query = $term
        documents = @()
        language = "en"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -ContentType "application/json" -Body $body
        
        Write-Host "Total matches: $($response.total_matches)" -ForegroundColor White
        
        # Analyze page distribution
        $pageCount = @{}
        $results = $response.results | Select-Object -First 10
        
        foreach ($result in $results) {
            $page = $result.page
            if ($pageCount.ContainsKey($page)) {
                $pageCount[$page]++
            } else {
                $pageCount[$page] = 1
            }
        }
        
        Write-Host "Page distribution (first 10 results):" -ForegroundColor Yellow
        $sortedPages = $pageCount.Keys | Sort-Object {[int]$_}
        foreach ($page in $sortedPages) {
            Write-Host "  Page $page`: $($pageCount[$page]) matches" -ForegroundColor White
        }
        
        # Show sample result
        if ($response.results.Count -gt 0) {
            $sample = $response.results[0]
            Write-Host "Sample result: Page $($sample.page), Section $($sample.section_number)" -ForegroundColor Green
            $contextPreview = $sample.context.Substring(0, [Math]::Min(100, $sample.context.Length))
            Write-Host "Context preview: $contextPreview..." -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "Error testing '$term': $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=== Test Complete ===" -ForegroundColor Green
