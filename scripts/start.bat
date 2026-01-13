@echo off
REM UHI-LST Platform Start Script
REM Starts both backend and frontend servers

echo ============================================
echo    UHI-LST Platform - Starting Servers
echo ============================================
echo.

REM Start Backend Server
echo [INFO] Starting Backend Server (Port 8000)...
cd /d "%~dp0..\backend"
start "UHI-LST Backend" cmd /k "call venv\Scripts\activate.bat && python main.py"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo [INFO] Starting Frontend Dev Server (Port 5173)...
cd /d "%~dp0..\frontend"
start "UHI-LST Frontend" cmd /k "npm run dev"

echo.
echo ============================================
echo    Servers Started!
echo ============================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:5173
echo API Docs:     http://localhost:8000/docs
echo.
echo To stop the servers, run: stop.bat
echo Or close the terminal windows manually.
echo.
pause
