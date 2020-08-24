from .file_deployer import FileDeployer
from .. import const

class SettingsPyEmailSnippet(FileDeployer): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/settings_py_email_snippet.jinja2'
