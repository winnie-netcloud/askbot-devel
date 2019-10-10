from importlib.util import find_spec
import os.path
import re
import tempfile
from askbot.utils import console
from askbot.deployment import messages
from askbot.deployment.parameters.base import ConfigField
from askbot.deployment.path_utils import has_existing_django_project
from askbot.deployment.base.exceptions import *

DEBUG_VERBOSITY = 2

class LogfileName(ConfigField):
    defaultOk = True
    user_prompt = "Please enter the name for Askbot's logfile."

class BaseDirName(ConfigField):
    """Base class for directory parameters.
    This extends ConfigField with a set of tests for directories and/or the
    filesystem layout, to be used in ConfigField classes for directories."""

    def _check_django_name_restrictions(self, directory):
        dir_name = os.path.basename(directory)
        if re.match(r'[_a-zA-Z][\w-]*$', dir_name) is None:
            raise RestrictionsError("""\nDirectory %s is not acceptable for a Django
            project. Please use lower case characters, numbers and underscore.
            The first character cannot be a number.\n""" % os.path.basename(directory))

    def _check_module_name_collision(self, directory):
        dir_name = os.path.basename(directory)
        spec = find_spec(dir_name,os.path.dirname(directory))
        if spec is not None:
            raise NameCollisionError(messages.format_msg_bad_dir_name(directory))

    def _check_is_file(self, directory):
        directory = os.path.normpath(directory)
        directory = os.path.abspath(directory)
        if os.path.isfile(directory):
            raise IsFileError(messages.CANT_INSTALL_INTO_FILE % {'path': directory})

    def _check_can_create_write_path(self, directory):
        self.print(f'_check_can_create_write_path({directory})', DEBUG_VERBOSITY)
        if not os.path.exists(directory):
            self._check_can_create_write_path(os.path.dirname(directory))
        else:
            try:
                with tempfile.NamedTemporaryFile(dir=directory) as f:
                    f.write(b"Hello World!")
            except:
                raise CreateWriteError(messages.format_msg_dir_not_writable(directory))

    def _check_nested_django_projects(self, directory):
        if has_existing_django_project(directory):
            raise NestedProjectsError(messages.format_msg_dir_unclean_django(directory))
        if len(os.path.split(directory)[1].strip()) > 0:
            self._check_nested_django_projects(os.path.dirname(directory))

    def _check_forced_overwrite(self, directory):
        if has_existing_django_project(directory) and self.force is False:
            raise OverwriteError(messages.CANNOT_OVERWRITE_DJANGO_PROJECT % \
                        {'directory': directory})

class ProjectDirName(BaseDirName):
    defaultOk = False

    def acceptable(self, value):
        self.print(f'Got "{value}" of type "{type(value)}".', DEBUG_VERBOSITY)
        try:
            self._check_django_name_restrictions(value)
            self._check_module_name_collision(value)
            path_to_value = os.path.abspath(value)
            self._check_is_file(path_to_value)
            self._check_can_create_write_path(path_to_value)
            self._check_nested_django_projects(os.path.dirname(path_to_value))
            self._check_forced_overwrite(path_to_value)
        except DirNameError as error:
            self.print(f'{error.__class__.__name__}:', DEBUG_VERBOSITY)
            self.print(error, 1)
            return False
        return True

    def ask_user(self, current_value):
        self.user_prompt = messages.WHERE_TO_DEPLOY
        user_input = os.path.abspath(
            super(ProjectDirName, self).ask_user(current_value))

        should_create_new = console.choice_dialog(
            messages.format_msg_create(user_input),
            choices=['yes', 'no'],
            invalid_phrase=messages.INVALID_INPUT
        )

        return None if should_create_new == 'no' else user_input

class AppDirName(BaseDirName):
    defaultOk = True,
    default = None,
    user_prompt = "Please enter a Django App name for this Askbot deployment."

    def acceptable(self, value):
        self.print(f'Got "{value}" of type "{type(value)}".', DEBUG_VERBOSITY)
        try:
            self._check_django_name_restrictions(value)
            self._check_module_name_collision(value)
            if os.path.sep in value:
                raise DirNameError(f'The App name must be a single valid name without any path information, not {value}.')
            path_to_value = os.path.abspath(value)
            self._check_is_file(path_to_value)
        except DirNameError as error:
            self.print(f'{error.__class__.__name__}:', DEBUG_VERBOSITY)
            self.print(error, 1)
            return False
        return True
