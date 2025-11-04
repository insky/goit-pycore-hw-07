"""Handlers for user commands."""

import sys
from address_book import AddressBook, Record, ValidationError


def parse_input(user_input: str) -> tuple[str | None, list[str]]:
    """
    Parses user input into command and arguments.

    Args:
        user_input (str): The user input string.

    Returns:
        tuple[str | None, list[str]]: A tuple containing the command and arguments.
    """
    parts = user_input.split()
    if not parts:
        return None, []

    cmd, *args = parts
    return cmd.lower(), args


def input_error(func):
    """
    Decorator for handling input errors.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.

    Raises:
        TypeError: If invalid number of parameters.
        KeyError: If contact not found.
        ValueError: If invalid input.
        ValidationError: If validation fails.
    """
    def wrapper(*args):
        try:
            return func(*args)
        except TypeError:
            return "Invalid number of parameters."
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Invalid input. Please enter the correct data."
        except AttributeError:
            return "Contact not found."
        except ValidationError as ve:
            return str(ve)
    return wrapper


@input_error
def handle_hello(_: AddressBook):
    """
    Greets the user.

    Args:
        _: The address book (unused).

    Returns:
        str: The greeting message.
    """
    return "How can I help you?"


@input_error
def handle_exit(_: AddressBook):
    """
    Exits the program.

    Args:
        _: The address book (unused).
    """
    print("Goodbye!")
    sys.exit(0)


@input_error
def handle_help(_: AddressBook):
    """
    Returns help text with available commands.

    Args:
        _: The address book (unused).

    Returns:
        str: The help text.
    """
    help_text = """Available commands:
    hello - Greet the bot
    help - Show this help message
    exit | close - Exit the bot
    add <name> <phone> - Add a new contact
    change <name> <old_phone> <new_phone> - Change the phone number of a contact
    phone <name> - Get the phone number of a contact
    all - List all contacts
    add-birthday <name> <birthday> - Add a birthday for a contact
    show-birthday <name> - Show the birthday of a contact
    birthdays - Show upcoming birthdays in the next week
    """
    return help_text


@input_error
def handle_add(book: AddressBook, name: str, phone: str):
    """
    Adds a new contact or update existing contact's phone number.

    Args:
        book (AddressBook): The address book.
        name (str): The contact name.
        phone (str): The phone number.

    Returns:
        str: The result message.
    """
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def handle_change(book: AddressBook, name: str, old_phone: str, new_phone: str):
    """
    Changes an existing contact's phone number.

    Args:
        book (AddressBook): The address book.
        name (str): The contact name.
        old_phone (str): The old phone number.
        new_phone (str): The new phone number.

    Returns:
        str: The result message.
    """
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)  # type: ignore
    return "Contact updated."


@input_error
def handle_phone(book: AddressBook, name: str):
    """
    Gets the phone number of a contact.

    Args:
        book (AddressBook): The address book.
        name (str): The contact name.

    Returns:
        str: The phone numbers or error message.
    """
    record = book.find(name)
    return f"{name}: {', '.join(phone.value for phone in record.phones)}"  # type: ignore


@input_error
def handle_all(book: AddressBook):
    """
    Lists all contacts.

    Args:
        book (AddressBook): The address book.

    Returns:
        str: The list of contacts or message if none.
    """
    if not book.data:
        return "No contacts found."

    result = []
    for record in book.data.values():
        phones = ', '.join(phone.value for phone in record.phones)
        birthday = record.birthday if record.birthday else 'N/A'
        result.append(f"name: {record.name}; phones: {phones}; birthday: {birthday}")
    return "\n- ".join(result)


@input_error
def handle_add_birthday(book: AddressBook, name: str, birthday: str):
    """
    Adds a birthday for a contact.

    Args:
        book (AddressBook): The address book.
        name (str): The contact name.
        birthday (str): The birthday in DD.MM.YYYY format.

    Returns:
        str: The result message.
    """
    record = book.find(name)
    record.add_birthday(birthday)  # type: ignore
    return "Birthday added."


@input_error
def handle_show_birthday(book: AddressBook, name: str):
    """
    Shows the birthday of a contact.

    Args:
        book (AddressBook): The address book.
        name (str): The contact name.

    Returns:
        str: The birthday or error message.
    """
    record = book.find(name)
    if record.birthday is None:  # type: ignore
        return "Birthday not set."

    return f"{name}'s birthday is {record.birthday}."  # type: ignore


@input_error
def handle_upcoming_birthdays(book: AddressBook):
    """
    Shows contacts with upcoming birthdays.

    Args:
        book (AddressBook): The address book.

    Returns:
        str: The list of upcoming birthdays or message if none.
    """
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."

    result = []
    for item in upcoming:
        result.append(f"{item['name']}: {item['congratulation_day'].strftime('%d.%m.%Y')}")
    return "\n".join(result)


commands: dict = {
    'hello': handle_hello,
    'help': handle_help,
    'close': handle_exit,
    'exit': handle_exit,
    'add': handle_add,
    'change': handle_change,
    'phone': handle_phone,
    'all': handle_all,
    'add-birthday': handle_add_birthday,
    'show-birthday': handle_show_birthday,
    'birthdays': handle_upcoming_birthdays
}
