$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }

if (-not $py) {
  Write-Host "Python 3 is not installed."
  Write-Host "Install it with: winget install -e --id Python.Python.3.12"
  exit 1
}

& $py.Source serve.py