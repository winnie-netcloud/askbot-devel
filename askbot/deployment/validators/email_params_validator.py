"""Validates email setup parameters"""
from .option_validator import OptionValidator
from django.core.validators import EmailValidator
from ..utils import DomainNameValidator, PortNumberValidator

class EmailParamsValidator: #pylint: disable=missing-class-docstring
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns valid email setting values"""
        return {'server_email': self.get_server_email(),
                'default_from_email': self.get_default_from_email(),
                'email_backend': self.options.email_backend,
                'email_subject_prefix': self.options.email_subject_prefix,
                'email_host_user': self.options.email_host_user,
                'email_host_password': self.options.email_host_password,
                'email_host': self.get_email_host(),
                'email_port': self.get_email_port(),
                'email_use_tls': self.options.email_use_tls}

    def get_server_email(self):
        """Returns server email"""
        if self.options.email_settings:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    required=False,
                                    default_value='',
                                    option_name='server_email',
                                    prompt='Enter server email address',
                                    validator=EmailValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --server-email is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Invalid email address'})
        return validator.get_value()

    def get_default_from_email(self):
        """Returns DEFAULT_FROM_EMAIL email"""
        if self.options.email_settings:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    required=False,
                                    default_value='',
                                    option_name='default_from_email',
                                    prompt='Enter value for the DEFAULT_FROM_EMAIL',
                                    validator=EmailValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --default-from-email is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Invalid email address'})
        return validator.get_value()

    def get_email_host(self):
        """Returns host name of the email server"""
        if self.options.email_settings:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='email_host',
                                    default_value='',
                                    prompt='Enter the mail server host',
                                    validator=DomainNameValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --email-host is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Host name is invalid'})
        return validator.get_value()

    def get_email_port(self):
        """Returns the mail server port number"""
        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='email_port',
                                    default_value='',
                                    prompt='Enter the mail server port number',
                                    validator=PortNumberValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --email-port is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Port is invalid'})
        return validator.get_value()
