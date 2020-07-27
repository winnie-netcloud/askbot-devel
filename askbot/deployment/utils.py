"""Utility functions for the deployment scripts"""
import os
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
