@echo off
REM Sauti ya Mwananchi - ngrok Quick Setup (Batch Launcher)
REM This makes it easy to run the setup script by double-clicking

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo SAUTI YA MWANANCHI - NGROK SETUP LAUNCHER
echo ============================================================
echo.

REM Check if PowerShell is available
powershell -Command "exit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not available
    echo This script requires PowerShell
    pause
    exit /b 1
)

REM Run the PowerShell setup script
echo Starting ngrok setup...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-ngrok.ps1"

if errorlevel 1 (
    echo.
    echo ERROR: Setup failed
    pause
    exit /b 1
)

pause
