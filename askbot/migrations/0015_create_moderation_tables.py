# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import askbot.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('askbot', '0014_populate_askbot_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationQueueItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_id', models.PositiveIntegerField()),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('language_code', askbot.models.fields.LanguageCodeField(default=b'en', max_length=16, choices=[(b'en', b'English')])),
                ('added_by', models.ForeignKey(related_name='moderation_queue_items', to=settings.AUTH_USER_MODEL)),
                ('item_content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'moderation queue item',
                'verbose_name_plural': 'moderation queue items',
            },
        ),
        migrations.CreateModel(
            name='ModerationReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=128)),
                ('reason_type', models.CharField(max_length=32, choices=[(b'post_moderation', 'Reasons why posts are moderated'), (b'user_moderation', 'Reasons why user profiles are moderated'), (b'question_closure', 'Reasons why questions are closed')])),
                ('description_html', models.TextField(null=True)),
                ('description_text', models.TextField(null=True)),
                ('is_predefined', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'moderation reason',
                'verbose_name_plural': 'moderation reasons',
            },
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='primary_language',
            field=models.CharField(default=b'en', max_length=16, choices=[(b'en', b'English')]),
        ),
        migrations.AddField(
            model_name='moderationqueueitem',
            name='reason',
            field=models.ForeignKey(related_name='moderation_queue_items', to='askbot.ModerationReason'),
        ),
    ]
