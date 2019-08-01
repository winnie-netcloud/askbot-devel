from askbot.utils import console

class ObjectWithOutput(object):
    def __init__(self, verbosity=1, force=False):
        self.verbosity = verbosity
        self.force = force

    def print(self, message, verbosity=1):
        if verbosity <= self.verbosity:
            print(message)

class ConfigManager(ObjectWithOutput):
    """ConfigManagers are used to ensure the installation can proceed.

    Each ConfigManager looks at some installation parameters, usually
    grouped by the aspect of Askbot they configure. For instance there is
    a ConfigManager for the database backend and another one for the cache
    backend. The task of a ConfigManager is to ensure that the combination
    of install parameters it analyses is sensible for an Askbot installation.

    The installer calls a ConfigManager's complete() method and passes it
    its entire collection of installation parameters, a dictionary.
    A ConfigManager only looks at those installation parameters which have
    been register()-ed with the ConfigManager.

    For each installation parameter there is registered class, derived from
    ConfigField, which can determine if a parameter's value is acceptable and
    ask the user to provide a value for the parameter.

    The ConfigManager knows in which order to process its registered
    installation parameters and contains all the logic determining if a user
    should be asked for a(nother) value. It also remembers all values it
    accepts and in the process may also modify the behaviour of the
    ConfigField classes, to fit with the previously accepted values. For
    instance, usually the DbConfigManager insists on credentials for accessing
    the database, but if a user selects SQLite as database backend, the
    DbConfigManager will *NOT* insist on credentials for accessing the
    database, because SQLite does not need authentication.
    """
    strings = {
        'eNoValue': 'You must specify a value for "{name}"!',
    }

    def __init__(self, interactive=True, verbosity=1, force=False):
        self._verbosity = verbosity
        self._interactive = interactive
        self._force = force
        self._catalog = dict()
        self.keys = set()
        self._managed_config = dict()
        super(ConfigManager, self).__init__(verbosity=verbosity)
        self.interactive = interactive

    @property
    def interactive(self):
        return self._interactive

    @interactive.setter
    def interactive(self, interactive):
        self._interactive = interactive
        for name, handler in self._catalog.items():
            if hasattr(handler,'interactive'):
                handler.interactive = interactive

    @property
    def force(self):
        return self._force

    @force.setter
    def force(self, force):
        self._force = force
        for name, handler in self._catalog.items():
            if hasattr(handler,'force'):
                handler.force = force

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        self._verbosity = verbosity
        for name, handler in self._catalog.items():
            if hasattr(handler, 'verbosity'):
                handler.verbosity = verbosity

    def register(self, name, handler):
        """Add the ability to handle a specific install parameter.
        Parameters:
        - name: the install parameter to handle
        - handler: the class to handle the parameter"""
        self._catalog[name] = handler
        self.keys.update({name})
        handler.verbosity = self.verbosity

    def configField(self, name):
        if name not in self.keys:
            raise KeyError(f'{self.__class__.__name__}: No handler for {name} registered.')
        return self._catalog[name]

    def _remember(self, name, value):
        """With this method, instances remember the accepted piece of
        information for a given name. Making this a method allows derived
        classes to perform additional work on accepting a piece of
        information."""
        self._managed_config.setdefault(name, value)

    def _complete(self, name, current_value):
        """The generic procedure to ensure an installation parameter is
        sensible and bug the user until a sensible value is provided.

        If this is not an interactive installation, a not acceptable() value
        raises a ValueError"""
        if name not in self.keys:
            raise KeyError

        configField   = self._catalog[name]

        while not configField.acceptable(current_value):
            self.print(f'Current value {current_value} not acceptable!', 2)
            if not self.interactive:
                raise ValueError(self.strings['eNoValue'].format(name=name))
            current_value = configField.ask_user(current_value)

        # remember the piece of information we just determined acceptable()
        self._remember(name, current_value)
        return current_value

    def _order(self, keys):
        """Gives implementations control over the order in which they process
        installation parameters."""
        return keys

    def complete(self, collection):
        """Main method of this :class:ConfigManager.
        Consumers use this method to ensure their data in :dict:collection is
        sensible for installing Askbot.
        """
        contribution = dict()
        keys = self.keys & set(collection.keys()) # scope to this instance
        for k in self._order(keys):
            v = self._complete(k, collection[k])
            contribution.setdefault(k, v)
        collection.update(contribution)

class ConfigField(ObjectWithOutput):
    defaultOk   = True
    default     = None
    user_prompt = 'Please enter something'

    def __init__(self, defaultOk=None, default=None, user_prompt=None, verbosity=1):
        super(ConfigField, self).__init__(verbosity=verbosity)
        self.defaultOk   = self.__class__.defaultOk   if defaultOk is None   else defaultOk
        self.default     = self.__class__.default     if default is None     else default
        self.user_prompt = self.__class__.user_prompt if user_prompt is None else user_prompt

    def acceptable(self, value):
        """High level sanity check for a specific value. This method is called
        for an installation parameter with the value provided by the user, or
        the default value, if the user didn't provide any value. There must be
        a boolean response, if the installation can proceed with :var:value as
        the setting for this ConfigField."""
        #self.print(f'This is {cls.__name__}.acceptable({value}) {cls.defaultOk}', 2)
        if value is None and self.default is None or value == self.default:
            return self.defaultOk
        return True

    def ask_user(self, current):
        """Prompt the user to provide a value for this installation
        parameter."""
        user_prompt = self.user_prompt
        if self.defaultOk is True:
            user_prompt += ' (Just press ENTER, to use the current '\
                        + f'value "{current}")'
        return console.simple_dialog(user_prompt)
