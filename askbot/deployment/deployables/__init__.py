"""
The main purpose of this code is to do a one-shot deployment of Askbot. It is
built on the premise that the chosen deployment is viable and possible. If an
error occurs, it is not this code's task to remedy the issue. If an error
occurs the deployment is considered as failed. Ideally, all the work this code
did up to the error is undone. Yet, this code has no means to undo anything.
"""

from .objects import RenderedFile, CopiedFile, EmptyFile, Directory, LinkedDir
from .components import AskbotApp, AskbotSite, ProjectRoot


__all__ = ['RenderedFile', 'CopiedFile', 'EmptyFile', 'Directory', 'LinkedDir',
           'AskbotApp', 'AskbotSite', 'ProjectRoot']
