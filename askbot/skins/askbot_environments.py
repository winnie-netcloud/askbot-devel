# We copy and therefore duplicate a lot of code from other askbot.skins
# modules and rid ourselves of Coffin along the way.

# It appears that the orginal Askbot code keeps one jinja2.Environment for
# each skin and known language around and picks the correct environment(TM) on
# every call to from_string, get_template and load_template. I have not the
# faintest idea if that is a wise thing to do. For now we will simply mimic
# this behaviour.

from jinja2 import Environment
from jinja2 import loaders as jinja_loaders
from jinja2.exceptions import TemplateNotFound

from django.utils import translation
from django.conf import settings as django_settings
try:
    from django.template.loaders.base import Loader as BaseLoader
except ImportError:
    from django.template.loader import BaseLoader
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist

from askbot.conf import settings as askbot_settings
from askbot.skins import utils
from askbot.utils.translation import get_language

from askbot.skins.template_backends import Template as AskbotTemplate

class MultilingualEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        lang_code = kwargs.pop('language_code', None) # atm I don't see this ever becoming None
        super(MultilingualEnvironment, self).__init__(*args, **kwargs)
        # The following caused problems before. Reverting to call set_language() explicitly
        # if lang_code is not None:
        #     self.set_language(lang_code)

    def set_language(self, language_code):
        """hooks up translation objects from django to jinja2
        environment.
        note: not so sure about thread safety here
        """
        self._language_code = language_code
        trans = translation.trans_real.translation(language_code)
        self.install_gettext_translations(trans)

class SkinEnvironment(MultilingualEnvironment):
    """Jinja template environment
    that loads templates from askbot skins
    """

    # we use this over the SKINS variable in the original code
    siblings = dict()

    def __init__(self, *args, **kwargs):
        """save the skin path and initialize the
        Jinja2 Environment
        """
        skin_name = kwargs.pop('skin')
        lang_code = kwargs.get('language_code', None) # atm I don't see this ever becoming None

        this_sibling_key = [ skin_name ]
        if lang_code is not None:
            this_sibling_key.append(lang_code)

        key = self.build_sibling_key(this_sibling_key)
        self.__class__.siblings[key] = self

        super(SkinEnvironment, self).__init__(*args, **kwargs)

    def _get_loaders(self):
        """this method is not used
        over-ridden function _get_loaders that creates
        the loader for the skin templates
        """
        loaders = list()
        skin_dirs = list(utils.get_available_skins(selected = self.skin).values())
        template_dirs = [os.path.join(skin_dir, 'templates') for skin_dir in skin_dirs]
        loaders.append(jinja_loaders.FileSystemLoader(template_dirs))
        return loaders

    @classmethod
    def build_sibling_key(cls,parts):
        return "-".join(parts)

    @classmethod
    def get_skin(cls):
        """retreives the skin environment
        for a given request (request var is not used at this time)"""
        key = cls.build_sibling_key([
            askbot_settings.ASKBOT_DEFAULT_SKIN,
            get_language()
            ])
        try:
            return cls.siblings[key]
        except KeyError:
            msg_fmt = 'skin "%s" not found, check value of "ASKBOT_EXTRA_SKINS_DIR"'
            raise ImproperlyConfigured(msg_fmt % askbot_settings.ASKBOT_DEFAULT_SKIN)

    # the Jinja2 backend will use these
    # Making these classmethods seems sensible as these first pick an
    # environment instance and then have them do the work, but there is no
    # real merrit in it
    @classmethod
    def from_string(cls, template_code):
        env = cls.get_skin()
        return super(SkinEnvironment,env).from_string(template_code)

    @classmethod
    def get_template(cls, template_name, parent=None, globals=None):
        env = cls.get_skin()
        return super(SkinEnvironment,env).get_template(template_name, parent, globals)



# I wonder why we have the following. Keeping it around as it was in askbot.skins.loaders
JINJA2_TEMPLATES_HELP_TEXT = """JINJA2_TEMPLATES setting must be tuple
where the items can be either of the two forms:
* '<app name>' (string)
* tuple ('<app name>', ('<dir1>', '<dir2>', ...))
  of app name and a tuple of directories.

For example:

JINJA2_TEMPLATES = (
    'askbot',
    ('askbot_audit', (
            '/home/joe/templates',
            '/home/joe/base_templates',
        )
    )
)

Above, for the app 'askbot' the templates will be loaded
only from the app directory: askbot/templates

For the second app 'askbot_audit' templates will be loaded from
three locations in this order:
1) /home/joe/templates
2) /home/joe/templates/base_templates
3) and finally - from the app directory:
   askbot_audit/templates
"""
class AppDirectoryEnvironment(MultilingualEnvironment):
    """Jinja2 environment which loads the templates as the
    django's app directories loader

    Directory locations depend on the JINJA2_TEMPLATES setting.
    """

    def get_app_setup_info(self, setup_item):
        if isinstance(setup_item, str):
            return setup_item, list()
        elif isinstance(setup_item, (list, tuple)):
            dir_list = setup_item[1]
            if len(setup_item) != 2 or not isinstance(dir_list, (list, tuple)):
                raise ImproperlyConfigured(JINJA2_TEMPLATES_HELP_TEXT)
            return setup_item, dir_list


    def get_app_template_dir(self, app_name):
        """returns path to directory `templates` within the app directory
        """
        assert(app_name in django_settings.INSTALLED_APPS)
        from django.utils.importlib import import_module
        try:
            mod = import_module(app_name)
        except ImportError as e:
            raise ImproperlyConfigured('ImportError %s: %s' % (app_name, e.args[0]))
        return os.path.join(os.path.dirname(mod.__file__), 'templates')

    def get_all_template_dirs(self):
        template_dirs = list()
        for app_setup_item in django_settings.JINJA2_TEMPLATES:

            app_name, app_dirs = self.get_app_setup_info(app_setup_item)

            #append custom app dirs first
            template_dirs.extend(app_dirs)

            #after that append the default app templates dir
            app_template_dir = self.get_app_template_dir(app_name)
            template_dirs.append(app_template_dir)

        return template_dirs

    def _get_loaders(self):
        template_dirs = self.get_all_template_dirs()
        return [jinja_loaders.FileSystemLoader(template_dirs)]

# FIXME: APP_DIR_ENV does not exist. If this is ever called there will be an exception
class JinjaAppDirectoryLoader(BaseLoader):
    """Optional Jinja2 template loader to support apps using
    Jinja2 templates.

    The loader must be placed before the django template loaders
    in the `TEMPLATE_LOADERS` setting and two more conditions
    must be met:

    1) Loaders requires to explicitly mark apps as using Jinja2
    templates, via the setting `JINJA2_TEMPLATES` (formatted
    the same way as the `INSTALLED_APPS` setting).

    2) Templates must be within the app directory's templates/appname/
    directory. For example, template XYZ_home.html must be in directory
    XYZ_app/templates/XYZ_app/, where the root directory
    is the app module directory itself.
    """
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        bits = template_name.split(os.path.sep)

        #setting JINJA2_TEMPLATES is list of apps using Jinja2 templates
        jinja2_apps = getattr(django_settings, 'JINJA2_TEMPLATES', None)
        if jinja2_apps != None and bits[0] not in jinja2_apps:
            raise TemplateDoesNotExist

        try:
            env = APP_DIR_ENVS[get_language()]
            return env.get_template(template_name), template_name
        except TemplateNotFound:
            raise TemplateDoesNotExist
# /wondering

