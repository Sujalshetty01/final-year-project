param(
    [string]$venvPath = ".venv"
)

Write-Host "Creating virtual environment at $venvPath"
python -m venv $venvPath
Write-Host "Activating virtualenv"
& "$venvPath\Scripts\Activate.ps1"
Write-Host "Upgrading pip and installing backend requirements"
pip install --upgrade pip
pip install -r backend/requirements.txt

Write-Host "Done. Activate the venv with: & $venvPath\Scripts\Activate.ps1"
