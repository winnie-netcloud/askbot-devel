from askbot.utils import console
from askbot.deployment.parameters.base import ConfigField, ConfigManager

class CacheConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
        the cache Askbot will use."""
    def __init__(self, interactive=True, verbosity=1):
        super(CacheConfigManager, self).__init__(interactive=interactive, verbosity=verbosity)
        db = ConfigField(
            defaultOk = True,
            user_prompt = 'Please enter the cache database name to use',
        )
        password = ConfigField(
            defaultOk = True,
            user_prompt = 'Please enter the shared secret for accessing the cache',
        )
        self.register('cache_engine', CacheEngine())
        self.register('cache_nodes', CacheNodes())
        self.register('cache_db', db)
        self.register('cache_password', password)

    def _order(self, keys):
        full_set = [ 'cache_engine', 'cache_nodes', 'cache_db',
                     'cache_password' ]
        return [ item for item in full_set if item in keys ]

    def _remember(self, name, value):
        if name == 'cache_engine':
            value = int(value)
        super(CacheConfigManager, self)._remember(name, value)
        if name == 'cache_engine':
            if value == 3:
                self._catalog['cache_nodes'].defaultOk = True
            elif value == 2:
                self._catalog['cache_db'].defaultOk = False
                self._catalog['cache_password'].defaultOk = False

class CacheEngine(ConfigField):
    defaultOk = False

    cache_engines = [
        (1, 'django.core.cache.backends.memcached.MemcachedCache', 'Memcached'),
        (2, 'redis_cache.RedisCache', 'Redis'),
        (3, 'django.core.cache.backends.locmem.LocMemCache', 'LocMem'),
    ]

    def acceptable(self, value):
        return value in [e[0] for e in self.cache_engines]

    def ask_user(self, current_value, depth=0):
        user_prompt = 'Please select cache engine:\n'
        for index, name in [(e[0], e[2]) for e in self.cache_engines]:
            user_prompt += f'{index} - for {name}; '
        user_input = console.choice_dialog(
            user_prompt,
            choices=[str(e[0]) for e in self.cache_engines]
        )

        try:
            user_input = int(user_input)
        except Exception as e:
            if depth > 7:
                raise e
            self.print(e)
            user_input = self.ask_user(user_input, depth + 1)

        return user_input

class CacheNodes(ConfigField):
    defaultOk = False
    user_prompt = 'Please provide exactly one cache node in the form '\
                  '<ip>:<port>. (In order to provide multiple cache nodes, '\
                  'please use the --cache-node option multiple times when '\
                  'invoking askbot-setup.)'

    def ask_user(self, current):
        value = super(CacheNodes, self).ask_user(current)
        return [ value ]
