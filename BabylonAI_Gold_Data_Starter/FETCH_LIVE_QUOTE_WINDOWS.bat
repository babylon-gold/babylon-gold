@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 scripts\fetch_live_goldapi.py
) else (
    python scripts\fetch_live_goldapi.py
)
pause
