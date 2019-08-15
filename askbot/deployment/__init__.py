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
from askbot.deployment.parameters import ConfigManagerCollection
import askbot.deployment.deployables as deployable
import shutil

class AskbotSetup:

    PROJECT_FILES_TO_CREATE = {'manage.py'}
    APP_FILES_TO_CREATE     = set(path_utils.FILES_TO_CREATE) - {'manage.py'}
    SOURCE_DIR              = os.path.dirname(os.path.dirname(__file__)) # a.k.a. ASKBOT_ROOT in settings.py

    def __init__(self, interactive=True, verbosity=-128):
        self.parser = ArgumentParser(description="Setup a Django project and app for Askbot")
        self.verbosity = verbosity
        self._todo = {}
        self.configManagers = ConfigManagerCollection(interactive=interactive, verbosity=verbosity)
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
        --create - project
        --dir-name, -n
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
            default='askbot_app',
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

    def _set_verbosity(self, v):
        self.verbosity = v
        self.configManagers.verbosity = v

    # I think this logic can be immediately attached to argparse
    # it would be a hack though
    def _set_create_project(self, options):
        # Currently the --create-project option only changes the installer's
        # behaviour if one passes "container-uwsgi" as argument
        todo = [ 'django' ] # This is the default as Askbot has always worked
        wish = str.lower(options['create_project'])
        if wish in [ 'no', 'none', 'false', '0']:
            todo = [ 'nothing' ]
        elif wish == 'container-uwsgi':
            todo.append(wish)
        self._todo['create_project'] = todo

    def __call__(self): # this is the main part of the original askbot_setup()
      try:
        options = self.parser.parse_args()
        options = vars(options)
        options['force'] = False # disable the --force switch!
        self._set_verbosity(options['verbosity'])
        self._set_create_project(options)
        print_message(messages.DEPLOY_PREAMBLE, self.verbosity)



        options['dir_name']   = path_utils.clean_directory(options['dir_name'])
        options['secret_key'] = '' if options['no_secret_key'] else generate_random_key()

        self.configManagers.complete(options)

        database_interface = [ e[1] for e in self.database_engines
                               if e[0] == options['database_engine'] ][0]
        options['database_engine'] = database_interface

        if options['dry_run']:
            from pprint import pformat
            print_message(pformat(options), self.verbosity)
            print_message(pformat(self.__dict__), self.verbosity)
            raise KeyboardInterrupt

        self.deploy_askbot_new(options)

        if database_interface == 'postgresql_psycopg2':
            try:
                import psycopg2
            except ImportError:
                print_message('\nNEXT STEPS: install python binding for postgresql', self.verbosity)
                print_message('pip install psycopg2-binary\n', self.verbosity)
        elif database_interface == 'mysql':
            try:
                import _mysql
            except ImportError:
                print_message('\nNEXT STEP: install python binding for mysql', self.verbosity)
                print_message('pip install mysql-python\n', self.verbosity)

      except KeyboardInterrupt:
        print_message("\n\nAborted.", self.verbosity)
        sys.exit(1)

    def _install_copy(self, copy_list, forced_overwrite=[], skip_silently=[]):
        print_message('Copying files:', self.verbosity)
        for src,dst in copy_list:
            print_message(f'* to {dst} from {src}', self.verbosity)
            if not os.path.exists(dst):
                shutil.copy(src, dst)
                continue
            matches = [ dst for c in forced_overwrite
                            if dst.endswith(f'{os.path.sep}{c}') ]
            if len(matches) > 0:
                print_message('  ^^^ forced overwrite!', self.verbosity)
                shutil.copy(src, dst)
            elif dst.split(os.path.sep)[-1] not in skip_silently:
                print_message(f'  ^^^ you already have one, please add contents of {src}', self.verbosity)
        print_message('Done.', self.verbosity)

    def _install_render_with_jinja2(self, render_list, context):
        print_message('Rendering files:', self.verbosity)
        template = DeploymentTemplate('dummy.name') # we use this a little differently than originally intended
        for src, dst in render_list:
            if os.path.exists(dst):
                print_message(f'* you already have a file "{dst}" please merge the contents', self.verbosity)
                continue
            print_message(f'*    {dst} from {src}', self.verbosity)
            template.tmpl_path = src
            output = template.render(context)
            with open(dst, 'w+') as output_file:
                output_file.write(output)
        print_message('Done.', self.verbosity)

    def _create_new_django_project(self, install_dir, options):
        log_dir  = os.path.join(install_dir, path_utils.LOG_DIR_NAME)
        log_file = os.path.join(log_dir, options['logfile_name'])

        create_me = [ install_dir, log_dir ]
        copy_me   = list()

        if 'django' in self._todo.get('create_project',[]):
            src = lambda x:os.path.join(self.SOURCE_DIR, 'setup_templates', x)
            dst = lambda x:os.path.join(install_dir, x)
            copy_me.extend([
               ( src(file_name), dst(file_name) )
               for file_name in self.PROJECT_FILES_TO_CREATE
            ])

        for d in create_me:
            path_utils.create_path(d)

        path_utils.touch(log_file)
        self._install_copy(copy_me, skip_silently=path_utils.BLANK_FILES)

    def _create_new_django_app(self, options):
        options['askbot_site'] = options['dir_name'] # b/c the jinja template uses askbot_site
        options['askbot_app']  = options['app_name'] # b/c the jinja template uses askbot_app
        app_dir = os.path.join(options['dir_name'], options['app_name'])

        create_me = [ app_dir ]
        copy_me   = list()
        render_me = list()

        if 'django' in self._todo.get('create_project',[]):
            src = lambda x:os.path.join(self.SOURCE_DIR, 'setup_templates', x)
            dst = lambda x:os.path.join(app_dir, x)
            copy_me.extend([
                ( src(file_name), dst(file_name) )
                for file_name in self.APP_FILES_TO_CREATE
                ])
            render_me.extend([
                ( src('settings.py.jinja2'), dst('settings.py') )
                ])

        if 'container-uwsgi' in self._todo.get('create_project',[]):
            src = lambda x:os.path.join(self.SOURCE_DIR, 'container', x)
            dst = lambda x:os.path.join(app_dir, x)
            copy_me.extend([
                ( src(file_name), dst(file_name) )
                for file_name in [ 'cron-askbot.sh', 'prestart.sh', 'prestart.py' ]
            ])
            render_me.extend([
                ( src(file_name), dst(file_name) )
                for file_name in [ 'crontab', 'uwsgi.ini' ]
            ])

        for d in create_me:
            path_utils.create_path(d)

        self._install_copy(copy_me, skip_silently=path_utils.BLANK_FILES,
                                    forced_overwrite=['urls.py'])

        self._install_render_with_jinja2(render_me, options)

        if len(options['local_settings']) > 0 \
        and os.path.exists(options['local_settings']):
            dst = os.path.join(app_dir, 'settings.py')
            print_message(f'Appending {options["local_settings"]} to {dst}', self.verbosity)
            with open(dst, 'a') as settings_file:
                with open(options['local_settings'], 'r') as local_settings:
                    settings_file.write('\n')
                    settings_file.write(local_settings.read())
            print_message('Done.', self.verbosity)

    def deploy_askbot(self, options):
        """function that creates django project files,
        all the neccessary directories for askbot,
        and the log file
        """

        create_new_project = True
        if os.path.exists(options['dir_name']) and \
           path_utils.has_existing_django_project(options['dir_name']) and \
           options['force'] is False:
             create_new_project = False

        options['staticfiles_app'] = "'django.contrib.staticfiles'," # Fixme: move this into the template
        options['auth_context_processor'] = 'django.contrib.auth.context_processors.auth' # Fixme: move this into the template

        if create_new_project is True:
            self._create_new_django_project(options['dir_name'], options)

        self._create_new_django_app(options)

        help_file = path_utils.get_path_to_help_file()

        if create_new_project:
            print_message(
                messages.HOW_TO_DEPLOY_NEW % {'help_file': help_file},
                self.verbosity
            )
        else:
            print_message(
                messages.HOW_TO_ADD_ASKBOT_TO_DJANGO % {'help_file': help_file},
                self.verbosity
            )

    def deploy_askbot_new(self, options):
        create_new_project = True
        if os.path.exists(options['dir_name']) and \
            path_utils.has_existing_django_project(options['dir_name']) and \
            options.force is False:
            create_new_project = False

        options['staticfiles_app'] = "'django.contrib.staticfiles',"
        options['auth_context_processor'] = 'django.contrib.auth.context_processors.auth'

        project = deployable.ProjectRoot(options['dir_name'])
        site = deployable.AskbotSite(project.name)

        if create_new_project is True:
            project.src_dir = os.path.join(self.SOURCE_DIR, 'setup_templates')
            project.contents.update({
                path_utils.LOG_DIR_NAME: {options['logfile_name']: deployable.EmptyFile}
            })
            project.context = {'settings_path': f'{site.name}.settings'}
            project.deploy()

        site.src_dir = os.path.join(self.SOURCE_DIR, 'setup_templates')
        site.dst_dir = options['dir_name']
        site.context.update(options)
        site.deploy()

        help_file = path_utils.get_path_to_help_file()

        if create_new_project:
            print_message(
                messages.HOW_TO_DEPLOY_NEW % {'help_file': help_file},
                self.verbosity
            )
        else:
            print_message(
                messages.HOW_TO_ADD_ASKBOT_TO_DJANGO % {'help_file': help_file},
                self.verbosity
            )



# set to askbot_setup_orig to return to original installer
askbot_setup = AskbotSetup(interactive=True, verbosity=1)
