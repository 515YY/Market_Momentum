@echo off
CHCP 65001 >NUL
echo [Market Momentum] Publishing to GitHub...
echo.

REM 1. Add all changes
echo [1/3] Adding files...
git add .

REM 2. Commit with current date/time
echo [2/3] Committing changes...
set "mydate=%date%"
set "mytime=%time%"
git commit -m "Auto-update: %mydate% %mytime%"

REM 3. Push to main branch
echo [3/3] Pushing to GitHub...
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Publish failed. Please check your internet connection or git settings.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] Published successfully! 
echo Your dashboard will be updated online in a few minutes.
echo.
pause
