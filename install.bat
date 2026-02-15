@echo off
setlocal enabledelayedexpansion

:: Colors via ANSI escape codes (Windows 10+)
set "RED=[31m"
set "GREEN=[32m"
set "BLUE=[34m"
set "NC=[0m"

echo.
echo %BLUE%  AI Commander - INSTALLER%NC%
echo %BLUE%  =================================%NC%
echo.

:: Check Python
echo Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%Python 3 not found%NC%
        echo Please install Python 3.10+ from: https://www.python.org/downloads/
        exit /b 1
    )
    set "PYTHON=python3"
) else (
    set "PYTHON=python"
)

:: Verify it's Python 3
for /f "tokens=*" %%i in ('%PYTHON% -c "import sys; print(sys.version_info[0])"') do set PY_MAJOR=%%i
if "%PY_MAJOR%" neq "3" (
    echo %RED%Python 3 is required, but found Python %PY_MAJOR%%NC%
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON% -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set PY_VERSION=%%i
echo %GREEN%Found Python %PY_VERSION%%NC%

:: Install location
set "INSTALL_DIR=%APPDATA%\ai-commander"
echo.
echo Installing to: %INSTALL_DIR%

:: Clean install if exists
if exist "%INSTALL_DIR%" (
    set /p "REPLY=Existing installation found. Reinstall? (y/n) "
    if /i "!REPLY!" neq "y" exit /b 0
    rmdir /s /q "%INSTALL_DIR%"
)

mkdir "%INSTALL_DIR%"

:: Download latest code
echo.
echo Downloading AI Commander...
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%curl not found. Please install curl or download manually.%NC%
    exit /b 1
)
where tar >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%tar not found. Please install tar or download manually.%NC%
    exit /b 1
)

curl -sL https://github.com/rohanashik/ai-commander/archive/main.tar.gz -o "%TEMP%\ai-commander.tar.gz"
tar xzf "%TEMP%\ai-commander.tar.gz" -C "%INSTALL_DIR%" --strip-components=1
del "%TEMP%\ai-commander.tar.gz"

:: Setup virtual environment
echo Setting up Python environment...
%PYTHON% -m venv "%INSTALL_DIR%\venv"
call "%INSTALL_DIR%\venv\Scripts\activate.bat"
pip install -q --upgrade pip
pip install -q -r "%INSTALL_DIR%\requirements.txt"
call deactivate

:: API Key setup
echo.
echo %BLUE%=====================================%NC%
echo %BLUE%API Key Setup%NC%
echo %BLUE%=====================================%NC%
echo.
echo You need a free Gemini API key to use AI Commander.
echo Get one here: https://aistudio.google.com/app/apikey
echo.

set "API_CONFIGURED="
if exist "%INSTALL_DIR%\.env" (
    set /p "REPLY=API key already configured. Update? (y/n) "
    if /i "!REPLY!" neq "y" set "API_CONFIGURED=1"
)

if not defined API_CONFIGURED (
    set /p "API_KEY=Enter your Gemini API key: "
    if "!API_KEY!"=="" (
        echo %RED%API key required%NC%
        exit /b 1
    )
    echo GEMINI_API_KEY=!API_KEY!> "%INSTALL_DIR%\.env"
    echo %GREEN%API key saved%NC%
)

:: Setup doskey macros via AutoRun registry
echo.
echo Configuring shell integration...

set "PYTHON_EXE=%INSTALL_DIR%\venv\Scripts\python.exe"
set "AI_SCRIPT=%INSTALL_DIR%\ai.py"
set "MACRO_CMD=doskey ??=%PYTHON_EXE% %AI_SCRIPT% --execute $* $T doskey ai=%PYTHON_EXE% %AI_SCRIPT% --execute $*"

:: Create a cmd init script
set "CMD_INIT=%INSTALL_DIR%\cmd_init.bat"
(
    echo @echo off
    echo doskey ??="%PYTHON_EXE%" "%AI_SCRIPT%" --execute $*
    echo doskey ai="%PYTHON_EXE%" "%AI_SCRIPT%" --execute $*
) > "%CMD_INIT%"

:: Register via AutoRun so it loads on every cmd.exe session
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "\"%CMD_INIT%\"" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%Shell integration configured (cmd AutoRun)%NC%
) else (
    echo %RED%Could not set AutoRun registry key.%NC%
    echo You can manually add this to your cmd startup:
    echo   "%CMD_INIT%"
)

:: Load macros for current session
call "%CMD_INIT%"

:: Success
echo.
echo %GREEN%=====================================%NC%
echo %GREEN%Installation Complete!%NC%
echo %GREEN%=====================================%NC%
echo.
echo Try it out (use ?? or ai):
echo      %BLUE%?? list all files including hidden ones%NC%
echo      %BLUE%ai show disk usage in human readable format%NC%
echo      %BLUE%?? find all python files modified today%NC%
echo.
echo The command will be shown for confirmation before running.
echo.
echo Open a new cmd window to start using AI Commander!
echo.

endlocal
