"""
module for deploying askbot
"""

import os.path
import sys

from argparse import ArgumentParser
from askbot.deployment import messages
from askbot.deployment.messages import print_message
from askbot.deployment import path_utils
from askbot.utils.functions import generate_random_key
from askbot.deployment.template_loader import DeploymentTemplate
from askbot.deployment.parameters import askbotCollection
from askbot.deployment.base import ObjectWithOutput
from askbot.deployment.deployables.components import DeployableComponent
import askbot.deployment.deployables as deployable

class AskbotSetup(ObjectWithOutput):
    ASKBOT_ROOT = os.path.dirname(os.path.dirname(__file__))
    SOURCE_DIR = 'setup_templates'

    def __init__(self, interactive=True, verbosity=-128):
        super(AskbotSetup, self).__init__(verbosity=verbosity)
        self.parser = ArgumentParser(description="Setup a Django project and app for Askbot")
        self._todo = {}
        self.configManagers = askbotCollection
        self.database_engines = self.configManagers.configManager(
                'database').configField(
                'database_engine').database_engines

        self._add_arguments()

    def _add_arguments(self):
        self._add_setup_args()
        self._add_settings_args()
        self._add_db_args()
        self._add_cache_args()


    def _add_settings_args(self):
        """Misc parameters for rendering settings.py
        Adds
        --logfile-name
        --append-settings
        --no-secret-key
        """

        self.parser.add_argument(
            "--logfile-name",
            dest="logfile_name",
            default='askbot.log',
            help="name of the askbot logfile."
        )

        self.parser.add_argument(
            "--append-settings",
            dest="local_settings",
            default='',
            help="Extra settings file to append custom settings"
        )

        self.parser.add_argument(
            "--no-secret-key",
            dest="no_secret_key",
            action='store_true',
            help="Don't generate a secret key. (not recommended)"
        )

    def _add_setup_args(self):
        """Control the behaviour of this setup procedure
        Adds
        --create-project
        --dir-name, -n
        --app-name
        --verbose, -v
        --force
        --dry-run
        --use-defaults
        """

        self.parser.add_argument(
            '--create-project',
            dest='create_project',
            action='store',
            default='django',
            help='Deploy a new Django project (default)'
        )

        self.parser.add_argument(
            "--dir-name", "-n",
            dest = "dir_name",
            default = '',
            help = "Directory where you want to install the Django project."
        )

        self.parser.add_argument(
            "--app-name",
            dest="app_name",
            default=None,
            help="Django app name (subdir) for this Askbot deployment in the target Django project."
        )

        self.parser.add_argument(
            "--verbose", "-v",
            dest = "verbosity",
            default = 1,
            type=int,
            choices=[0,1,2],
            help = "verbosity level with 0 being the lowest"
        )

        self.parser.add_argument(
            "--force",
            dest="force",
            action='store_true',
            help="(DEFUNCT!) Force overwrite settings.py file"
        )

        self.parser.add_argument(
            "--dry-run",
            dest = "dry_run",
            action='store_true',
            help="Dump parameters and do not install askbot after input validation."
        )

        self.parser.add_argument(
            "--use-defaults",
            dest="use_defaults",
            action='store_true',
            help="Use Askbot defaults where applicable. Defaults will be overwritten by commandline arguments."
        )

        self.parser.add_argument(
            "--no-input",
            dest="interactive",
            action='store_false',
            help="The installer will fail instead of asking for missing values."
        )

    def _add_cache_args(self):
        """Cache settings
        Adds
        --cache-engine
        --cache-node
        --cache-db
        --cache-password
        """
        engines = self.configManagers.configManager('cache').configField('cache_engine').cache_engines
        engine_choices = [e[0] for e in engines]
        self.parser.add_argument('--cache-engine',
            dest='cache_engine',
            action='store',
            default=None,
            type=int,
            choices=engine_choices,
            help='Select which Django cache backend to use.'
        )

        self.parser.add_argument('--cache-node',
            dest='cache_nodes',
            action='append',
            help='Add cache node to list of nodes. Specify node as <ip-address>:<port>. Can be provided multiple times.'
        )

        # only used by redis at the moment
        self.parser.add_argument('--cache-db',
            dest='cache_db',
            action='store',
            default=1,
            type=int,
            help='The name of the cache DB to use.'
        )

        # only used by redis at the moment
        self.parser.add_argument('--cache-password',
            dest='cache_password',
            action='store',
            help='The password to connect to the cache.'
        )

    def _add_db_args(self):
        """How to connect to the database
        Adds
        --db-engine,   -e
        --db-name,     -d
        --db-user",    -u
        --db-password, -p
        --db-host
        --db-port
        """

        engine_choices = [e[0] for e in self.database_engines]
        self.parser.add_argument(
            '--db-engine', '-e',
            dest='database_engine',
            action='store',
            choices=engine_choices,
            default=None,
            type=int,
            help='Database engine, type 1 for PostgreSQL, 2 for SQLite, 3 for MySQL, 4 for Oracle'
        )

        self.parser.add_argument(
            "--db-name", "-d",
            dest = "database_name",
            default = None,
            help = "The database name Askbot will use"
        )

        self.parser.add_argument(
            "--db-user", "-u",
            dest = "database_user",
            default = None,
            help = "The username Askbot uses to connect to the database"
        )

        self.parser.add_argument(
            "--db-password", "-p",
            dest = "database_password",
            default = None,
            help = "The password Askbot uses to connect to the database"
        )

        self.parser.add_argument(
            "--db-host",
            dest = "database_host",
            default = None,
            help = "The database host"
        )

        self.parser.add_argument(
            "--db-port",
            dest = "database_port",
            default = None,
            type=int,
            help = "The database port"
        )

    @ObjectWithOutput.verbosity.setter
    def verbosity(self, v):
        self._verbosity = v
        self.configManagers.verbosity = v

    def _process_args(self, options):
        """
        In this method we fiddle with askbot-setup parameters, i.e. cli
        arguments. This is run BEFORE the installer uses the ConfigManagers to
        do sanity checks and interact with the user.
        """
        options = vars(options)  # use dictionary instead of Namespace
        # force
        force = False  # effectively disables the --force switch!
        # logdir
        logdir_name = path_utils.LOG_DIR_NAME  # will become a parameter soon, me thinks
        # secret_key
        secret_key = generate_random_key()
        if options['no_secret_key']:
            secret_key = ''
        # app_name
        app_name = options['app_name']
        if app_name is None:
            app_name = os.path.basename(options['dir_name'])
        options['force'] = force
        options['logdir_name'] = logdir_name
        options['secret_key'] = secret_key
        options['app_name'] = app_name
        options['create_project'] = str.lower(options['create_project'])
        return options

    def __call__(self): # this is the main part of the original askbot_setup()
      try:
        self.print(messages.DEPLOY_PREAMBLE)

        options = self.parser.parse_args()
        options = self._process_args(options)

        self.verbosity = options['verbosity']
        self.configManagers.complete(options)

        #database_interface = [ e[1] for e in self.database_engines
        #                       if e[0] == options['database_engine'] ][0]
        #options['database_engine'] = database_interface

        nothing = DeployableComponent()
        nothing.deploy = lambda: None

        # install into options['dir_name']
        project = deployable.ProjectRoot(options['dir_name'])

        # select where to look for source files and templates
        project.src_dir = os.path.join(self.ASKBOT_ROOT, self.SOURCE_DIR)

        # set log dir an log file
        project.contents.update({
            options['logdir_name']: {options['logfile_name']: deployable.EmptyFile}
        })

        # set the directory where settings.py etc. go, defaults to
        site = deployable.AskbotSite(options['app_name'])

        # install as a sub-directory to the intall directory
        site.dst_dir = options['dir_name']

        # select where to look for source files and templates
        site.src_dir = os.path.join(self.ASKBOT_ROOT, self.SOURCE_DIR)

        # use user provided paramters to render files
        site.context.update(options)

        # install container specifics, analogous to site
        uwsgi = deployable.AskbotApp()
        uwsgi.src_dir = os.path.join(self.ASKBOT_ROOT, self.SOURCE_DIR)
        uwsgi.dst_dir = options['dir_name']
        uwsgi.context.update({
            'askbot_site': options['dir_name'],
            'askbot_app': uwsgi.name, # defaults to askbot_app
        })

        # put the path to settings.py into manage.py
        project.context = {'settings_path': f'{site.name}.settings'}

        todo = [ project, site ]

        if options['create_project'] in ['no', 'none', 'false', '0', 'nothing']:
            todo = [ nothing ]  # undocumented noop for the installer
        elif options['create_project'] == 'container-uwsgi':
            # if we install into a container we additionally want these files
            project.contents.update({
            'cron': {
                'crontab': deployable.RenderedFile,  # askbot_site, askbot_app
                'cron-askbot.sh': deployable.CopiedFile,
            }})
            todo.append(uwsgi)

        # maybe we could just use the noop nothing instead of this?
        if options['dry_run']:
            raise StopIteration

        # install askbot
        for component in todo:
            component.deploy()

        # the happily ever after section for successful deployments
        help_file = path_utils.get_path_to_help_file()

        self.print(messages.HOW_TO_DEPLOY_NEW % {'help_file': help_file})

        if options['database_engine'] == 'postgresql_psycopg2':
            try:
                import psycopg2
            except ImportError:
                self.print('\nNEXT STEPS: install python binding for postgresql')
                self.print('pip install psycopg2-binary\n')
        elif options['database_engine'] == 'mysql':
            try:
                import _mysql
            except ImportError:
                self.print('\nNEXT STEP: install python binding for mysql')
                self.print('pip install mysql-python\n')

      except KeyboardInterrupt:
        self.print("\n\nAborted.")
        sys.exit(1)

      except StopIteration:
          from pprint import pformat
          self.print(pformat(options))
          self.print(pformat(self.__dict__))
          sys.exit(0)

        # ToDo: The following is not yet implemented in the new code
        #if len(options['local_settings']) > 0 \
        #and os.path.exists(options['local_settings']):
        #    dst = os.path.join(app_dir, 'settings.py')
        #    print_message(f'Appending {options["local_settings"]} to {dst}', self.verbosity)
        #    with open(dst, 'a') as settings_file:
        #        with open(options['local_settings'], 'r') as local_settings:
        #            settings_file.write('\n')
        #            settings_file.write(local_settings.read())
        #    print_message('Done.', self.verbosity)


askbot_setup = AskbotSetup(interactive=True, verbosity=1)
