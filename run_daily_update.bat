@echo off
CHCP 65001 >NUL
echo [Market Momentum] Starting Daily Update...

REM 1. Run the Python script to process data
echo [1/3] Processing StockList.csv...
"C:\Users\owo72\anaconda3\envs\research\python.exe" conclude_data.py

REM 2. Check if successful
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python script failed. Please check StockList.csv.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/3] Data processing complete (dashboard_data.js updated).

REM 3. Optional: Auto-push to GitHub (Uncomment if you want full automation)
REM echo [3/3] Pushing to GitHub...
REM git add .
REM git commit -m "Daily data update"
REM git push

echo.
echo [SUCCESS] Update finished! 
echo Now you can manually push to GitHub:
echo   git add .
echo   git commit -m "update"
echo   git push
echo.
pause
