<#
PowerShell build script for the paper PDF.

Usage:
  powershell -ExecutionPolicy Bypass -File build.ps1

Behavior:
- Checks for pdflatex in PATH. If missing, prints instruction to install MiKTeX and exits.
- Changes directory to the script location (project root).
- Compiles paper/ieee_paper_main.tex (falls back to paper/ieee_paper.tex if main not present).
- Runs pdflatex twice to resolve references. Captures all output to paper/build.log.
- On failure prints last 40 lines of the log and exits non-zero.
- On success opens the generated PDF.
#>

# Ensure script runs from its own folder (project root)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $ScriptDir

function Abort($code, $msg) {
    Write-Host $msg -ForegroundColor Red
    Exit $code
}

# Check for pdflatex
$pdflatexCmd = Get-Command pdflatex -ErrorAction SilentlyContinue
if (-not $pdflatexCmd) {
    Write-Host "ERROR: 'pdflatex' not found in PATH." -ForegroundColor Red
    Write-Host "Install MiKTeX (https://miktex.org/download) or TeX Live and ensure pdflatex is on PATH." -ForegroundColor Yellow
    Exit 1
}

# Determine tex file to build
$preferred = Join-Path $ScriptDir "paper\ieee_paper_main.tex"
$fallback = Join-Path $ScriptDir "paper\ieee_paper.tex"
$tex = $null
if (Test-Path $preferred) {
    $tex = $preferred
} elseif (Test-Path $fallback) {
    Write-Host "Note: $preferred not found; falling back to paper/ieee_paper.tex" -ForegroundColor Yellow
    $tex = $fallback
} else {
    Abort 2 "ERROR: Neither paper/ieee_paper_main.tex nor paper/ieee_paper.tex found. Please ensure the paper file exists under the 'paper' folder."
}

$outdir = Join-Path $ScriptDir "paper"
if (-not (Test-Path $outdir)) { New-Item -ItemType Directory -Path $outdir | Out-Null }

$log = Join-Path $outdir "build.log"
if (Test-Path $log) { Remove-Item $log -Force }

Write-Host "Building $tex" -ForegroundColor Cyan

$pdflatexArgs = "-interaction=nonstopmode", "-output-directory=$outdir", $tex

$failed = $false
for ($i = 1; $i -le 2; $i++) {
    Write-Host "pdflatex pass $i/2..." -NoNewline
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "pdflatex"
    $startInfo.Arguments = $pdflatexArgs -join ' '
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.UseShellExecute = $false
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $startInfo
    $p.Start() | Out-Null
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    $exitCode = $p.ExitCode
    # Append to log
    Add-Content -Path $log -Value "`n=== pdflatex pass $i ===`n"
    Add-Content -Path $log -Value $stdout
    if ($stderr) { Add-Content -Path $log -Value "`nSTDERR:`n"; Add-Content -Path $log -Value $stderr }

    if ($exitCode -ne 0) {
        Write-Host " FAILED" -ForegroundColor Red
        $failed = $true
        break
    } else {
        Write-Host " OK" -ForegroundColor Green
    }
}

if ($failed) {
    Write-Host "Compilation failed. Showing last 40 lines of $log" -ForegroundColor Red
    if (Test-Path $log) {
        Get-Content -Path $log -Tail 40 | ForEach-Object { Write-Host $_ }
    }
    Exit 3
}

# Determine PDF path and open it
$texBase = [System.IO.Path]::GetFileNameWithoutExtension($tex)
$pdfPath = Join-Path $outdir ($texBase + ".pdf")
if (-not (Test-Path $pdfPath)) {
    Write-Host "Warning: Build reported success but PDF not found at $pdfPath" -ForegroundColor Yellow
    Write-Host "Check $log for details." -ForegroundColor Yellow
    Exit 4
}

Write-Host "Build succeeded. Opening $pdfPath" -ForegroundColor Green
Start-Process -FilePath $pdfPath

Exit 0
