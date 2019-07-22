from askbot.utils import console

class ConfigManager(object):
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

    def __init__(self, interactive=True):
        self.interactive = interactive
        self._catalog = dict()
        self.keys = set()
        self._managed_config = dict()

    def register(self, name, handler):
        """Add the ability to handle a specific install parameter.
        Parameters:
        - name: the install parameter to handle
        - handler: the class to handle the parameter"""
        self._catalog[name] = handler
        self.keys.update({name})

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
            raise Exception

        configField   = self._catalog[name]

        while not configField.acceptable(current_value):
            print(f'Current value {current_value} not acceptable!')
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

class ConfigField(object):
    defaultOk   = True
    default     = None
    user_prompt = 'Please enter something'

    @classmethod
    def acceptable(cls, value):
        """High level sanity check for a specific value. This method is called
        for an installation parameter with the value provided by the user, or
        the default value, if the user didn't provide any value. There must be
        a boolean response, if the installation can proceed with :var:value as
        the setting for this ConfigField."""
        if value is None and cls.default is None \
        or value == cls.default:
            return cls.defaultOk
        return True

    @classmethod
    def ask_user(cls, current):
        """Prompt the user to provide a value for this installation
        parameter."""
        user_prompt = cls.user_prompt
        if cls.defaultOk is True:
            user_prompt += ' (Just press ENTER, to use the current '\
                        + f'value "{current}")'
        return console.simple_dialog(user_prompt)
