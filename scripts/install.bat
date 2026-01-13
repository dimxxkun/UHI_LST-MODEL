@echo off
REM UHI-LST Platform Installation Script
REM Run this script to install all dependencies for both frontend and backend

echo ============================================
echo    UHI-LST Platform Installation Script
echo ============================================
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo [INFO] Python version:
python --version
echo.
echo [INFO] Node.js version:
node --version
echo.

REM Install Backend Dependencies
echo ============================================
echo [1/2] Installing Backend Dependencies...
echo ============================================
cd /d "%~dp0..\backend"

if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing Python packages...
pip install -r requirements.txt

echo.
echo [SUCCESS] Backend dependencies installed!
echo.

REM Install Frontend Dependencies
echo ============================================
echo [2/2] Installing Frontend Dependencies...
echo ============================================
cd /d "%~dp0..\frontend"

echo [INFO] Installing npm packages...
call npm install

echo.
echo [SUCCESS] Frontend dependencies installed!
echo.

echo ============================================
echo    Installation Complete!
echo ============================================
echo.
echo To start the platform, run: start.bat
echo.
pause
