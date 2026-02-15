#!/bin/bash
set -e

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "  ▄▖▄▖  ▄▖             ▌    "
echo "  ▌▌▐   ▌ ▛▌▛▛▌▛▛▌▀▌▛▌▛▌█▌▛▘"
echo "  ▛▌▟▖  ▙▖▙▌▌▌▌▌▌▌█▌▌▌▙▌▙▖▌ "
echo -e "${NC}"
echo -e "  ${BLUE}╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸${NC}"
echo -e "  ${GREEN}         ⚡  INSTALLER  ⚡${NC}"
echo -e "  ${BLUE}╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸${NC}"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3.10+ from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Install location
INSTALL_DIR="$HOME/.ai-commander"
echo ""
echo "Installing to: $INSTALL_DIR"

# Clean install if exists
if [ -d "$INSTALL_DIR" ]; then
    read -p "Existing installation found. Reinstall? (y/n) " -n 1 -r < /dev/tty
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        exit 0
    fi
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download latest code
echo ""
echo "Downloading AI Commander..."
curl -sL https://github.com/rohanashik/ai-commander/archive/main.tar.gz | tar xz --strip-components=1

# Setup virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# API Key setup
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}API Key Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "You need a free Gemini API key to use AI Commander."
echo "Get one here: https://aistudio.google.com/app/apikey"
echo ""

if [ -f ".env" ]; then
    read -p "API key already configured. Update? (y/n) " -n 1 -r < /dev/tty
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        API_CONFIGURED=true
    fi
fi

if [ -z "$API_CONFIGURED" ]; then
    read -p "Enter your Gemini API key: " API_KEY < /dev/tty
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}❌ API key required${NC}"
        exit 1
    fi
    echo "GEMINI_API_KEY=$API_KEY" > .env
    echo -e "${GREEN}✓ API key saved${NC}"
fi

# Detect shell
echo ""
echo "Configuring shell integration..."

SHELL_RC=""
SHELL_NAME=""

if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
    SHELL_FUNCTION='setopt nonomatch 2>/dev/null
function ?? {
    cmd=$('$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@")
    print -z "$cmd"
}
function ai {
    if [[ "$1" == "--config" ]]; then
        '$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@"
        return
    fi
    cmd=$('$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@")
    print -z "$cmd"
}'
elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
    SHELL_FUNCTION='function ?? {
    cmd=$('$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@")
    READLINE_LINE="$cmd"
    READLINE_POINT=${#READLINE_LINE}
}
function ai {
    if [[ "$1" == "--config" ]]; then
        '$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@"
        return
    fi
    cmd=$('$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@")
    READLINE_LINE="$cmd"
    READLINE_POINT=${#READLINE_LINE}
}'
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_RC="$HOME/.bash_profile"
    SHELL_NAME="bash"
    SHELL_FUNCTION='function ?? {
    cmd=$('$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@")
    READLINE_LINE="$cmd"
    READLINE_POINT=${#READLINE_LINE}
}
function ai {
    if [[ "$1" == "--config" ]]; then
        '$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@"
        return
    fi
    cmd=$('$INSTALL_DIR'/venv/bin/python '$INSTALL_DIR'/ai.py "$@")
    READLINE_LINE="$cmd"
    READLINE_POINT=${#READLINE_LINE}
}'
fi

if [ -z "$SHELL_RC" ]; then
    echo -e "${RED}❌ Could not detect shell configuration file${NC}"
    echo "Please manually add the function to your shell config."
    exit 1
fi

# Check if already installed
if grep -q "AI Commander" "$SHELL_RC" 2>/dev/null; then
    echo -e "${GREEN}✓ Shell integration already configured${NC}"
else
    echo "" >> "$SHELL_RC"
    echo "# AI Commander - Natural language terminal commands" >> "$SHELL_RC"
    echo "$SHELL_FUNCTION" >> "$SHELL_RC"
    echo -e "${GREEN}✓ Added to $SHELL_RC${NC}"
fi

# Success message
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Try it out (use ${BLUE}??${NC} or ${BLUE}ai${NC}):"
echo -e "     ${BLUE}?? list all files including hidden ones${NC}"
echo -e "     ${BLUE}ai show disk usage in human readable format${NC}"
echo -e "     ${BLUE}?? find all python files modified today${NC}"
echo ""
echo "The command will appear in your terminal - press Enter to run it!"
echo ""
echo "Reloading shell..."
exec $SHELL