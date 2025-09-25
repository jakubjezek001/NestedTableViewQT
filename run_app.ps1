#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Runs the Qt Product Table View application in the activated virtual environment.

.DESCRIPTION
    This script activates the virtual environment and starts the main.py application.
    It includes error handling and provides feedback about the application startup process.

.EXAMPLE
    .\run_app.ps1
    Runs the application with default settings.

.NOTES
    Author: Auto-generated
    Requires: Python virtual environment at .\.venv
#>

# Set error handling
$ErrorActionPreference = "Stop"

# Get script directory (project root)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = $ScriptDir

# Define paths
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
$MainPyPath = Join-Path $ProjectRoot "product_table_view\main.py"

Write-Host "Qt Product Table View Application Launcher" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "ERROR: Virtual environment not found at: $VenvPath" -ForegroundColor Red
    Write-Host "Please create the virtual environment first." -ForegroundColor Yellow
    exit 1
}

# Check if activation script exists
if (-not (Test-Path $VenvActivateScript)) {
    Write-Host "ERROR: Virtual environment activation script not found at: $VenvActivateScript" -ForegroundColor Red
    Write-Host "The virtual environment may be corrupted." -ForegroundColor Yellow
    exit 1
}

# Check if main.py exists
if (-not (Test-Path $MainPyPath)) {
    Write-Host "ERROR: Main application file not found at: $MainPyPath" -ForegroundColor Red
    exit 1
}

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Green
Write-Host "Virtual Environment: $VenvPath" -ForegroundColor Green
Write-Host "Main Script: $MainPyPath" -ForegroundColor Green
Write-Host ""

try {
    # Change to project root directory
    Set-Location $ProjectRoot
    Write-Host "Changed to project directory: $ProjectRoot" -ForegroundColor Yellow

    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $VenvActivateScript

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate virtual environment"
    }

    Write-Host "Virtual environment activated successfully!" -ForegroundColor Green
    Write-Host ""

    # Check if Python is available in the activated environment
    $PythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Using Python: $PythonVersion" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Could not determine Python version" -ForegroundColor Yellow
    }

    # Show Python executable path
    $PythonPath = python -c "import sys; print(sys.executable)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python executable: $PythonPath" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Starting Qt Product Table View Application..." -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""

    # Run the application
    python $MainPyPath

    $ExitCode = $LASTEXITCODE
    Write-Host ""
    Write-Host "Application exited with code: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } else { "Red" })

} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Ensure the virtual environment is properly created" -ForegroundColor White
    Write-Host "2. Check that all required dependencies are installed" -ForegroundColor White
    Write-Host "3. Verify that data.json exists in the project root" -ForegroundColor White
    Write-Host "4. Make sure you have the required Qt bindings (PySide6/PyQt5)" -ForegroundColor White
    exit 1
} finally {
    # Return to original location if needed
    Write-Host ""
    Write-Host "Script execution completed." -ForegroundColor Cyan
}
