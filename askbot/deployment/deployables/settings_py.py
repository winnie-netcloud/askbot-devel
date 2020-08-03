"""Class that deploys the settings.py file where it belongs"""
import os
from askbot.deployment.deployables.deployable_file import DeployableFile

class SettingsPy(DeployableFile): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/settings.py.jinja2'

    def get_file_path(self):
        """Returns deployment path to the settings.py file"""
        return os.path.join(self.params['proj_dir'], 'settings.py')

    def get_params(self):
        """Returns parameters for the settings.py template"""
        return {
            'admins_settings': self.get_admins_settings(),
            'caching_settings': self.get_caching_settings(),
            'database_settings': self.get_database_settings(),
            'domain_name': self.params.domain_name,
            'email_settings': self.get_email_settings(),
            'language_settings': self.get_language_settings(),
            'logging_settings': self.get_logging_settings(),
        }

    def get_logging_settings(self):
        """
        log_file_path
        logging_settings
        """
        pass
