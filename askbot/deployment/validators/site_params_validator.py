class SiteParamsValidator:
    """Validates website parameters"""
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns setup-related parameters"""
        return {
            'domain_name': self.get_domain_name(),
            'language_code': self.get_timezone(),
            'timezone': self.get_timezone(),
            'language_settings': self.options.language_settings
        }

    def get_domain_name(self):
        """Returns the site domain name"""
        self.options.domain_name

    def get_language_code(self):
        """Returns language code usable by the LANGUAGE_CODE setting"""
        # if have language_settings - override
        #validate the lanuage code string
        pass

    def get_timezone(self):
        """Returns the time zone, e.g. America/Chicago"""
        # validate the timezone string
