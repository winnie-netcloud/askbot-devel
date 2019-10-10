from askbot.deployment.base import DeployableFile, DeployableDir

class RenderedFile(DeployableFile):
    """Render a file using Jinja2.
    This class expects the source file to have a .jinja2-suffix and uses a
    common render method.
    """
    def _deploy_now(self):
        self._render_with_jinja2(self.context)

    @property
    def src(self):
        return f'{super().src}.jinja2'

class CopiedFile(DeployableFile):
    """Copy a file from the source directory into the target directory."""
    def _deploy_now(self):
        self._copy()

class EmptyFile(DeployableFile):
    """Create an empty file."""
    def _deploy_now(self):
        self._touch()

# Changing this file will not(!) alter the behaviour of deployable components,
# as it uses the base class DeployableDir. We only have the Directory for
# completeness sake.
class Directory(DeployableDir):
    """Create an empty directory."""

class LinkedDir(DeployableDir):
    """Create a symbolic link to an existing directory."""
    def _deploy_now(self):
        self._link_dir()
