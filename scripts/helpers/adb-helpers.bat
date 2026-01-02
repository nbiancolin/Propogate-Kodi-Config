@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM   call adb_helpers.bat connect_and_verify 192.168.1.50
REM Requires ADB variable set to path of adb.exe


if "%1"=="" exit /b 1

set COMMAND=%1
shift

if "%COMMAND%"=="connect_and_verify" goto :connect_and_verify

echo ERROR: Unknown helper "%COMMAND%"
exit /b 1

REM ============================
:connect_and_verify
REM %1 = IP
%ADB% disconnect >nul 2>&1
%ADB% connect %1 >nul

if errorlevel 1 exit /b 1

for /f "tokens=1,2" %%A in ('%ADB% devices') do (
    if "%%A"=="%1" if "%%B"=="device" exit /b 0
)

exit /b 1
