from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext as _
from askbot.models.fields import LanguageCodeField

MODERATION_REASON_TYPES = (
    ('post_moderation', _('Reasons why posts are placed on the moderation queue')),
    ('post_rejection', _('Reasons why posts are rejected')),
    # the  below items are to be used in the future
    ('user_moderation', _('Reasons why user profiles are moderated')),
    ('question_closure', _('Reasons why questions are closed'))
)

class ModerationReason(models.Model):
    """Reason why a given item was placed on the queue.
    """
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('auth.User', null=True)
    title = models.CharField(max_length=128)
    reason_type = models.CharField(max_length=32, choices=MODERATION_REASON_TYPES)
    description_html = models.TextField(null=True)  # html rendition of the input source
    description_text = models.TextField(null=True)  # could be markdown input source
    # is_predefined = True items are reserved for the pre-defined moderation reasons
    is_predefined = models.BooleanField(default=False)

    class Meta:
        app_label = 'askbot'
        verbose_name = 'moderation reason'
        verbose_name_plural = 'moderation reasons'


class ModerationQueueItem(models.Model):
    item_content_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = GenericForeignKey('item_content_type', 'item_id')
    reason = models.ForeignKey(ModerationReason, related_name='moderation_queue_items')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('auth.User', related_name='moderation_queue_items')
    language_code = LanguageCodeField() 

    class Meta:
        app_label = 'askbot'
        verbose_name = 'moderation queue item'
        verbose_name_plural = 'moderation queue items'
