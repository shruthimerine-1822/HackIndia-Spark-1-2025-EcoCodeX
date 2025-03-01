Write-Host "Starting Federated Learning Tests..." -ForegroundColor Green

# Train Model on Local Server
Write-Host "1. Training Model on Local Server..."
$trainResponse = Invoke-WebRequest -Uri "http://192.168.72.76:5001/train" -Method Post -TimeoutSec 30
Write-Host $trainResponse.Content
Write-Host ""

# Send Local Model to Central Server
Write-Host "2. Sending Model to Central Server..."
$sendResponse = Invoke-WebRequest -Uri "http://192.168.72.76:5001/send_model" -Method Post -TimeoutSec 30
Write-Host $sendResponse.Content
Write-Host ""

# Aggregate Model on Central Server
Write-Host "3. Aggregating Model on Central Server..."
$aggregateResponse = Invoke-WebRequest -Uri "http://192.168.72.183:5000/aggregate" -Method Post -TimeoutSec 30
Write-Host $aggregateResponse.Content
Write-Host ""

# Fetch Updated Global Model at Local Server
Write-Host "4. Fetching Updated Global Model at Local Server..."
$fetchResponse = Invoke-WebRequest -Uri "http://192.168.72.76:5001/fetch_global_model" -Method Get -TimeoutSec 30
Write-Host $fetchResponse.Content
Write-Host ""

Write-Host "✅ All Tests Completed Successfully!" -ForegroundColor Cyan
