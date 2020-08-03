from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from askbot.deployment.validators import OptionValidator

class SiteParamsValidator:
    """Validates website parameters"""
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns setup-related parameters"""
        #todo: validate the values
        return {
            'admin_name': self.get_admin_name(),
            'admin_email': self.get_admin_email(),
            'domain_name': self.options.domain_name,
            'language_code': self.options.language_code,
            'timezone': self.options.timezone,
            'language_settings': self.options.language_settings
        }

    def get_admin_name(self): #pylint: disable=missing-function-docstring
        if self.options.admin_settings:
            # we won't use this if admin_settings is provided
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='admin_name',
                                    required=True,
                                    prompt='Enter name of the site admin',
                                    cli_error_messages={'missing': '--admin-name is required'},
                                    interactive_error_messages={'missing': 'Admin name is required'})
        return validator.get_value()

    def get_admin_email(self):
        """Returns valid email"""
        if self.options.admin_settings:
            # we won't use this if admin_settings is provided
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    required=True,
                                    option_name='admin_email',
                                    prompt='Enter email of the site admin',
                                    validator=EmailValidator,
                                    cli_error_messages={'missing': '--admin-email is required',
                                                        'invalid': 'value of --admin-email is invalid'},
                                    interactive_error_messages={'missing': 'Admin email is required',
                                                                'invalid': 'Invalid email address'})
        return validator.get_value()
