"""Validates any option, given the `validator` class, and other parameters
"""
from django.core.exceptions import ValidationError

class OptionValidator:
    """The validator class.
    .get_value() method
    is the only one you need to use
    after the proper setup"""

    def __init__(self, console, parser, option_name=None, required=False,
                 prompt=None, validator=None, cli_error_messages=None,
                 interactive_error_messages=None):

        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.option_name = option_name
        self.required = required
        self.validator = validator
        self.cli_error_messages = cli_error_messages
        self.interactive_error_messages = interactive_error_messages

    def get_value(self):
        """Returns a valid value or raises an exception"""
        if self.options.interactive:
            self.get_value_from_user_input()

        return self.get_value_from_cli_input()

    def get_value_from_cli_input(self):
        """Validates and returns value as entered via the CLI"""
        value = getattr(self.options, self.option_name)
        if self.required and not value:
            raise ValidationError(self.cli_error_messages['missing'])

        if self.validator:
            try:
                self.validator(value)
            except ValidationError:
                raise ValidationError(self.cli_error_messages['invalid'])
        return value

    def get_value_from_user_input(self):
        """Returns validated value as entered by the user, however
        also checks the value in case it was given with the CLI parameter"""
        # if cli value !== default
        # validate the value and if it is invalid
        # print the error message

        # enter the interactive loop

        # return the valid value
