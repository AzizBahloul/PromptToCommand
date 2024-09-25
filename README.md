# Bourguiba

Bourguiba is a Python library that generates commands based on descriptions using the T5-small model from Meta AI.

## Installation

You can install Bourguiba using pip:

```
pip install bourguiba
```

During installation, the T5-small model will be downloaded and stored in your home directory under `.bourguiba_model`.

## Usage

After installation, you can use Bourguiba from the command line:

```
bourguiba "create a Python file"
```

This will generate a command based on the given description.

You can also use Bourguiba in your Python scripts:

```python
from bourguiba import Bourguiba

bourguiba = Bourguiba()
command = bourguiba.generate_command("create a Python file")
print(f"Generated command: {command}")
```

## Requirements

- Python 3.6+
- torch
- transformers
- sentencepiece

## License

This project is licensed under the MIT License.