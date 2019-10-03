"""utilities in addition to os.path
that
* help to test existing paths on usability for the installation
* create necessary directories
* install deployment files
"""

import os
import os.path
import tempfile
import re
import glob
import imp

from askbot.deployment import messages
from askbot.utils import console


FILES_TO_CREATE = ('__init__.py', 'manage.py', 'urls.py', 'django.wsgi', 'celery_app.py')
BLANK_FILES     = ('__init__.py', 'manage.py')
LOG_DIR_NAME    = 'log'

def split_at_break_point(directory):
    """splits directory path into two pieces
    first that exists and secon - that does not
    by determining a point at which path breaks

    exception will be raised if directory in fact exists
    """
    assert(os.path.exists(directory) == False)

    head = directory
    tail_bits = list()
    while os.path.exists(head) == False:
        head, tail = os.path.split(head)
        tail_bits.insert(0, tail)
    return head, os.path.join(*tail_bits)

def clean_directory(directory):
    """Returns normalized absolute path to the directory
    regardless of whether it exists or not
    or ``None`` - if the path is a file or if ``directory``
    parameter is ``None``"""
    if directory is None:
        return None

    directory = os.path.normpath(directory)
    directory = os.path.abspath(directory)

    if os.path.isfile(directory):
        print(messages.CANT_INSTALL_INTO_FILE % {'path':directory})

        return None
    return directory

# Only used in can_create_path
def directory_is_writable(directory):
    """returns True if directory exists
    and is writable, False otherwise
    """
    try:
        #run writability test
        temp_path = tempfile.mktemp(dir=directory)
        assert(os.path.dirname(temp_path) == directory)
        temp_file = open(temp_path, 'w')
        temp_file.close()
        os.unlink(temp_path)
        return True
    except IOError:
        return False


# Only used in get_install_directory
def can_create_path(directory):
    """returns True if user can write file into
    directory even if it does not exist yet
    and False otherwise
    """
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            return False
    else:
        directory = split_at_break_point(directory)[0]
    return directory_is_writable(directory)


IMPORT_RE1 = re.compile(r'from django.*import')
IMPORT_RE2 = re.compile(r'import django')
def has_existing_django_project(directory):
    """returns True is any of the .py files
    in a given directory imports anything from django
    """
    directory = os.path.normpath(directory)
    file_list = glob.glob(directory  + os.path.sep + '*.py')
    for file_name in file_list:
        if file_name.endswith(os.path.sep + 'manage.py'):
            #a hack allowing to install into the distro directory
            continue
        with open(file_name, 'r') as py_file:
            for line in py_file:
                if IMPORT_RE1.match(line) or IMPORT_RE2.match(line):
                    return True
    return False


def find_parent_dir_with_django(directory):
    """returns path to Django project anywhere
    above the directory
    if nothing is found returns None
    """
    parent_dir = os.path.dirname(directory)
    while parent_dir != directory:
        if has_existing_django_project(parent_dir):
            return parent_dir
        else:
            directory = parent_dir
            parent_dir = os.path.dirname(directory)
    return None


# Only used in get_install_directory
def path_is_clean_for_django(directory):
    """returns False if any of the parent directories
    contains a Django project, otherwise True
    does not check the current directory
    """
    django_dir = find_parent_dir_with_django(directory)
    return (django_dir is None)


# Can be removed after fixing askbot.tests.test_installer
def create_path(directory):
    """equivalent to mkdir -p"""
    if os.path.isdir(directory):
        return
    elif os.path.exists(directory):
        raise ValueError('expect directory or a non-existing path')
    else:
        os.makedirs(directory)


SOURCE_DIR = os.path.dirname(os.path.dirname(__file__))
def get_path_to_help_file():
    """returns path to the main plain text help file"""
    return os.path.join(SOURCE_DIR, 'doc', 'INSTALL')

# Only used in get_install_directory
def dir_name_unacceptable_for_django_project(directory):
    dir_name = os.path.basename(directory)
    if re.match(r'[_a-zA-Z][\w-]*$', dir_name):
        return False
    return True

# Only used in get_install_directory
def dir_taken_by_python_module(directory):
    """True if directory is not taken by another python module"""
    dir_name = os.path.basename(directory)
    try:
        imp.find_module(dir_name)
        return True
    except ImportError:
        return False

def get_install_directory(force = False):
    """returns a directory where a new django app/project
    can be installed.
    If ``force`` is ``True`` - will permit
    using a directory with an existing django project.
    """
    from askbot.deployment import messages
    where_to_deploy_msg = messages.WHERE_TO_DEPLOY
    directory = input(where_to_deploy_msg + ' ')

    if directory.strip() == '':
        return None

    directory = clean_directory(directory)

    if directory is None:
        return None

    if can_create_path(directory) == False:
        print(messages.format_msg_dir_not_writable(directory))
        return None

    if os.path.exists(directory):
        if path_is_clean_for_django(directory):
            if has_existing_django_project(directory):
                if not force:
                    print(messages.CANNOT_OVERWRITE_DJANGO_PROJECT % \
                        {'directory': directory})
                    return None
        else:
            print(messages.format_msg_dir_unclean_django(directory))
            return None
    elif force == False:
        message = messages.format_msg_create(directory)
        should_create_new = console.choice_dialog(
                            message,
                            choices = ['yes','no'],
                            invalid_phrase = messages.INVALID_INPUT
                        )
        if should_create_new == 'no':
            return None

    if dir_taken_by_python_module(directory):
        print(messages.format_msg_bad_dir_name(directory))
        return None
    if dir_name_unacceptable_for_django_project(directory):
        print("""\nDirectory %s is not acceptable for a Django project.
Please use lower case characters, numbers and underscore.
The first character cannot be a number.\n""" % os.path.basename(directory))
        return None

    return directory
