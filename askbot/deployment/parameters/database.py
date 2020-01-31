import os
from askbot.utils import console
from askbot.deployment import path_utils
from askbot.deployment.base import ConfigField

class DbUser(ConfigField):
    defaultOk = False
    default = ''
    user_prompt = 'Please enter the username for accessing the database'


class DbPass(ConfigField):
    defaultOk = False
    default = ''
    user_prompt = 'Please enter the password for accessing the database'


class DbHost(ConfigField):
    defaultOk = False
    default = ''
    user_prompt = 'Please enter the database hostname'


class DbPort(ConfigField):
    defaultOk = False
    default = ''
    user_prompt = 'Please enter the database port'


class DbEngine(ConfigField):
    defaultOk = False

    database_engines = [
        (1, 'postgresql_psycopg2', 'PostgreSQL'),
        (2, 'sqlite3', 'SQLite'),
        (3, 'mysql', 'MySQL'),
        (4, 'oracle', 'Oracle'),
    ]

    def acceptable(self, value):
        self.print(f'DbEngine.complete called with {value} of type {type(value)}', 2)
        try:
            return value in [e[0] for e in self.database_engines]
        except AttributeError:
            return False

    def ask_user(self, current_value, depth=0):
        user_prompt = 'Please select database engine:\n'
        for index, name in [(e[0], e[2]) for e in self.database_engines]:
            user_prompt += f'{index} - for {name}; '
        user_input = console.choice_dialog(
            user_prompt,
            choices=[str(e[0]) for e in self.database_engines]
        )

        try:
            user_input = int(user_input)
        except Exception as e:
            if depth > 7:
                raise e
            self.print(e)
            user_input = self.ask_user(user_input, depth + 1)

        return user_input


class DbName(ConfigField):
    defaultOk = False
    db_type = 1

    def set_user_prompt(self):
        if self.db_type == 2:
            self.user_prompt = 'Please enter database file name'
        else:
            self.user_prompt = 'Please enter database name'

    def acceptable(self, value):
        if value is None:
            return False
        if self.db_type != 2:
            return len(value.split(' ')) < 2
        if os.path.isfile(value):
            message = 'file %s exists, use it anyway?' % value
            if console.get_yes_or_no(message) == 'yes':
                return True
        elif os.path.isdir(value):
            self.print('%s is a directory, choose another name' % value)
        elif value in path_utils.FILES_TO_CREATE:
            self.print('name %s cannot be used for the database name' % value)
        elif value == path_utils.LOG_DIR_NAME:
            self.print('name %s cannot be used for the database name' % value)
        else:
            return True
        return False
