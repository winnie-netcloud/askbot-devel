from django.core.management import BaseCommand
from django.db import connection as conn
import os.path
import askbot
from askbot.search.postgresql import setup_full_text_search

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--interactive',
                            action='store_true',
                            dest='interactive',
                            default=False,
                            help='force the issue'
                           )

    def handle(self, **options):
        dir_path = askbot.get_install_directory()

        script_name = 'thread_and_post_models_03012016.plsql'
        version = conn.cursor().connection.server_version
        if version > 109999: # if PostgreSQL 11+
            script_name = 'thread_and_post_models_03012016_pg11.plsql'

        script_path = os.path.join(
                            dir_path,
                            'search',
                            'postgresql',
                            script_name
                        )
        setup_full_text_search(script_path)

        script_path = os.path.join(
                            dir_path,
                            'search',
                            'postgresql',
                            'user_profile_search_12202015.plsql'
                        )
        setup_full_text_search(script_path)
