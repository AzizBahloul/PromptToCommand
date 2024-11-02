
**Bourguiba - Command Generation Library**

Bourguiba is a Python library designed to generate shell commands based on natural language input. This tool leverages advanced machine learning models to understand user intent and produce valid shell commands, making it easier for users to interact with the command line.

**Features:**

- Generates common shell commands based on user descriptions.
- Includes a comprehensive list of 150 common commands.
- Utilizes a pretrained GPT-2 model for command generation.
- Supports fuzzy matching to improve command accuracy based on user input.
- Simple command-line interface for easy usage.

**Usage:**

To use bourguiba, simply import the library and create an instance of the CommandGenerator class. You can then call the `generate_command` method with a description of the command you wish to create.

Example:

```python
from bourguiba import CommandGenerator

generator = CommandGenerator()
command = generator.generate_command("I want to create a folder")
print(command)  # Output: mkdir [folder_name]
```


**Contributing:**

Contributions are welcome! If you would like to contribute to bourguiba, please fork the repository and submit a pull request.

**License:**

This project is licensed under the MIT License. See the LICENSE file for details.



Special thanks to the creators of the GPT-2 model and the developers of the transformers library, which make this project possible.

For more information, please visit the GitHub repository.

---

Feel free to modify any sections to better fit your preferences!
