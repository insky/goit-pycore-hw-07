"""Address Book Module."""

from collections import UserDict
from datetime import datetime, timedelta, date


class ValidationError(Exception):
    """Custom exception for validation errors."""


class Field:
    """Base class for all fields."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value and isinstance(other, type(self))

    def __hash__(self):
        return hash(self.value)


class Name(Field):
    """Represents a contact's name."""

    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise ValidationError("Invalid name")
        # Now name can not contain space-like characters
        if any(char.isspace() for char in value):
            raise ValidationError("Name cannot contain spaces")
        super().__init__(value)


class Phone(Field):
    """Represents a contact's phone number."""

    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValidationError("Invalid phone number")
        super().__init__(value)


class Birthday(Field):
    """Represents a contact's birthday."""

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday)
        except ValueError as e:
            raise ValidationError("Invalid date format. Use DD.MM.YYYY") from e

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Checks if a year is a leap year.

        Args:
            year (int): The year to check.

        Returns:
            bool: True if leap year, False otherwise.
        """
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def is_29th_february(self) -> bool:
        """Checks if the birthday is on 29th February.

        Returns:
            bool: True if birthday is February 29, False otherwise.
        """
        if self.value is None:
            return False
        return self.value.month == 2 and self.value.day == 29

    def next_congratulation_date(self) -> date | None:
        """
        The next birthday celebration date, adjusted for weekends.

        Returns:
            date | None: The next celebration date, adjusted for weekends.
        """
        if self.value is None:
            return None

        today = datetime.now().date()
        if self.is_29th_february() and not Birthday.is_leap_year(today.year):
            # If today is not a leap year, celebrate on 28th February
            next_birthday = self.value.replace(year=today.year, day=28)
        else:
            next_birthday = self.value.replace(year=today.year)

        # If next birthday is in the past, move to next year
        if next_birthday < today:
            # special case for 29th February
            if self.is_29th_february():
                if Birthday.is_leap_year(today.year + 1):
                    next_birthday = next_birthday.replace(year=today.year + 1, day=29)
                else:
                    next_birthday = next_birthday.replace(year=today.year + 1, day=28)
            else:
                next_birthday = next_birthday.replace(year=today.year + 1)

        # If birthday falls on weekend, move to next Monday
        if next_birthday.weekday() == 5:  # Saturday
            next_birthday += timedelta(days=2)
        elif next_birthday.weekday() == 6:  # Sunday
            next_birthday += timedelta(days=1)

        return next_birthday


class Record:
    """Represents a contact record."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.birthday = None
        self.phones = set()

    def __str__(self):
        name_str = self.name.value
        phones_str = ', '.join(p.value for p in self.phones)
        birthday_str = str(self.birthday) if self.birthday else 'N/A'
        return f"Contact name: {name_str}, phones: {phones_str}, birthday: {birthday_str}"

    def add_phone(self, phone: str) -> None:
        """
        Adds a phone number to the contact.

        Args:
            phone (str): The phone number to add.

        Raises:
            ValidationError: If phone number is invalid.
        """

        self.phones.add(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        """
        Removes a phone number from the contact.

        Args:
            phone (str): The phone number to remove.

        Raises:
            ValidationError: If phone number is invalid.
            KeyError: If phone number is not found.
        """
        phone_obj = Phone(phone)
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """
        Edits an existing phone number.

        Args:
            old_phone (str): The old phone number.
            new_phone (str): The new phone number.

        Raises:
            ValidationError: If old phone number is not found or new phone number is invalid.
        """
        old_phone_obj = Phone(old_phone)
        if old_phone_obj not in self.phones:
            raise ValidationError("Old phone number not found")

        self.phones.add(Phone(new_phone))
        self.phones.remove(old_phone_obj)

    def find_phone(self, phone: str) -> Phone | None:
        """
        Finds and returns a phone number if it exists.

        Args:
            phone (str): The phone number to find.

        Returns:
            Phone | None: The phone object if found, None otherwise.
        """
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str) -> None:
        """Adds a birthday to the contact.

        Args:
            birthday (str): The birthday in DD.MM.YYYY format.

        Raises:
            ValueError: If date format is invalid.
        """
        self.birthday = Birthday(birthday)


class AddressBook(UserDict):
    """Represents the address book."""

    def add_record(self, record: Record) -> None:
        """Adds a record to the address book.

        Args:
            record (Record): The record to add.
        """
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        """
        Finds and returns a record by name.

        Args:
            name (str): The name to search for.

        Returns:
            Record | None: The record if found, None otherwise.
        """
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Deletes a record by name.

        Args:
            name (str): The name of the record to delete.
        """
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days_ahead: int = 7) -> list[dict]:
        """
        Returns a list of contacts with birthdays in the next 'days_ahead' days.

        Args:
            days_ahead (int): Number of days to look ahead (default 7).

        Returns:
            list[dict]: List of dictionaries with name and congratulation_day.
        """
        upcoming_birthdays = []
        today = datetime.now().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            congratulation_day = record.birthday.next_congratulation_date()

            if 0 <= (congratulation_day - today).days <= days_ahead:
                upcoming_birthdays.append({
                    "name": record.name,
                    "congratulation_day": congratulation_day
                })

        return upcoming_birthdays
