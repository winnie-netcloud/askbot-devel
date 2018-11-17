# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('askbot', '0018_init_spam_moderation_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderationqueueitem',
            name='followup_item',
            field=models.ForeignKey(related_name='origin_items', blank=True, to='askbot.ModerationQueueItem', help_text=b'Used if resolution_status is "followup"', null=True),
        ),
        migrations.AddField(
            model_name='moderationqueueitem',
            name='resolution_status',
            field=models.CharField(default=b'waiting', max_length=16, choices=[(b'waiting', 'Awaiting moderation'), (b'upheld', 'Decision was upheld and the appropriate action was taken'), (b'dismissed', 'Moderation memo was dismissed, no changes to the content'), (b'followup', 'Moderation memo was accepted, but the final resolution is made with a different reason')]),
        ),
        migrations.AddField(
            model_name='moderationqueueitem',
            name='resolved_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='moderationqueueitem',
            name='resolved_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='moderationreason',
            name='is_manually_assignable',
            field=models.BooleanField(default=True, help_text=b'Reasons that are not manually assignable\nare only automatically assigned by the system\nand should not be assigned by the users\nvia the user interface'),
        ),
        migrations.AlterField(
            model_name='moderationreason',
            name='added_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='moderationreason',
            name='reason_type',
            field=models.CharField(max_length=32, choices=[(b'post_moderation', 'Reasons why posts are placed on the moderation queue'), (b'user_moderation', 'Reasons why user profiles are moderated'), (b'question_closure', 'Reasons why questions are closed')]),
        ),
    ]
