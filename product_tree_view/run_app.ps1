#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Product Tree View application with virtual environment activation.

.DESCRIPTION
    This script activates the Python virtual environment and runs the application.
    Supports both normal mode and test mode for automated testing.

.PARAMETER Mode
    Run mode: "run" (default) or "test"

.PARAMETER TestFile
    Test file to run when in test mode (optional)

.EXAMPLE
    .\run_app.ps1
    Run the application normally

.EXAMPLE
    .\run_app.ps1 test
    Run in test mode

.EXAMPLE
    .\run_app.ps1 test .\test_main.py
    Run specific test file
#>

param(
    [string]$Mode = "run",
    [string]$TestFile = ""
)

# Script configuration
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $RepoRoot ".venv"
$VenvActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $Reset
    )
    Write-Host "${Color}${Message}${Reset}"
}

function Test-Prerequisites {
    """Check if all prerequisites are available."""

    Write-ColorOutput "Checking prerequisites..." $Blue

    # Check if virtual environment exists
    if (-not (Test-Path $VenvPath)) {
        Write-ColorOutput "❌ Virtual environment not found at: $VenvPath" $Red
        Write-ColorOutput "Please ensure the .venv directory exists in the repository root." $Red
        return $false
    }

    # Check if activation script exists
    if (-not (Test-Path $VenvActivateScript)) {
        Write-ColorOutput "❌ Virtual environment activation script not found: $VenvActivateScript" $Red
        return $false
    }

    # Check if main.py exists
    $MainPyPath = Join-Path $ScriptDir "main.py"
    if (-not (Test-Path $MainPyPath)) {
        Write-ColorOutput "❌ Main application file not found: $MainPyPath" $Red
        return $false
    }

    Write-ColorOutput "✅ Prerequisites check passed" $Green
    return $true
}

function Activate-VirtualEnvironment {
    """Activate the Python virtual environment."""

    Write-ColorOutput "Activating virtual environment..." $Blue

    try {
        & $VenvActivateScript
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to activate virtual environment"
        }
        Write-ColorOutput "✅ Virtual environment activated" $Green
        return $true
    }
    catch {
        Write-ColorOutput "❌ Failed to activate virtual environment: $_" $Red
        return $false
    }
}

function Run-Application {
    """Run the main application."""

    Write-ColorOutput "Starting Product Tree View application..." $Blue

    try {
        Set-Location $ScriptDir
        python main.py

        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Application completed successfully" $Green
        } else {
            Write-ColorOutput "⚠️ Application exited with code: $LASTEXITCODE" $Yellow
        }

        return $LASTEXITCODE
    }
    catch {
        Write-ColorOutput "❌ Failed to run application: $_" $Red
        return 1
    }
}

function Run-Tests {
    param([string]$TestFile)

    """Run application in test mode."""

    if ($TestFile -and (Test-Path $TestFile)) {
        Write-ColorOutput "Running specific test file: $TestFile" $Blue

        try {
            Set-Location $ScriptDir
            python $TestFile
            return $LASTEXITCODE
        }
        catch {
            Write-ColorOutput "❌ Failed to run test file: $_" $Red
            return 1
        }
    }
    else {
        Write-ColorOutput "Running application in test mode..." $Blue

        try {
            Set-Location $ScriptDir
            python main.py test

            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ Tests completed successfully" $Green
            } else {
                Write-ColorOutput "❌ Tests failed with code: $LASTEXITCODE" $Red
            }

            return $LASTEXITCODE
        }
        catch {
            Write-ColorOutput "❌ Failed to run tests: $_" $Red
            return 1
        }
    }
}

function Main {
    """Main script execution function."""

    Write-ColorOutput "=== Product Tree View Runner ===" $Blue
    Write-ColorOutput "Repository Root: $RepoRoot" $Blue
    Write-ColorOutput "Project Root: $ScriptDir" $Blue
    Write-ColorOutput "Mode: $Mode" $Blue

    if ($TestFile) {
        Write-ColorOutput "Test File: $TestFile" $Blue
    }

    Write-ColorOutput ""

    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        return 1
    }

    # Activate virtual environment
    if (-not (Activate-VirtualEnvironment)) {
        return 1
    }

    Write-ColorOutput ""

    # Run based on mode
    switch ($Mode.ToLower()) {
        "test" {
            return Run-Tests -TestFile $TestFile
        }
        "run" {
            return Run-Application
        }
        default {
            Write-ColorOutput "❌ Unknown mode: $Mode" $Red
            Write-ColorOutput "Valid modes: run, test" $Yellow
            return 1
        }
    }
}

# Trap Ctrl+C and cleanup
trap {
    Write-ColorOutput "`n⚠️ Script interrupted by user" $Yellow
    exit 130
}

# Run main function and exit with its return code
$ExitCode = Main
Write-ColorOutput ""
Write-ColorOutput "Script completed with exit code: $ExitCode" $(if ($ExitCode -eq 0) { $Green } else { $Red })
exit $ExitCode
