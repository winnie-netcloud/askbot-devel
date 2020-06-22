class DbParamsValidator:
    def __init__(self, console, parser):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()

    def get_params(self):
        """Returns database-related parameters"""
        return {
            'database_settings': self.options.database_settings,
            'database_engine': self.options.database_engine,
            'database_name': self.options.database_name,
            'database_user': self.options.database_user,
            'database_password': self.options.database_password
        }
