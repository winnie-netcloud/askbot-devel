from askbot.utils import console
import os
from askbot.deployment import path_utils

from askbot.deployment.parameters.base import ConfigField, ConfigManager

class DbConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
    the database Askbot will use."""
    def __init__(self, interactive=True):
        super(DbConfigManager, self).__init__(interactive)
        self.register('database_engine', DbEngine)
        self.register('database_name', DbName)
        self.register('database_user', DbUser)
        self.register('database_password', DbPass)
        self.register('database_host', DbHost)
        self.register('database_port', DbPort)

    def _order(self, keys):
        full_set = [ 'database_engine', 'database_name', 'database_user',
                     'database_password', 'database_host', 'database_port' ]
        return [ item for item in full_set if item in keys ]

    def _remember(self, name, value):
        super(DbConfigManager, self)._remember(name, value)
        if name == 'database_engine':
            self._catalog['database_name'].db_type = value
            self._catalog['database_name'].set_user_prompt()
            if value == '2':
                self._catalog['database_user'].defaultOk = True
                self._catalog['database_password'].defaultOk = True

class DbEngine(ConfigField):
    defaultOk = False

    database_engines = [
        ('1', 'postgresql_psycopg2', 'PostgreSQL'),
        ('2', 'sqlite3', 'SQLite'),
        ('3', 'mysql', 'MySQL'),
        ('4', 'oracle', 'Oracle'),
    ]

    @classmethod
    def acceptable(cls, value):
        return value in [ e[0] for e in cls.database_engines ]

    @classmethod
    def ask_user(cls, current_value):
        user_prompt = 'Please select database engine:\n'
        for index, name in [ (e[0], e[2]) for e in cls.database_engines ]:
            user_prompt += f'{index} - for {name}; '
        return console.choice_dialog(
            user_prompt,
            choices=[ e[0] for e in cls.database_engines ]
        )

class DbName(ConfigField):
    defaultOk = False
    db_type = 1

    @classmethod
    def set_user_prompt(cls):
        if cls.db_type == '2':
            cls.user_prompt = 'Please enter database file name'
        else:
            cls.user_prompt = 'Please enter database name'

    @classmethod
    def acceptable(cls, value):
        if value is None:
            return False
        if cls.db_type != '2':
            return len(value.split(' ')) < 2
        if os.path.isfile(value):
            message = 'file %s exists, use it anyway?' % value
            if console.get_yes_or_no(message) == 'yes':
                return True
        elif os.path.isdir(value):
            print('%s is a directory, choose another name' % value)
        elif value in path_utils.FILES_TO_CREATE:
            print('name %s cannot be used for the database name' % value)
        elif value == path_utils.LOG_DIR_NAME:
            print('name %s cannot be used for the database name' % value)
        else:
            return True
        return False

class DbUser(ConfigField):
    defaultOk = False
    user_prompt = 'Please enter the username for accessing the database'

class DbPass(ConfigField):
    defaultOk = False
    user_prompt = 'Please enter the password for the database user'

# As it stands, we will never prompt the user to provide DbHost nor DbPort.
# One would have to add a class method acceptable() which can actually fail to
# create use cases where Askbot install may prompt the user.
class DbHost(ConfigField):
    defaultOk = True
    user_prompt = 'Please enter the database hostname'

class DbPort(ConfigField):
    defaultOk = True
    user_prompt = 'Please enter the database port'
