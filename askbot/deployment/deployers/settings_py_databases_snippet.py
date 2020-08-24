from .file_deployer import FileDeployer
from .. import const

class SettingsPyDatabasesSnippet(FileDeployer): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/settings_py_databases_snippet.jinja2'

    def render(self):
        if self.params['database_settings']:
            return self.params['database_settings']
        return super(SettingsPyDatabasesSnippet, self).render()
