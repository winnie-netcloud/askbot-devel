from askbot.deployment.base import ConfigManagerCollection, ConfigManager
from .configmanagers import CacheConfigManager, DbConfigManager

from .cache import *
from .database import *
from .filesystem import *

"""
In this module we assemble the input validation capabilities for the Askbot
installer.

The goal is to provide a single ConfigManagerCollection instance
(currently named askbotCollection), the installer will use to validate its
parameters.

The idea is askbotCollection will be able to validate just the
parameters that are register()-ed in this module/file. First we create the
collection and managers. Then we register() all the parameters for which we
want validation.

The validation implementations vary in complexity. Therefore, all
implementations are defined in derived classes in submodules, structured by
their topic, e.g. cache, database and filesystem. Here, at this level, we
import all classes and use register() as a mapping from parameter name, to
validation implementation.

The parameter names must match the argpare argument destinations, i.e. the
`dest` argument to ArgumentParser.add_argument(), do be effective.

THE ORDER IN WHICH VALIDATIONS ARE register()-ed WITH THEIR ConfigManagers
MATTERS!
"""

# use these values while inizializing this module
interactive=False
verbosity=0

# the ConfigManagerCollection the installer will use
askbotCollection = ConfigManagerCollection(interactive=interactive, verbosity=verbosity)

# the ConfigManagers the installer will use
cacheManager = CacheConfigManager(interactive=interactive, verbosity=verbosity)
databaseManager = DbConfigManager(interactive=interactive, verbosity=verbosity)
filesystemManager = ConfigManager(interactive=interactive, verbosity=verbosity)

# register the ConfigManagers with the ConfigManagerCollection
askbotCollection.register('filesystem', filesystemManager)
askbotCollection.register('database', databaseManager)
askbotCollection.register('cache', cacheManager)

# register parameters with config managers. THE ORDERING MATTERS!
cacheManager.register('cache_engine', CacheEngine())
cacheManager.register('cache_nodes', CacheNodes())
cacheManager.register('cache_db', CacheDb())
cacheManager.register('cache_password', CachePass())

databaseManager.register('database_engine', DbEngine())
databaseManager.register('database_name', DbName())
databaseManager.register('database_user', DbUser())
databaseManager.register('database_password', DbPass())
databaseManager.register('database_host', DbHost())
databaseManager.register('database_port', DbPort())

filesystemManager.register('dir_name', ProjectDirName())
filesystemManager.register('app_name', AppDirName())
filesystemManager.register('logfile_name', LogfileName())


__all__ = ['askbotCollection', 'cacheManager', 'databaseManager', 'filesystemManager']
