# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

_ = lambda v: v # fake translation function

def create_moderation_reasons(apps, schema_editor):
    ModerationReason = apps.get_model('askbot', 'ModerationReason')

    description_text =_('Post contains offensive language or sentiment')
    ModerationReason.objects.create(
        title=_('Offensive'),
        description_text=description_text,
        description_html=u'<p>{}</p>'.format(description_text),
        is_predefined=True
    )

    description_text =_('May be assigned automatically when someone creates a new post')
    ModerationReason.objects.create(
        title=_('New post'),
        description_text=description_text,
        description_html=u'<p>{}</p>'.format(description_text),
        is_predefined=True
    )

    description_text =_('Maybe be assigned automatically when someone edits a post')
    ModerationReason.objects.create(
        title=_('Post edit'),
        description_text=description_text,
        description_html=u'<p>{}</p>'.format(description_text),
        is_predefined=True
    )

class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0015_create_moderation_tables'),
    ]

    operations = [
        migrations.RunPython(create_moderation_reasons)
    ]
