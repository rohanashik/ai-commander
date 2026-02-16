# AI Commander

**Stop Googling terminal commands. Just describe what you want.**

![AI Commander Demo](demo.gif)

<p align="center">
  <a href="https://github.com/rohanashik/ai-commander/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/rohanashik/ai-commander/stargazers"><img src="https://img.shields.io/github/stars/rohanashik/ai-commander?style=social" alt="GitHub stars"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://github.com/rohanashik/ai-commander/releases"><img src="https://img.shields.io/github/v/release/rohanashik/ai-commander" alt="Release"></a>
</p>

---

## Table of Contents

- [The Problem](#the-problem)
- [If You're in DevOps, This Is Your Secret Weapon](#if-youre-in-devops-this-is-your-secret-weapon)
- [How It Works](#how-it-works)
- [What Powers It](#what-powers-it)
- [Built With](#built-with)
- [Roadmap](#roadmap)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Manual Setup](#manual-setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Uninstall](#uninstall)
- [Security Note](#security-note)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## The Problem

I've been coding professionally for years. I can architect systems, debug production issues, and ship features under pressure. But ask me to write a `tar` command from memory? I'm opening a new browser tab.

Every single time I need a command — whether it's a `find` with the right flags, a `git reset` that doesn't destroy my work, or an `awk` one-liner — I either Google it or dig through my own notes to confirm the syntax. It's a 30-second detour that happens dozens of times a day.

I got tired of it. So I built **AI Commander** — a tool that sits right in your terminal and converts plain English into the exact command you need. No context switching. No browser tabs. No Stack Overflow rabbit holes.

```bash
?? undo my last commit but keep the changes
# git reset --soft HEAD~1

?? compress this folder into a tar.gz
# tar -czf folder.tar.gz .

?? what is using port 3000
# lsof -i :3000

?? show my public IP address
# curl -s ifconfig.me
```

Type `??`, describe what you want, and the command appears in your terminal ready to run. That's it.

---

## If You're in DevOps, This Is Your Secret Weapon

You know the pain. Azure CLI, AWS CLI, GCP, kubectl, terraform — every cloud provider has its own syntax, its own flags, its own way of doing things. Nobody memorizes all of it.

With AI Commander, you don't have to. Just tell it what you want to achieve:

```bash
?? list all running EC2 instances in us-east-1
?? scale my kubernetes deployment to 5 replicas
?? create a new S3 bucket called my-backup-bucket
```

It figures out the right command. You review it, hit Enter, done.

---

## How It Works

1. You type `??` followed by what you want to do in plain English
2. AI Commander reads your system context — your OS, shell, and current directory
3. It generates the right command using AI
4. **macOS/Linux:** The command appears in your shell buffer — press Enter to run, or edit it first
5. **Windows:** The command shows up with a Y/n confirmation prompt

Your commands never leave your machine in any stored form. The AI call uses your own API key, and nothing is logged or tracked.

---

## What Powers It

AI Commander currently runs on **Google Gemini Flash** — fast, accurate, and free to start with.

Support for other AI providers and **local LLMs** is on the roadmap, so you'll be able to run it fully offline if you want.

---

## Built With

- **Python 3.10+** - Core language
- **Google Gemini API** - AI-powered command generation
- **Shell Integration** - zsh, bash, PowerShell, cmd support
- **Cross-platform** - macOS, Linux, Windows support

---

## Roadmap

- [x] Google Gemini Flash integration
- [x] Cross-platform support (macOS, Linux, Windows)
- [x] One-line installer scripts
- [x] Shell buffer integration (macOS/Linux)
- [ ] **Local LLM support** (run fully offline with Ollama, LM Studio, etc.)
- [ ] **Multi-provider support** (OpenAI, Anthropic, Azure OpenAI)
- [ ] Command history and favorites
- [ ] Interactive mode for complex multi-step commands
- [ ] Command explanation mode (understand existing commands)
- [ ] Auto-update mechanism
- [ ] Plugin system for custom command templates

See the [open issues](https://github.com/rohanashik/ai-commander/issues) for a full list of proposed features and known issues.

---

## Quick Start

### Prerequisites

- macOS, Linux, or Windows 10+
- Python 3.10 or higher
- A Google Gemini API key ([Get one here](https://aistudio.google.com/))

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.sh | bash
```

### Windows (PowerShell)

Download and run the installer in PowerShell **as Administrator**:
```powershell
powershell -ExecutionPolicy Bypass -Command "iwr -useb https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.ps1 | iex"
```

### Windows (cmd)

Download and run the installer in Command Prompt **as Administrator**:
```cmd
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.bat -o install.bat && install.bat
```

**What the installer does:**
- Checks Python version
- Downloads and sets up AI Commander
- Guides you through API key setup
- Configures your shell automatically
- Ready to use in 30 seconds

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
    $cmd = & "$env:APPDATA\ai-commander\venv\Scripts\python.exe" "$env:APPDATA\ai-commander\ai.py" @args 2>&1 | Where-Object { $_ -is [string] -or $_.GetType().Name -eq 'ErrorRecord' } | Out-String
    $cmd = $cmd.Trim()
    if ($cmd -and -not $cmd.StartsWith('Error:')) {
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

---

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
powershell -ExecutionPolicy Bypass -Command "iwr -useb https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.ps1 | iex"
```

Or download and run locally:
```powershell
powershell -ExecutionPolicy Bypass -File uninstall.ps1
```

**Windows (cmd):**
```cmd
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.bat -o uninstall.bat && uninstall.bat
```

This removes the installation directory and cleans up shell integration (rc files on macOS/Linux, PowerShell profile/AutoRun registry on Windows). The PowerShell uninstaller includes robust error handling for locked files and read-only attributes in the venv folder.

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

**Windows PowerShell: "cannot be loaded because running scripts is disabled on this system"**

This occurs when PowerShell's execution policy blocks the profile script. Fix it by running this command in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then open a new PowerShell window. This allows locally-created scripts to run while still requiring remote scripts to be signed.

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### How to Contribute

1. **Fork the Project**
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Reporting Bugs

If you find a bug, please [open an issue](https://github.com/rohanashik/ai-commander/issues/new) with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your OS, shell, and Python version

### Suggesting Features

Feature requests are welcome! Please [open an issue](https://github.com/rohanashik/ai-commander/issues/new) and tag it as `enhancement`. Include:
- A clear use case
- Why this feature would be useful
- Any implementation ideas you have

### Development Setup

```bash
# Clone the repo
git clone https://github.com/rohanashik/ai-commander.git
cd ai-commander

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your API key
export GEMINI_API_KEY="your-api-key-here"

# Test the tool
python ai.py "list files"
```

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Keep functions focused and testable
- Write clear commit messages

---

## Support

If you find AI Commander helpful, please consider:

- ⭐ **Starring the repository** - It helps others discover the project
- 🐛 **Reporting issues** - Help improve the tool for everyone
- 💡 **Suggesting features** - Share your ideas for improvements
- 📢 **Sharing with others** - Spread the word if you find it useful

### Get Help

- **Bug Reports:** [GitHub Issues](https://github.com/rohanashik/ai-commander/issues)
- **Feature Requests:** [GitHub Issues](https://github.com/rohanashik/ai-commander/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rohanashik/ai-commander/discussions)

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

This means you are free to use, modify, and distribute this software, even for commercial purposes, as long as you include the original copyright notice.

---

## Acknowledgments

- **Google Gemini** for providing the powerful and accessible AI API
- The open-source community for inspiration and feedback
- All contributors who help improve this project
- Everyone who has starred, forked, or shared this project

---

**If you found this helpful, please consider giving it a ⭐ star on GitHub!**
