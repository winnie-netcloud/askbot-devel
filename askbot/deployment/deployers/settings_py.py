"""Class that deploys the settings.py file where it belongs"""
import os
from askbot.deployment.deployers.file_deployer import FileDeployer
from askbot.deployment.deployers.settings_py_admins_snippet import SettingsPyAdminsSnippet
from askbot.deployment.deployers.settings_py_databases_snippet import SettingsPyDatabasesSnippet
from askbot.deployment.deployers.settings_py_email_snippet import SettingsPyEmailSnippet

class SettingsPy(FileDeployer): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/settings_py.jinja2'

    def get_file_path(self):
        """Returns deployment path to the settings.py file"""
        return os.path.join(self.params['proj_dir'], 'settings.py')

    def get_template_parameters(self):
        """Returns parameters for the settings.py template"""
        return {
            'admins_settings': SettingsPyAdminsSnippet(self.params).render(),
            'caching_settings': self.get_caching_settings(),
            'databases_settings': SettingsPyDatabasesSnippet(self.params).render(),
            'allowed_host': self.params['domain_name'] or '*',
            'email_settings': SettingsPyEmailSnippet(self.params).render(),
            'language_settings': self.get_language_settings(),
            'logging_settings': self.get_logging_settings(),
        }

    def get_logging_settings(self):
        """
        log_file_path
        logging_settings
        """
        return ''

    def get_caching_settings(self):
        return ''

    def get_language_settings(self):
        return ''

    def get_email_settings(self):
        return ''
