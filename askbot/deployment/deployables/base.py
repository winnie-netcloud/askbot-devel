class AskbotDeploymentError(Exception):
    """Use this when something goes wrong while deploying Askbot"""


class ObjectWithOutput(object):
    def __init__(self, verbosity=1, force=False):
        self._verbosity = verbosity
        self._force = force

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        self._verbosity = value

    def print(self, message, verbosity=1):
        if verbosity <= self.verbosity:
            print(message)
