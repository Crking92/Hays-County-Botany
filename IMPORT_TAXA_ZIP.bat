@echo off
setlocal
cd /d "%~dp0"

set "ZIP=%~1"
if "%ZIP%"=="" set "ZIP=%CD%\taxa.zip"

if not exist "%ZIP%" (
  echo.
  echo Could not find taxa.zip.
  echo.
  echo EITHER:
  echo   1. Copy taxa.zip into this Hays-County-Botany folder and run this file again
  echo OR
  echo   2. Drag taxa.zip directly onto IMPORT_TAXA_ZIP.bat
  echo.
  pause
  exit /b 1
)

echo.
echo Hays Botany historical taxa/photo backfill
echo ZIP: %ZIP%
echo.
echo This preserves newer canonical non-Asteraceae botany data,
echo imports the Asteraceae backlog, backfills photos, skips obsolete
echo Conoclinium greggii, rebuilds the manifest, commits, and pushes to GitHub.
echo.
pause

py scripts\import_taxa_zip.py "%ZIP%" --apply --commit-push
if errorlevel 1 (
  echo.
  echo Import failed. Nothing else will be run.
  pause
  exit /b 1
)

echo.
echo DONE. Run git pull later only if another machine/chat has added newer GitHub work.
echo Refresh http://localhost:8000 to see the imported taxa.
pause
