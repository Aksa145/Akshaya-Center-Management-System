@echo off
title Akshaya Center Software

REM --- Always move to this folder ---
cd /d "%~dp0"

REM --- Kill anything already stuck on port 8000 ---
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Closing old process on port 8000, PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

REM --- Activate virtual environment ---
call myvenv\Scripts\activate.bat

REM --- Open browser after a short delay, in the background ---
start "" cmd /c "timeout /t 6 /nobreak >nul && start http://127.0.0.1:8000"

REM --- Start Django server, auto-restart if it ever crashes ---
:loop
python manage.py runserver 127.0.0.1:8000
echo.
echo Server stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop