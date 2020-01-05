# -*- coding: utf-8 -*-

from askbot.search.postgresql import setup_full_text_search
from django.db import models, migrations
import askbot
import os.path

def init_postgresql_fts(apps, schema_editor):
    conn = schema_editor.connection
    if hasattr(conn, 'vendor') and conn.vendor == 'postgresql':
        cursor = conn.cursor()
        cursor.execute('select version()')
        version_info = cursor.fetchone()[0].strip().split(' ')[1]
        if int(version_info.split('.')[0]) >= 11:
            script_name = 'thread_and_post_models_03012016_pg11.plsql'
        else:
            script_name = 'thread_and_post_models_03012016.plsql'

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

