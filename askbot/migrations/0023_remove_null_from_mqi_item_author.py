# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0022_populate_moderation_queue_item_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderationqueueitem',
            name='item_author',
            field=models.ForeignKey(related_name='authored_moderation_queue_items', to=settings.AUTH_USER_MODEL),
        ),
    ]
