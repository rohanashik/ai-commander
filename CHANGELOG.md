# Changelog

All notable changes to AI Commander will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-16

### Added
- Initial release of AI Commander
- Natural language to shell command conversion using Google Gemini Flash
- Support for macOS, Linux, and Windows
- Context-aware command generation (OS, shell, current directory)
- Interactive configuration menu (`--config`)
- Automatic update checking
- Installation scripts for all platforms (install.sh, install.bat, install.ps1)
- Uninstallation scripts for all platforms
- Smart command injection for macOS/Linux (appears in shell buffer)
- Confirmation prompt for Windows users
- `--execute` flag for direct command execution

### Features
- `??` prefix for natural language commands
- Cross-platform support (macOS, Linux, Windows)
- Shell integration (bash, zsh, PowerShell, cmd)
- API key configuration
- Error handling for rate limits, auth failures, and network issues

[0.1.0]: https://github.com/rohanashik/ai-commander/releases/tag/v0.1.0
