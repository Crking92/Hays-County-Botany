@echo off
title Hays Botany ID

where node >nul 2>&1
if errorlevel 1 (
  echo Node.js 22 is required. Install it from https://nodejs.org/ and try again.
  pause
  exit /b 1
)

if not exist node_modules (
  echo Preparing Hays Botany ID for the first time...
  call npm ci
  if errorlevel 1 (
    echo Setup failed. Review the message above.
    pause
    exit /b 1
  )
)

echo Starting the private local preview...
call npm run dev
pause
