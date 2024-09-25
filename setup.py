from setuptools import setup, find_packages

setup(
    name='Bourguiba',  # Replace with your package name
    version='1.0.9',   # Increment this with each release
    packages=find_packages(),
    install_requires=[
        'torch', 
        'transformers'
    ],
    entry_points={
        'console_scripts': [
            'bourguiba=bourguiba.bourguiba:main',  # Point to your main function
        ],
    },
    author='si mohamed aziz bahloul wo chrikou il mangouli mahdi magroun',  # Replace with your name
    author_email='azizbahloul3@gmail.com',  # Replace with your email
    description='A command line generator based on user input',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AzizBahloul/PromptToCommand',  # Replace with your repo link
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Adjust if necessary
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  
)
