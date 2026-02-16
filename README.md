# AI Commander

Convert natural language to terminal commands using AI.

## Features

- Natural language to terminal command conversion
- Context-aware (detects OS, shell, current directory)
- Fast command generation with Gemini 2.5 Flash
- Cross-platform: macOS, Linux, and Windows
- Commands appear in your shell buffer ready to execute (macOS/Linux) or prompt for confirmation (Windows)

## Prerequisites

- macOS, Linux, or Windows 10+
- Python 3.10 or higher
- A Google Gemini API key ([Get one here](https://aistudio.google.com/))

## Installation

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.sh | bash
```

### Windows (PowerShell)

Download and run the installer in PowerShell:
```powershell
iwr -useb https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.ps1 | iex
```

### Windows (cmd)

Download and run the installer in Command Prompt:
```cmd
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.bat -o install.bat && install.bat
```

**What the installer does:**
- ✅ Checks Python version
- ✅ Downloads and sets up AI Commander
- ✅ Guides you through API key setup
- ✅ Configures your shell automatically
- ✅ Ready to use in 30 seconds

### Manual Setup

<details>
<summary>macOS / Linux (zsh)</summary>

Add the following to your `~/.zshrc` (replace `/path/to/ai-commander` with the actual path):

```zsh
# AI Commander - Natural language terminal commands
setopt nonomatch

function '??' {
    cmd=$(/path/to/ai-commander/.venv/bin/python /path/to/ai-commander/ai.py "$@")
    print -z "$cmd"
}
```

Then reload your shell:
```bash
source ~/.zshrc
```
</details>

<details>
<summary>Windows (PowerShell)</summary>

Add the following to your PowerShell profile (`$PROFILE`):

```powershell
# AI Commander - Natural language terminal commands
function global:ai {
    if ($args[0] -eq '--config') {
        & "$env:APPDATA\ai-commander\venv\Scripts\python.exe" "$env:APPDATA\ai-commander\ai.py" @args
        return
    }
    $cmd = & "$env:APPDATA\ai-commander\venv\Scripts\python.exe" "$env:APPDATA\ai-commander\ai.py" --execute @args
    if ($cmd) {
        try {
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert($cmd)
        } catch {
            Write-Host $cmd
        }
    }
}
function global:?? { ai @args }
```

Then reload your profile:
```powershell
. $PROFILE
```
</details>

<details>
<summary>Windows (cmd)</summary>

Create a file at `%APPDATA%\ai-commander\cmd_init.bat`:
```cmd
@echo off
doskey ??="%APPDATA%\ai-commander\venv\Scripts\python.exe" "%APPDATA%\ai-commander\ai.py" --execute $*
doskey ai="%APPDATA%\ai-commander\venv\Scripts\python.exe" "%APPDATA%\ai-commander\ai.py" --execute $*
```

Then register it to run on every cmd session:
```cmd
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "\"%APPDATA%\ai-commander\cmd_init.bat\"" /f
```
</details>


## Usage

Simply type `??` followed by your natural language request:

```bash
?? list all files including hidden ones
# Generates: ls -la

?? show disk usage in human readable format
# Generates: df -h

?? find all python files in current directory
# Generates: find . -name "*.py"

?? what processes are using port 8080
# Generates: lsof -i :8080
```

**macOS / Linux:** The command appears in your shell buffer — press Enter to execute, or edit it first.

**Windows (cmd):** The command is displayed with a confirmation prompt:
```
> dir /a /b
Run this command? (Y/n):
```
Press Enter or type `y` to run, or `n` to cancel.

## Configuration

To open the settings menu (update API key, uninstall, etc.):

```bash
ai --config
```

## Uninstall

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.bat | iex
```

**Windows (cmd):**
```cmd
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.bat -o uninstall.bat && uninstall.bat
```

This removes the installation directory and cleans up shell integration (rc files on macOS/Linux, PowerShell profile/AutoRun registry on Windows).

## How It Works

1. You type a natural language request after `??`
2. The script sends your request + system context to Gemini AI
3. AI generates the appropriate terminal command
4. **macOS/Linux:** Command appears in your shell buffer ready to execute
5. **Windows:** Command is shown with a Y/n confirmation prompt, then executed

## Security Note

Your API key should be stored as an environment variable, never hardcoded. The installation script will guide you through this setup.

## Troubleshooting

**Command not found: ??**
- macOS/Linux: Make sure you've reloaded your shell: `source ~/.zshrc`
- Windows (PowerShell): Reload your profile: `. $PROFILE` or open a new PowerShell window
- Windows (cmd): Open a new cmd window after installation

**API Error**
- Verify your `GEMINI_API_KEY` is set: `echo $GEMINI_API_KEY` (or `set GEMINI_API_KEY` on Windows)
- Check your API key is valid at [Google AI Studio](https://aistudio.google.com/)

**Windows: `??` or `ai` not recognized**
- Ensure the AutoRun registry key is set: `reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun`
- Open a new cmd window (macros don't apply to already-open sessions)
