class DirNameError(Exception):
    """There is something about the chosen install dir we don't like."""

class RestrictionsError(DirNameError):
    """The install dir name does not meet our requirements."""

class NameCollisionError(DirNameError):
    """There is already a module with that name."""

class IsFileError(DirNameError):
    """Cannot use that path."""

class CreateWriteError(DirNameError):
    """Cannot write there."""

class NestedProjectsError(DirNameError):
    """Cannot do a sensible deployment."""

class OverwriteError(DirNameError):
    """This would overwrite things we don't want to overwrite."""

class AskbotDeploymentError(Exception):
    """Use this when something goes wrong while deploying Askbot"""
