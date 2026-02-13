param(
    [long]$RunId = 21949110133,
    [int]$IntervalSeconds = 6,
    [int]$MaxAttempts = 20
)

Write-Host "Monitoring workflow run $RunId (up to $MaxAttempts attempts, $IntervalSeconds s interval)"
for ($i = 1; $i -le $MaxAttempts; $i++) {
    try {
        $r = Invoke-RestMethod "https://api.github.com/repos/Sujalshetty01/final-year-project/actions/runs/$RunId" -UseBasicParsing
    } catch {
        Write-Host "API request failed: $_"
        exit 2
    }
    Write-Host "Attempt $i/$MaxAttempts - status: $($r.status) - conclusion: $($r.conclusion)"
    if ($r.status -ne 'in_progress' -and $r.status -ne 'queued') {
        $r | ConvertTo-Json -Depth 5
        exit 0
    }
    Start-Sleep -Seconds $IntervalSeconds
}

Write-Host "Timed out waiting for run $RunId to finish"
exit 3
