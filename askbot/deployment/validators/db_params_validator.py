import os
from askbot.utils.console import choice_dialog, simple_dialog
from askbot.deployment import const

class DbParamsValidator:
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
            'database_user': self.get_db_user(),
            'database_password': self.get_db_password(db_engine)
        }

    def get_db_engine(self):
        """Dialog asking for a value 1-4"""
        if self.options.database_settings:
            return None
        choices = [ch[0] for ch in const.DATABASE_ENGINE_CHOICES]
        prompt = 'Select the ' + const.bold('database engine') + \
                 ': 1 - Postgresql, 2 - SQLite, 3 - MySQL, 4 - Oracle'
        return choice_dialog(prompt, choices=choices, default=const.SQLITE)

    def get_db_user(self):
        if self.options.database_settings:
            return None
        return simple_dialog('Enter ' + const.bold('database user name') + '.', required=True)

    def get_db_name(self, db_engine):
        if self.options.database_settings:
            return None
        if db_engine == str(const.SQLITE):
            prompt = const.get_sqlite_db_path_prompt(self.prev_params['proj_dir'])
            db_path = simple_dialog(prompt, required=True)
            if os.path.isabs(db_path):
                return db_path
            return os.path.join(self.prev_params['proj_dir'], db_path)

        return simple_dialog('Enter ' + const.bold('database name') + '.', required=True)

    def get_db_password(self, db_engine):
        if self.options.database_settings:
            return None
        if db_engine == str(const.SQLITE):
            return simple_dialog('Enter ' + const.bold('database password') + \
                '.\nPress ENTER to omit password.', required=False)
        return simple_dialog('Enter ' + const.bold('database password') + '.', required=True)
