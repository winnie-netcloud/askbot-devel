"""Deletes all items from the post moderation queue"""
from django.core.management.base import NoArgsCommand
from askbot.models import ModerationQueueItem

class Command(NoArgsCommand):
    #pylint: disable=missing-docstring
    help = 'deletes all items from the post moderation queue'
    def handle_noargs(self, *args, **kwargs): #pylint: disable=unused-argument, arguments-differ
        items = ModerationQueueItem.objects.filter( #pylint: disable=no-member
            reason__reason_type='post_moderation'
        )
        items.delete()
