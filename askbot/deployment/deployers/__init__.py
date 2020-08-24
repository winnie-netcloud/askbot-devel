"""Module with helpers for creating of the deployable components"""
import os
from askbot.deployment.exceptions import DeploymentError
from .manage_py import ManagePy
from .settings_py import SettingsPy
from .urls_py import UrlsPy

def makedir(path, force):
    """Create a directory path.
    If path exists, and force is False, raise an exception.
    Otherwise force-create the directory/directories.
    Equivalent of mkdir -p
    """
    if os.path.exists(path) and not force:
        raise DeploymentError(f'Directory {path} exists')

    if force:
        # to be on the safe side put this in a branch
        os.makedirs(path, exists_ok=True)
    os.makedirs(path)
