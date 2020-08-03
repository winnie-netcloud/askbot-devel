from .deployable_file import DeployableFile

class UrlsPy(DeployableFile):
    template_path = 'deployment/templates/urls.py'

    def get_file_path(self):
        """Returns the target path of the urls.py file"""
        return os.path.join(self.params['proj_dir'], 'urls.py')
