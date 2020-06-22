class SiteParamsValidator:
    """Validates website parameters"""
    def __init__(self, console, parser):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()

    def get_params(self):
        """Returns setup-related parameters"""
        return {
            'domain_name': self.options.domain_name,
            'language_code': self.options.language_code,
            'timezone': self.options.timezone,
            'language_settings': self.options.language_settings
        }
