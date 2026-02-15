# AI Commander

Convert natural language to terminal commands using AI.

## Features

- Natural language to terminal command conversion
- Context-aware (detects OS, shell, current directory)
- Fast command generation with Gemini 2.5 Flash
- Commands appear in your shell buffer ready to execute

## Prerequisites

- macOS
- Python 3.10 or higher
- A Google Gemini API key ([Get one here](https://aistudio.google.com/))

## Installation


### One-Line Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/install.sh | bash
```

**What this does:**
- ✅ Checks Python version
- ✅ Downloads and sets up AI Commander
- ✅ Guides you through API key setup
- ✅ Configures your shell automatically
- ✅ Ready to use in 30 seconds

### Manual Setup

If you prefer to set things up manually instead of using `install.sh`, add the following to your `~/.zshrc` (replace `/path/to/ai-commander` with the actual path):

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

The command will appear in your terminal buffer. Press Enter to execute it, or edit it first if needed.

## Configuration

To open the settings menu (update API key, uninstall, etc.):

```bash
ai --config
```

## Uninstall

To completely remove AI Commander:

```bash
curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.sh | bash
```

This will remove the installation directory (`~/.ai-commander`) and clean up shell functions from your rc files.

## How It Works

1. You type a natural language request after `??`
2. The script sends your request + system context to Gemini AI
3. AI generates the appropriate terminal command
4. Command appears in your shell ready to execute

## Security Note

Your API key should be stored as an environment variable, never hardcoded. The installation script will guide you through this setup.

## Troubleshooting

**Command not found: ??**
- Make sure you've reloaded your shell: `source ~/.zshrc`

**API Error**
- Verify your `GEMINI_API_KEY` is set: `echo $GEMINI_API_KEY`
- Check your API key is valid at [Google AI Studio](https://aistudio.google.com/)
