# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('askbot', '0020_mark_internal_moderation_reasons'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderationqueueitem',
            name='item_author',
            field=models.ForeignKey(related_name='authored_moderation_queue_items', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
