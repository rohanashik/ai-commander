from litellm import completion

from .constants import SHELL_EXAMPLES


def build_prompt(user_input, ctx):
    """Build the LLM prompt from user input and system context."""
    examples = SHELL_EXAMPLES.get(ctx['shell'], SHELL_EXAMPLES['unix'])

    return f"""Convert this natural language request to a terminal command: {user_input}

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


def get_command(prompt):
    """Call the LLM and return the cleaned command string."""
    response = completion(
        model="gemini/gemini-2.5-flash",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=900,
    )

    command = response.choices[0].message.content.strip().split('\n')[0].strip()
    if command.startswith('`') and command.endswith('`'):
        command = command[1:-1]
    return command
