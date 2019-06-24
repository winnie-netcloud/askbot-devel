"""Utilities for loading modules"""
import importlib

from django.conf import settings as django_settings


def load_module(mod_path):
    """an equivalent of:
    from some.where import module
    import module
    """
    return importlib.import_module(mod_path)


def load_plugin(setting_name, default_path):
    """loads custom module/class/function
    provided with setting with the fallback
    to the default module/class/function"""
    python_path = getattr(
                        django_settings,
                        setting_name,
                        default_path
                    )
    return load_module(python_path)


def module_exists(mod_path):
    try:
        load_module(mod_path)
    except ImportError:
        return False
    return True
