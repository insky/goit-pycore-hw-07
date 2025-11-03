"""
Unit tests for the address book application.

To run the tests:
    python3 -m unittest tests.py
    or
    python3 -m unittest tests.py -v  # for verbose output
"""

import unittest
from unittest.mock import patch
from datetime import datetime, date, timedelta
from address_book import (
    Field, Name, Phone, Birthday, Record, AddressBook,
    ValidationError
)
from handlers import (
    parse_input, handle_hello, handle_exit, handle_help,
    handle_add, handle_change, handle_phone, handle_all,
    handle_add_birthday, handle_show_birthday, handle_upcoming_birthdays
)


class TestCaseWithMockDatetime(unittest.TestCase):
    """Base TestCase class with datetime mocking utility."""

    def _setup_datetime_mock(self, mock_datetime_class, year, month, day):
        mock_datetime_class.now.return_value = datetime(year, month, day)
        mock_datetime_class.strptime = datetime.strptime
        mock_datetime_class.timedelta = timedelta


class TestFieldClasses(TestCaseWithMockDatetime):
    """Test cases for Field base class and its subclasses."""

    def test_field_creation(self):
        """Test basic Field creation and methods."""
        field = Field("test_value")
        self.assertEqual(field.value, "test_value")
        self.assertEqual(str(field), "test_value")
        self.assertEqual(repr(field), "Field(test_value)")

    def test_field_equality(self):
        """Test Field equality and hashing."""
        field1 = Field("value")
        field2 = Field("value")
        field3 = Field("different")

        self.assertEqual(field1, field2)
        self.assertNotEqual(field1, field3)
        self.assertEqual(hash(field1), hash(field2))

    def test_name_valid(self):
        """Test Name field with valid input."""
        name = Name("John")
        self.assertEqual(name.value, "John")

    def test_name_invalid_empty(self):
        """Test Name field with empty string."""
        with self.assertRaises(ValidationError):
            Name("")

    def test_name_invalid(self):
        """Test Name field with spaces."""
        with self.assertRaises(ValidationError):
            Name("John Doe")

    def test_name_invalid_type(self):
        """Test Name field with non-string input."""
        with self.assertRaises(ValidationError):
            Name(None)  # type: ignore

    def test_phone_valid(self):
        """Test Phone field with valid 10-digit number."""
        phone = Phone("1234567890")
        self.assertEqual(phone.value, "1234567890")

    def test_phone_invalid_length(self):
        """Test Phone field with wrong length."""
        with self.assertRaises(ValidationError):
            Phone("123456789")  # 9 digits

        with self.assertRaises(ValidationError):
            Phone("12345678901")  # 11 digits

    def test_phone_invalid_characters(self):
        """Test Phone field with non-digit characters."""
        with self.assertRaises(ValidationError):
            Phone("123456789a")

    def test_birthday_valid(self):
        """Test Birthday field with valid date."""
        birthday = Birthday("15.08.1990")
        expected_date = date(1990, 8, 15)
        self.assertEqual(birthday.value, expected_date)

    def test_birthday_invalid_format(self):
        """Test Birthday field with invalid date format."""
        with self.assertRaises(ValidationError):
            Birthday("1990-08-15")

        with self.assertRaises(ValidationError):
            Birthday("15/08/1990")

        with self.assertRaises(ValidationError):
            Birthday("invalid")

    def test_birthday_str_representation(self):
        """Test Birthday string representation."""
        birthday = Birthday("15.08.1990")
        self.assertEqual(str(birthday), "15.08.1990")

    def test_birthday_leap_year(self):
        """Test leap year detection."""
        self.assertTrue(Birthday.is_leap_year(2020))
        self.assertFalse(Birthday.is_leap_year(2021))
        self.assertTrue(Birthday.is_leap_year(2000))
        self.assertFalse(Birthday.is_leap_year(1900))

    def test_birthday_is_29_february(self):
        """Test 29th February detection."""
        birthday_leap = Birthday("29.02.2000")
        birthday_regular = Birthday("15.08.1990")

        self.assertTrue(birthday_leap.is_29th_february())
        self.assertFalse(birthday_regular.is_29th_february())

    @patch('address_book.datetime')
    def test_birthday_next_congratulation_date_regular(self, mock_datetime_class):
        """Test next congratulation date for regular birthday."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 10, 30)
        birthday = Birthday("15.10.1990")
        next_date = birthday.next_congratulation_date()
        expected = date(2026, 10, 15)  # Next year since Oct 15 is past
        self.assertEqual(next_date, expected)

    @patch('address_book.datetime')
    def test_birthday_next_congratulation_date_future(self, mock_datetime_class):
        """Test next congratulation date when birthday is in future."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 10, 1)
        birthday = Birthday("15.10.1990")
        next_date = birthday.next_congratulation_date()
        expected = date(2025, 10, 15)  # This year
        self.assertEqual(next_date, expected)

    @patch('address_book.datetime')
    def test_birthday_next_congratulation_date_weekend_adjustment(self, mock_datetime_class):
        """Test weekend adjustment for birthday celebrations."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 1, 1)
        birthday = Birthday("25.10.1990")  # Saturday
        next_date = birthday.next_congratulation_date()
        expected = date(2025, 10, 27)  # Monday after Saturday
        self.assertEqual(next_date, expected)

    @patch('address_book.datetime')
    def test_birthday_leap_year_29_february_leap_year(self, mock_datetime_class):
        """Test 29 Feb birthday in leap year."""
        self._setup_datetime_mock(mock_datetime_class, 2024, 4, 1)  # 2024 is leap year
        birthday = Birthday("29.02.2000")
        next_date = birthday.next_congratulation_date()
        expected = date(2025, 2, 28)  # Friday 28 Feb in leap year
        self.assertEqual(next_date, expected)

    @patch('address_book.datetime')
    def test_birthday_leap_year_29_february_leap_year_future(self, mock_datetime_class):
        """Test 29 Feb birthday in leap year in future."""
        self._setup_datetime_mock(mock_datetime_class, 2024, 1, 1)  # 2024 is leap year
        birthday = Birthday("29.02.2000")
        next_date = birthday.next_congratulation_date()
        expected = date(2024, 2, 29)  # Thursday 29 Feb in leap year
        self.assertEqual(next_date, expected)

    @patch('address_book.datetime')
    def test_birthday_leap_year_29_february_non_leap_year(self, mock_datetime_class):
        """Test 29 Feb birthday in non-leap year."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 1, 1)  # 2025 is not leap year
        birthday = Birthday("29.02.2000")
        next_date = birthday.next_congratulation_date()
        expected = date(2025, 2, 28)  # Friday 28 Feb in non-leap year
        self.assertEqual(next_date, expected)


class TestRecord(TestCaseWithMockDatetime):
    """Test cases for Record class."""

    def test_record_creation(self):
        """Test Record creation."""
        record = Record("John")
        self.assertEqual(record.name.value, "John")
        self.assertIsNone(record.birthday)
        self.assertEqual(len(record.phones), 0)

    def test_record_str_representation(self):
        """Test Record string representation."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_birthday("15.08.1990")

        expected = "Contact name: John, phones: 1234567890, birthday: 15.08.1990"
        self.assertEqual(str(record), expected)

    def test_record_str_no_birthday(self):
        """Test Record string representation without birthday."""
        record = Record("John")
        record.add_phone("1234567890")

        expected = "Contact name: John, phones: 1234567890, birthday: N/A"
        self.assertEqual(str(record), expected)

    def test_add_phone_valid(self):
        """Test adding valid phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        self.assertEqual(len(record.phones), 1)
        self.assertIn(Phone("1234567890"), record.phones)

    def test_add_phone_invalid(self):
        """Test adding invalid phone number."""
        record = Record("John")
        with self.assertRaises(ValidationError):
            record.add_phone("invalid")

    def test_add_multiple_phones(self):
        """Test adding multiple phone numbers."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("0987654321")
        self.assertEqual(len(record.phones), 2)

    def test_remove_phone_valid(self):
        """Test removing existing phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        record.remove_phone("1234567890")
        self.assertEqual(len(record.phones), 0)

    def test_remove_phone_invalid(self):
        """Test removing invalid phone number."""
        record = Record("John")
        with self.assertRaises(ValidationError):
            record.remove_phone("invalid")

    def test_remove_phone_not_found(self):
        """Test removing non-existent phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        with self.assertRaises(KeyError):
            record.remove_phone("0987654321")

    def test_edit_phone_valid(self):
        """Test editing existing phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        record.edit_phone("1234567890", "0987654321")

        self.assertEqual(len(record.phones), 1)
        self.assertIn(Phone("0987654321"), record.phones)
        self.assertNotIn(Phone("1234567890"), record.phones)

    def test_edit_phone_old_not_found(self):
        """Test editing non-existent phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        with self.assertRaises(ValidationError):
            record.edit_phone("0987654321", "1111111111")

    def test_edit_phone_new_invalid(self):
        """Test editing with invalid new phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        with self.assertRaises(ValidationError):
            record.edit_phone("1234567890", "invalid")

    def test_find_phone_exists(self):
        """Test finding existing phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        found = record.find_phone("1234567890")
        self.assertIsNotNone(found)
        if found:
            self.assertEqual(found.value, "1234567890")

    def test_find_phone_not_exists(self):
        """Test finding non-existent phone number."""
        record = Record("John")
        record.add_phone("1234567890")
        found = record.find_phone("0987654321")
        self.assertIsNone(found)

    def test_add_birthday_valid(self):
        """Test adding valid birthday."""
        record = Record("John")
        record.add_birthday("15.08.1990")
        self.assertIsNotNone(record.birthday)
        if record.birthday:
            self.assertEqual(record.birthday.value, date(1990, 8, 15))

    def test_add_birthday_invalid(self):
        """Test adding invalid birthday."""
        record = Record("John")
        with self.assertRaises(ValidationError):
            record.add_birthday("invalid")


class TestAddressBook(TestCaseWithMockDatetime):
    """Test cases for AddressBook class."""

    def setUp(self):
        """Set up test fixtures."""
        self.book = AddressBook()
        self.record1 = Record("John")
        self.record1.add_phone("1234567890")
        self.record2 = Record("Jane")
        self.record2.add_phone("0987654321")

    def test_add_record(self):
        """Test adding a record."""
        self.book.add_record(self.record1)
        self.assertIn("John", self.book.data)
        self.assertEqual(self.book.data["John"], self.record1)

    def test_find_existing_record(self):
        """Test finding existing record."""
        self.book.add_record(self.record1)
        found = self.book.find("John")
        self.assertEqual(found, self.record1)

    def test_find_non_existing_record(self):
        """Test finding non-existent record."""
        found = self.book.find("Non Existent")
        self.assertIsNone(found)

    def test_delete_existing_record(self):
        """Test deleting existing record."""
        self.book.add_record(self.record1)
        self.book.delete("John")
        self.assertNotIn("John", self.book.data)

    def test_delete_non_existing_record(self):
        """Test deleting non-existent record."""
        # Should not raise error
        self.book.delete("Non Existent")

    @patch('address_book.datetime')
    def test_get_upcoming_birthdays(self, mock_datetime_class):
        """Test getting upcoming birthdays."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 10, 30)
        record = Record("John")
        record.add_birthday("31.10.1990")  # Oct 31 - 1 day from now
        self.book.add_record(record)

        record2 = Record("Jane")
        record2.add_birthday("15.11.1990")  # Nov 15 - more than 7 days
        self.book.add_record(record2)

        upcoming = self.book.get_upcoming_birthdays(7)
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0]["name"].value, "John")

    @patch('address_book.datetime')
    def test_get_upcoming_birthdays_weekend_adjustment(self, mock_datetime_class):
        """Test weekend adjustment in upcoming birthdays."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 10, 21)
        record = Record("John")
        record.add_birthday("25.10.1990")  # Oct 25 - Saturday
        self.book.add_record(record)

        upcoming = self.book.get_upcoming_birthdays(7)
        congratulation_date = upcoming[0]["congratulation_day"]
        # Should be moved to Monday (Oct 27)
        self.assertEqual(congratulation_date, date(2025, 10, 27))

    def test_get_upcoming_birthdays_no_birthdays(self):
        """Test getting upcoming birthdays when none exist."""
        upcoming = self.book.get_upcoming_birthdays()
        self.assertEqual(len(upcoming), 0)


class TestParseInput(TestCaseWithMockDatetime):
    """Test cases for parse_input function."""

    def test_parse_input_valid_command(self):
        """Test parsing valid command with arguments."""
        cmd, args = parse_input("add John 1234567890")
        self.assertEqual(cmd, "add")
        self.assertEqual(args, ["John", "1234567890"])

    def test_parse_input_command_only(self):
        """Test parsing command without arguments."""
        cmd, args = parse_input("hello")
        self.assertEqual(cmd, "hello")
        self.assertEqual(args, [])

    def test_parse_input_empty_input(self):
        """Test parsing empty input."""
        cmd, args = parse_input("")
        self.assertIsNone(cmd)
        self.assertEqual(args, [])

    def test_parse_input_whitespace_only(self):
        """Test parsing whitespace-only input."""
        cmd, args = parse_input("   ")
        self.assertIsNone(cmd)
        self.assertEqual(args, [])


class TestHandlers(TestCaseWithMockDatetime):
    """Test cases for handler functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.book = AddressBook()
        self.record = Record("John")
        self.record.add_phone("1234567890")
        self.book.add_record(self.record)

    def test_handle_hello(self):
        """Test hello handler."""
        result = handle_hello(self.book)
        self.assertEqual(result, "How can I help you?")

    def test_handle_help(self):
        """Test help handler."""
        result = handle_help(self.book)
        self.assertIn("Available commands:", result)
        self.assertIn("hello", result)
        self.assertIn("add", result)

    @patch('handlers.sys.exit')
    def test_handle_exit(self, mock_exit):
        """Test exit handler."""
        handle_exit(self.book)
        mock_exit.assert_called_once_with(0)

    def test_handle_add_new_contact(self):
        """Test adding new contact."""
        result = handle_add(self.book, "Jane", "0987654321")
        self.assertEqual(result, "Contact added.")
        self.assertIn("Jane", self.book.data)

    def test_handle_add_existing_contact(self):
        """Test adding phone to existing contact."""
        result = handle_add(self.book, "John", "0987654321")
        self.assertEqual(result, "Contact updated.")
        self.assertEqual(len(self.book.data["John"].phones), 2)

    def test_handle_add_invalid_phone(self):
        """Test adding contact with invalid phone."""
        result = handle_add(self.book, "Jane", "invalid")
        self.assertEqual(result, "Invalid phone number")

    def test_handle_change_valid(self):
        """Test changing phone number."""
        result = handle_change(self.book, "John", "1234567890", "0987654321")
        self.assertEqual(result, "Contact updated.")
        self.assertIn(Phone("0987654321"), self.book.data["John"].phones)

    def test_handle_change_contact_not_found(self):
        """Test changing phone for non-existent contact."""
        result = handle_change(self.book, "Non Existent", "1234567890", "0987654321")
        self.assertEqual(result, "Contact not found.")

    def test_handle_change_phone_not_found(self):
        """Test changing non-existent phone."""
        result = handle_change(self.book, "John", "0987654321", "1111111111")
        self.assertEqual(result, "Old phone number not found")

    def test_handle_phone_existing_contact(self):
        """Test getting phone for existing contact."""
        result = handle_phone(self.book, "John")
        self.assertEqual(result, "John: 1234567890")

    def test_handle_phone_contact_not_found(self):
        """Test getting phone for non-existent contact."""
        result = handle_phone(self.book, "Non Existent")
        self.assertEqual(result, "Contact not found.")

    def test_handle_all_with_contacts(self):
        """Test listing all contacts."""
        result = handle_all(self.book)
        self.assertIn("name: John; phones: 1234567890; birthday: N/A", result)

    def test_handle_all_empty_book(self):
        """Test listing all contacts when book is empty."""
        empty_book = AddressBook()
        result = handle_all(empty_book)
        self.assertEqual(result, "No contacts found.")

    def test_handle_add_birthday_valid(self):
        """Test adding birthday to existing contact."""
        result = handle_add_birthday(self.book, "John", "15.08.1990")
        self.assertEqual(result, "Birthday added.")
        self.assertIsNotNone(self.book.data["John"].birthday)

    def test_handle_add_birthday_contact_not_found(self):
        """Test adding birthday to non-existent contact."""
        result = handle_add_birthday(self.book, "Non Existent", "15.08.1990")
        self.assertEqual(result, "Contact not found.")

    def test_handle_add_birthday_invalid_date(self):
        """Test adding invalid birthday."""
        result = handle_add_birthday(self.book, "John", "invalid")
        self.assertEqual(result, "Invalid date format. Use DD.MM.YYYY")

    def test_handle_show_birthday_existing(self):
        """Test showing birthday for contact with birthday."""
        self.book.data["John"].add_birthday("15.08.1990")
        result = handle_show_birthday(self.book, "John")
        self.assertEqual(result, "John's birthday is 15.08.1990.")

    def test_handle_show_birthday_not_set(self):
        """Test showing birthday when not set."""
        result = handle_show_birthday(self.book, "John")
        self.assertEqual(result, "Birthday not set.")

    def test_handle_show_birthday_contact_not_found(self):
        """Test showing birthday for non-existent contact."""
        result = handle_show_birthday(self.book, "Non Existent")
        self.assertEqual(result, "Contact not found.")

    @patch('address_book.datetime')
    def test_handle_upcoming_birthdays_with_upcoming(self, mock_datetime_class):
        """Test showing upcoming birthdays."""
        self._setup_datetime_mock(mock_datetime_class, 2025, 10, 25)
        self.book.data["John"].add_birthday("30.10.1990")
        result = handle_upcoming_birthdays(self.book)
        self.assertIn("John:", result)

    @patch('address_book.datetime')
    def test_handle_upcoming_birthdays_none(self, mock_datetime_class):
        """Test showing upcoming birthdays when none."""
        self._setup_datetime_mock(mock_datetime_class, 2023, 10, 25)
        self.book.data["John"].add_birthday("15.11.1990")  # More than 7 days away
        result = handle_upcoming_birthdays(self.book)
        self.assertEqual(result, "No upcoming birthdays.")


if __name__ == '__main__':
    unittest.main()
