# AI Commander - PowerShell Installer
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  AI Commander - INSTALLER" -ForegroundColor Cyan
Write-Host "  =================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..."
$Python = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $Python = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $Python = "python3"
} else {
    Write-Host "[ERROR] Python 3 not found" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from: https://www.python.org/downloads/"
    exit 1
}

# On Windows, "python" from the Store can be a stub that opens the Store.
# Verify it actually runs by checking the major version.
$PyMajor = & $Python -c "import sys; print(sys.version_info[0])" 2>$null
if ($LASTEXITCODE -ne 0 -or $PyMajor -ne "3") {
    Write-Host "[ERROR] Python 3 is required (found: $PyMajor)" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from: https://www.python.org/downloads/"
    exit 1
}

$PyVersion = & $Python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
Write-Host "[OK] Found Python $PyVersion" -ForegroundColor Green

# Install location
$InstallDir = "$env:APPDATA\ai-commander"
Write-Host ""
Write-Host "Installing to: $InstallDir"

# Clean install if exists
if (Test-Path $InstallDir) {
    $reply = Read-Host "Existing installation found. Reinstall? (y/n)"
    if ($reply -ne "y") { exit 0 }
    Remove-Item -Recurse -Force $InstallDir
}

New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# Download latest code
Write-Host ""
Write-Host "Downloading AI Commander..."

# Use curl.exe explicitly to avoid PowerShell's Invoke-WebRequest alias
if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] curl not found. Please install curl or download manually." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command tar -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] tar not found. Please install tar or download manually." -ForegroundColor Red
    exit 1
}

$TarFile = "$env:TEMP\ai-commander.tar.gz"
curl.exe -sL https://github.com/rohanashik/ai-commander/archive/main.tar.gz -o $TarFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Download failed." -ForegroundColor Red
    exit 1
}
tar xzf $TarFile -C $InstallDir --strip-components=1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Extraction failed." -ForegroundColor Red
    exit 1
}
Remove-Item $TarFile -ErrorAction SilentlyContinue

# Setup virtual environment
Write-Host "Setting up Python environment..."
& $Python -m venv "$InstallDir\venv"
& "$InstallDir\venv\Scripts\python.exe" -m pip install -q --upgrade pip
& "$InstallDir\venv\Scripts\python.exe" -m pip install -q -r "$InstallDir\requirements.txt"

# API Key setup
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "API Key Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need a free Gemini API key to use AI Commander."
Write-Host "Get one here: https://aistudio.google.com/app/apikey"
Write-Host ""

$ApiConfigured = $false
$EnvFile = "$InstallDir\.env"
if (Test-Path $EnvFile) {
    $reply = Read-Host "API key already configured. Update? (y/n)"
    if ($reply -ne "y") { $ApiConfigured = $true }
}

if (-not $ApiConfigured) {
    $ApiKey = Read-Host "Enter your Gemini API key"
    if ([string]::IsNullOrWhiteSpace($ApiKey)) {
        Write-Host "[ERROR] API key required" -ForegroundColor Red
        exit 1
    }
    # Write without BOM to avoid breaking dotenv parsers
    [IO.File]::WriteAllText($EnvFile, "GEMINI_API_KEY=$ApiKey")
    Write-Host "[OK] API key saved" -ForegroundColor Green
}

# Shell integration
Write-Host ""
Write-Host "Configuring shell integration..."

$PythonExe = "$InstallDir\venv\Scripts\python.exe"
$AiScript = "$InstallDir\ai.py"

# --- PowerShell profile integration ---
$ProfileDir = Split-Path $PROFILE -Parent
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
}

# Use a function for ?? instead of Set-Alias, because ?? is the
# null-coalescing operator in PowerShell 7+ and an alias would conflict.
# PSConsoleReadLine::Insert is wrapped in a try/catch for environments
# where PSReadLine is not loaded (ISE, VS Code debug console, etc).
$PsFunctionBlock = @"

# AI Commander - Natural language terminal commands
function global:ai {
    if (`$args[0] -eq '--config') {
        & "$PythonExe" "$AiScript" @args
        return
    }
    Write-Host 'Thinking...' -NoNewline
    `$cmd = & "$PythonExe" "$AiScript" @args 2>&1 | Out-String
    `$cmd = `$cmd.Trim()
    Write-Host "`r           `r" -NoNewline
    if (`$cmd -and -not `$cmd.StartsWith('Error:')) {
        try {
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert(`$cmd)
        } catch {
            Write-Host `$cmd
        }
    } elseif (`$cmd) {
        Write-Host `$cmd
    }
}
function global:?? { ai @args }
# AI Commander - END
"@

if (Test-Path $PROFILE) {
    $profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
    if ($profileContent -and $profileContent.Contains("AI Commander")) {
        Write-Host "[OK] PowerShell profile integration already configured" -ForegroundColor Green
    } else {
        # Append using .NET to avoid BOM/encoding issues with existing profile
        [IO.File]::AppendAllText($PROFILE, $PsFunctionBlock)
        Write-Host "[OK] Added to PowerShell profile: $PROFILE" -ForegroundColor Green
    }
} else {
    [IO.File]::WriteAllText($PROFILE, $PsFunctionBlock)
    Write-Host "[OK] Created PowerShell profile: $PROFILE" -ForegroundColor Green
}

# --- CMD integration (AutoRun) ---
$CmdInit = "$InstallDir\cmd_init.bat"
$CmdContent = "@echo off`r`ndoskey ??=`"$PythonExe`" `"$AiScript`" --execute `$*`r`ndoskey ai=`"$PythonExe`" `"$AiScript`" --execute `$*"
[IO.File]::WriteAllText($CmdInit, $CmdContent, [System.Text.Encoding]::GetEncoding(437))

reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "`"$CmdInit`"" /f 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] CMD shell integration configured via AutoRun" -ForegroundColor Green
} else {
    Write-Host "[WARN] Could not set CMD AutoRun registry key." -ForegroundColor Yellow
    Write-Host "  You can manually add this to your cmd startup: `"$CmdInit`""
}

# Success
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Try it out:"
Write-Host "     ?? list all files including hidden ones" -ForegroundColor Cyan
Write-Host "     ai show disk usage in human readable format" -ForegroundColor Cyan
Write-Host "     ?? find all python files modified today" -ForegroundColor Cyan
Write-Host ""
Write-Host "The command will be shown for confirmation before running."
Write-Host ""
Write-Host "Open a new PowerShell window to start using AI Commander!"
Write-Host ""
