# Test script for the updated search functionality
Write-Host "Testing updated search functionality..."

try {
    # Test health endpoint
    Write-Host "Testing health endpoint..."
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -ErrorAction Stop
    Write-Host "Health: $($health.status), Documents: $($health.documents_indexed)"
    
    # Test exact phrase search for "head clearance"
    Write-Host "`nTesting exact phrase search for 'head clearance'..."
    $searchBody = @{
        query = '"head clearance"'
        documents = @("MIL-STD-1472H.pdf")
    } | ConvertTo-Json
    
    $searchResult = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -Body $searchBody -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "Total matches: $($searchResult.total_matches)"
    Write-Host "Search terms: $($searchResult.search_terms -join ', ')"
    
    if ($searchResult.results.Count -gt 0) {
        Write-Host "`nFirst match details:"
        $firstMatch = $searchResult.results[0]
        Write-Host "Document: $($firstMatch.document)"
        Write-Host "Page: $($firstMatch.page)"
        Write-Host "Section: $($firstMatch.section_title)"
        Write-Host "Section Number: $($firstMatch.section_number)"
        Write-Host "Match Type: $($firstMatch.matched_term)"
        Write-Host "Context: $($firstMatch.context.Substring(0, [Math]::Min(200, $firstMatch.context.Length)))..."
    }
    
    # Test individual word search to compare
    Write-Host "`nTesting individual word search for 'head clearance'..."
    $individualSearchBody = @{
        query = 'head clearance'
        documents = @("MIL-STD-1472H.pdf")
    } | ConvertTo-Json
    
    $individualResult = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -Body $individualSearchBody -ContentType "application/json" -ErrorAction Stop
    Write-Host "Individual word search total matches: $($individualResult.total_matches)"
    
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Full error: $($_.Exception)"
}
