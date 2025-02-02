from setuptools import setup, find_packages

setup(
    name="prompt to command",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "shell-command-generator=shell_command_generator.main:main",
        ],
    },
    author="si aziz bahloul",
    author_email="azizbahloul3@gmail.com",
    description="Enhanced Shell Command Generator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AzizBahloul/PromptToCommand",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)