@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM   call adb_helpers.bat connect_and_verify 192.168.1.50
REM   call adb_helpers.bat resolve_hostname android-4
REM Requires ADB variable set to path of adb.exe (for connect_and_verify only)


if "%1"=="" exit /b 1

set COMMAND=%1
shift

if "%COMMAND%"=="connect_and_verify" goto :connect_and_verify
if "%COMMAND%"=="resolve_hostname" goto :resolve_hostname

echo ERROR: Unknown helper "%COMMAND%"
exit /b 1

REM ============================
:connect_and_verify
REM %1 = IP or hostname
REM Resolve hostname to IP if needed
set "TARGET=%1"
echo %TARGET% | findstr /R "^[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*$" >nul
if errorlevel 1 (
    REM Not an IP, resolve hostname using internal function
    set "RESOLVE_HOSTNAME=%TARGET%"
    goto :resolve_hostname_internal
)

:connect_after_resolve
"%ADB%" disconnect >nul 2>&1
"%ADB%" connect !TARGET! >nul

if errorlevel 1 exit /b 1

for /f "tokens=1,2" %%A in ('"%ADB%" devices') do (
    if "%%A"=="!TARGET!" if "%%B"=="device" exit /b 0
)

exit /b 1

REM ============================
:resolve_hostname
REM %1 = hostname
REM Returns IP in RESOLVED_IP variable, or exits with error
REM This is the external entry point - when called from another script
if "%1"=="" exit /b 1

set "RESOLVE_HOSTNAME=%1"
goto :resolve_hostname_internal

:resolve_hostname_internal
REM Internal function to resolve hostname
REM Uses RESOLVE_HOSTNAME variable, sets RESOLVED_IP variable
set "RESOLVED_IP="

REM Use PowerShell to resolve hostname to IP (more reliable than ping)
for /f "tokens=*" %%I in ('powershell -NoProfile -Command "try { [System.Net.Dns]::GetHostAddresses('!RESOLVE_HOSTNAME!')[0].IPAddressToString } catch { exit 1 }"') do (
    set "RESOLVED_IP=%%I"
)

if not defined RESOLVED_IP (
    echo ERROR: Failed to resolve hostname "!RESOLVE_HOSTNAME!"
    exit /b 1
)

REM If called from connect_and_verify, update TARGET and continue
if "%COMMAND%"=="connect_and_verify" (
    set "TARGET=!RESOLVED_IP!"
    goto :connect_after_resolve
)

REM If called externally, we need to make RESOLVED_IP available to the caller
REM Since we're in a setlocal scope, use the standard pattern to preserve the variable
REM The %RESOLVED_IP% is expanded before endlocal executes
endlocal & set "RESOLVED_IP=%RESOLVED_IP%"
exit /b 0
