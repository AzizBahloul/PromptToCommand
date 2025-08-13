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
- **⚡ Performance Optimized**: Smart model selection based on system resources

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
bourguibagpt/
├── src/
│   └── bourguibagpt/
│       ├── main.py              # Application entry point
│       ├── config.py            # Configuration management
│       ├── validators.py        # Command validation logic
│       ├── windows.py           # Windows-specific functions
│       ├── models/              # AI model configurations
│       ├── utils/               # Utility functions
│       └── tests/               # Test suite
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pyproject.toml              # Modern Python packaging
└── README.md                   # This file
```

### File Descriptions

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | Application core | Banner display, command generation, Ollama management |
| `config.py` | Settings management | Model configuration, user preferences, OS detection |
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
git clone https://github.com/yourusername/bourguibagpt.git
cd bourguibagpt

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
git clone https://github.com/yourusername/bourguibagpt.git
cd bourguibagpt
pip install -e .
```

### Automatic Ollama Setup

BourguibaGPT automatically detects and installs Ollama if not present:

- **Windows**: Uses winget or direct installer download
- **macOS**: Uses Homebrew or direct download
- **Linux**: Uses curl installation script

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
| `history` | Display command history | `history` |
| `execute <cmd>` | Execute specific command | `execute ls -la` |
| `model` | Change AI model | `model` |
| `sibourguiba` | Model selection alias | `sibourguiba` |
| `config` | Show configuration | `config` |
| `stats` | Usage statistics | `stats` |
| `export` | Export command history | `export history.json` |
| `clear` | Clear screen | `clear` |
| `exit/quit` | Exit application | `exit` |

### Advanced Features

#### Model Selection
```bash
> model
Available models:
1. llama3.2:1b (Fast, 1GB RAM)
2. llama3.1:8b (Balanced, 8GB RAM)
3. codellama:13b (Code-focused, 16GB RAM)
Choose model [1-3]: 2
```

#### Command History Management
```bash
> history --filter "git"
> history --export json
> history --clear
```

#### Safety Configuration
```bash
> config safety --level strict
> config whitelist --add "custom-command"
> config validation --enable-deep-scan
```

## 🔧 Configuration

### Configuration File Location
- **Linux/macOS**: `~/.config/bourguibagpt/settings.json`
- **Windows**: `%APPDATA%\bourguibagpt\settings.json`

### Sample Configuration
```json
{
  "model": {
    "preferred": "llama3.1:8b",
    "fallback": "llama3.2:1b",
    "auto_select": true
  },
  "safety": {
    "validation_level": "strict",
    "allow_sudo": false,
    "enable_whitelist": true,
    "log_commands": true
  },
  "ui": {
    "show_banner": true,
    "color_scheme": "tunisia",
    "animation_speed": "normal"
  },
  "ollama": {
    "host": "localhost",
    "port": 11434,
    "timeout": 30
  }
}
```

### Environment Variables

```bash
export BOURGUIBA_MODEL="llama3.1:8b"
export BOURGUIBA_SAFETY_LEVEL="strict"
export OLLAMA_HOST="localhost:11434"
export BOURGUIBA_LOG_LEVEL="INFO"
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
- **RAM**: 8GB+ (for larger models)
- **Storage**: 10GB+ (for model storage)
- **CPU**: Quad-core processor
- **GPU**: NVIDIA GPU (optional, for faster inference)

### Model Performance Comparison

| Model | Size | RAM Usage | Speed | Accuracy |
|-------|------|-----------|-------|----------|
| llama3.2:1b | 1GB | 2GB | ⚡⚡⚡ | ⭐⭐⭐ |
| llama3.1:8b | 8GB | 10GB | ⚡⚡ | ⭐⭐⭐⭐ |
| codellama:13b | 13GB | 16GB | ⚡ | ⭐⭐⭐⭐⭐ |

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

# Pull missing model
ollama pull llama3.1:8b

# Check system resources
bourguibagpt --check-system
```

#### Permission Errors
```bash
# Linux/macOS
chmod +x $(which ollama)
sudo chown $USER ~/.ollama

# Windows (run as administrator)
icacls "%USERPROFILE%\.ollama" /grant %USERNAME%:F
```

### Debug Mode
```bash
python -m src.bourguibagpt.main --debug --log-level DEBUG
```

### Log Locations
- **Linux/macOS**: `~/.config/bourguibagpt/logs/`
- **Windows**: `%APPDATA%\bourguibagpt\logs\`

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
git clone https://github.com/yourusername/bourguibagpt.git
cd bourguibagpt

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
