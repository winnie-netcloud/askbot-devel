# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from askbot.utils.console import ProgressBar

def get_content_object(apps, obj, content_type_id_field='content_type_id', object_id_field='object_id'):
    """Returns the object normally referred by the GenericForegnKey using
    the corresponding 'content type id' and 'object id fields"""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ct = ContentType.objects.get(pk=getattr(obj, content_type_id_field))
    rel_model = apps.get_model(ct.app_label, ct.model)
    rel_obj = rel_model.objects.get(pk=getattr(obj, object_id_field))
    return rel_obj

def populate_item_author(apps, schema_editor):
    MQI = apps.get_model('askbot', 'ModerationQueueItem')
    items = MQI.objects.all()
    message = 'Assigning item authors to moderation queue items'
    for item in ProgressBar(items.iterator(), items.count(), message):
        mod_item = get_content_object(apps, item, 'item_content_type_id', 'item_id')
        item.item_author = mod_item.author
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0021_add_moderation_queue_item_author'),
    ]

    operations = [
        migrations.RunPython(populate_item_author)
    ]
