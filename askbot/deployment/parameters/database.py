from askbot.utils import console
import os
from askbot.deployment import path_utils

from askbot.deployment.parameters.base import ConfigField, ConfigManager

class DbConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
    the database Askbot will use."""
    def __init__(self, interactive=True, verbosity=1):
        super(DbConfigManager, self).__init__(interactive=interactive, verbosity=verbosity)
        engine = DbEngine()
        name   = DbName()
        username = ConfigField(
            defaultOk=False,
            user_prompt='Please enter the username for accessing the database',
        )
        password = ConfigField(
            defaultOk=False,
            user_prompt='Please enter the password for accessing the database',
        )
        host = ConfigField(
            defaultOk=True,
            user_prompt='Please enter the database hostname',
        )
        port = ConfigField(
            defaultOk=True,
            user_prompt='Please enter the database port',
        )

        self.register('database_engine', engine)
        self.register('database_name', name)
        self.register('database_user', username)
        self.register('database_password', password)
        self.register('database_host', host)
        self.register('database_port', port)

    def _order(self, keys):
        full_set = [ 'database_engine', 'database_name', 'database_user',
                     'database_password', 'database_host', 'database_port' ]
        return [ item for item in full_set if item in keys ]

    def _remember(self, name, value):
        if name == 'database_engine':
            value = int(value)
        super(DbConfigManager, self)._remember(name, value)
        if name == 'database_engine':
            self._catalog['database_name'].db_type = value
            self._catalog['database_name'].set_user_prompt()
            if value == 2:
                self._catalog['database_user'].defaultOk = True
                self._catalog['database_password'].defaultOk = True

    def _complete(self, name, current_value):
        """
        Wrap the default _complete() to implement a special handling of
        `database_engine`. While the user selects database engines by index,
        i.e. 1,2,3 or 4, at the time of this writing, the installer and Askbot
        use Django module names (I think that's what this is). Therefore we
        perform a lookup after the user made their final choice and return
        the name, rather than the index.
        """
        ret = super(DbConfigManager, self)._complete(name, current_value)
        if name == 'database_engine':
            return [ e[1] for e in
                     self.configField(name).database_engines
                     if e[0] == ret ].pop()
        return ret

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
        except:
            pass
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

