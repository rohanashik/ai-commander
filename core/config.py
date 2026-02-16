import sys
import os

from .constants import __version__, BLUE, GREEN, RED, NC
from .updater import check_for_updates


def config_menu():
    """Interactive configuration menu"""
    install_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(install_dir, '.env')

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
                install_dir = os.path.join(os.environ.get('APPDATA', ''), 'ai-commander')

                print(f"{RED}  AI Commander - UNINSTALLER{NC}")
                print(f"{BLUE}  ================================={NC}")
                print()

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
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
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
