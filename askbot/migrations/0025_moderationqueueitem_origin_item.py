# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0024_auto_20190106_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderationqueueitem',
            name='origin_item',
            field=models.ForeignKey(related_name='followup_items', blank=True, to='askbot.ModerationQueueItem', help_text=b'Used for the followup items', null=True),
        ),
    ]
