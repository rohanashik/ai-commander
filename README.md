# TerminalAI

Convert natural language to terminal commands using AI.

## Features

- 🤖 Natural language to terminal command conversion
- 🎯 Context-aware (detects OS, shell, current directory)
- ⚡ Fast command generation with Gemini 2.5 Flash
- 🔄 Commands appear in your shell buffer ready to execute

## Prerequisites

- macOS
- Python 3.10 or higher
- A Google Gemini API key ([Get one here](https://aistudio.google.com/))

## Installation

If you prefer to set things up manually instead of using `install.sh`, add the following to your `~/.zshrc` (replace `/path/to/TerminalAI` with the actual path):

```zsh
# TerminalAI - Natural language terminal commands
setopt nonomatch

function '??' {
    cmd=$(/path/to/TerminalAI/.venv/bin/python /path/to/TerminalAI/ai.py "$@")
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

