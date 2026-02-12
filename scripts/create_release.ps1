param(
  [string]$OutZip = "release-v1.0.0.zip"
)

if (-not (Test-Path -Path paper\ieee_paper_main.pdf)) {
  Write-Host "Warning: paper/ieee_paper_main.pdf not found"
}

$out = "release-artifacts"
if (Test-Path $out) { Remove-Item -Recurse -Force $out }
New-Item -ItemType Directory -Path $out | Out-Null

if (Test-Path "paper\ieee_paper_main.pdf") { Copy-Item "paper\ieee_paper_main.pdf" $out }
if (Test-Path "paper\build.log") { Copy-Item "paper\build.log" $out }
if (Test-Path "docs") { Copy-Item -Recurse "docs" $out }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($out, $OutZip)
Write-Host "Created $OutZip"
Write-Host "Publish with gh CLI: gh release create v1.0.0 --title 'v1.0.0' --notes-file RELEASE_DRAFT.md $OutZip"
