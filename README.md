
------------------------------------------------------------
BourguibaGPT - Tunisian Shell Command Assistant
------------------------------------------------------------

OVERVIEW
--------
BourguibaGPT is an interactive shell command generator that helps users generate, validate, and execute safe shell commands using natural language prompts. Powered by Ollama AI, it offers an engaging interface with animated banners and interactive prompts. The tool is designed with safety in mind—it validates commands before execution and keeps a history of generated commands along with user feedback.

FEATURES
--------
• Interactive command generation using AI (Ollama API)
• Animated banner display for a dynamic user experience
• Command validation to ensure only safe commands are executed
• Command history tracking and feedback mechanism
• Cross-platform support (Linux, macOS, and Windows)
• Customizable model selection based on system memory and user preferences
• OS-specific installation and service management routines

FILE STRUCTURE
--------------
Project files are organized under the "src/bourguibagpt" directory as follows:

1. main.py
   - Main application entry point.
   - Displays the animated banner.
   - Manages interactive command generation and execution.
   - Handles installation and verification of the Ollama CLI.

2. config.py
   - Contains default model configurations and OS-specific settings.
   - Manages user preferences for the preferred model.
   - Provides utility functions to load and save configuration settings.

3. validators.py
   - Implements command validation logic to ensure only safe commands are executed.
   - Checks the base command against a predefined whitelist and validates arguments.

4. windows.py
   - Contains Windows-specific functions.
   - Handles installation of Ollama on Windows.
   - Provides functions to verify installation and start the Ollama service.

DEPENDENCIES
------------
• Python 3.7 or later
• Rich (for enhanced terminal UI) - Install with: pip install rich
• Requests (for HTTP API calls) - Install with: pip install requests
• psutil (for system memory detection) - Install with: pip install psutil
• Standard libraries: argparse, json, subprocess, logging, time, os, platform, etc.

INSTALLATION
------------
1. Ensure Python 3.7 or later is installed on your system.
2. Clone the repository to your local machine.
3. Navigate to the repository’s root directory.
4. Install the required Python packages. If a requirements file is available, run:
       pip install -r requirements.txt
   Otherwise, manually install the necessary packages (rich, requests, psutil).
5. The application will check for the Ollama CLI. If not found, it will attempt to install it automatically based on your operating system.
   - On Windows, it will use winget or download the installer directly.
   - On Linux and macOS, it will attempt installation via curl or brew, respectively.
6. Ensure you have the necessary permissions on your system to install and run external software.

USAGE
-----
To launch the application, run the following command from the project root:

    python -m src.bourguibagpt.main

Once started, the application will display an animated banner followed by a prompt. You can interact with the tool using the following commands:

• help          - Display help information and available commands.
• history       - Show the history of generated commands.
• execute <cmd> - Execute a specific shell command.
• model         - Change the AI model used for command generation.
• sibourguiba   - Alias for changing the model.
• exit / quit   - Exit the application.

At the prompt, simply type a natural language description of the desired shell command. BourguibaGPT will generate the command, display it, and ask for confirmation before executing it.

CONFIGURATION
-------------
User preferences are saved in a configuration file located at:
    (Your Home Directory)/.config/bourguibagpt/settings.json

This file stores your preferred AI model and the last used timestamp. The application automatically updates this file when you change the model preference.

TROUBLESHOOTING
---------------
• If the Ollama service is not running, the tool will attempt to start it automatically. On Linux and macOS, ensure that you have the necessary permissions.
• In case of errors during command generation or execution, refer to the error messages displayed in the terminal.
• Log messages are printed to the console for further troubleshooting. Check these messages if unexpected behavior occurs.
• For command validation failures, ensure that your command requests use allowed commands and safe argument formats.

LICENSE & SUPPORT
-----------------
This project is released under the MIT License. For support, contact the project maintainer or consult the issue tracker provided in the repository.

------------------------------------------------------------
  