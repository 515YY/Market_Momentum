@echo off
CHCP 65001 >NUL
echo [Market Momentum] Starting Concept Data Update...
echo This process fetches latest concept data from MoneyDJ. 
echo It may take a few minutes depending on network speed.
echo.

REM 1. Run the Python script to scrape concepts
"C:\Users\owo72\anaconda3\envs\research\python.exe" update_concepts.py

REM 2. Check if successful
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Concept update failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] Concept data updated (concept_map.json).
echo Please run 'run_daily_update.bat' again to apply these new concepts to your stock list.
echo.
pause
