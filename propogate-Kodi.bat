@echo off
setlocal EnableExtensions EnableDelayedExpansion

set SRC_IP=%1
set DST_IP=%2

set "SCRIPT_DIR=%~dp0"

if "%SRC_IP%"=="" (
    echo ERROR: Missing source IP
    exit /b 1
)
if "%DST_IP%"=="" (
    echo ERROR: Missing destination IP
    exit /b 1
)

call "%SCRIPT_DIR%helpers\download_adb.bat" "%SCRIPT_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to download or extract ADB
    exit /b 1
)


set ADB=adb\adb.exe

echo Propagating Kodi settings from %SRC_IP% to %DST_IP%...

REM ----- Pull from source -----
call "%SCRIPT_DIR%helpers\adb_helpers.bat" connect_and_verify %SRC_IP%
if errorlevel 1 (
    echo ERROR: Source connection failed
    exit /b 1
)

if exist temp rmdir /s /q temp
mkdir temp

%ADB% pull /sdcard/Android/data/org.xbmc.kodi/files/.kodi temp\.kodi
if errorlevel 1 (
    echo ERROR: Failed to pull Kodi data
    exit /b 1
)

%ADB% disconnect

REM ----- Push to destination -----
call "%SCRIPT_DIR%helpers\adb_helpers.bat" connect_and_verify %DST_IP%
if errorlevel 1 (
    echo ERROR: Destination connection failed
    exit /b 1
)

%ADB% push temp\.kodi /sdcard/Android/data/org.xbmc.kodi/files/
if errorlevel 1 (
    echo ERROR: Failed to push Kodi data
    exit /b 1
)

%ADB% disconnect

echo Kodi config data successfully transferred. Have a nice day!
exit /b 0
