@echo off
setlocal enabledelayedexpansion

:: Colors via ANSI escape codes (Windows 10+)
set "RED=[31m"
set "GREEN=[32m"
set "BLUE=[34m"
set "NC=[0m"

echo.
echo %RED%  AI Commander - UNINSTALLER%NC%
echo %BLUE%  =================================%NC%
echo.

set "INSTALL_DIR=%APPDATA%\ai-commander"

:: Check if installed
if not exist "%INSTALL_DIR%" (
    echo %RED%AI Commander is not installed at %INSTALL_DIR%%NC%
    exit /b 0
)

:: Remove AutoRun registry entry
echo Removing shell integration...
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun 2^>nul') do set "CURRENT_AUTORUN=%%b"

if defined CURRENT_AUTORUN (
    echo !CURRENT_AUTORUN! | findstr /i "ai-commander" >nul 2>&1
    if !errorlevel! equ 0 (
        reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
        echo %GREEN%Removed cmd AutoRun registry entry%NC%
    )
)

:: Remove installation directory
echo Removing %INSTALL_DIR%...
rmdir /s /q "%INSTALL_DIR%"
echo %GREEN%Removed installation directory%NC%

:: Done
echo.
echo %GREEN%=====================================%NC%
echo %GREEN%AI Commander has been uninstalled.%NC%
echo %GREEN%=====================================%NC%
echo.
echo Open a new cmd window for changes to take effect.
echo.

endlocal
