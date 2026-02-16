import os
import sys


def get_shell():
    """Detect the current shell, cross-platform"""
    if os.name == 'nt':
        try:
            import psutil
            parent = psutil.Process(os.getppid())
            parent_name = parent.name().lower()

            if 'powershell' in parent_name or 'pwsh' in parent_name:
                return 'powershell'
            elif 'cmd' in parent_name:
                return 'cmd'
        except (ImportError, Exception):
            psmodpath = os.environ.get('PSModulePath', '')
            if psmodpath and ('WindowsPowerShell' in psmodpath or 'PowerShell' in psmodpath):
                return 'powershell'

        return 'cmd'
    return os.environ.get('SHELL', 'unknown').split('/')[-1]


def get_context():
    """Gather system context for better command generation"""
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
        files = files[:50]
        folders = folders[:50]
    except Exception:
        files = []
        folders = []

    return {
        'os': sys.platform,
        'shell': get_shell(),
        'cwd': os.getcwd(),
        'home': os.path.expanduser('~'),
        'files': files,
        'folders': folders,
    }
