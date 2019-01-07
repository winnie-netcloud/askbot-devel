# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0023_remove_null_from_mqi_item_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderationreason',
            name='is_manually_assignable',
            field=models.BooleanField(default=True, help_text=b'Reasons that are not manually assignable\ncan be assigned only by the system. Users should never assign them\nvia the user interface'),
        ),
    ]
