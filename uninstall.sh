#!/bin/bash
set -e

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}"
echo "  ▄▖▄▖  ▄▖             ▌    "
echo "  ▌▌▐   ▌ ▛▌▛▛▌▛▛▌▀▌▛▌▛▌█▌▛▘"
echo "  ▛▌▟▖  ▙▖▙▌▌▌▌▌▌▌█▌▌▌▙▌▙▖▌ "
echo -e "${NC}"
echo -e "  ${BLUE}╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸${NC}"
echo -e "  ${RED}        ⚠  UNINSTALLER  ⚠${NC}"
echo -e "  ${BLUE}╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸${NC}"
echo ""

INSTALL_DIR="$HOME/.ai-commander"

# Check if installed
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}AI Commander is not installed at $INSTALL_DIR${NC}"
    exit 0
fi

# Remove shell integration from rc files
echo "Removing shell integration..."

for RC_FILE in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile"; do
    if [ -f "$RC_FILE" ] && grep -q "AI Commander" "$RC_FILE" 2>/dev/null; then
        # Remove the comment and function block
        sed -i.bak '/# AI Commander - Natural language terminal commands/,/^}/d' "$RC_FILE"
        # Clean up any trailing blank lines left behind
        sed -i.bak -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$RC_FILE"
        rm -f "${RC_FILE}.bak"
        echo -e "${GREEN}✓ Removed shell functions from $RC_FILE${NC}"
    fi
done

# Remove installation directory
echo "Removing $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
echo -e "${GREEN}✓ Removed installation directory${NC}"

# Done
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ AI Commander has been uninstalled.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Please reload your shell or run:"
echo -e "  ${BLUE}source ~/.zshrc${NC}  (or your shell's rc file)"
echo ""
