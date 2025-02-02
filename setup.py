from setuptools import setup, find_packages

setup(
    name='bourguibaGPT',
    version='0.1.0',
    author='Siaziz',
    author_email='azizbahloul3@gmail.com',
    description='A prompt to command program that generates terminal commands based on user input.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AzizBahloul/PromptToCommand.git',
    packages=find_packages(),
    install_requires=[
        'transformers',
        'torch',
        'textblob',
        'pyspellchecker',
        'numpy<2.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)