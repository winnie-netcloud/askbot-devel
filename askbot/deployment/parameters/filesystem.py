from askbot.utils import console
from askbot.deployment.parameters.base import ConfigField, ConfigManager
from askbot.deployment import messages
from askbot.deployment.path_utils import has_existing_django_project

import os.path
import re
from importlib.machinery import PathFinder
import tempfile

class FilesystemConfigManager(ConfigManager):
    """A config manager for validating setup parameters pertaining to
            files and directories Askbot will use."""

    def __init__(self, interactive=True, verbosity=1):
        super(FilesystemConfigManager, self).__init__(interactive=interactive, verbosity=verbosity)
        logfile = ConfigField(
            defaultOk=True,
            user_prompt="Please enter the name for Askbot's logfile.",
        )
        self.register('dir_name', DirName())
        self.register('logfile_name', logfile)


    def _order(self, keys):
        full_set = ['dir_name', 'logfile_name']
        return [item for item in full_set if item in keys]

class DirNameError(Exception):
    """There is something about the chosen install dir we don't like."""

class DirName(ConfigField):
    defaultOk = False

    def _check_django_name_restrictions(self, directory):
        dir_name = os.path.basename(directory)
        if not re.match(r'[_a-zA-Z][\w-]*$', dir_name):
            raise DirNameError("""\nDirectory %s is not acceptable for a Django
            project. Please use lower case characters, numbers and underscore.
            The first character cannot be a number.\n""" % os.path.basename(directory))

    def _check_module_name_collision(self, directory):
        dir_name = os.path.basename(directory)
        finder = PathFinder.find_spec(dir_name,os.path.dirname(directory))
        if finder is not None:
            raise DirNameError(messages.format_msg_bad_dir_name(directory))

    def _check_is_file(self, directory):
        directory = os.path.normpath(directory)
        directory = os.path.abspath(directory)
        if os.path.isfile(directory):
            raise DirNameError(messages.CANT_INSTALL_INTO_FILE % {'path': directory})

    def _check_can_create_write_path(self, directory):
        if not os.path.exists(directory):
            self._check_can_create_write_path(os.path.dirname(directory))
        else:
            try:
                with tempfile.NamedTemporaryFile(dir=directory) as f:
                    f.write("Hello World!")
            except:
                raise DirNameError(messages.format_msg_dir_not_writable(directory))

    def _check_nested_django_projects(self, directory):
        if has_existing_django_project(directory):
            raise DirNameError(messages.format_msg_dir_unclean_django(directory))
        if len(os.path.split(directory)[1].strip()) > 0:
            self._check_nested_django_projects(os.path.dirname(directory))

    def _check_forced_overwrite(self, directory):
        if has_existing_django_project(directory) and self.force is False:
            raise DirNameError(messages.CANNOT_OVERWRITE_DJANGO_PROJECT % \
                        {'directory': directory})

    def acceptable(self, value):
        try:
            self._check_django_name_restrictions(value)
            self._check_module_name_collision(value)
            self._check_is_file(value)
            self._check_can_create_write_path(value)
            self._check_nested_django_projects(os.path.dirname(value))
            self._check_forced_overwrite(value)
        except DirNameError as error:
            self.print(error)
            return False
        return True
