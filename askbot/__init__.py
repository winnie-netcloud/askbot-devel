"""
:synopsis: the Django Q&A forum application

Functions in the askbot module perform various
basic actions on behalf of the forum application
"""
import os
import platform

VERSION = (0, 10, 2)

default_app_config = 'askbot.apps.AskbotConfig'

#keys are module names used by python imports,
#values - the package qualifier to use for pip
REQUIREMENTS = {
    'appconf': 'django-appconf',
    'akismet': 'akismet==1.0.1',
    'avatar': 'django-avatar==3.1.0',
    'bs4': 'beautifulsoup4<=4.7.1',
    'coffin': 'Coffin>=2.0',
    'compressor': 'django-compressor>=2.0,<=2.2',
    'django': 'django>=1.9,<1.12',
    'django_countries': 'django-countries>=3.3',
    'django_jinja': 'django-jinja>=2.0',
    'djcelery': 'django-celery>=3.0.11,<=3.3.0',
    'celery': 'celery==3.1.18',
    'djkombu': 'django-kombu==0.9.4',
    'followit': 'django-followit>=0.3.0',
    'html5lib': 'html5lib==0.9999999',
    'jinja2': 'Jinja2>=2.8',
    'jsonfield': 'jsonfield>=2.0.0',
    'jwt': 'pyjwt<=1.7.1',
    'keyedcache': 'django-keyedcache3>=1.5.1',
    'markdown2': 'markdown2<=2.3.8',
    'mock': 'mock==3.0.5',
    'oauth2': 'oauth2<=1.9.0.post1',
    'openid': 'python-openid<=2.2.5',
    'picklefield': 'django-picklefield==1.0.0',
    'pystache': 'pystache==0.3.1',
    'pytz': 'pytz<=2019.1',
    'captcha': 'django-recaptcha>=1.0.3,<=1.3.0',
    'cas': 'python-cas==1.4.0',
    'responses': 'responses>=0.9.0',
    'requirements': 'requirements-parser==0.2.0',
    'robots': 'django-robots==1.1',
    'robots': 'django-robots==3.0',
    'regex': 'regex',
    'sanction': 'sanction==0.3.1',
    'simplejson': 'simplejson<=3.16.1',
    'six': 'six==1.10.0',
    'tinymce': 'django-tinymce>=2.8.0',
    'unidecode': 'unidecode<=1.0.23',
    #'stopforumspam': 'stopforumspam'
}

#necessary for interoperability of django and coffin
try:
    from askbot import patches
    from askbot.deployment.assertions import assert_package_compatibility
    assert_package_compatibility()
    patches.patch_django()
    patches.patch_coffin()  # must go after django
except ImportError:
    pass


def get_install_directory():
    """returns path to directory
    where code of the askbot django application
    is installed
    """
    return os.path.dirname(__file__)


def get_path_to(relative_path):
    """returns absolute path to a file
    relative to ``askbot`` directory
    ``relative_path`` must use only forward slashes
    and must not start with a slash
    """
    root_dir = get_install_directory()
    assert(relative_path[0] != 0)
    path_bits = relative_path.split('/')
    return os.path.join(root_dir, *path_bits)


def get_version():
    """returns version of the askbot app
    this version is meaningful for pypi only
    """
    return '.'.join([str(subversion) for subversion in VERSION])


def get_database_engine_name():
    """returns name of the database engine,
    independently of the version of django
    - for django >=1.2 looks into ``settings.DATABASES['default']``,
    (i.e. assumes that askbot uses database named 'default')
    , and for django 1.1 and below returns settings.DATABASE_ENGINE
    """
    import django
    from django.conf import settings as django_settings
    major_version = django.VERSION[0]
    minor_version = django.VERSION[1]
    if major_version == 1:
        if minor_version > 1:
            return django_settings.DATABASES['default']['ENGINE']
        else:
            return django_settings.DATABASE_ENGINE


def get_lang_mode():
    from django.conf import settings as django_settings
    try:
        return django_settings.ASKBOT_LANGUAGE_MODE
        return getattr(django_settings, 'ASKBOT_LANGUAGE_MODE', 'single-lang')
    except:
        import traceback
        traceback.print_stack()
        import sys
        sys.exit()


def is_multilingual():
    return get_lang_mode() != 'single-lang'
