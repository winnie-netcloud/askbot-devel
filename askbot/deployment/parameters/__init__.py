from askbot.deployment.parameters.base import ConfigManager
from askbot.deployment.parameters.cache import CacheConfigManager
from askbot.deployment.parameters.database import DbConfigManager
from askbot.deployment.parameters.filesystem import FilesystemConfigManager

# one could make a case for not deriving ConfigManagerCollection from
# ConfigManager because the collection serves a different purpose than the
# individual manager, but they are still quite similar
class ConfigManagerCollection(ConfigManager):
    """
    This is the main config manager that will be used by the Askbot installer.
    It is a hard coded ordered collection of all config managers the installer
    shall use.
    """
    def __init__(self, interactive=False, verbosity=0):
        super(ConfigManagerCollection, self).__init__(interactive=interactive, verbosity=verbosity)
        self.register('database', DbConfigManager(interactive=interactive, verbosity=verbosity))
        self.register('cache', CacheConfigManager(interactive=interactive, verbosity=verbosity))
        self.register('filesystem', FilesystemConfigManager(interactive=interactive, verbosity=verbosity))

    def _order(self, keys):
        full_set = ['filesystem', 'database', 'cache']
        return [item for item in full_set if item in keys]

    def configManager(self, name):
        return super(ConfigManagerCollection, self).configField(name)

    def complete(self, *args, **kwargs):
        for manager in self._order(self.keys):
            handler = self.configManager(manager)
            handler.complete(*args, **kwargs)

    # these should never be called. we keep these, just in case
    def _remember(self, name, value):
        raise NotImplementedError(f'Not implemented in {self.__class__.__name__}.')

    def _complete(self, name, value):
        raise NotImplementedError(f'Not implemented in {self.__class__.__name__}.')

__all__ = [ 'DbConfigManager', 'CacheConfigManager', 'FilesystemConfigManager', 'ConfigManagerCollection']
