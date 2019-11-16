from askbot.deployment.base import ConfigManager

class CacheConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
        the cache Askbot will use."""

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

    def reset(self):
        super(CacheConfigManager, self).reset()
        self._catalog['cache_nodes'].defaultOk = False
        self._catalog['cache_db'].defaultOk = True
        self._catalog['cache_password'].defaultOk = True

class DbConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
    the database Askbot will use."""

    def reset(self):
        super(DbConfigManager, self).reset()
        self._catalog['database_user'].defaultOk = False
        self._catalog['database_password'].defaultOk = False

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
        Wrap the default _complete() and implement a special handling of
        `database_engine`. While the user selects database engines by index,
        i.e. 1,2,3 or 4, at the time of this writing, the installer and Askbot
        use Django module names (I think that's what it is). Therefore we
        perform a lookup after the user made their final choice and return
        the name, rather than the index.
        """
        ret = super(DbConfigManager, self)._complete(name, current_value)
        if name == 'database_engine':
            return [ e[1] for e in
                     self.configField(name).database_engines
                     if e[0] == ret ].pop()
        return ret
