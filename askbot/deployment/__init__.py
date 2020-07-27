"""
Creates a development/evaluation deployment.
Initializes all files necessary for the Django project,
and does not set up anything to interface with the
web-facing server. The latter is the responsibility
of the deployment scripts (e.g. Dockerfile).
"""

import os.path
import sys

from argparse import ArgumentParser
from askbot.deployment import messages
from askbot.deployment.messages import print_message
from askbot.deployment import const
from askbot.deployment import deployables
from askbot.deployment.validators import ParamsValidator
from askbot.deployment.console import Console
from askbot.deployment.exceptions import ValidationError

DESCRIPTION = """Creates files for the django project of Askbot.

The goal of this script is to create a working project and
sample settings. This setup is sufficient for the development.

Use the produced settings.py as a template for your production deployment.

If you wish to contribute to a more functional deployment script
have a look at the Dockerfile.
"""

class AskbotSetup:
    """Class that does the job of this module."""

    ASKBOT_ROOT = os.path.dirname(os.path.dirname(__file__))
    SOURCE_DIR = 'setup_templates'

    def __init__(self):
        self.parser = ArgumentParser(description=DESCRIPTION)
        self.add_arguments()

    def add_arguments(self):
        """Configures the CLI parameters"""
        self.add_setup_args()
        self.add_db_args()
        self.add_site_args()
        # these override some of the detailed settings
        self.add_settings_snippet_args()

    def add_site_args(self):
        """Settings specific to the workings of the site"""
        self.parser.add_argument(
            '--domain-name',
            dest='domain_name',
            action='store',
            default=None,
            help=const.DOMAIN_NAME_HELP
        )

        self.parser.add_argument(
            '--language-code', '-l',
            dest='language_code',
            action='store',
            default='en',
            help=const.LANGUAGE_CODE_HELP
        )

        self.parser.add_argument(
            '--timezone', '-t',
            dest='timezone',
            action='store',
            default='America/Chicago',
            help='Name of the timezone, for example Europe/Berlin'
        )

    def add_settings_snippet_args(self):
        """Arguments for the settings snippets.
        Values of these must be a Python code in the format of the
        django settings.py file, containing the specific groups of settings.
        Use of these is intended with the scripted deployments, e.g. - with Docker.

        The values are not validated. It is the responsibility of the user
        to test the produced settings.py file.

        When provided, these settings completely override corresponding detailed parameters.
        For example - `--db-settings` if provided, will override --db-name, --db-password, etc.
        """
        self.parser.add_argument(
            '--email-settings',
            dest='email_settings',
            action='store',
            default=None,
            help='Settings snippet for the email - Python code.'
        )

        self.parser.add_argument(
            '--language-settings',
            dest='language_settings',
            default=None,
            help='Settings snippet for the language - Python code.'
        )

        self.parser.add_argument(
            '--logging-settings',
            dest='logging_settings',
            default=None,
            help='Settings snippet for the logging - Python code.'
        )

        self.parser.add_argument(
            '--caching-settings',
            dest='caching_settings',
            help='Settings snippet for caching - Python code.'
        )

        self.parser.add_argument(
            '--append-settings',
            dest='extra_settings',
            default=None,
            help='Extra settings snippet - python code - ' + \
                'appended to the settings.py file - Python code.'
        )

    def add_db_args(self):
        """DB parameters for the settings.py"""

        self.parser.add_argument(
            '--db-settings',
            dest='database_settings',
            action='store',
            default=None,
            help='Database settings snippet - Python code.\n' + \
                    'If given, all remaining db parameters will be ignored.'
        )

        self.parser.add_argument(
            '--db-engine', '-e',
            dest='database_engine',
            action='store',
            choices=[eng[0] for eng in const.DATABASE_ENGINE_CHOICES],
            default=const.SQLITE,
            type=int,
            help=const.DATABASE_ENGINE_HELP
        )

        self.parser.add_argument(
            '--db-name', '-d',
            dest='database_name',
            default='askbot',
            help='Database name'
        )

        self.parser.add_argument(
            '--db-user', '-u',
            dest='database_user',
            default=None,
            help='Database user name'
        )

        self.parser.add_argument(
            '--db-password', '-p',
            dest='database_password',
            default='',
            help='Database password'
        )

    def add_setup_args(self):
        """Control the behaviour of this setup procedure"""
        self.parser.add_argument(
            '--root-directory', '-r',
            dest='root_dir',
            default='', # default is handled by the validator
            help=const.ROOT_DIR_HELP
        )

        self.parser.add_argument(
            '--proj-name',
            dest='proj_name',
            default='', # default is handled by the validator as it matches basename of the root dir
            help=const.PROJ_NAME_HELP
        )

        self.parser.add_argument(
            '--media-root',
            dest='media_root',
            action='store',
            default=None, # real value is handled by the validator, b/c it matches the root
            help=const.MEDIA_ROOT_HELP
        )

        self.parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            help='Overwrite the existing files'
        )

        self.parser.add_argument(
            '--noinput',
            dest='interactive',
            action='store_false',
            help='The installer will fail instead of asking for missing values.'
        )

    def __call__(self): # this is the main part of the original askbot_setup()
        try:
            # If necessary and if we are in the interactive mode,
            # will ask for the missing parameters.
            # Otherwise will use the default values.
            console = Console()
            validator = ParamsValidator(console, self.parser)
            params = validator.get_params()

            for key, val in params.items():
                print(f'{key}={val}')

            # make the directories
            """
            deployables.ProjectRoot().deploy(params)
            deployables.ProjectDir().deploy(params)
            deployables.MediaRoot().deploy(params)
            deployables.StaticRoot().deploy(params)

            # make the manage.py file
            deployables.ManagePy().deploy(params)
            # make the settings.py file
            deployables.SettingsPy().deploy(params)
            # make the urls.py file
            deployables.UrlsPy().deploy(params)
            # print next steps help
            self.print_postamble()
            """

        except ValidationError as error:
            print(f'\n\n{error}\nAborted')
            sys.exit(1)

        except KeyboardInterrupt:
            print("\n\nAborted.")
            sys.exit(1)

askbot_setup = AskbotSetup()
