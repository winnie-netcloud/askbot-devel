"""Validator for the directory parameters and
the setup procedure parameters"""
import os.path
from askbot.deployment import const
from askbot.deployment.validators.proj_dir_validator import ProjDirValidator
from askbot.deployment.validators.root_dir_validator import RootDirValidator

class SetupParamsValidator:
    #pylint: disable=missing-class-docstring

    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params


    def get_params(self):
        """Returns setup parameters"""
        root_dir = RootDirValidator(self.console, self.parser).get_value()
        return {
            'force': self.options.force,
            'interactive': self.options.interactive,
            'root_dir': root_dir,
            'proj_dir': ProjDirValidator(self.console, self.parser, root_dir).get_value(),
            'media_root': self.get_valid_media_root(root_dir)
        }


    def get_valid_media_root(self, root_dir):
        """Returns valid value for the `MEDIA_ROOT` setting."""
        raw_value = self.options.media_root
        # if missing - return default
        if not raw_value:
            return os.path.join(root_dir, const.DEFAULT_MEDIA_ROOT_SUBDIR)

        return os.path.abspath(raw_value)
