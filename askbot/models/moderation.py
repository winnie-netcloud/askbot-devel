"""Models used for the moderation functionality"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.translation import ugettext as _
from askbot.models.fields import LanguageCodeField

MODERATION_REASON_TYPES = (
    ('post_moderation', _('Reasons why posts are placed on the moderation queue')),
    # the  below items are to be used in the future
    ('user_moderation', _('Reasons why user profiles are moderated')),
    ('question_closure', _('Reasons why questions are closed'))
)
MANUALLY_ASSIGNABLE_HELP_TEXT = """Reasons that are not manually assignable
can be assigned only by the system. Users should never assign them
via the user interface"""

def init_reason(**kwargs):
    if ModerationReason.objects.filter(title=kwargs['title']).exists():
        # todo: maybe update values
        return
    kwargs['description_html'] = u'<p>{}</p>'.format(kwargs['description_text'])
    ModerationReason.objects.create(**kwargs)

def init_reasons():
    """This method is used only by the testing module.
    These same moderation reasons are set up with migrations
    for the purposes of normal runs.
    """
    init_reason(
        title='Offensive',
        description_text='Post contains offensive language or sentiment',
        reason_type='post_moderation',
        is_predefined=True,
        is_manually_assignable=True
    )

    init_reason(
        title='New post',
        description_text='May be assigned automatically when someone creates a new post',
        reason_type='post_moderation',
        is_predefined=True,
        is_manually_assignable=False
    )

    init_reason(
        title='Post edit',
        description_text='Maybe be assigned automatically when someone edits a post',
        reason_type='post_moderation',
        is_predefined=True,
        is_manually_assignable=False
    )

    init_reason(
        title='Spam',
        description_text ='Post contains irrelevant or unsolicited content',
        reason_type='post_moderation',
        is_predefined=True,
        is_manually_assignable=True
    )

class ModerationReasonManager(models.Manager):
    def filter_as_dicts(self, order_by=None, **params):
        """Returns list of dictionaries of the moderation reasons"""
        items = self.get_queryset()
        items = items.filter(**params)
        if order_by:
            items = items.order_by(order_by)

        result = list()
        for item in items:
            result.append({
                'id': item.id,
                'title': item.title,
                'description_text': item.description_text,
                'is_predefined': item.is_predefined,
                'is_manually_assignable': item.is_manually_assignable,
                'reason_type': item.reason_type
            })

        return result

class ModerationReason(models.Model):
    """Reason why a given item was placed on the queue.
    """
    #pylint: disable=no-init,too-few-public-methods
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('auth.User', null=True, blank=True)
    title = models.CharField(max_length=128)
    reason_type = models.CharField(max_length=32, choices=MODERATION_REASON_TYPES)
    description_html = models.TextField(null=True) # html rendition of the input source
    description_text = models.TextField(null=True) # could be markdown input source
    # is_predefined = True items are reserved for the pre-defined moderation reasons
    is_predefined = models.BooleanField(default=False)
    is_manually_assignable = models.BooleanField(default=True,
                                                 help_text=MANUALLY_ASSIGNABLE_HELP_TEXT)

    objects = ModerationReasonManager()

    class Meta: #pylint: disable=missing-docstring,old-style-class
        app_label = 'askbot'
        verbose_name = 'moderation reason'
        verbose_name_plural = 'moderation reasons'

    def __unicode__(self):
        """Returns string representation of the item"""
        tpl = u'ModerationReason(title="{}", is_predefined={}, is_manually_assignable={})'
        return tpl.format(self.title,
                          self.is_predefined,
                          self.is_manually_assignable)

    def delete(self):
        if self.is_predefined:
            raise PermissionDenied('Cannot delete predefined moderation reasons')
        super(ModerationReason, self).delete()


RESOLUTION_CHOICES = (
    ('waiting', _('Awaiting moderation')),
    ('upheld', _('Decision was upheld and the appropriate action was taken')),
    ('dismissed', _('Moderation memo was dismissed, no changes to the content')),
    #('outdated', _('Moderation memo was dismissed because the content was changed thereafter')),
    ('followup', _('Moderation memo was accepted, but the final resolution '
                   'is made with a different reason'))
)

class ModerationQueueItem(models.Model):
    """Items that are displayed in the moderation queue(s)"""
    #pylint: disable=no-init,too-few-public-methods
    item_content_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = GenericForeignKey('item_content_type', 'item_id')
    item_author = models.ForeignKey('auth.User', related_name='authored_moderation_queue_items')
    reason = models.ForeignKey(ModerationReason, related_name='moderation_queue_items')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('auth.User', related_name='moderation_queue_items')

    # resolution status, timestamp and the user link provide some
    # audit trail to the moderation items and allow implementation
    # of undoing of the moderation decisions
    #
    # For the queue items of reason "New post", "Post edit":
    # * if the post or edit are accepted - the queue item is marked
    #   with resolution_status = 'dismissed' and the post/revision is published
    # * if the post/edit are rejected - resolution status is set to 'followup'
    # and a new Moderation queue item is created with any of the manually assignable
    # reasons and that queue item is immediately resolved by the same moderator.
    resolution_status = models.CharField(max_length=16,
                                         choices=RESOLUTION_CHOICES,
                                         default='waiting')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('auth.User', null=True, blank=True)
    origin_item = models.ForeignKey('self', related_name='followup_items',
                                    null=True, blank=True,
                                    help_text='Used for the followup items')
    followup_item = models.ForeignKey('self', related_name='origin_items',
                                      null=True, blank=True,
                                      help_text='Used if resolution_status is "followup"')
    language_code = LanguageCodeField()

    class Meta: #pylint: disable=no-init,old-style-class,missing-docstring
        app_label = 'askbot'
        verbose_name = 'moderation queue item'
        verbose_name_plural = 'moderation queue items'

    def create_followup_item(self, moderator, reason):
        """Returns an newly created item for the same content as the `self`
        with the provided reason. The status is set to 'upheld',
        the resolved_by - set to the value of `moderator`
        and the timestamp is set to current time value.
        """
        new_item = ModerationQueueItem()
        # system assigned items are deleted on moderation followup
        if self.reason.is_manually_assignable:
            new_item.origin_item = self
        new_item.item = self.item
        new_item.item_author_id = self.item_author_id
        new_item.reason = reason
        new_item.added_by = moderator
        new_item.resolution_status = 'upheld'
        new_item.resolved_at = timezone.now()
        new_item.resolved_by = moderator
        new_item.language_code = self.language_code
        new_item.save()
        return new_item

    def get_reason_title(self):
        """Returns title of the moderation reason"""
        #todo: cache the reasons
        return self.reason.title #pylint: disable=no-member

    def get_item_object_type(self):
        """Returns type of the object"""
        from askbot.models import PostRevision
        if self.item.__class__ == PostRevision:
            return self.item.post.post_type
        raise NotImplementedError

    def get_item_author(self):
        """Returns the User instance of the item author"""
        from askbot.models import PostRevision
        if self.item.__class__ == PostRevision:
            return self.item.author
        raise NotImplementedError

    def get_item_ip_address(self):
        """Returns ip address from where the item was posted"""
        from askbot.models import PostRevision
        if self.item.__class__ == PostRevision:
            return self.item.ip_addr
        raise NotImplementedError

    def get_item_timestamp(self):
        """Returns the DateTime objects of the item creation"""
        from askbot.models import PostRevision
        if self.item.__class__ == PostRevision:
            return self.item.revised_at
        raise NotImplementedError

    def get_item_headline(self):
        """Returns display info of the item"""
        from askbot.models import PostRevision
        if self.item.__class__ == PostRevision:
            title = self.reason.title.lower()
            params = {
                'post_type': self.get_item_object_type(),
                'flag_type': title
            }
            if self.reason.is_manually_assignable:
                return _('%(post_type)s flagged "%(flag_type)s"') % params
            if title == 'new post':
                return _('new %(post_type)s') % params
            elif title == 'post edit':
                return _('%(post_type)s edit') % params

        raise NotImplementedError

    def get_item_snippet(self):
        """Returns cleaned html snippet of the item"""
        from askbot.models import PostRevision
        if self.item.__class__ == PostRevision:
            return self.item.get_full_snippet(max_length=500, add_expander=True)
        raise NotImplementedError
