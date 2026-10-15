# Run DelftDashboard from the repo (source, no install needed).
#
# Usage:
#   .\run_delftdashboard.ps1
#   .\run_delftdashboard.ps1 -Env hydromt-sfincs-dev   # use a different conda env
#
param(
    [string]$Env = "delftdashboard_dev"
)

$ErrorActionPreference = "Stop"

# Repo root = folder this script lives in.
$RepoRoot = $PSScriptRoot
$Src      = Join-Path $RepoRoot "src"
$Entry    = Join-Path $Src "delftdashboard\start_delftdashboard.py"

# Conda env python (miniforge). Adjust the base path if yours differs.
$Python = Join-Path $env:LOCALAPPDATA "miniforge3\envs\$Env\python.exe"

if (-not (Test-Path $Python)) { throw "Python not found for env '$Env': $Python" }
if (-not (Test-Path $Entry))  { throw "Entry script not found: $Entry" }

# Run from src so the package resolves without an editable install.
$env:PYTHONPATH = $Src
Write-Host "Launching DelftDashboard ($Env) ..." -ForegroundColor Cyan
& $Python $Entry
