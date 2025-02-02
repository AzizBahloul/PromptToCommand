
```markdown
# BourguibaGPT 🇹🇳

**Your AI-Powered Tunisian Shell Command Assistant**

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/bourguibagpt)](https://pypi.org/project/bourguibagpt/)

BourguibaGPT is an intelligent CLI tool that transforms natural language requests into safe shell commands using advanced AI models. Designed with a focus on safety and usability, it's your perfect companion for terminal productivity.

![CLI Demo](https://via.placeholder.com/800x400.png?text=BourguibaGPT+Interactive+CLI+Demo)

## Features ✨

- **Natural Language Understanding** 🇹🇳  
  Describe tasks in plain English/French/Arabic (Tunisian dialect friendly!)
- **AI-Powered Command Generation** 🤖  
  Leverages local LLMs via Ollama (default: deepseek-r1:1.5b)
- **Safety First** 🔒  
  Multi-layer validation against dangerous commands
- **Interactive CLI** 💻  
  Rich terminal interface with syntax highlighting and progress indicators
- **Command History** 📚  
  Automatic tracking of generated commands with execution status
- **Cross-Platform** 🌍  
  Supports Linux, macOS, and Windows Subsystem for Linux
- **Smart Execution** ⚡  
  Optional auto-execution with confirmation prompts

## Installation 📦

1. **Install Ollama** (required):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull deepseek-r1:1.5b
   ```

2. Install BourguibaGPT:
   ```bash
   pip install bourguibagpt
   ```

## Quick Start 🚀

```bash
$ bourguibagpt

╔══════════════════════════════════════════════════════════════╗
║              Your Tunisian Shell Command Assistant           ║
╚══════════════════════════════════════════════════════════════╝

🇹🇳 BourguibaGPT → list all json files modified last week
Generated command: find . -name "*.json" -mtime -7

Execute? [yes/no]: yes
✅ Command executed successfully
```

## Advanced Usage 🛠️

### Command Line Options
```bash
bourguibagpt [OPTIONS]
  --model MODEL_NAME        # Specify Ollama model (default: deepseek-r1:1.5b)
  --temperature FLOAT       # Control creativity (0.1-1.0, default: 0.7)
  --auto-execute            # Auto-execute validated commands
  --history-file PATH       # Custom command history location
```

### Manage History
```bash
# Show last 10 commands
bourguibagpt --history

# Execute from history
bourguibagpt execute "find . -name *.json -mtime -7"
```

## Safety Measures ⚠️

BourguibaGPT includes multiple protection layers:
- Pattern matching against dangerous commands (e.g., `rm -rf /`)
- Command structure validation
- Execution confirmation prompts
- Restricted special characters handling
- Model prompt engineering for safety

## Roadmap 🗺️

- [ ] Browser-based GUI
- [ ] Command explanation mode
- [ ] Plugin system for custom validations
- [ ] Shared team history sync
- [ ] Alternative AI backend support

## Contributing 🤝

We welcome contributions! Please see our [Contribution Guidelines](CONTRIBUTING.md) for details.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ in Tunisia by Aziz Bahloul  
[GitHub Repository](https://github.com/AzizBahloul/PromptToCommand) | [Report Issue](https://github.com/AzizBahloul/PromptToCommand/issues)
```
