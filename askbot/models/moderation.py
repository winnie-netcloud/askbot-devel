"""Models used for the moderation functionality"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext as _
from askbot.models.fields import LanguageCodeField

MODERATION_REASON_TYPES = (
    ('post_moderation', _('Reasons why posts are placed on the moderation queue')),
    # the  below items are to be used in the future
    ('user_moderation', _('Reasons why user profiles are moderated')),
    ('question_closure', _('Reasons why questions are closed'))
)
MANUALLY_ASSIGNABLE_HELP_TEXT = """Reasons that are not manually assignable
are only automatically assigned by the system
and should not be assigned by the users
via the user interface"""

class ModerationReason(models.Model):
    """Reason why a given item was placed on the queue.
    """
    #pylint: disable=no-init,too-few-public-methods
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('auth.User', null=True, blank=True)
    title = models.CharField(max_length=128)
    reason_type = models.CharField(max_length=32, choices=MODERATION_REASON_TYPES)
    description_html = models.TextField(null=True)  # html rendition of the input source
    description_text = models.TextField(null=True)  # could be markdown input source
    # is_predefined = True items are reserved for the pre-defined moderation reasons
    is_predefined = models.BooleanField(default=False)
    is_manually_assignable = models.BooleanField(default=True,
                                                 help_text=MANUALLY_ASSIGNABLE_HELP_TEXT)

    class Meta: #pylint: disable=missing-docstring,old-style-class
        app_label = 'askbot'
        verbose_name = 'moderation reason'
        verbose_name_plural = 'moderation reasons'


RESOLUTION_CHOICES = (
    ('waiting', _('Awaiting moderation')),
    ('upheld', _('Decision was upheld and the appropriate action was taken')),
    ('dismissed', _('Moderation memo was dismissed, no changes to the content')),
    ('followup', _('Moderation memo was accepted, but the final resolution '
                   'is made with a different reason'))
)

class ModerationQueueItem(models.Model):
    """Items that are displayed in the moderation queue(s)"""
    #pylint: disable=no-init,too-few-public-methods
    item_content_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = GenericForeignKey('item_content_type', 'item_id')
    reason = models.ForeignKey(ModerationReason, related_name='moderation_queue_items')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('auth.User', related_name='moderation_queue_items')

    # resolution status, timestamp and the user link provide some
    # audit trail to the moderation items and allow implementation
    # of undoing of the moderation decisions
    resolution_status = models.CharField(max_length=16,
                                         choices=RESOLUTION_CHOICES,
                                         default='waiting')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('auth.User', null=True, blank=True)
    followup_item = models.ForeignKey('self', related_name='origin_items',
                                      null=True, blank=True,
                                      help_text='Used if resolution_status is "followup"')
    language_code = LanguageCodeField()

    class Meta: #pylint: disable=no-init,old-style-class,missing-docstring
        app_label = 'askbot'
        verbose_name = 'moderation queue item'
        verbose_name_plural = 'moderation queue items'
