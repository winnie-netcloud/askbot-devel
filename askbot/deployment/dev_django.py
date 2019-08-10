"""
The main purpose of this code is to do a one-shot deployment of Askbot. It is
built on the premise that the chosen deployment is viable and possible. If an
error occurs, it is not this code's task to remedy the issue. If an error
occurs the deployment is considered as failed. Ideally, all the work this code
did up to the error is undone. Yet, this code has no means to undo anything.
"""

from askbot.deployment.messages import print_message
from askbot.deployment.template_loader import DeploymentTemplate
import os.path
import shutil

class AskbotDeploymentError(Exception):
    """Use this when something goes wrong while deploying Askbot"""

class DeployObject(object):
    def __init__(self, name, src_path=None, dst_path=None):
        self._verbosity = 2
        self.name = name
        self._src_path = src_path
        self._dst_path = dst_path

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        self._verbosity = value

    @property
    def src_path(self):
        return self._src_path

    @src_path.setter
    def src_path(self, value):
        self._src_path = value

    @property
    def dst_path(self):
        return self._dst_path

    @dst_path.setter
    def dst_path(self, value):
        self._dst_path = value

    @property
    def src(self):
        return os.path.join(self.src_path, self.name)

    @property
    def dst(self):
        return os.path.join(self.dst_path, self.name)

    def _deploy_now(self):
        """virtual protected"""

    def deploy(self):
        print_message(f'*    {self.dst} from {self.src}', self.verbosity)
        try:
            self._deploy_now()
        except AskbotDeploymentError as e:
            print_message(e, self.verbosity)


class DeployFile(DeployObject):
    """This class collects all logic w.r.t. writing files. It has to be
    subclassed and the subclasses must/should overwrite _deploy_now to call
    one of the methods defined in this class. At the time of this writing, this
    is either _render_with_jinja2 or _copy."""
    def __init__(self, name, src_path=None, dst_path=None):
        super(DeployFile, self).__init__(name, src_path, dst_path)
        self.context = dict()
        self.skip_silently = list()
        self.forced_overwrite = list()

    # the different approaches for force and skip feel a little odd.
    def __validate(self):
        matches = [self.dst for c in self.forced_overwrite
                   if self.dst.endswith(f'{os.path.sep}{c}')]
        exists = os.path.exists(self.dst)
        force  = len(matches) > 0
        skip   = self.dst.split(os.path.sep)[-1] in self.skip_silently
        return exists, force, skip

    def _render_with_jinja2(self, context):
        exists, force, skip = self.__validate()
        if exists:
            raise AskbotDeploymentError(f'     You already have a file "{self.dst}" please merge the contents.')
        template = DeploymentTemplate('dummy.name')  # we use this a little differently than originally intended
        template.tmpl_path = self.src
        with open(self.dst, 'w+') as output_file:
            output_file.write(template.render(context))

    def _copy(self):
        exists, force, skip = self.__validate()
        if exists:
            if skip: # this makes skip more important than force. This is good, because when in doubt, we rather leave the current installation the way it is. This is bad because we cannot explicitly force an overwrite.
                return
            elif force:
                print_message('     ^^^ forced overwrite!', self.verbosity)
            else:
                raise AskbotDeploymentError(f'     You already have a file "{self.dst}", please add contents of {self.src}.')
        shutil.copy(self.src, self.dst)


class DeployDir(DeployObject):
    def __init__(self, name, parent=None, *content):
        super(DeployDir, self).__init__(name)
        self.content = list(content)
        if parent is not None:
            self.dst_path = self.__clean_directory(parent)

    @property
    def src_path(self):
        return super().src_path

    @src_path.setter
    def src_path(self, value):
        value = self.__clean_directory(value)
        self._src_path = value
        for child in self.content:
            child.src_path = value

    @property
    def dst_path(self):
        return super().dst_path

    @dst_path.setter
    def dst_path(self, value):
        value = self.__clean_directory(value)
        self._dst_path = value
        for child in self.content:
            child.dst_path = self.dst

    @property
    def context(self):
        raise AttributeError(f'{self.__class__} does not store context information')

    @property
    def skip_silently(self):
        raise AttributeError(f'{self.__class__} does not store file skip information')

    @property
    def forced_overwrite(self):
        raise AttributeError(f'{self.__class__} does not store file overwrite information')

    # maybe deepcopy() in the following three setters. maybe there's an advantage in not deepcopy()ing here. time will tell.
    @context.setter
    def context(self, value):
        for child in self.content: # in theory, we only want this for directories and rendered files.
            child.context = value

    @skip_silently.setter
    def skip_silently(self, value):
        for child in self.content: # in practice, we only need this for directories and copied files.
            child.skip_silently = value

    @forced_overwrite.setter
    def forced_overwrite(self, value):
        for child in self.content: # in practice, we only need this for directories and copied files.
            child.forced_overwrite = value

    #####################
    ## from path_utils ##
    #####################
    def __create_path(self):
        """equivalent to mkdir -p"""
        if os.path.isdir(self.dst):
            return
        elif os.path.exists(self.dst):
            raise AskbotDeploymentError('expect directory or a non-existing path')
        else:
            os.makedirs(self.dst)

    @staticmethod
    def __clean_directory(directory):
        """Returns normalized absolute path to the directory
        regardless of whether it exists or not
        or ``None`` - if the path is a file or if ``directory``
        parameter is ``None``"""
        if directory is None:
            return None

        directory = os.path.normpath(directory)
        directory = os.path.abspath(directory)

        #if os.path.isfile(directory):
        #    print(messages.CANT_INSTALL_INTO_FILE % {'path': directory})
        #    return None
        return directory

    def _deploy_now(self):
        self.__create_path()

    def deploy(self):
        self._deploy_now() # we don't try-except this, b/c input validation is supposed to identify problems before this code runs. If an exception is raised here, it's an issue that must be handled elsewhere.
        for node in self.content:
            node.deploy()

class RenderedFile(DeployFile):
    def _deploy_now(self):
        self._render_with_jinja2(self.context)

    @property
    def src(self):
        return f'{super().src}.jinja2'

class CopiedFile(DeployFile):
    def _deploy_now(self):
        self._copy()

class Directory(DeployDir):
    pass

class LinkedDir(DeployDir):
    pass


class DeployableComponent(object):
    """These constitue sensible deployment chunks of Askbot. For instance,
    one would never deploy just a settings.py, because Django projects need
    additional files as well."""
    default_name = 'unset'
    contents = dict()

    def __init__(self, name=None, contents=None):
        name = name if name is not None else self.__class__.default_name
        contents = contents if contents is not None else self.__class__.contents

        self.name = name
        self.contents = contents
        self._src_dir = None
        self._dst_dir = None
        self.context = dict()
        self.skip_silently = list()
        self.forced_overwrite = list()

    def _grow_deployment_tree(self, component):
        todo = list()
        for name, deployable in component.items():
            if isinstance(deployable,dict):
                branch = self._grow_deployment_tree(deployable)
                todo.append(
                    Directory(
                        name,
                        None,
                        *branch
                 ))
            else:
                todo.append(deployable(name))
        return todo

    def _root_deployment_tree(self, tree):
        root = Directory(self.name, None, *tree)
        root.src_path = self.src_dir
        root.dst_path = self.dst_dir
        root.context = self.context
        root.forced_overwrite = self.forced_overwrite
        root.skip_silently = self.skip_silently
        return root

    @property
    def src_dir(self):
        return self._src_dir

    @src_dir.setter
    def src_dir(self, value):
        self._src_dir = value

    @property
    def dst_dir(self):
        return self._dst_dir

    @dst_dir.setter
    def dst_dir(self, value):
        self._dst_dir = value

    def deploy(self):
        """Recursively deploy all DeployItems we know about. This method is
        meant to be overwritten by subclasses to provide more fine grained
        configurations to individual branches and/or nodes."""
        tree = self._grow_deployment_tree(self.contents)
        root = self._root_deployment_tree(tree)
        root.deploy()


class AskbotSite(DeployableComponent):
    default_name = 'askbot_site'
    contents = {
        'settings.py': RenderedFile,
        '__init__.py': CopiedFile,
        'celery_app.py': CopiedFile,
        'urls.py': CopiedFile,
    }

class AskbotApp(DeployableComponent):
    default_name = 'askbot_app'
    contents = {
        'cron': {
            'send_email_alerts.sh': CopiedFile,
        },
        'doc': LinkedDir,
        'upfiles': {},
    }

class ProjectRoot(DeployableComponent):
    contents = { 'manage.py': RenderedFile }

    def __init__(self, install_path):
        dirname, basename = os.path.split(install_path)
        if len(basename) == 0:
            dirname, basename = os.path.split(dirname)
        super(ProjectRoot, self).__init__(basename)
        self.dst_dir = dirname

if __name__ == '__main__':
    test = CopiedFile('testfile', '/tmp/foo', '/tmp/bar')
    test.deploy()
    test = RenderedFile('testfile01', '/tmp/foo', '/tmp/bar')
    test.context = {'x': 'World'}
    test.deploy()
    test = Directory('baz', '/tmp')
    test.deploy()
    askbot_site = AskbotSite()
    askbot_app = AskbotApp()
    project_root = ProjectRoot('/tmp/project_root_install_dir')
    project_root.src_dir = '/tmp/foo'
    project_root.deploy()
