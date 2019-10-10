from askbot.deployment.base import ObjectWithOutput
from .deployableobject import DeployableDir as Directory

class DeployableComponent(ObjectWithOutput):
    """These constitute sensible deployment chunks of Askbot. For instance,
    one would never deploy just a settings.py, because Django projects need
    additional files as well."""
    default_name = 'unset'
    contents = dict()

    def __init__(self, name=None, contents=None):
        super(DeployableComponent, self).__init__(verbosity=2)
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
                    Directory(name, None, *branch)
                 )
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
        root.verbosity = self.verbosity
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
