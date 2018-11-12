from django.core.management.base import NoArgsCommand
from askbot import const
from askbot.models import Activity
from askbot.models import PostFlag

ACTIVITY_TYPES = (
    const.TYPE_ACTIVITY_MODERATED_NEW_POST,
    const.TYPE_ACTIVITY_MODERATED_POST_EDIT
)

class Command(NoArgsCommand):
    help = 'deletes all items from the moderation queue'
    def handle_noargs(self, *args, **kwargs):
        acts = Activity.objects.filter(activity_type__in=ACTIVITY_TYPES)
        acts.delete()
        PostFlag.objects.all().delete()
