# BourguibaGPT - Tunisian Shell Command Assistant

<div align="center">

![BourguibaGPT Logo](https://via.placeholder.com/200x100/2E86AB/FFFFFF?text=BourguibaGPT)

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-green.svg)](#)
[![GitHub Stars](https://img.shields.io/github/stars/username/bourguibagpt?style=social)](#)
[![Donations](https://img.shields.io/badge/Donate-PayPal-blue.svg)](#donation)

*Empowering Tunisian developers with AI-powered shell command assistance*

[Installation](#installation) • [Usage](#usage) • [Features](#features) • [Documentation](#documentation) • [Contributing](#contributing) • [Support](#donation)

</div>

## 🌟 Overview

BourguibaGPT is an innovative, AI-powered shell command assistant specifically designed for Tunisian developers and system administrators. Named after Tunisia's founding father, this tool bridges the gap between natural language and shell commands, making terminal operations more accessible and safer for users of all skill levels.

### Why BourguibaGPT?

- **🇹🇳 Tunisian Heritage**: Built with pride for the Tunisian tech community
- **🤖 AI-Powered**: Leverages Ollama's powerful language models
- **🛡️ Safety First**: Advanced command validation prevents dangerous operations
- **🎨 Beautiful Interface**: Animated banners and rich terminal UI
- **📚 Educational**: Learn shell commands through natural language interaction

## ✨ Features

### Core Functionality
- **🧠 Intelligent Command Generation**: Convert natural language to precise shell commands
- **🔒 Advanced Safety Validation**: Multi-layer command validation system
- **📖 Command History & Feedback**: Track usage patterns and improve recommendations
- **🌐 Cross-Platform Support**: Works seamlessly on Linux, macOS, and Windows
- **⚡ Fast Local Decisions**: Uses one small, deterministic local model with structured output

### Enhanced User Experience
- **🎬 Animated Welcome Banner**: Dynamic startup experience
- **🎨 Rich Terminal UI**: Beautiful, colorful output using Rich library
- **💬 Interactive Prompts**: Intuitive conversation-style interface
- **🔄 Real-time Feedback**: Immediate command validation and suggestions
- **📊 Usage Analytics**: Track your command generation patterns

### Safety & Security
- **✅ Command Whitelist**: Only safe, pre-approved commands are executed
- **🔍 Argument Validation**: Deep inspection of command parameters
- **🚫 Dangerous Command Blocking**: Prevents destructive operations
- **📝 Execution Logging**: Complete audit trail of all operations
- **🛡️ Sandboxed Execution**: Isolated command execution environment

## 📁 Project Structure

```
PromptToCommand/
├── src/
│   └── bourguibagpt/
│       ├── main.py                  # Application entry point, Ollama management, execution loop
│       ├── config.py                # Model name and version (single source of truth)
│       ├── prompt_engineering.py    # Shell-aware system prompt + response parsing
│       ├── validators.py            # Command whitelist and argument safety checks
│       └── windows.py               # Windows-specific Ollama install/service functions
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup (also installs Ollama + pulls the model)
├── setup.cfg                        # Package metadata and version
├── pyproject.toml                   # Build backend configuration
└── README.md                        # This file
```

### File Descriptions

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | Application core | Banner display, command generation, Ollama management |
| `config.py` | Settings management | Fixed model name and app version |
| `prompt_engineering.py` | Prompt design | Builds the per-shell system prompt, parses/cleans the model's response |
| `validators.py` | Security layer | Command whitelist, argument validation, safety checks |
| `windows.py` | Windows support | Ollama installation, service management, Windows-specific features |

## 🚀 Installation

### Prerequisites
- **Python 3.7+** (Python 3.9+ recommended)
- **4GB RAM minimum** (8GB+ recommended for larger models)
- **Internet connection** (for initial Ollama setup)

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/AzizBahloul/PromptToCommand.git
cd PromptToCommand

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.bourguibagpt.main
```

### Advanced Installation Options

#### Using pip (recommended)
```bash
pip install bourguibagpt
bourguibagpt
```

#### Using conda
```bash
conda create -n bourguibagpt python=3.9
conda activate bourguibagpt
pip install bourguibagpt
```

#### Development Installation
```bash
git clone https://github.com/AzizBahloul/PromptToCommand.git
cd PromptToCommand
pip install -e .
```

### Automatic Ollama Setup

BourguibaGPT automatically installs Ollama during direct package installation and also checks for it at startup:

- **Windows**: Uses winget
- **macOS**: Uses Homebrew
- **Linux**: Uses the official Ollama installation script

The application uses the single fixed model `qwen2.5-coder:1.5b` (about 1 GB). It is a local open-source alternative for this shell-command task, not the proprietary Jev model. Jev returns typed decisions and does not generate shell commands; this application uses Ollama JSON schema output, confidence, deterministic inference, and no-thinking mode to provide a similar bounded-output workflow. (An earlier build used `qwen3.5:0.8b`; it was replaced after testing showed a code-tuned model gives more accurate commands at the same download size.)

## 📖 Usage

### Basic Usage

```bash
# Start BourguibaGPT
python -m src.bourguibagpt.main

# Example interactions
> "list all files in the current directory"
Generated: ls -la
Execute this command? (y/n): y

> "find all Python files modified in the last 7 days"
Generated: find . -name "*.py" -mtime -7
Execute this command? (y/n): y
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show help information | `help` |
| `history` | Display the last 10 generated commands | `history` |
| `execute <cmd>` | Run a specific command directly, still safety-validated | `execute ls -la` |
| `model` / `sibourguiba` | Show the fixed local model | `model` |
| `exit` / `quit` | Exit application | `exit` |

Anything else you type is treated as a natural-language request and sent to the model.

## 🔧 Configuration

### Environment Variables

```bash
export OLLAMA_HOST="localhost:11434"  # point at a remote or non-default Ollama instance
```

## 🛡️ Security & Safety

### Command Validation Layers

1. **Whitelist Checking**: Commands must be in approved list
2. **Argument Validation**: Parameters are sanitized and validated
3. **Destructive Operation Detection**: Dangerous commands are blocked
4. **User Confirmation**: Interactive approval for all executions
5. **Execution Logging**: Complete audit trail

### Blocked Operations
- File deletion commands (`rm -rf`, `del`)
- System modification commands (`format`, `fdisk`)
- Network-based attacks (`curl` to suspicious URLs)
- Privilege escalation without confirmation
- Recursive operations without limits

### Safe Command Categories
- File operations (list, copy, move)
- Text processing (grep, sed, awk)
- System information (ps, top, df)
- Development tools (git, docker, npm)
- Archive operations (tar, zip)

## 📊 Performance & System Requirements

### Minimum Requirements
- **RAM**: 4GB
- **Storage**: 2GB free space
- **CPU**: Dual-core processor
- **Network**: Stable internet for initial setup

### Recommended Configuration
- **RAM**: 8GB+ (comfortable headroom; the model itself only needs about 2GB)
- **Storage**: 2GB+ free (the fixed model is about 1GB)
- **CPU**: Quad-core processor
- **GPU**: NVIDIA GPU (optional; the model runs fine on CPU, just slower)

The app always uses the single fixed model described above (`qwen2.5-coder:1.5b`, ~1GB) — there is no larger/smaller model to opt into from the UI.

## 🔧 Troubleshooting

### Common Issues

#### Ollama Not Starting
```bash
# Check Ollama status
ollama list

# Manually start Ollama
ollama serve

# Restart BourguibaGPT
python -m src.bourguibagpt.main
```

#### Model Loading Issues
```bash
# Verify model availability
ollama list

# Pull the model BourguibaGPT expects
ollama pull qwen2.5-coder:1.5b
```

#### Permission Errors
```bash
# Linux/macOS
chmod +x $(which ollama)
sudo chown $USER ~/.ollama

# Windows (run as administrator)
icacls "%USERPROFILE%\.ollama" /grant %USERNAME%:F
```

### Logs

BourguibaGPT logs to the console it's running in (no separate log file). Command history is saved to `~/.shell_command_history.json` by default, or the path passed via `--history-file`.

## 🤝 Contributing

We welcome contributions from the Tunisian developer community and beyond!

### Ways to Contribute
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🧪 Write tests
- 🌍 Add internationalization
- 🎨 Enhance UI/UX

### Development Setup
```bash
# Fork the repository
git clone https://github.com/AzizBahloul/PromptToCommand.git
cd PromptToCommand

# Create development environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Install pre-commit hooks
pre-commit install
```

### Coding Standards
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Add type hints where appropriate
- Include unit tests for new features
- Update documentation

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 BourguibaGPT Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```
## 💝 Support & Donations

If CrashSense has helped streamline your debugging workflow, consider supporting continued development:

<div align="center">

| Platform | ID |
|----------|-----|
| 💳 **RedotPay** | `1951109247` |
| 🟡 **Binance** | `1104913076` |

*Your support helps keep CrashSense free and continuously improving!*

</div>





 
### How Donations Help

Your contributions directly support:
- 🔧 **Development Time**: New features and bug fixes
- 💻 **Infrastructure**: Server costs and CI/CD
- 📚 **Documentation**: Better guides and tutorials
- 🧪 **Testing**: Comprehensive test coverage
- 🌍 **Community**: Events and workshops in Tunisia
- 🎓 **Education**: Free coding workshops for students

## 🌟 Acknowledgments

### Special Thanks
- **Habib Bourguiba** - Inspiration for the project name
- **Ollama Team** - Amazing local AI inference
- **Rich Library** - Beautiful terminal interfaces
- **Tunisian Developer Community** - Continuous support and feedback

### Built With Love In Tunisia 🇹🇳

This project was created with pride in Tunisia, inspired by our rich history of innovation and technological advancement. We dedicate this work to all Tunisian developers pushing the boundaries of technology.

## 📞 Support & Contact
- 📧 **Email**: azizbahloul3@gmail.com

---

<div align="center">


*"The best way to predict the future is to create it"* - Habib Bourguiba

[⬆ Back to Top](#bourguibagpt---tunisian-shell-command-assistant)

</div>
