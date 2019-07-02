"""utilities that determine versions of packages
that are part of askbot

versions of all packages are normalized to three-tuples
of integers (missing zeroes added)
"""
import django

def get_django_version():
    """returns three-tuple for the version
    of django"""
    return django.VERSION[:3]
