from askbot.utils import console
from askbot.deployment.parameters.base import ConfigField, ConfigManager

class CacheConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
        the cache Askbot will use."""
    def __init__(self, interactive=True):
        super(CacheConfigManager, self).__init__(interactive)
        self.register('cache_engine', CacheEngine)
        self.register('cache_nodes', CacheNodes)
        self.register('cache_db', CacheDb)
        self.register('cache_password', CachePass)

    def _order(self, keys):
        full_set = [ 'cache_engine', 'cache_nodes', 'cache_db',
                     'cache_password' ]
        return [ item for item in full_set if item in keys ]

    def _remember(self, name, value):
        super(CacheConfigManager, self)._remember(name, value)
        if name == 'cache_engine':
            if value == '3':
                self._catalog['cache_nodes'].defaultOk = True
            elif value == '2':
                self._catalog['cache_db'].defaultOk = False
                self._catalog['cache_password'].defaultOk = False

class CacheEngine(ConfigField):
    defaultOk = False

    cache_engines = [
        ('1', 'django.core.cache.backends.memcached.MemcachedCache', 'Memcached'),
        ('2', 'redis_cache.RedisCache', 'Redis'),
        ('3', 'django.core.cache.backends.locmem.LocMemCache', 'LocMem'),
    ]

    @classmethod
    def acceptable(cls, value):
        return value in [ e[0] for e in cls.cache_engines ]

    @classmethod
    def ask_user(cls, current_value):
        user_prompt = 'Please select cache engine:\n'
        for index, name in [ (e[0], e[2]) for e in cls.cache_engines ]:
            user_prompt += f'{index} - for {name}; '
        return console.choice_dialog(
            user_prompt,
            choices=[ e[0] for e in cls.cache_engines ]
        )

class CacheNodes(ConfigField):
    defaultOk = False
    user_prompt = 'Please provide exactly one cache node in the form '\
                  '<ip>:<port>. (In order to provide multiple cache nodes, '\
                  'please use the --cache-node option multiple times when '\
                  'invoking askbot-setup.)'

    @classmethod
    def ask_user(cls, current):
        value = super(CacheNodes, cls).ask_user(current)
        return [ value ]

class CacheDb(ConfigField):
    defaultOk   = True
    user_prompt = 'Please enter the cache database name to use'

class CachePass(ConfigField):
    defaultOk   = True
    user_prompt = 'Please enter the shared secret for accessing the cache'
