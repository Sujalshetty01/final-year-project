Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrWhiteSpace($scriptRoot)) { $scriptRoot = (Get-Location).ProviderPath }
# Ensure single string path (avoid passing arrays into Join-Path)
$scriptRoot = [string]($scriptRoot | Select-Object -First 1)
try {
    $scriptRoot = (Get-Item -LiteralPath $scriptRoot).FullName
} catch {
    $scriptRoot = [string]$scriptRoot
}
Set-Location $scriptRoot

function Write-Log { param([string]$m) $ts = (Get-Date).ToString('s'); Write-Host "[auto_pdflatex][$ts] $m" }

try {
    Write-Log 'Starting auto_pdflatex_build.ps1'

    # Safely detect pdflatex (single object)
    $pdCmd = Get-Command pdflatex -ErrorAction SilentlyContinue | Select-Object -First 1
    $pdPath = $null
    if ($pdCmd) {
        if ($pdCmd.Path -and -not [string]::IsNullOrWhiteSpace($pdCmd.Path)) { $pdPath = $pdCmd.Path }
        elseif ($pdCmd.Definition -and -not [string]::IsNullOrWhiteSpace($pdCmd.Definition)) { $pdPath = $pdCmd.Definition }
        elseif ($pdCmd.Source -and -not [string]::IsNullOrWhiteSpace($pdCmd.Source)) { $pdPath = $pdCmd.Source }
    }

    # Probe common MiKTeX locations if not found
    if (-not $pdPath) {
        $candidates = @()
        if ($env:LOCALAPPDATA) { $candidates += Join-Path $env:LOCALAPPDATA 'Programs\MiKTeX\miktex\bin\x64' }
        $candidates += 'C:\Program Files\MiKTeX\miktex\bin\x64'
        $candidates += 'C:\Program Files (x86)\MiKTeX\miktex\bin'
        if ($env:APPDATA) { $candidates += Join-Path $env:APPDATA 'MiKTeX\miktex\bin\x64' }

        foreach ($cand in $candidates) {
            if ([string]::IsNullOrWhiteSpace($cand)) { continue }
            $exe = Join-Path $cand 'pdflatex.exe'
            if (Test-Path $exe) { $pdPath = $exe; break }
        }
    }

    if (-not $pdPath) { Write-Log 'pdflatex not installed or not in PATH'; exit 1 }

    if ($pdPath -is [System.Array]) { $pdPath = $pdPath | Select-Object -First 1 }
    $pdPath = [string]$pdPath
    Write-Log "Using pdflatex at: $pdPath"

    # Ensure pdflatex dir on PATH for session
    $pdDir = Split-Path -Parent $pdPath
    $currentPathItems = $env:PATH -split ';'
    if (-not ($currentPathItems -contains $pdDir)) { $env:PATH = $pdDir + ';' + $env:PATH; Write-Log "Prepended $pdDir to PATH" }

    # Determine repository root (parent of scripts) and TeX source
    try { $repoRoot = (Get-Item -LiteralPath $scriptRoot).Parent.FullName } catch { $repoRoot = $scriptRoot }
    if (-not $repoRoot) { $repoRoot = $scriptRoot }

    $texCandidates = @(
        [System.IO.Path]::Combine($repoRoot, 'PROJECT_SUMMARY.tex'),
        [System.IO.Path]::Combine($repoRoot, 'paper', 'ieee_paper_main.tex'),
        [System.IO.Path]::Combine($repoRoot, 'paper', 'ieee_paper.tex')
    )
    $texFile = $null
    foreach ($t in $texCandidates) { if (Test-Path $t) { $texFile = $t; break } }
    if (-not $texFile) { Write-Log 'No TeX source found to build.'; exit 2 }
    Write-Log "Building TeX file: $texFile"

    $logDir = Join-Path $repoRoot 'paper'
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $logFile = Join-Path $logDir 'build.log'
    Remove-Item -ErrorAction SilentlyContinue -Force $logFile

    for ($run = 1; $run -le 2; $run++) {
        Write-Log "pdflatex run #$run"
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $pdPath
        $psi.Arguments = "-interaction=nonstopmode -halt-on-error -output-directory `"$logDir`" `"$texFile`""
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError  = $true
        $psi.UseShellExecute = $false
        $proc = [System.Diagnostics.Process]::Start($psi)
        $stdOut = $proc.StandardOutput.ReadToEnd()
        $stdErr = $proc.StandardError.ReadToEnd()
        $proc.WaitForExit()
        $exitCode = $proc.ExitCode
        $header = "===== pdflatex run #$run - $(Get-Date -Format 's') =====`n"
        $header | Out-File -FilePath $logFile -Append -Encoding utf8
        $stdOut | Out-File -FilePath $logFile -Append -Encoding utf8
        $stdErr | Out-File -FilePath $logFile -Append -Encoding utf8
        "`n" | Out-File -FilePath $logFile -Append -Encoding utf8
        Write-Log "pdflatex exit code: $exitCode"
        if ($exitCode -ne 0) { Write-Log "pdflatex failed on run #$run (exit $exitCode). See $logFile"; exit $exitCode }
    }

    $pdf = [System.IO.Path]::ChangeExtension($texFile, '.pdf')
    if (-not (Test-Path $pdf)) { $pdf = Join-Path $logDir ([System.IO.Path]::GetFileNameWithoutExtension($texFile) + '.pdf') }
    if (Test-Path $pdf) { Write-Log "Build succeeded. PDF: $pdf"; exit 0 } else { Write-Log "Build finished but PDF not found; check $logFile"; exit 3 }

} catch {
    Write-Log "Unhandled error: $($_.Exception.Message)"
    if ($_.Exception.InnerException) { Write-Log "Inner exception: $($_.Exception.InnerException.Message)" }
    exit 99
}
