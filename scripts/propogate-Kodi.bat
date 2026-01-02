@echo off
setlocal EnableExtensions EnableDelayedExpansion

set SRC_IP=%1
set DST_IP=%2

if "%SRC_IP%"=="" (
    echo ERROR: Missing source IP
    exit /b 1
)
if "%DST_IP%"=="" (
    echo ERROR: Missing destination IP
    exit /b 1
)

if not exist "adb\adb.exe" (
    echo ADB not found. Downloading platform-tools...

    set ADB_ZIP=platform-tools-latest-windows.zip
    set ADB_URL=https://dl.google.com/android/repository/platform-tools-latest-windows.zip

    powershell -NoProfile -Command ^
        "Invoke-WebRequest -Uri '!ADB_URL!' -OutFile '!ADB_ZIP!'"

    if errorlevel 1 (
        echo ERROR: Failed to download ADB
        exit /b 1
    )

    powershell -NoProfile -Command ^
        "Expand-Archive -Force '!ADB_ZIP!' ."

    if errorlevel 1 (
        echo ERROR: Failed to extract ADB
        exit /b 1
    )

    rename platform-tools adb
    del "!ADB_ZIP!"
)

set ADB=adb\adb.exe

REM ============================
REM Start work
REM ============================
echo Propagating Kodi settings from %SRC_IP% to %DST_IP%...

REM ----- Pull from source -----
call helpers\adb_helpers.bat connect_and_verify %SRC_IP%
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
call helpers\adb_helpers.bat connect_and_verify %DST_IP%
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
