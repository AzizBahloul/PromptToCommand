from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='bourguiba',
    version='1.0.0',
    description='A Python library to generate commands based on descriptions using T5-small from Meta AI',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='si mohamed aziz bahloul wo chrikou si mahdi magroun',
    author_email='azizbahloul3@gmail.com',
    url='https://github.com/AzizBahloul/PromptToCommand',  # Replace with your actual GitHub repo URL
    packages=find_packages(),
    install_requires=[
        'torch',
        'transformers',
        'sentencepiece'
    ],
    entry_points={
        'console_scripts': [
            'bourguiba=bourguiba.bourguiba:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)