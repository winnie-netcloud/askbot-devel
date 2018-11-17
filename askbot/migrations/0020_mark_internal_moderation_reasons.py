# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def mark_internal_moderation_reasons(apps, schema_editor):
    ModerationReason = apps.get_model('askbot', 'ModerationReason')
    titles = ('New post', 'Post edit')
    reasons = ModerationReason.objects.filter(title__in=titles)
    reasons.update(is_manually_assignable=False)

class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0019_auto_20181117_1428'),
    ]

    operations = [
        migrations.RunPython(mark_internal_moderation_reasons)
    ]
