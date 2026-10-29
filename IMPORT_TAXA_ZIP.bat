@echo off
setlocal
cd /d "%~dp0"

rem Family-first importer: old Hays-County-Botany plant files are read-only.
rem The new importer plans safe writes to your local cloned Hays-Botany-* repos.
rem It does NOT import new photos, publish, commit or push.
set "ZIP=%~1"
if "%ZIP%"=="" set "ZIP=%CD%\taxa.zip"
if not exist "%ZIP%" (
  echo.
  echo No ZIP found. Drag a curated taxa ZIP onto this file or put taxa.zip here.
  echo.
  pause
  exit /b 1
)

echo.
echo NEW HAYS BOTANY FAMILY WRITE SYSTEM
echo -----------------------------------
echo Input: %ZIP%
echo This is a READ-ONLY ROUTING PLAN. It will not change the old site.
echo Assigned family repositories must be cloned as siblings of this folder,
echo and each must be checked out on its assigned active write branch.
echo No automatic photo downloads or commits.
echo.
py scripts\family_repo_installer.py "%ZIP%" --destination-root "%~dp0.."
if errorlevel 1 (
  echo.
  echo PLAN BLOCKED: Check the exact error and the family branch before continuing.
  pause
  exit /b 1
)
echo.
echo PLAN COMPLETE; NO FILES CHANGED. After reviewing results, manually run:
echo py scripts\family_repo_installer.py "YOUR-ZIP-PATH" --destination-root ".." --apply
echo Then run the destination family validation script and review commits manually.
pause
