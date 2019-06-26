"""module for monkey patching that is
necessary for interoperability of different
versions of various components used in askbot
"""
import django
from askbot.patches import django_patches
from askbot.deployment import package_utils

def patch_django():
    (major, minor, micro) = package_utils.get_django_version()

    if major == 1 and minor > 4:
        # This shouldn't be required with django < 1.4.x
        # And not after kee_lazy lands in django.utils.functional
        try:
            from django.utils.functional import keep_lazy
        except ImportError:
            django_patches.fix_lazy_double_escape()

    if major == 1 and minor > 5:
        django_patches.add_hashcompat()
        django_patches.add_simplejson()

    if major == 1 and minor == 8:
        django_patches.patch_django_template()
