"""Main module for the assistant bot."""

from handlers import commands, parse_input
from address_book import AddressBook


def main():
    """Main function to run the assistant bot."""
    book = AddressBook()

    print("Welcome to the assistant bot!")
    while True:
        try:
            user_input = input("\nEnter a command: ")
        except (KeyboardInterrupt, EOFError):
            print("\n- Goodbye!")
            break

        command, args = parse_input(user_input)

        if command is None:
            print("- No command entered.")
            continue

        func = commands.get(command)
        if func is None:
            print("- Invalid command.")
            continue

        print('-', func(book, *args))


if __name__ == "__main__":
    main()
