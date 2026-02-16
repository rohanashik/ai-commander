#!/usr/bin/env python3
import sys
import os
import threading
import time
from dotenv import load_dotenv
from litellm import completion
import litellm
import urllib.request
import json
from packaging import version

load_dotenv()

litellm.suppress_debug_info = True

IS_WINDOWS = sys.platform == 'win32'

__version__ = "1.0.0"
GITHUB_REPO = "rohanashik/ai-commander"

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
                YELLOW = '\033[1;33m'
                GREEN = '\033[0;32m'
                NC = '\033[0m'
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
        # Silently fail if update check fails (offline, timeout, etc.)
        if not silent:
            print("⚠ Could not check for updates. Please check your internet connection.\n")
    return False

def show_loader(stop_event, shell=''):
    """Display an animated spinner while loading"""
    # Skip spinner if stderr is not a terminal (spinner writes to stderr)
    if not sys.stderr.isatty():
        stop_event.wait()
        return
    spinner = ['-', '\\', '|', '/'] if IS_WINDOWS else ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while not stop_event.is_set():
        sys.stderr.write(f'\r{spinner[idx % len(spinner)]} Thinking...')
        sys.stderr.flush()
        idx += 1
        time.sleep(0.1)
    sys.stderr.write('\r' + ' ' * 50 + '\r')
    sys.stderr.flush()

def get_shell():
    """Detect the current shell, cross-platform"""
    if os.name == 'nt':
        # Windows: Detect shell by checking parent process
        try:
            import psutil
            parent = psutil.Process(os.getppid())
            parent_name = parent.name().lower()
            
            if 'powershell' in parent_name or 'pwsh' in parent_name:
                return 'powershell'
            elif 'cmd' in parent_name:
                return 'cmd'
        except (ImportError, Exception):
            # Fallback: check environment variables
            # PSModulePath exists in both, but PowerShell adds specific paths
            psmodpath = os.environ.get('PSModulePath', '')
            if psmodpath and ('WindowsPowerShell' in psmodpath or 'PowerShell' in psmodpath):
                return 'powershell'
        
        # Default to cmd if uncertain
        return 'cmd'
    return os.environ.get('SHELL', 'unknown').split('/')[-1]

def get_context():
    """Gather system context for better command generation"""
    # Get files and folders in current directory
    try:
        items = os.listdir(os.getcwd())
        files = []
        folders = []
        for item in sorted(items):
            item_path = os.path.join(os.getcwd(), item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                folders.append(item)
        # Limit to first 50 of each to avoid token bloat
        files = files[:50]
        folders = folders[:50]
    except Exception:
        files = []
        folders = []

    return {
        'os': sys.platform,  # darwin, linux, win32
        'shell': get_shell(),  # zsh, bash, cmd, powershell
        'cwd': os.getcwd(),  # current directory
        'home': os.path.expanduser('~'),  # home directory
        'files': files,  # files in current directory
        'folders': folders  # folders in current directory
    }

def config_menu():
    """Interactive configuration menu"""
    install_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(install_dir, '.env')

    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    NC = '\033[0m'

    print(f"{BLUE}")
    print("  ▄▖▄▖  ▄▖             ▌    ")
    print("  ▌▌▐   ▌ ▛▌▛▛▌▛▛▌▀▌▛▌▛▌█▌▛▘")
    print("  ▛▌▟▖  ▙▖▙▌▌▌▌▌▌▌█▌▌▌▙▌▙▖▌ ")
    print(f"{NC}")
    print(f"  {BLUE}╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸{NC}")
    print(f"  {GREEN}         ⚙️  CONFIG  ⚙️{NC}")
    print(f"  {BLUE}╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸{NC}")
    print(f"  Version: v{__version__}\n")

    print(f"  {BLUE}1.{NC} Update API Key")
    print(f"  {BLUE}2.{NC} Check for Updates")
    print(f"  {BLUE}3.{NC} Uninstall")
    print(f"  {BLUE}0.{NC} Cancel\n")

    try:
        choice = input(f"{BLUE}Choose an option:{NC} ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(0)

    if choice == '1':
        # Show current key status
        current_key = os.environ.get("GEMINI_API_KEY", "")
        if current_key:
            masked = current_key[:4] + '...' + current_key[-4:]
            print(f"\n  Current key: {masked}")
        else:
            print(f"\n  {RED}No API key configured.{NC}")

        try:
            new_key = input(f"\n  Enter new Gemini API key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)

        if not new_key:
            print(f"\n  {RED}No key entered. Cancelled.{NC}")
            sys.exit(1)

        with open(env_path, 'w') as f:
            f.write(f"GEMINI_API_KEY={new_key}\n")

        print(f"\n  {GREEN}✓ API key updated successfully.{NC}\n")

    elif choice == '2':
        print()
        check_for_updates(silent=False)

    elif choice == '3':
        try:
            confirm = input(f"\n  {RED}Are you sure you want to uninstall AI Commander? (y/N):{NC} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)

        if confirm == 'y':
            import subprocess
            print()
            if os.name == 'nt':
                # Windows: perform cleanup then spawn a detached process to
                # delete the install directory after Python exits (the venv's
                # .pyd files and python.exe are locked while this process runs).
                install_dir = os.path.join(os.environ.get('APPDATA', ''), 'ai-commander')

                print(f"{RED}  AI Commander - UNINSTALLER{NC}")
                print(f"{BLUE}  ================================={NC}")
                print()

                # Remove CMD AutoRun registry entry
                print("Removing shell integration...")
                try:
                    import winreg
                    key_path = r"Software\Microsoft\Command Processor"
                    try:
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                        try:
                            val, _ = winreg.QueryValueEx(key, "AutoRun")
                            if val and "ai-commander" in val.lower():
                                winreg.DeleteValue(key, "AutoRun")
                                print(f"{GREEN}Removed cmd AutoRun registry entry{NC}")
                        except FileNotFoundError:
                            pass
                        winreg.CloseKey(key)
                    except FileNotFoundError:
                        pass
                except Exception:
                    pass

                # Spawn a detached cmd that waits for this Python process to
                # exit, then removes the install directory.
                pid = os.getpid()
                cleanup_cmd = (
                    f'cmd /c "title AI Commander Cleanup'
                    f' & echo Waiting for process to exit...'
                    f' & :wait'
                    f' & tasklist /fi "PID eq {pid}" 2>nul | find "{pid}" >nul'
                    f' && (timeout /t 1 /nobreak >nul & goto wait)'
                    f' & rmdir /s /q "{install_dir}"'
                    f' & echo.'
                    f' & echo AI Commander has been uninstalled.'
                    f' & echo Open a new terminal for changes to take effect.'
                    f' & timeout /t 5"'
                )
                subprocess.Popen(
                    cleanup_cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS,
                )

                print(f"\n{GREEN}AI Commander has been uninstalled.{NC}")
                print("A cleanup window will remove remaining files after this process exits.")
                print("Open a new terminal for changes to take effect.")
            else:
                subprocess.run(['bash', '-c', 'curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.sh | bash'])
        else:
            print(f"\n  Uninstall cancelled.")

    else:
        print("Cancelled.")

    sys.exit(0)

def execute_with_confirm(command):
    """Print command and ask for confirmation before executing"""
    import subprocess as sp

    if IS_WINDOWS:
        print(f"\n> {command}\n")
        try:
            choice = input("Run this command? (Y/n): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)
    else:
        BLUE = '\033[0;34m'
        GREEN = '\033[0;32m'
        RED = '\033[0;31m'
        NC = '\033[0m'
        print(f"\n{BLUE}>{NC} {command}\n")
        try:
            choice = input(f"Run this command? ({GREEN}Y{NC}/{RED}n{NC}): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)

    if choice.lower() in ('', 'y', 'yes'):
        sp.run(command, shell=True)
    else:
        print("Cancelled.")

def main():
    # Handle --config flag
    if '--config' in sys.argv:
        config_menu()

    # Handle --execute flag (Windows cmd mode: confirm then run)
    execute_mode = False
    args = sys.argv[1:]
    if '--execute' in args:
        execute_mode = True
        args = [a for a in args if a != '--execute']

    # Check for Gemini API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("echo 'Error: GEMINI_API_KEY environment variable not set'", file=sys.stderr)
        sys.exit(1)

    # Check for updates silently (non-blocking)
    check_for_updates(silent=True)

    # Get everything after '??'
    user_input = ' '.join(args)
    
    # Get system context
    ctx = get_context()
    
    # Start loader animation in separate thread
    stop_loader = threading.Event()
    loader_thread = threading.Thread(target=show_loader, args=(stop_loader, ctx['shell']))
    loader_thread.start()

    # Build shell-specific examples
    if ctx['shell'] == 'cmd':
        examples = """Examples for Windows CMD:
    Input: list all files
    Output: dir /a

    Input: show current directory
    Output: cd

    Input: delete a file
    Output: del filename.txt"""
    elif ctx['shell'] == 'powershell':
        examples = """Examples for PowerShell:
    Input: list all files
    Output: Get-ChildItem -Force

    Input: show current directory
    Output: Get-Location

    Input: delete a file
    Output: Remove-Item filename.txt"""
    else:
        # Unix-like shells (bash, zsh, sh, etc.)
        examples = """Examples for Unix/Linux:
    Input: list all files
    Output: ls -la

    Input: show disk usage
    Output: df -h

    Input: find files
    Output: find . -name "*.txt" """

    prompt = f"""Convert this natural language request to a terminal command: {user_input}

    CONTEXT:
    - OS: {ctx['os']}
    - Shell: {ctx['shell']}
    - Current Directory: {ctx['cwd']}
    - Home Directory: {ctx['home']}
    - Files in Directory: {', '.join(ctx['files']) if ctx['files'] else 'none'}
    - Folders in Directory: {', '.join(ctx['folders']) if ctx['folders'] else 'none'}

    CRITICAL RULES:
    - YOU MUST generate a command that works ONLY in {ctx['shell'].upper()}
    - DO NOT mix syntax from different shells (e.g., NO PowerShell cmdlets in cmd, NO Unix commands in Windows)
    - If shell is 'cmd': use Windows CMD syntax ONLY (dir, copy, del, cd, etc.)
    - If shell is 'powershell': use PowerShell cmdlets ONLY (Get-ChildItem, Copy-Item, Remove-Item, etc.)
    - If shell is bash/zsh/sh: use Unix/Linux commands ONLY (ls, cp, rm, find, grep, etc.)
    - Output ONLY the raw command, nothing else
    - NO backticks, NO code blocks, NO markdown formatting
    - NO explanations, NO comments, NO extra text
    - NO quotes around the command
    - NO shell prompts like $ or # or >
    - The output must be directly executable in {ctx['shell']}

    {examples}"""

    # print(f"# Prompt sent to LLM:\n{prompt}\n", file=sys.stderr)
    
    try:
        # Call LLM via LiteLLM
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=900
        )

        # Extract command — take only the first line to avoid explanations
        command = response.choices[0].message.content.strip().split('\n')[0].strip()
        # Strip markdown artifacts if model wraps in backticks
        if command.startswith('`') and command.endswith('`'):
            command = command[1:-1]
        # Stop loader
        stop_loader.set()
        loader_thread.join()

        # Output the command
        if execute_mode:
            execute_with_confirm(command)
        else:
            print(command)
    except litellm.RateLimitError:
        stop_loader.set()
        loader_thread.join()
        print("Error: Rate limit reached. Please wait a moment and try again.", file=sys.stderr)
        sys.exit(1)
    except litellm.AuthenticationError:
        stop_loader.set()
        loader_thread.join()
        print("Error: Invalid API key. Check your GEMINI_API_KEY.", file=sys.stderr)
        sys.exit(1)
    except litellm.Timeout:
        stop_loader.set()
        loader_thread.join()
        print("Error: Request timed out. Please try again.", file=sys.stderr)
        sys.exit(1)
    except litellm.APIConnectionError:
        stop_loader.set()
        loader_thread.join()
        print("Error: Could not connect to the API. Check your internet connection.", file=sys.stderr)
        sys.exit(1)
    except litellm.BadRequestError as e:
        stop_loader.set()
        loader_thread.join()
        print(f"Error: Bad request — {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        stop_loader.set()
        loader_thread.join()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()