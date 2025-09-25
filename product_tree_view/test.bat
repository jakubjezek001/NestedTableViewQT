@echo off
setlocal

echo === Product Tree View Test Runner ===
echo.

REM Set paths
set REPO_ROOT=%~dp0..
set PROJECT_ROOT=%~dp0
set VENV_PATH=%REPO_ROOT%\.venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

echo Repository Root: %REPO_ROOT%
echo Project Root: %PROJECT_ROOT%
echo Virtual Environment: %VENV_PATH%
echo.

REM Check if virtual environment exists
if not exist "%VENV_PATH%" (
    echo ERROR: Virtual environment not found at %VENV_PATH%
    echo Please ensure .venv directory exists in repository root
    pause
    exit /b 1
)

REM Check if Python executable exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python executable not found at %PYTHON_EXE%
    pause
    exit /b 1
)

REM Check if test file exists
if not exist "%PROJECT_ROOT%\test_main.py" (
    echo ERROR: Test file not found at %PROJECT_ROOT%\test_main.py
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Running tests...
cd /d "%PROJECT_ROOT%"
"%PYTHON_EXE%" test_main.py

set TEST_RESULT=%ERRORLEVEL%

echo.
if %TEST_RESULT% equ 0 (
    echo Tests completed successfully
) else (
    echo Tests failed with exit code %TEST_RESULT%
)

echo.
pause
exit /b %TEST_RESULT%
