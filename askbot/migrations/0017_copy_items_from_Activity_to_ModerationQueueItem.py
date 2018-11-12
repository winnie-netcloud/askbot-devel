# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from askbot.utils.console import ProgressBar

def get_post_revision_by_timestamp(post, timestamp):
    """Returns the latest post revision that 
    happened before the timestamp or latest revision
    or `None` if for some reason post has no revisions."""
    revs = post.revisions.filter(revised_at__lt=timestamp).order_by('-revised_at')
    if revs.count():
        return revs[0]
    if post.revisions.count():
        return post.revisions.order_by('-id')[0]
    return None


def get_contenttype(apps, model):
    """Returns ContentType instance for the Askbot by
    it's lowercased model name (e.g. 'postrevision' for 'PostRevision')"""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    return ContentType.objects.get(app_label='askbot', model=model.lower())


def get_content_object(apps, obj, content_type_id_field='content_type_id', object_id_field='object_id'):
    """Returns the object normally referred by the GenericForegnKey using
    the corresponding 'content type id' and 'object id fields"""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ct = ContentType.objects.get(pk=getattr(obj, content_type_id_field))
    rel_model = apps.get_model(ct.app_label, ct.model)
    rel_obj = rel_model.objects.get(pk=getattr(obj, object_id_field))
    return rel_obj

def move_mod_queue_items(apps, schema_editor):
    Activity = apps.get_model('askbot', 'Activity')
    ModerationReason = apps.get_model('askbot', 'ModerationReason')
    ModerationQueueItem = apps.get_model('askbot', 'ModerationQueueItem')

    #1) move new post activities
    # TYPE_ACTIVITY_MODERATED_NEW_POST = 24
    reason = ModerationReason.objects.get(title='New post')
    acts = Activity.objects.filter(activity_type=24)
    message = 'Copying "new post" Activity items to ModerationQueueItem'
    for act in ProgressBar(acts.iterator(), acts.count(), message):
        content_object = get_content_object(apps, act)
        ModerationQueueItem.objects.create(
                    reason=reason,
                    added_by=act.user,
                    added_at=act.active_at,
                    item_content_type=act.content_type,
                    item_id=act.object_id,
                    language_code=content_object.post.language_code,
                )

    #2) move post edit activities
    # TYPE_ACTIVITY_MODERATED_POST_EDIT = 25
    reason = ModerationReason.objects.get(title='Post edit')
    acts = Activity.objects.filter(activity_type=25)
    message = 'Copying "post edit" Activity items to ModerationQueueItem'
    for act in ProgressBar(acts.iterator(), acts.count(), message):
        content_object = get_content_object(apps, act)
        ModerationQueueItem.objects.create(
                    reason=reason,
                    added_by=act.user,
                    added_at=act.active_at,
                    item_content_type=act.content_type,
                    item_id=act.object_id,
                    language_code=content_object.post.language_code,
                )

    #3) move offensive flag activities
    # TYPE_ACTIVITY_MARK_OFFENSIVE = 14
    revision_content_type = get_contenttype(apps, 'postrevision')
    reason = ModerationReason.objects.get(title='Offensive')
    acts = Activity.objects.filter(activity_type=14)
    message = 'Copying "offensive" flags Activity items to ModerationQueueItem'
    for act in ProgressBar(acts.iterator(), acts.count(), message):
        post = get_content_object(apps, act)
        post_revision = get_post_revision_by_timestamp(post, act.active_at)
        if post_revision is None:
            # revision was lost - so we don't assign the flag
            # ideally user should run "fix revisionless posts" before
            # this migration
            continue

        ModerationQueueItem.objects.create(
                    reason=reason,
                    added_by=act.user,
                    added_at=act.active_at,
                    item_content_type=revision_content_type,
                    item_id=post_revision.pk,
                    language_code=post.language_code,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0016_init_moderation_reasons'),
    ]

    operations = [
        migrations.RunPython(move_mod_queue_items)
    ]
