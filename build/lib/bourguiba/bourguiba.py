from .model_downloader import download_model
from .instruction import CommandGenerator

def main():
    model_dir = download_model()
    generator = CommandGenerator(model_dir)

    while True:
        user_input = input("Enter command description (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        commands = generator.generate_command(user_input)
        print("\nGenerated commands:")
        print(commands)
        print()

if __name__ == "__main__":
    main()