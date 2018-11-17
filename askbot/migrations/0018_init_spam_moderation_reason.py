# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

_ = lambda v: v # fake translation function

def create_moderation_reasons(apps, schema_editor):
    ModerationReason = apps.get_model('askbot', 'ModerationReason')

    # 1) take previous moderation reasons and mark them with type
    # 'post_moderation' - forgot about that after adding the fild reason_type
    titles = ('Offensive', 'New post', 'Post edit')
    old_reasons = ModerationReason.objects.filter(title__in=titles)
    old_reasons.update(reason_type='post_moderation')

    # 2) add new moderation reason titled "Spam"
    description_text =_('Post contains irrelevant or unsolicited content')
    ModerationReason.objects.create(
        title=_('Spam'),
        description_text=description_text,
        description_html=u'<p>{}</p>'.format(description_text),
        is_predefined=True,
        reason_type='post_moderation'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0017_copy_items_from_Activity_to_ModerationQueueItem'),
    ]

    operations = [
        migrations.RunPython(create_moderation_reasons)
    ]
