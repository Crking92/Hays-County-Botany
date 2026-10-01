@echo off
cd /d "%~dp0"

echo.
echo Starting Hays Botany Visual Learner...
echo This local server disables browser caching so GitHub interface updates load correctly.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  start "" "http://localhost:8000/?fresh=1"
  py scripts\dev_server.py
  goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
  start "" "http://localhost:8000/?fresh=1"
  python scripts\dev_server.py
  goto :eof
)

echo Python was not found.
echo Install Python OR open this folder in VS Code and use the Live Server extension.
pause
