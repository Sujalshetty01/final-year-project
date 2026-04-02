# PowerShell script to ensure npm is installed on Windows

# Check if npm is installed
$npmVersion = ""
try {
    $npmVersion = npm -v
} catch {
    $npmVersion = ""
}

if ($npmVersion -ne "") {
    Write-Host "npm is already installed. Version: $npmVersion"
    exit 0
}

# Download latest Node.js LTS .msi installer
$nodeLTSUrl = "https://nodejs.org/dist/latest-v18.x/node-v18.19.0-x64.msi"
$installerPath = "$env:TEMP\nodejs-lts-installer.msi"
Invoke-WebRequest -Uri $nodeLTSUrl -OutFile $installerPath

# Install Node.js silently
Start-Process msiexec.exe -ArgumentList "/i `$installerPath` /quiet /norestart" -Wait

# Update environment variables (refresh PATH)
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# Verify installation
try {
    $nodeVersion = node -v
    $npmVersion = npm -v
    Write-Host "npm is ready to use. Node version: $nodeVersion, npm version: $npmVersion"
} catch {
    Write-Host "npm installation failed. Please check installer logs."
}
