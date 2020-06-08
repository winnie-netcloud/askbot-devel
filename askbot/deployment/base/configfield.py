from .objectwithoutput import ObjectWithOutput
from askbot.utils import console

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
            user_prompt += f'\nTo use the "{current}" value anyway - prest ENTER'
        return console.simple_dialog(user_prompt)
