from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.template.backends.base import BaseEngine
from django.template.context import BaseContext
from askbot.utils.loading import load_function
from django_jinja.base import dict_from_context

try:
    import django.template.backends.jinja2 # exists only in Django1.8+
    from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
except ImportError:
    pass # b/c we are not using any of this atm

try:
    from django.template.backends.jinja2 import Origin

except ImportError:
    pass # b/c we only use it with Django 1.11 and then it does exist


CONTEXT_PROCESSORS = list()

class Template(object):

    # backend parameter was added with Django 1.11
    def __init__(self, template, backend=None):
        self.template = template
        if backend is not None:
            self.backend = backend
            self.origin = Origin(
                name=template.filename, template_name=template.name,
            )

    # I doubt we want the following classmethods with the Template.
    @classmethod
    def load_context_processors(cls, paths):
        processors = list()
        for path in paths:
            processors.append(load_function(path))
        return processors

    @classmethod
    def get_engine_config(cls):
        t_settings = django_settings.TEMPLATES
        for config in t_settings:
            backend = 'askbot.skins.template_backends.AskbotSkinTemplates'
            if config['BACKEND'] == backend:
                return config
        raise ImproperlyConfigured('template backend %s is required', backend)


    @classmethod
    def get_extra_context_processor_paths(cls):
        conf = cls.get_engine_config()
        if 'OPTIONS' in conf and 'context_processors' in conf['OPTIONS']:
            return conf['OPTIONS']['context_processors']
        return tuple()

    @classmethod
    def get_context_processors(cls):
        global CONTEXT_PROCESSORS
        if len(CONTEXT_PROCESSORS) == 0:
            context_processor_paths = (
                'askbot.context.application_settings',
                'askbot.user_messages.context_processors.user_messages',#must be before auth
                'django.contrib.auth.context_processors.auth', #this is required for the admin app
                'askbot.deps.group_messaging.context.group_messaging_context',
            )
            extra_paths = [] # cls.get_extra_context_processor_paths() # Disabled for now
            for path in extra_paths:
                if path not in context_processor_paths:
                    context_processor_paths += (path,)

            CONTEXT_PROCESSORS = cls.load_context_processors(context_processor_paths)

        return CONTEXT_PROCESSORS

    @classmethod
    def update_context(cls, context, request):
        for processor in cls.get_context_processors():
            context.update(processor(request))
        return context

    def render(self, context=None, request=None):
        if context is None:
            context = {}
        elif isinstance(context,BaseContext):
            context = dict_from_context(context)

        if request is not None:
            context['request'] = request
            context['csrf_input'] = csrf_input_lazy(request)
            context['csrf_token'] = csrf_token_lazy(request)
            context = self.update_context(context, request)

        return self.template.render(context)

django.template.backends.jinja2.Template = Template
