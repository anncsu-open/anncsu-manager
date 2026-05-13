@echo off
setlocal

set SCRIPT_DIR=%~dp0

call "%SCRIPT_DIR%activate.bat"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to activate the environment.
    pause
    exit /b %ERRORLEVEL%
)

start "" qgis
endlocal
