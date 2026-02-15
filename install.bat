@echo off
setlocal enabledelayedexpansion

echo.
echo   AI Commander - INSTALLER
echo   =================================
echo.

:: Check Python
echo Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 goto :try_python3
set "PYTHON=python"
goto :check_py3

:try_python3
where python3 >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 not found
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    exit /b 1
)
set "PYTHON=python3"

:check_py3
for /f "tokens=*" %%i in ('%PYTHON% -c "import sys; print(sys.version_info[0])"') do set PY_MAJOR=%%i
if "%PY_MAJOR%" neq "3" (
    echo [ERROR] Python 3 is required, but found Python %PY_MAJOR%
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON% -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set PY_VERSION=%%i
echo [OK] Found Python %PY_VERSION%

:: Install location
set "INSTALL_DIR=%APPDATA%\ai-commander"
echo.
echo Installing to: %INSTALL_DIR%

:: Clean install if exists
if not exist "%INSTALL_DIR%" goto :fresh_install
set /p "REPLY=Existing installation found. Reinstall? (y/n) "
if /i "!REPLY!" neq "y" exit /b 0
rmdir /s /q "%INSTALL_DIR%"

:fresh_install
mkdir "%INSTALL_DIR%"

:: Download latest code
echo.
echo Downloading AI Commander...
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] curl not found. Please install curl or download manually.
    exit /b 1
)
where tar >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] tar not found. Please install tar or download manually.
    exit /b 1
)

curl -sL https://github.com/rohanashik/ai-commander/archive/main.tar.gz -o "%TEMP%\ai-commander.tar.gz"
tar xzf "%TEMP%\ai-commander.tar.gz" -C "%INSTALL_DIR%" --strip-components=1
del "%TEMP%\ai-commander.tar.gz"

:: Setup virtual environment
echo Setting up Python environment...
%PYTHON% -m venv "%INSTALL_DIR%\venv"
call "%INSTALL_DIR%\venv\Scripts\activate.bat"
call pip install -q --upgrade pip
call pip install -q -r "%INSTALL_DIR%\requirements.txt"
call deactivate

:: API Key setup
echo.
echo =====================================
echo API Key Setup
echo =====================================
echo.
echo You need a free Gemini API key to use AI Commander.
echo Get one here: https://aistudio.google.com/app/apikey
echo.

set "API_CONFIGURED="
if not exist "%INSTALL_DIR%\.env" goto :ask_key
set /p "REPLY=API key already configured. Update? (y/n) "
if /i "!REPLY!" neq "y" set "API_CONFIGURED=1"

:ask_key
if defined API_CONFIGURED goto :setup_shell
set /p "API_KEY=Enter your Gemini API key: "
if "!API_KEY!"=="" (
    echo [ERROR] API key required
    exit /b 1
)
echo GEMINI_API_KEY=!API_KEY!> "%INSTALL_DIR%\.env"
echo [OK] API key saved

:setup_shell
:: Setup doskey macros via AutoRun registry
echo.
echo Configuring shell integration...

set "PYTHON_EXE=%INSTALL_DIR%\venv\Scripts\python.exe"
set "AI_SCRIPT=%INSTALL_DIR%\ai.py"

:: Create a cmd init script
set "CMD_INIT=%INSTALL_DIR%\cmd_init.bat"
echo @echo off> "%CMD_INIT%"
echo doskey ??="!PYTHON_EXE!" "!AI_SCRIPT!" --execute $*>> "%CMD_INIT%"
echo doskey ai="!PYTHON_EXE!" "!AI_SCRIPT!" --execute $*>> "%CMD_INIT%"

:: Register via AutoRun so it loads on every cmd.exe session
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "\"%CMD_INIT%\"" /f >nul 2>&1
if %errorlevel% neq 0 goto :shell_fail
echo [OK] Shell integration configured via cmd AutoRun
goto :shell_done
:shell_fail
echo [ERROR] Could not set AutoRun registry key.
echo You can manually add this to your cmd startup:
echo   "%CMD_INIT%"
:shell_done

:: Load macros for current session
call "%CMD_INIT%"

:: Success
echo.
echo =====================================
echo   Installation Complete!
echo =====================================
echo.
echo Try it out:
echo      ?? list all files including hidden ones
echo      ai show disk usage in human readable format
echo      ?? find all python files modified today
echo.
echo The command will be shown for confirmation before running.
echo.
echo Open a new cmd window to start using AI Commander!
echo.

endlocal
