@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 scripts\make_demo.py
    py -3 scripts\validate_csv.py data\demo\XAUUSD_15min_SYNTHETIC.csv
) else (
    python scripts\make_demo.py
    python scripts\validate_csv.py data\demo\XAUUSD_15min_SYNTHETIC.csv
)
pause
