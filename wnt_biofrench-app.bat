@echo off
REM ==============================================================================
REM BioFrench Android App Management Script
REM Automatically export all variables defined in this file.

REM ------------------------------------------------------------------------------
REM Paths
set "APP_DIR=C:\Work\Documents\xcoll\Personal\BioFrench\biofrench-app"
set "GRADLEW=%APP_DIR%\gradlew.bat"
set "APK_OUTPUT_DIR=%APP_DIR%\app\build\outputs\apk"

REM ------------------------------------------------------------------------------
REM Git Configuration
set "GIT_REPO=%APP_DIR%"
set "TO_BRANCH=main"

REM ------------------------------------------------------------------------------
cd /d %APP_DIR%

REM ------------------------------------------------------------------------------
:menu
if "%~1"=="" (
	echo Select Mode
	echo 1. Build Release APK
	echo 2. Test
	echo 3. Commit and Push changes
	echo 4. Create GitHub Release
	echo 5. update_code
	set /p MODE=Enter choice:
	goto handle_mode
) else (
	set "MODE=%~1"
	goto handle_arg
)

:handle_mode
if "%MODE%"=="1" goto build
if "%MODE%"=="2" goto test
if "%MODE%"=="3" goto commit_push
if "%MODE%"=="4" goto create_release
if "%MODE%"=="5" goto update_code
echo Incorrect Mode
exit /b 1

:handle_arg
if /i "%MODE%"=="build" goto build
if /i "%MODE%"=="test" goto test
if /i "%MODE%"=="commit_push" goto commit_push
if /i "%MODE%"=="create_release" goto create_release
if /i "%MODE%"=="update_code" goto update_code
echo Unknown Mode
exit /b 1

:build
echo Building Android app...
call "%GRADLEW%" assembleRelease
if %errorlevel% neq 0 (
	echo Build failed!
	exit /b 1
)
echo Build completed successfully.
echo APK location: %APK_OUTPUT_DIR%\release\biofrench-android-app.apk
goto :eof

:test
echo Running tests...
call "%GRADLEW%" testDebugUnitTest
if %errorlevel% neq 0 (
	echo Unit tests failed!
	exit /b 1
)
echo Unit tests completed successfully.
goto :eof

:commit_push
echo Committing and pushing changes...
cd /d "%GIT_REPO%"
git add .
set /p COMMIT_MSG=Enter commit message:
if "x%COMMIT_MSG%"=="x" (
	echo No commit message provided.
	goto :eof
)
git commit -m "%COMMIT_MSG%"
git push
echo Changes committed and pushed successfully.
goto :eof

:create_release
setlocal enabledelayedexpansion
echo    ===============   Creating GitHub Release    =================
REM Fetch the latest release tag and details
for /f "tokens=*" %%i in ('gh release list --limit 1 --json tagName --jq ".[0].tagName" 2^>nul') do set LATEST_TAG=%%i
if not "!LATEST_TAG!"=="" (
	echo Latest release tag: !LATEST_TAG!
	
) else (
	echo No previous releases found
)

set /p RELEASE_VERSION=Enter RELEASE_VERSION (e.g., v1.0):
if "x%RELEASE_VERSION%"=="x" (
	echo No release version provided.
	goto :eof
)

set TAG=%RELEASE_VERSION%

REM Get current commit hash for comparison
for /f %%i in ('git rev-parse HEAD') do set TMP_GIT_NEW=%%i
for /f %%i in ('git rev-parse HEAD~1') do set TMP_GIT_OLD=%%i

echo Creating git tag %TAG%...
git tag -a %TAG% -m "Release %TAG%"
git push origin %TAG%

pause
set /p RELEASE_NOTES=Enter RELEASE_NOTES:

REM === Create GitHub Release with comparison URL ===
gh release create %TAG% ^
  --title "%TAG%" ^
  --target "%TO_BRANCH%" ^
  --notes "Changes from %TMP_GIT_OLD% to %TMP_GIT_NEW%: %RELEASE_NOTES%" ^
  "%APK_OUTPUT_DIR%\release\biofrench-android-app.apk" ^
  "%APP_DIR%\app\src\main\assets\medicines.json"

echo GitHub release created successfully!
goto :eof

:update_code
echo Updating code from repository...
cd /d "%GIT_REPO%"
git pull
echo Code updated successfully.
goto :eof