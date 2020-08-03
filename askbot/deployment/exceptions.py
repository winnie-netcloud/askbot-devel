"""Exceptions"""

class ValidationError(ValueError):
    """Raised when CLI option is invalid"""


class DeploymentError(RuntimeError):
    """Raised when deployment becomes impossible
    due to some runtime errro"""
