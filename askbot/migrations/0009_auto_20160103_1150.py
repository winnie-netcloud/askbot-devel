# -*- coding: utf-8 -*-

from askbot.search.postgresql import setup_full_text_search
from django.db import models, migrations
import askbot
import os.path

def init_postgresql_fts(apps, schema_editor):
    conn = schema_editor.connection
    # if conn does not have an attribute vendor, there is probalby something
    # wrong with Django and we should raise an exception, i.e. provoke the
    # AttributeError
    if not hasattr(conn, 'vendor') or conn.vendor != 'postgresql':
        return

    script_name = 'thread_and_post_models_03012016.plsql'
    version = conn.cursor().connection.server_version
    if version > 109999: # if PostgreSQL 11+
        script_name = 'thread_and_post_models_03012016_pg11.plsql'

    script_path = os.path.join(
                        askbot.get_install_directory(),
                        'search',
                        'postgresql',
                        script_name
                    )
    setup_full_text_search(script_path)

class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0008_auto_20160101_0951'),
    ]

    operations = [
            migrations.RunPython(init_postgresql_fts)
    ]

