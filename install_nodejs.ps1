# PowerShell script to install Node.js automatically on Windows

# Check if Node.js is installed
$nodeVersion = ""
try {
    $nodeVersion = node -v
} catch {
    $nodeVersion = ""
}

if ($nodeVersion -ne "") {
    Write-Host "Node.js is already installed. Version: $nodeVersion"
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
    Write-Host "Node.js installed successfully. Node version: $nodeVersion, npm version: $npmVersion"
} catch {
    Write-Host "Node.js installation failed. Please check installer logs."
}
