"""`DbParamsValidator` - class that provides valid database parameters"""
import os
from django.core.exceptions import ValidationError
from askbot.utils.console import bold
from askbot.deployment import const
from askbot.deployment.console import get_sqlite_db_path_prompt

class DbParamsValidator: #pylint: disable=missing-class-docstring
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns database-related parameters"""
        db_engine = None
        if not self.options.database_settings:
            db_engine = self.get_db_engine()

        return {
            'database_settings': self.options.database_settings,
            'database_engine': db_engine,
            'database_name': self.get_db_name(db_engine),
            'database_user': self.get_db_user(db_engine),
            'database_password': self.get_db_password(db_engine)
        }

    def get_db_engine(self):
        """Dialog asking for a value 1-4"""
        if self.options.database_settings:
            return None

        choices = [ch[0] for ch in const.DATABASE_ENGINE_CHOICES]
        if not self.options.interactive:
            cli_value = self.options.database_engine
            if not cli_value:
                return str(const.SQLITE)
            if cli_value not in choices:
                raise ValidationError('Invaild choice for the --db-engine parameter')

        prompt = 'Select the ' + bold('database engine') + \
                 ': 1 - Postgresql, 2 - SQLite, 3 - MySQL, 4 - Oracle'
        return self.console.choice_dialog(prompt, choices=choices, default=const.SQLITE)

    def get_db_user(self, db_engine):
        """Asks for the database user name"""
        if self.options.database_settings:
            return None

        if db_engine == str(const.SQLITE):
            return ''

        if not self.options.interactive:
            cli_value = self.options.database_user
            if not cli_value:
                raise ValidationError('--db-user parameter is required')
            return cli_value

        prompt = 'Enter ' + bold('database user name') + '.'
        return self.console.simple_dialog(prompt, required=True)

    def get_db_name(self, db_engine):
        """Asks user to enter the database name"""
        if self.options.database_settings:
            return None

        if not self.options.interactive:
            cli_value = self.options.database_name
            if not cli_value:
                if db_engine == str(const.SQLITE):
                    return const.DEFAULT_SQLITE_DB_NAME
                raise ValidationError('--db-name parameter is required')
            return cli_value

        if db_engine == str(const.SQLITE):
            prompt = get_sqlite_db_path_prompt(self.prev_params['proj_dir'])
            db_path = self.console.simple_dialog(prompt,
                                                 default=const.DEFAULT_SQLITE_DB_NAME)
            if os.path.isabs(db_path):
                return db_path
            return os.path.join(self.prev_params['proj_dir'], db_path)

        return self.console.simple_dialog('Enter ' + bold('database name') + '.', required=True)

    def get_db_password(self, db_engine):
        """Asks user to enter the database password"""
        if self.options.database_settings:
            return None

        if not self.options.interactive:
            if db_engine != str(const.SQLITE):
                raise ValidationError('--db-password parameter is required')

        if db_engine == str(const.SQLITE):
            return ''

        prompt = 'Enter ' + bold('database password') + '.'
        return self.console.simple_dialog(prompt, required=True)
