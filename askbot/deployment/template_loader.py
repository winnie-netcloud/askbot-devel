import os
from copy import deepcopy
from jinja2 import Template as Jinja2Template


class DeploymentTemplate(object):
    def __init__(self, tmpl_name, tmpl_dir='setup_templates', context={}):
        self.context = context
        self.tmpl_name = tmpl_name
        self.tmpl_dir = tmpl_dir
        source_dir = os.path.dirname(os.path.dirname(__file__))
        self.tmpl_path = os.path.join(source_dir,self.tmpl_dir,self.tmpl_name)

    def render(self, param_context={}):
        this_context = deepcopy(self.context)
        this_context.update(param_context)
        with open(self.tmpl_path, 'r') as template_file:
            return Jinja2Template(template_file.read()).render(this_context)
