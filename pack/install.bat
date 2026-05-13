@echo off
setlocal

set SCRIPT_DIR=%~dp0
set DEST_DIR=%USERPROFILE%\Desktop\qgis

echo Installing ANNCSU QGIS environment...
echo Destination: %DEST_DIR%

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
