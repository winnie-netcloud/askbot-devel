"""Utility functions for the deployment scripts"""
import os
import re
from django.core.exceptions import ValidationError
from askbot.utils.loading import load_module

def dir_clashes_with_python_module(path):
    """Returns a boolean"""
    try:
        mod = load_module(os.path.basename(path))
    except ModuleNotFoundError:
        return False
    else:
        if path not in mod.__path__:
            return True
    return False

class DomainNameValidator: # pylint: disable=too-few-public-methods
    """Django-style domain name validator"""
    @classmethod
    def __call__(cls, value):
        """Validates the domain name"""
        if not re.match(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', value):
            raise ValidationError('Invalid domain name')

class PortNumberValidator: # pylint: disable=too-few-public-methods
    """Django-style port number validator"""

    @classmethod
    def __call__(cls, value):
        """Validates the domain name"""
        if not re.match(r'^[1-9][0-9]*$', value):
            raise ValidationError('Invalid domain name')
