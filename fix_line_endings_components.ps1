# PowerShell script to convert all .js and .jsx files in the correct frontend/src/components directory to LF line endings
$folder = "C:/Users/sujal/OneDrive/Desktop/major_project/frontend/src/components"
Get-ChildItem -Path $folder -Include *.js,*.jsx -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace "\r", "" | Set-Content -NoNewline $_.FullName
    Write-Host "Converted $($_.FullName) to LF line endings."
}
Write-Host "All .js and .jsx files in $folder converted to LF line endings."
