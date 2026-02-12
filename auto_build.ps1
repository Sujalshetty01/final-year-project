<#
auto_build.ps1

Fully automated Windows PowerShell script to ensure `pdflatex` is available
and to build the LaTeX paper. Usage:

  powershell -ExecutionPolicy Bypass -File auto_build.ps1

Behavior:
- If `pdflatex` exists, compiles `paper/ieee_paper_main.tex` twice, logs to `paper/build.log`.
- If `pdflatex` is missing, tries to install MiKTeX via `winget`, then `choco`, then direct installer.
- Adds the MiKTeX bin folder to the user PATH, refreshes environment variables for the session,
  verifies `pdflatex --version`, then compiles.

Notes:
- Installing system packages may require administrator privileges. The script attempts
  a user installation when possible and falls back to elevated installers. If an
  elevated install is required and fails, the script will exit with a non-zero code.
- The script tries common installers and silent flags but cannot guarantee success
  on every Windows configuration.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Log { param($msg) Write-Host "[auto_build] $msg" }

function Test-PdfLaTeX {
    return (Get-Command pdflatex -ErrorAction SilentlyContinue) -ne $null
}

function Find-Pdflatex { 
    $candidates = @()
    $searchRoots = @($env:LocalAppData, $env:ProgramFiles, $env:'ProgramFiles(x86)', $env:ProgramData, $env:AppData)
    foreach ($root in $searchRoots | Where-Object { $_ }) {
        try {
            $found = Get-ChildItem -Path $root -Filter pdflatex.exe -Recurse -ErrorAction SilentlyContinue -Force | Select-Object -First 1
            if ($found) { return $found.FullName }
        } catch {
            # skip permission errors
        }
    }
    return $null
}

function Add-ToUserPath($newPath) {
    if (-not (Test-Path $newPath)) { return }
    $current = [Environment]::GetEnvironmentVariable('PATH', 'User')
    if ($current -and $current.Split(';') -contains $newPath) { return }
    $updated = if ($current) { "$current;$newPath" } else { $newPath }
    [Environment]::SetEnvironmentVariable('PATH', $updated, 'User')
    # Also update current process PATH so subsequent commands can find pdflatex
    $env:PATH = [Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User')
}

function Try-Install-MiKTeX {
    Write-Log "Attempting to install MiKTeX..."

    # 1) Try winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Log "Found winget — installing MiKTeX silently via winget"
        try {
            winget install --id MiKTeX.MiKTeX -e --silent --accept-source-agreements --accept-package-agreements
            return $true
        } catch { Write-Log "winget install failed: $_" }
    }

    # 2) Try Chocolatey
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Log "Found Chocolatey — installing MiKTeX via choco"
        try {
            choco install miktex -y --no-progress
            return $true
        } catch { Write-Log "choco install failed: $_" }
    }

    # 3) Download the basic MiKTeX installer and try unattended install
    $tmp = [IO.Path]::GetTempPath()
    $installer = Join-Path $tmp 'basic-miktex-installer.exe'
    $urls = @(
        'https://miktex.org/download/ctan/systems/win32/miktex/setup/basic-miktex-x64.exe',
        'https://ctan.org/tex-archive/systems/win32/miktex/setup/basic-miktex-x64.exe'
    )
    $downloaded = $false
    foreach ($u in $urls) {
        try {
            Write-Log "Downloading MiKTeX from $u"
            Invoke-WebRequest -Uri $u -OutFile $installer -UseBasicParsing -ErrorAction Stop
            $downloaded = $true; break
        } catch { Write-Log "Download failed from $u: $_" }
    }
    if (-not $downloaded) {
        Write-Log "Failed to download MiKTeX installer. Please install MiKTeX or TeX Live manually."
        return $false
    }

    # Try common unattended flags. The exact flag set differs between installers; try a few.
    $attempts = @( '--unattended', '/S', '/quiet', '/silent' )
    foreach ($flag in $attempts) {
        try {
            Write-Log "Running installer with flag: $flag"
            $proc = Start-Process -FilePath $installer -ArgumentList $flag -Wait -PassThru -WindowStyle Hidden
            if ($proc.ExitCode -eq 0) { Write-Log "Installer finished (exit 0)"; return $true }
        } catch { Write-Log "Installer attempt ($flag) failed: $_" }
    }

    Write-Log "MiKTeX installer did not succeed silently. Manual intervention may be required."
    return $false
}

function Compile-TeX($texFile, $logFile) {
    New-Item -ItemType Directory -Path (Split-Path $logFile) -Force | Out-Null
    Remove-Item -Force -ErrorAction SilentlyContinue $logFile

    for ($i = 1; $i -le 2; $i++) {
        Write-Log "pdflatex run #$i"
        $args = "-interaction=nonstopmode -output-directory paper `"$texFile`""
        & pdflatex -interaction=nonstopmode -output-directory paper $texFile 2>&1 | Tee-Object -FilePath $logFile -Append
        $code = $LASTEXITCODE
        Write-Log "pdflatex exit code: $code"
        if ($code -ne 0) { return $code }
    }
    return 0
}

try {
    Write-Log "Starting auto_build.ps1"

    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Set-Location $scriptRoot

    if (Test-PdfLaTeX) {
        Write-Log "pdflatex already available."
    } else {
        Write-Log "pdflatex not found on PATH."
        $installed = Try-Install-MiKTeX
        if (-not $installed) {
            Write-Log "Unable to install MiKTeX automatically. Exiting with error."
            exit 1
        }

        # Try to locate pdflatex in common install locations
        Start-Sleep -Seconds 3
        $pdflatexPath = Find-Pdflatex
        if (-not $pdflatexPath) {
            Write-Log "Could not locate pdflatex.exe automatically. Refreshing PATH and retrying..."
            # Common MiKTeX user bin locations
            $candidates = @(
                "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64",
                "$env:ProgramFiles\MiKTeX\miktex\bin\x64",
                "$env:ProgramFiles(x86)\MiKTeX\miktex\bin",
                "$env:APPDATA\MiKTeX\miktex\bin\x64"
            )
            foreach ($p in $candidates) {
                if (Test-Path $p) { Add-ToUserPath $p; Write-Log "Added $p to PATH" }
            }
            # update current process PATH from environment
            $env:PATH = [Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User')
            Start-Sleep -Seconds 2
            $pdflatexPath = Find-Pdflatex
        }
        if ($pdflatexPath) {
            $dir = Split-Path -Parent $pdflatexPath
            Add-ToUserPath $dir
            Write-Log "Found pdflatex at $pdflatexPath and added to PATH."
        } else {
            Write-Log "pdflatex still not found after install. Exiting."
            exit 2
        }
    }

    # Verify pdflatex works
    try {
        Write-Log "Verifying pdflatex --version"
        & pdflatex --version 2>&1 | Tee-Object -FilePath (Join-Path $scriptRoot 'paper\pdflatex_version.log')
    } catch {
        Write-Log "pdflatex invocation failed: $_"
        exit 3
    }

    # Determine tex file
    $texMain = Join-Path $scriptRoot 'paper\ieee_paper_main.tex'
    $texFallback = Join-Path $scriptRoot 'paper\ieee_paper.tex'
    if (Test-Path $texMain) { $texFile = $texMain } elseif (Test-Path $texFallback) { $texFile = $texFallback } else { Write-Log "No tex source found in paper/"; exit 4 }

    $logFile = Join-Path $scriptRoot 'paper\build.log'
    $ret = Compile-TeX $texFile $logFile
    if ($ret -ne 0) {
        Write-Log "Build failed (pdflatex exit code $ret). Showing last 50 lines of $logFile"
        if (Test-Path $logFile) { Get-Content $logFile -Tail 50 | ForEach-Object { Write-Host $_ } }
        exit $ret
    }

    # Success — open PDF
    $pdf = [IO.Path]::ChangeExtension($texFile, '.pdf')
    if (-not (Test-Path $pdf)) {
        # Some setups place output in paper\ directory
        $pdf = Join-Path $scriptRoot ('paper\' + ([IO.Path]::GetFileNameWithoutExtension($texFile) + '.pdf'))
    }
    if (Test-Path $pdf) {
        Write-Log "Build succeeded. Opening $pdf"
        Start-Process -FilePath $pdf
        exit 0
    } else {
        Write-Log "Build succeeded but PDF not found at expected location: $pdf"
        exit 0
    }

} catch {
    Write-Log "Unhandled error: $_"
    exit 10
}
