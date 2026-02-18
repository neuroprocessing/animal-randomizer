# Build Neuroprocessing Randomizer Windows executable
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "[1/5] Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "[2/5] Installing app dependencies..."
python -m pip install -e .

Write-Host "[3/5] Installing Windows build dependencies..."
python -m pip install -r requirements-windows-build.txt

Write-Host "[4/5] Cleaning previous build artifacts..."
if (Test-Path .\build) { Remove-Item .\build -Recurse -Force }
if (Test-Path .\dist) { Remove-Item .\dist -Recurse -Force }

Write-Host "[5/5] Building executable with PyInstaller..."
pyinstaller --noconfirm --clean .\scripts\animal-randomizer.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

Write-Host "Build complete. Output folder: .\dist\NeuroprocessingRandomizer"
