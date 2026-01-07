@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"

REM Download ADB if needed
call "%SCRIPT_DIR%helpers\download_adb.bat" "%SCRIPT_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to download or extract ADB
    exit /b 1
)

set "ADB=%SCRIPT_DIR%adb\adb.exe"

REM Check if config.ini exists
if not exist "%SCRIPT_DIR%config.ini" (
    echo ERROR: config.ini not found
    exit /b 1
)

REM Parse config.ini and build device list
set DEVICE_COUNT=0
set IN_SECTION=0

for /f "usebackq tokens=1,* delims==" %%A in ("%SCRIPT_DIR%config.ini") do (
    set "LINE=%%A"
    REM Check if we're in the firesticks section
    if "!LINE!"=="[firesticks]" (
        set IN_SECTION=1
    ) else if "!LINE:~0,1!"=="[" (
        set IN_SECTION=0
    ) else if !IN_SECTION!==1 (
        REM Skip empty lines and comments
        if not "!LINE!"=="" (
            if not "!LINE:~0,1!"=="#" (
                REM Only process lines that have an = sign (key=value format)
                REM Check if %%B is defined (meaning there was a value after =)
                if not "%%B"=="" (
                    set /a DEVICE_COUNT+=1
                    set "DEVICE_NAME_!DEVICE_COUNT!=%%A"
                    set "DEVICE_HOSTNAME_!DEVICE_COUNT!=%%B"
                )
            )
        )
    )
)

if %DEVICE_COUNT%==0 (
    echo ERROR: No devices found in config.ini
    exit /b 1
)

REM Display device list
echo.
echo Available devices:
echo.
for /l %%I in (1,1,%DEVICE_COUNT%) do (
    echo   %%I. !DEVICE_NAME_%%I!
)

echo.
set /p SELECTION="Select a device (1-%DEVICE_COUNT%): "

REM Validate selection
if "%SELECTION%"=="" (
    echo ERROR: No selection made
    exit /b 1
)

REM Check if selection is a valid number
set /a SELECTION_NUM=%SELECTION% 2>nul
if errorlevel 1 (
    echo ERROR: Invalid selection
    exit /b 1
)

if %SELECTION_NUM% LSS 1 (
    echo ERROR: Selection must be at least 1
    exit /b 1
)

if %SELECTION_NUM% GTR %DEVICE_COUNT% (
    echo ERROR: Selection must be at most %DEVICE_COUNT%
    exit /b 1
)

REM Get selected device info
set "SELECTED_NAME=!DEVICE_NAME_%SELECTION_NUM%!"
set "SELECTED_HOSTNAME=!DEVICE_HOSTNAME_%SELECTION_NUM%!"

echo.
echo Resolving hostname for %SELECTED_NAME% (%SELECTED_HOSTNAME%)...

REM Resolve hostname to IP
call "%SCRIPT_DIR%helpers\adb_helpers.bat" resolve_hostname "%SELECTED_HOSTNAME%"
if errorlevel 1 (
    echo ERROR: Failed to resolve hostname "%SELECTED_HOSTNAME%"
    exit /b 1
)

set "SELECTED_IP=!RESOLVED_IP!"
echo Resolved to IP: %SELECTED_IP%

echo.
echo Connecting to %SELECTED_NAME% (%SELECTED_HOSTNAME% - %SELECTED_IP%)...

REM Disconnect any existing connections first
"%ADB%" disconnect >nul 2>&1

REM Connect to the device
"%ADB%" connect %SELECTED_IP%
if errorlevel 1 (
    echo ERROR: Failed to connect to %SELECTED_NAME%
    exit /b 1
)

REM Wait a moment for connection to establish
timeout /t 2 /nobreak >nul

REM Check if device is connected
"%ADB%" devices | findstr /C:"%SELECTED_IP%" | findstr /C:"device" >nul
if errorlevel 1 (
    echo WARNING: Device connected but may not be authorized
) else (
    echo Successfully connected to %SELECTED_NAME%!
)

echo.
echo Disconnecting...
"%ADB%" disconnect %SELECTED_IP%
if errorlevel 1 (
    echo WARNING: Failed to disconnect cleanly
) else (
    echo Disconnected successfully.
)

exit /b 0
