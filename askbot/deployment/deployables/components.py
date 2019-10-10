import os

from .objects import *
from askbot.deployment.base import DeployableComponent

"""The classes defined herein are what we want to do when we talk about
deploying askbot.

We write dictionaries, mostly named "contents" where we specify file/directory
names as keys and put the deployment object type as the value. The deployment
object type is basically how a particular filesystem object is to be created.
Nested dictionaries will result in a nested directory structure. 

Splitting the deployment into these three DeployableComponents is completely
arbitrary and seemed reasonable at the time. The intention was to keep
deployment details away from the main installer. However, the installer can
(and does) change the components before deploying them.
"""

class AskbotSite(DeployableComponent):
    default_name = 'askbot_site'
    contents = {
        'settings.py': RenderedFile,
        '__init__.py': CopiedFile,
        'celery_app.py': CopiedFile,
        'urls.py': CopiedFile,
        'django.wsgi': CopiedFile,
    }

# The naming is terribly misleading here. This is just some of the stuff we use
# for building Askbot containers. This has nothing to do with Django.
class AskbotApp(DeployableComponent):
    default_name = 'askbot_app'
    contents = {
        'prestart.sh': CopiedFile,
        'prestart.py': CopiedFile,
        'uwsgi.ini': RenderedFile,  # askbot_site, askbot_app
    }

class ProjectRoot(DeployableComponent):
    contents = {
        'manage.py': RenderedFile,
        'cron': {
            'send_email_alerts.sh': CopiedFile,
        },
        'doc': LinkedDir,
        'upfiles': {},
        'static': {},
    }

    def __init__(self, install_path):
        dirname, basename = os.path.split(install_path)
        if len(basename) == 0:
            dirname, basename = os.path.split(dirname)
        super(ProjectRoot, self).__init__(basename)
        self.dst_dir = dirname

    def deploy(self):
        tree = self._grow_deployment_tree(self.contents)
        root = self._root_deployment_tree(tree)
        # doc has no template in setup_templates. we point src_dir to the
        # correct directory after applying all defaults in _root_deployment_tree()
        doc = [ node for node in root.content
                if isinstance(node,LinkedDir)
                and node.name == 'doc' ][0]
        doc.src_path = os.path.dirname(doc.src_path)
        root.deploy()
