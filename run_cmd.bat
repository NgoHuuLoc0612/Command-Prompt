@echo off
REM Command Prompt Launcher
REM This batch file launches the Python CMD

title Command Prompt

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo Error: main.py not found in current directory
    echo Please ensure all files are in the same directory
    pause
    exit /b 1
)

REM Launch the CMD
echo Starting Command Prompt...
echo.
python main.py

REM Pause before closing if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Command Prompt exited with error code %errorlevel%
    pause
)
