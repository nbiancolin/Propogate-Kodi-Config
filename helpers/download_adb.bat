@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Downloads and extracts ADB platform-tools if not already present
REM Usage: call download_adb.bat [SCRIPT_DIR]
REM   SCRIPT_DIR: Optional. Directory where the script is located. If not provided, uses current directory.

set "SCRIPT_DIR=%~1"
if "%SCRIPT_DIR%"=="" set "SCRIPT_DIR=%~dp0"

REM Ensure SCRIPT_DIR ends with a backslash
if not "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR%\"

if exist "%SCRIPT_DIR%adb\adb.exe" (
    exit /b 0
)

echo ADB not found. Downloading platform-tools...

set ADB_ZIP=%SCRIPT_DIR%platform-tools-latest-windows.zip
set ADB_URL=https://dl.google.com/android/repository/platform-tools-latest-windows.zip

powershell -NoProfile -Command ^
    "Invoke-WebRequest -Uri '%ADB_URL%' -OutFile '%ADB_ZIP%'"

if errorlevel 1 (
    echo ERROR: Failed to download ADB
    exit /b 1
)

powershell -NoProfile -Command ^
    "Expand-Archive -Force '%ADB_ZIP%' '%SCRIPT_DIR%'"

if errorlevel 1 (
    echo ERROR: Failed to extract ADB
    if exist "%ADB_ZIP%" del "%ADB_ZIP%"
    exit /b 1
)

if exist "%SCRIPT_DIR%platform-tools" (
    if exist "%SCRIPT_DIR%adb" rmdir /s /q "%SCRIPT_DIR%adb"
    rename "%SCRIPT_DIR%platform-tools" adb
)

if exist "%ADB_ZIP%" del "%ADB_ZIP%"

if not exist "%SCRIPT_DIR%adb\adb.exe" (
    echo ERROR: ADB extraction failed
    exit /b 1
)

exit /b 0

