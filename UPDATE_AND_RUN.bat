@echo off
cd /d "%~dp0"

echo.
echo Hays Botany - Update and Run
echo ============================
echo Safely updates GitHub files, preserves local approval decisions,
echo then opens the no-cache localhost learner.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py scripts\safe_update.py
  if errorlevel 1 (
    echo.
    pause
    exit /b 1
  )
  call RUN_LOCAL_SERVER.bat
  goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
  python scripts\safe_update.py
  if errorlevel 1 (
    echo.
    pause
    exit /b 1
  )
  call RUN_LOCAL_SERVER.bat
  goto :eof
)

echo Python was not found.
echo Install Python or use RUN_LOCAL_SERVER.bat without auto-update.
pause
