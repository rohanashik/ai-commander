import sys
import litellm
from dotenv import load_dotenv

load_dotenv()

litellm.suppress_debug_info = True

IS_WINDOWS = sys.platform == 'win32'

__version__ = "1.0.0"
GITHUB_REPO = "rohanashik/ai-commander"

# ANSI color constants
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

SHELL_EXAMPLES = {
    'cmd': """Examples for Windows CMD:
    Input: list all files
    Output: dir /a

    Input: show current directory
    Output: cd

    Input: delete a file
    Output: del filename.txt""",

    'powershell': """Examples for PowerShell:
    Input: list all files
    Output: Get-ChildItem -Force

    Input: show current directory
    Output: Get-Location

    Input: delete a file
    Output: Remove-Item filename.txt""",

    'unix': """Examples for Unix/Linux:
    Input: list all files
    Output: ls -la

    Input: show disk usage
    Output: df -h

    Input: find files
    Output: find . -name "*.txt" """,
}

LLM_ERROR_MESSAGES = {
    litellm.RateLimitError: "Error: Rate limit reached. Please wait a moment and try again.",
    litellm.AuthenticationError: "Error: Invalid API key. Check your GEMINI_API_KEY.",
    litellm.Timeout: "Error: Request timed out. Please try again.",
    litellm.APIConnectionError: "Error: Could not connect to the API. Check your internet connection.",
}
