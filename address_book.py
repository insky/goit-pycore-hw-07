''' Address Book Module '''
from collections import UserDict
from datetime import datetime, timedelta, date


class ValidationError(Exception):
    ''' Custom exception for validation errors '''


class Field:
    ''' Base class for all fields '''

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
    ''' Represents a contact's name '''

    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise ValidationError("Invalid name")
        super().__init__(value)


class Phone(Field):
    ''' Represents a contact's phone number '''

    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValidationError("Invalid phone number")
        super().__init__(value)


class Birthday(Field):
    ''' Represents a contact's birthday '''

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday)
        except ValueError as e:
            raise ValidationError("Invalid date format. Use DD.MM.YYYY") from e

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

    @classmethod
    def is_leap_year(cls, year: int) -> bool:
        '''
            Checks if a year is a leap year
        '''
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def is_29th_february(self) -> bool:
        '''
            Checks if the birthday is on 29th February
        '''
        if self.value is None:
            return False
        return self.value.month == 2 and self.value.day == 29

    def next_congritulation_date(self) -> date | None:
        '''
            Returns the next birthday celebration date
        '''
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
            if self.is_29th_february() and Birthday.is_leap_year(today.year + 1):
                next_birthday = self.value.replace(year=today.year + 1, day=29)
            else:
                next_birthday = next_birthday.replace(year=today.year + 1)

        # If birthday falls on weekend, move to next Monday
        if next_birthday.weekday() == 5: # Saturday
            next_birthday += timedelta(days=2)
        elif next_birthday.weekday() == 6: # Sunday
            next_birthday += timedelta(days=1)

        return next_birthday


class Record:
    ''' Represents a contact record '''

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
        '''
            Adds a phone number to the contact
            Raises ValidationError if phone number is invalid
        '''

        self.phones.add(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        '''
            Removes a phone number from the contact
            Raises ValidationError if phone number is invalid
            Raises KeyError if phone number is not found
        '''
        phone_obj = Phone(phone)
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        '''
            Edits an existing phone number
            Raises ValidationError if old phone number is not found or new phone number is invalid
        '''
        old_phone_obj = Phone(old_phone)
        if old_phone_obj not in self.phones:
            raise ValidationError("Old phone number not found")

        self.phones.add(Phone(new_phone))
        self.phones.remove(old_phone_obj)

    def find_phone(self, phone: str) -> Phone | None:
        '''
            Finds and returns a phone number if it exists
            Returns None if not found
        '''
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str) -> None:
        '''
            Adds a birthday to the contact
            Raises ValueError if date format is invalid
        '''
        self.birthday = Birthday(birthday)


class AddressBook(UserDict):
    ''' Represents the address book '''

    def add_record(self, record: Record) -> None:
        '''
            Adds a record to the address book
        '''
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        '''
            Finds and returns a record by name
            Returns None if not found
        '''
        return self.data.get(name)

    def delete(self, name: str) -> None:
        '''
            Deletes a record by name
        '''
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days_ahead: int = 7) -> list[dict]:
        '''
            Returns a list of contacts with birthdays in the next 'days_ahead' days
            Adjusts for weekends by moving celebrations to the next Monday
        '''
        upcoming_birthdays = []
        today = datetime.now().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            congratulation_day = record.birthday.next_congritulation_date()

            if 0 <= (congratulation_day - today).days < days_ahead:
                upcoming_birthdays.append({
                    "name": record.name,
                    "congratulation_day": congratulation_day
                })

        return upcoming_birthdays
