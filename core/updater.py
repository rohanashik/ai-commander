import sys
import os
import urllib.request
import json
from packaging import version

from .constants import __version__, GITHUB_REPO, YELLOW, GREEN, NC


def check_for_updates(silent=False):
    """Check GitHub for new releases"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'ai-commander')

        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            latest_version = data['tag_name'].lstrip('v')

            if version.parse(latest_version) > version.parse(__version__):
                print(f"\n{YELLOW}┌────────────────────────────────────────────┐{NC}", file=sys.stderr)
                print(f"{YELLOW}│  📦 Update Available!                     │{NC}", file=sys.stderr)
                print(f"{YELLOW}│  Current: v{__version__:<10s} Latest: v{latest_version:<10s} │{NC}", file=sys.stderr)
                print(f"{YELLOW}└────────────────────────────────────────────┘{NC}", file=sys.stderr)
                if os.name == 'nt':
                    print(f"{GREEN}Run this to update:{NC} powershell -Command \"irm https://raw.githubusercontent.com/{GITHUB_REPO}/main/install.bat -OutFile install.bat; .\\install.bat\"\n", file=sys.stderr)
                else:
                    print(f"{GREEN}Run this to update:{NC} curl -fsSL https://raw.githubusercontent.com/{GITHUB_REPO}/main/install.sh | bash\n", file=sys.stderr)
                return True
            elif not silent:
                print(f"✓ You're running the latest version (v{__version__})\n")
                return False
    except Exception:
        if not silent:
            print("⚠ Could not check for updates. Please check your internet connection.\n")
    return False
