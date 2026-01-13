@echo off
REM UHI-LST Platform Stop Script
REM Stops both backend and frontend servers

echo ============================================
echo    UHI-LST Platform - Stopping Servers
echo ============================================
echo.

REM Kill processes on port 8000 (Backend)
echo [INFO] Stopping Backend Server (Port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)

REM Kill processes on port 5173 (Frontend)
echo [INFO] Stopping Frontend Server (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)

REM Also kill any Node processes that might be running Vite
taskkill /F /IM node.exe /FI "WINDOWTITLE eq UHI-LST Frontend*" 2>nul

echo.
echo ============================================
echo    Servers Stopped!
echo ============================================
echo.
pause
