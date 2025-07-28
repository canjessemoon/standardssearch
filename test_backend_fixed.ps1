# Wait for server to start and test
Start-Sleep -Seconds 8

Write-Host "Testing backend server..."

try {
    # Test health endpoint
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 10
    Write-Host "SUCCESS: Server is running!"
    Write-Host "Status: $($health.status)"
    Write-Host "Documents indexed: $($health.documents_indexed)"
      # Test search functionality
    Write-Host "`nTesting search functionality..."
    $searchBody = @{
        query = '"accidental activation"'
        documents = @("MIL-STD-1472H.pdf")
    } | ConvertTo-Json
    
    $searchResult = Invoke-RestMethod -Uri "http://localhost:5000/api/search" -Method POST -Body $searchBody -ContentType "application/json" -TimeoutSec 10
    
    Write-Host "Search completed successfully!"
    Write-Host "Total matches: $($searchResult.total_matches)"
    
    if ($searchResult.results.Count -gt 0) {
        $result = $searchResult.results[0]
        Write-Host "`n=== SEARCH RESULT DETAILS ==="
        Write-Host "Document: $($result.document)"
        Write-Host "Page: $($result.page)"
        Write-Host "Section: $($result.section_title)"
        Write-Host "Section Number: $($result.section_number)"
        Write-Host "Match Type: $($result.matched_term)"
        Write-Host "Context Preview: $($result.context.Substring(0, [Math]::Min(150, $result.context.Length)))..."
        
        # Check if page and section look correct
        if ($result.page -eq 1 -and $result.section_number -eq "1") {
            Write-Host "`nWARNING: Result shows page 1, section 1 - this may indicate the page/section extraction issue still exists."
        } else {
            Write-Host "`nPage and section information appears to be working correctly."
        }
    } else {
        Write-Host "No matches found."
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    Write-Host "Full error details:"
    Write-Host $_.Exception
}
