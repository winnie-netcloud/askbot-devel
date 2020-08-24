from .file_deployer import FileDeployer

class SettingsPyAdminsSnippet(FileDeployer): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/settings_py_admins_snippet.jinja2'
