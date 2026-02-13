# Auto demo check and restart script
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\auto_demo_check.ps1

Write-Host "Auto-demo check starting..."

$backend = "http://localhost:8000/api/v1"
$frontend = "http://localhost:8082"

function Check-Endpoint($url) {
    try {
        $r = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
        Write-Host "OK: $url"
        Write-Host ($r | ConvertTo-Json -Depth 3)
        return $true
    } catch {
        Write-Host "ERROR: $url - $($_.Exception.Message)"
        return $false
    }
}

Write-Host "\n-- Checking backend endpoints --"
Check-Endpoint "$backend/health"
Check-Endpoint "$backend/ready"
Check-Endpoint "$backend/stats"

Write-Host "\n-- Fetching frontend assets --"
try {
    $cfg = (Invoke-WebRequest -Uri "$frontend/js/config.js" -UseBasicParsing -TimeoutSec 10).Content
    $cfg | Out-File -FilePath ".\scripts\latest_config.js" -Encoding utf8
    Write-Host "Fetched frontend config.js -> .\scripts\latest_config.js"
} catch {
    Write-Host "Failed to fetch frontend config.js: $($_.Exception.Message)"
}

try {
    $apijs = (Invoke-WebRequest -Uri "$frontend/js/api.js" -UseBasicParsing -TimeoutSec 10).Content
    $apijs | Out-File -FilePath ".\scripts\latest_api.js" -Encoding utf8
    Write-Host "Fetched frontend api.js -> .\scripts\latest_api.js"
} catch {
    Write-Host "Failed to fetch frontend api.js: $($_.Exception.Message)"
}

Write-Host "\n-- Restarting backend and frontend (docker compose restart) --"
try {
    docker compose restart backend frontend
    Write-Host "Restart command issued. Waiting 5s for services to settle..."
    Start-Sleep -Seconds 5
} catch {
    Write-Host "Failed to run 'docker compose restart': $($_.Exception.Message)"
}

Write-Host "\n-- Re-checking backend health --"
Check-Endpoint "$backend/health"

Write-Host "\nAutomation finished. Please hard-refresh your browser (Ctrl+F5) and open DevTools -> Console/Network. If any JS errors or network failures occur, save Console output and paste it here."

try {
    Write-Host "Opening demo in default browser: $frontend"
    Start-Process $frontend
} catch {
    Write-Host "Failed to open browser: $($_.Exception.Message)"
}

exit 0
