#!/usr/bin/env python3
import sys
import os
import threading
import time
from dotenv import load_dotenv
from litellm import completion
import litellm

load_dotenv()

litellm.suppress_debug_info = True

def show_loader(stop_event):
    """Display an animated spinner while loading"""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while not stop_event.is_set():
        sys.stderr.write(f'\r{spinner[idx % len(spinner)]} Thinking...')
        sys.stderr.flush()
        idx += 1
        time.sleep(0.1)
    sys.stderr.write('\r' + ' ' * 50 + '\r')  # Clear the line
    sys.stderr.flush()

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
        'os': sys.platform,  # Darwin, Linux, Windows
        'shell': os.environ.get('SHELL', 'unknown').split('/')[-1],  # zsh, bash, etc
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

    print(f"\n{BLUE}┌────────────────────────────────────┐{NC}")
    print(f"{BLUE}│   🤖 AI Commander Settings        │{NC}")
    print(f"{BLUE}└────────────────────────────────────┘{NC}\n")

    print(f"  {BLUE}1.{NC} Update API Key")
    print(f"  {BLUE}2.{NC} Uninstall")
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
        try:
            confirm = input(f"\n  {RED}Are you sure you want to uninstall AI Commander? (y/N):{NC} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)

        if confirm == 'y':
            import subprocess
            print()
            subprocess.run(['bash', '-c', 'curl -fsSL https://raw.githubusercontent.com/rohanashik/ai-commander/main/uninstall.sh | bash'])
        else:
            print(f"\n  Uninstall cancelled.")

    else:
        print("Cancelled.")

    sys.exit(0)

def main():
    # Handle --config flag
    if len(sys.argv) >= 2 and sys.argv[1] == '--config':
        config_menu()

    # Check for Gemini API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("echo 'Error: GEMINI_API_KEY environment variable not set'", file=sys.stderr)
        sys.exit(1)

    # Get everything after '??'
    user_input = ' '.join(sys.argv[1:])
    
    # Get system context
    ctx = get_context()
    
    # Start loader animation in separate thread
    stop_loader = threading.Event()
    loader_thread = threading.Thread(target=show_loader, args=(stop_loader,))
    loader_thread.start()

    prompt = f"""Convert this natural language request to a terminal command: {user_input}

    CONTEXT:
    - OS: {ctx['os']}
    - Shell: {ctx['shell']}
    - Current Directory: {ctx['cwd']}
    - Home Directory: {ctx['home']}
    - Files in Directory: {', '.join(ctx['files']) if ctx['files'] else 'none'}
    - Folders in Directory: {', '.join(ctx['folders']) if ctx['folders'] else 'none'}

    CRITICAL RULES:
    - Output ONLY the raw command, nothing else
    - Use correct syntax for {ctx['os']} and {ctx['shell']}
    - NO backticks, NO code blocks, NO markdown formatting
    - NO explanations, NO comments, NO extra text
    - NO quotes around the command
    - NO shell prompts like $ or #
    - The output must be directly executable

    Examples:
    Input: list all files
    Output: ls -la

    Input: show disk usage
    Output: df -h"""

    # print(f"# Prompt sent to LLM:\n{prompt}\n", file=sys.stderr)
    
    try:
        # Call LLM via LiteLLM
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=300
        )

        # Extract command — take only the first line to avoid explanations
        command = response.choices[0].message.content.strip().split('\n')[0].strip()
        # Strip markdown artifacts if model wraps in backticks
        if command.startswith('`') and command.endswith('`'):
            command = command[1:-1]
        # Stop loader
        stop_loader.set()
        loader_thread.join()

        # Print the command
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