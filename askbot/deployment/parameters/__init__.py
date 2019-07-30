from askbot.deployment.parameters.database import DbConfigManager
from askbot.deployment.parameters.cache import CacheConfigManager
from askbot.deployment.parameters.filesystem import FilesystemConfigManager

class ConfigManagerCollection(object):
    def __init__(self, interactive=False, verbosity=0):
        self.verbosity = verbosity
        self.interactive = interactive
        self.database = DbConfigManager(interactive=interactive, verbosity=verbosity)
        self.cache = CacheConfigManager(interactive=interactive, verbosity=verbosity)

    def complete(self, *args, **kwargs):
        self.database.complete(*args, **kwargs)
        self.cache.complete(*args, **kwargs)

__all__ = [ 'DbConfigManager', 'CacheConfigManager', 'FilesystemConfigManager']
