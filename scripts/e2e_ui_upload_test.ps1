# End-to-end simulated UI upload test
# Sends a FormData multipart POST to the frontend-backed analyze endpoint

$api = 'http://localhost:8000/api/v1'
$sample = 'sample_flows.json'

if (-not (Test-Path $sample)) {
    Write-Host "Sample file $sample not found"
    exit 1
}

# The frontend's JS sends 'file' form field; backend accepts JSON flows endpoint, so send JSON file as 'file' to /analyze
$boundary = [System.Guid]::NewGuid().ToString()
$content = Get-Content -Raw $sample
$lf = "`r`n"
$body = "--$boundary$lf" + "Content-Disposition: form-data; name=`"file`"; filename=`"$sample`"$lf" + "Content-Type: application/json$lf$lf" + $content + "$lf" + "--$boundary--$lf"

$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$wc = New-Object System.Net.WebClient
$wc.Headers.Add("Content-Type","multipart/form-data; boundary=$boundary")
try {
    $resp = $wc.UploadData("$api/analyze", "POST", $bytes)
    $text = [System.Text.Encoding]::UTF8.GetString($resp)
    Write-Host "Response:`n$text"
    exit 0
} catch {
    Write-Host "Upload failed: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        try { $_.Exception.Response.GetResponseStream() | ForEach-Object { $sr = New-Object System.IO.StreamReader($_); Write-Host $sr.ReadToEnd() } } catch {}
    }
    exit 2
}
