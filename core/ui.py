import sys
import time
import threading
from contextlib import contextmanager

from .constants import IS_WINDOWS, BLUE, GREEN, NC


def show_loader(stop_event, shell=''):
    """Display an animated spinner while loading"""
    if not sys.stderr.isatty():
        stop_event.wait()
        return
    if IS_WINDOWS:
        sys.stderr.write('Thinking...\n')
        sys.stderr.flush()
        stop_event.wait()
        return
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while not stop_event.is_set():
        sys.stderr.write(f'\r{spinner[idx % len(spinner)]} Thinking...')
        sys.stderr.flush()
        idx += 1
        time.sleep(0.1)
    sys.stderr.write('\r' + ' ' * 50 + '\r')
    sys.stderr.flush()


@contextmanager
def loader(shell=''):
    """Context manager that runs the spinner in a background thread and ensures cleanup."""
    stop_event = threading.Event()
    thread = threading.Thread(target=show_loader, args=(stop_event, shell))
    thread.start()
    try:
        yield
    finally:
        stop_event.set()
        thread.join()


def prefill_input(prompt, text):
    """Display an input prompt pre-filled with editable text using readline."""
    import readline

    def hook():
        readline.insert_text(text)
        readline.redisplay()

    readline.set_pre_input_hook(hook)
    try:
        return input(prompt)
    finally:
        readline.set_pre_input_hook()


def execute_with_confirm(command):
    """Print command and ask for confirmation before executing"""
    import subprocess as sp

    if IS_WINDOWS:
        sys.stderr.write(f"\n> {command}\n\n")
        sys.stderr.flush()
        try:
            sys.stderr.write("Run this command? (Y/n) ")
            sys.stderr.flush()
            choice = sys.stdin.readline().strip().lower()
        except (KeyboardInterrupt, EOFError):
            sys.stderr.write("\nCancelled.\n")
            sys.exit(0)
        if choice in ('', 'y', 'yes'):
            sp.run(command, shell=True)
        else:
            sys.stderr.write("Cancelled.\n")
    else:
        try:
            print(f"{GREEN}Edit command or press Enter to run (Ctrl+C to cancel):{NC}")
            edited_command = prefill_input(f"{BLUE}>{NC} ", command).strip()
            if not edited_command:
                edited_command = command
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)
        except ImportError:
            print(f"> {command}\n")
            print("Edit command or press Enter to run (Ctrl+C to cancel):")
            try:
                edited_command = input("> ").strip()
                if not edited_command:
                    edited_command = command
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled.")
                sys.exit(0)

        sp.run(edited_command, shell=True)
