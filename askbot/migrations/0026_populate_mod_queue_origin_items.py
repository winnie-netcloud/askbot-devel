# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from askbot.utils.console import ProgressBar

def populate_origin_items(app, schema_editor):
    MQI = app.get_model('askbot', 'ModerationQueueItem')
    items = MQI.objects.filter(resolution_status='followup')
    message = 'Reversing direction of the followup item on the ModerationQueueItem'
    for item in ProgressBar(items.iterator(), items.count(), message):
        followup_items = MQI.objects.filter(pk=item.followup_item_id)
        followup_items.update(origin_item=item)


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0025_moderationqueueitem_origin_item'),
    ]

    operations = [
        migrations.RunPython(populate_origin_items)
    ]
