import sys
import os
import litellm

from .constants import IS_WINDOWS, LLM_ERROR_MESSAGES
from .config import config_menu
from .context import get_context
from .llm import build_prompt, get_command
from .ui import loader, execute_with_confirm
from .updater import check_for_updates


def main():
    if '--config' in sys.argv:
        config_menu()

    execute_mode = False
    args = sys.argv[1:]
    if '--execute' in args:
        execute_mode = True
        args = [a for a in args if a != '--execute']

    if not os.environ.get("GEMINI_API_KEY"):
        print("echo 'Error: GEMINI_API_KEY environment variable not set'", file=sys.stderr)
        sys.exit(1)

    check_for_updates(silent=True)

    user_input = ' '.join(args)
    ctx = get_context()
    prompt = build_prompt(user_input, ctx)

    try:
        with loader(ctx['shell']):
            command = get_command(prompt)

        if execute_mode:
            execute_with_confirm(command)
        elif IS_WINDOWS:
            sys.stderr.write(command + '\n')
            sys.stderr.flush()
        else:
            print(command)

    except litellm.BadRequestError as e:
        print(f"Error: Bad request — {e.message}", file=sys.stderr)
        sys.exit(1)
    except (litellm.RateLimitError, litellm.AuthenticationError,
            litellm.Timeout, litellm.APIConnectionError) as e:
        print(LLM_ERROR_MESSAGES[type(e)], file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
