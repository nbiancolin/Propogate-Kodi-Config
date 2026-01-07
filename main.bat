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

REM Main menu loop
:main_menu
cls
echo.
echo ========================================
echo    Kodi Configuration Manager
echo ========================================
echo.
echo Available devices:
echo.
for /l %%I in (1,1,%DEVICE_COUNT%) do (
    echo   %%I. !DEVICE_NAME_%%I!
)
echo.
echo Options:
echo   1. Test connection to a device
echo   2. Propagate Kodi config between devices
echo   3. Exit
echo.
set /p MENU_CHOICE="Select an option (1-3): "

if "%MENU_CHOICE%"=="1" goto :test_connection
if "%MENU_CHOICE%"=="2" goto :propagate_config
if "%MENU_CHOICE%"=="3" goto :exit_script

echo.
echo Invalid choice. Please try again.
timeout /t 2 /nobreak >nul
goto :main_menu

REM ============================
:test_connection
echo.
echo ========================================
echo    Test Connection
echo ========================================
echo.
echo Available devices:
echo.
for /l %%I in (1,1,%DEVICE_COUNT%) do (
    echo   %%I. !DEVICE_NAME_%%I!
)
echo.
set /p SELECTION="Select a device to test (1-%DEVICE_COUNT%): "

REM Validate selection
if "%SELECTION%"=="" (
    echo ERROR: No selection made
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

set /a SELECTION_NUM=%SELECTION% 2>nul
if errorlevel 1 (
    echo ERROR: Invalid selection
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %SELECTION_NUM% LSS 1 (
    echo ERROR: Selection must be at least 1
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %SELECTION_NUM% GTR %DEVICE_COUNT% (
    echo ERROR: Selection must be at most %DEVICE_COUNT%
    timeout /t 2 /nobreak >nul
    goto :main_menu
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
    timeout /t 3 /nobreak >nul
    goto :main_menu
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
    timeout /t 3 /nobreak >nul
    goto :main_menu
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

echo.
pause
goto :main_menu

REM ============================
:propagate_config
echo.
echo ========================================
echo    Propagate Kodi Config
echo ========================================
echo.
echo Available devices:
echo.
for /l %%I in (1,1,%DEVICE_COUNT%) do (
    echo   %%I. !DEVICE_NAME_%%I!
)
echo.

REM Get source device
set /p SRC_SELECTION="Select SOURCE device (1-%DEVICE_COUNT%): "

REM Validate source selection
if "%SRC_SELECTION%"=="" (
    echo ERROR: No selection made
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

set /a SRC_SELECTION_NUM=%SRC_SELECTION% 2>nul
if errorlevel 1 (
    echo ERROR: Invalid selection
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %SRC_SELECTION_NUM% LSS 1 (
    echo ERROR: Selection must be at least 1
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %SRC_SELECTION_NUM% GTR %DEVICE_COUNT% (
    echo ERROR: Selection must be at most %DEVICE_COUNT%
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

REM Get destination device
set /p DST_SELECTION="Select DESTINATION device (1-%DEVICE_COUNT%): "

REM Validate destination selection
if "%DST_SELECTION%"=="" (
    echo ERROR: No selection made
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

set /a DST_SELECTION_NUM=%DST_SELECTION% 2>nul
if errorlevel 1 (
    echo ERROR: Invalid selection
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %DST_SELECTION_NUM% LSS 1 (
    echo ERROR: Selection must be at least 1
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %DST_SELECTION_NUM% GTR %DEVICE_COUNT% (
    echo ERROR: Selection must be at most %DEVICE_COUNT%
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

if %SRC_SELECTION_NUM%==%DST_SELECTION_NUM% (
    echo ERROR: Source and destination cannot be the same device
    timeout /t 2 /nobreak >nul
    goto :main_menu
)

REM Get device info
set "SRC_NAME=!DEVICE_NAME_%SRC_SELECTION_NUM%!"
set "SRC_HOSTNAME=!DEVICE_HOSTNAME_%SRC_SELECTION_NUM%!"
set "DST_NAME=!DEVICE_NAME_%DST_SELECTION_NUM%!"
set "DST_HOSTNAME=!DEVICE_HOSTNAME_%DST_SELECTION_NUM%!"

echo.
echo Resolving hostnames...
echo Resolving source: %SRC_NAME% (%SRC_HOSTNAME%)...

REM Resolve source hostname to IP
call "%SCRIPT_DIR%helpers\adb_helpers.bat" resolve_hostname "%SRC_HOSTNAME%"
if errorlevel 1 (
    echo ERROR: Failed to resolve hostname "%SRC_HOSTNAME%"
    timeout /t 3 /nobreak >nul
    goto :main_menu
)
set "SRC_IP=!RESOLVED_IP!"
echo   Resolved to: %SRC_IP%

echo Resolving destination: %DST_NAME% (%DST_HOSTNAME%)...

REM Resolve destination hostname to IP
call "%SCRIPT_DIR%helpers\adb_helpers.bat" resolve_hostname "%DST_HOSTNAME%"
if errorlevel 1 (
    echo ERROR: Failed to resolve hostname "%DST_HOSTNAME%"
    timeout /t 3 /nobreak >nul
    goto :main_menu
)
set "DST_IP=!RESOLVED_IP!"
echo   Resolved to: %DST_IP%

echo.
echo Propagating Kodi settings from %SRC_NAME% to %DST_NAME%...
echo.

REM Call the propagate script with the resolved IPs
call "%SCRIPT_DIR%propogate-Kodi.bat" %SRC_IP% %DST_IP%

if errorlevel 1 (
    echo.
    echo ERROR: Propagation failed
    pause
    goto :main_menu
) else (
    echo.
    echo Propagation completed successfully!
    pause
    goto :main_menu
)

REM ============================
:exit_script
echo.
echo Goodbye!
exit /b 0

