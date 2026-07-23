@echo off
setlocal

set SCRIPT_DIR=%~dp0

rem When this script is run elevated under a separate administrator account,
rem %USERPROFILE% points to the admin's profile, not the real desktop user's.
rem Recover the real user from the NTFS owner of the install files instead
rem (they were normally extracted by the real user before elevating to run this).
rem Ask PowerShell for the folder's NTFS owner, stripping any DOMAIN\ prefix
rem so only the bare username remains (empty if the lookup fails).
set PS_GET_OWNER=(Get-Acl '%SCRIPT_DIR%' -ErrorAction SilentlyContinue).Owner -replace '^.*\\'
set SCRIPT_OWNER=
for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "%PS_GET_OWNER%"`) do set SCRIPT_OWNER=%%A

set DEST_DIR=%USERPROFILE%\Desktop\qgis
if defined SCRIPT_OWNER if exist "%SystemDrive%\Users\%SCRIPT_OWNER%" (
    set DEST_DIR=%SystemDrive%\Users\%SCRIPT_OWNER%\Desktop\qgis
)

echo Installing ANNCSU QGIS environment...
echo Destination: %DEST_DIR%
echo File owner: "%SCRIPT_OWNER%" - Script running as: "%USERNAME%"

if not exist "%SCRIPT_DIR%anncsu_manager_win.tar" (
    echo ERROR: anncsu_manager_win.tar not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%pixi-unpack-x86_64-pc-windows-msvc.exe" (
    echo ERROR: pixi-unpack-x86_64-pc-windows-msvc.exe not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

echo Unpacking environment (this may take a few minutes)...
"%SCRIPT_DIR%pixi-unpack-x86_64-pc-windows-msvc.exe" "%SCRIPT_DIR%anncsu_manager_win.tar" -o "%DEST_DIR%" --shell cmd

if %ERRORLEVEL% neq 0 (
    echo ERROR: Unpacking failed with exit code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

copy "%SCRIPT_DIR%startqgis.bat" "%DEST_DIR%\startqgis.bat" >nul

echo.
echo Installation complete.
echo Environment unpacked to: %DEST_DIR%
echo To launch QGIS, double-click:
echo   %DEST_DIR%\startqgis.bat
echo.
pause
endlocal
