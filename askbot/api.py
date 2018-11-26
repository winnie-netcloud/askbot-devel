"""place for the API calls into askbot
at this point most of the useful functions are still
in the askbot.models module, but
api must become a place to manupulate the data in the askbot application
so that other implementations of the data storage could be possible
"""
from django.db.models import Q
from askbot import models

def get_moderation_items_count(user):
    """returns count of items on the mod queue"""
    if user.is_anonymous():
        return None
    if not(user.is_moderator() or user.is_administrator()):
        return None

    items = models.ModerationQueueItem.objects.filter(#pylint: disable=no-member
        reason__reason_type='post_moderation')
    return items.count()


def get_admin(seed_user_id=None):
    """returns user objects with id == seed_user_id
    if the user with that id is not an administrator,
    the function will try to find another admin or moderator
    who has the smallest user id

    if the user is not found, or there are no moderators/admins
    User.DoesNotExist will be raised

    The reason this function is here and not on a manager of
    the user object is because we still patch the django-auth User table
    and it's probably better not to patch the manager
    """
    if seed_user_id:
        user = models.User.objects.get(id=seed_user_id)  # let it raise error here
        if user.is_administrator() or user.is_moderator():
            return user
    try:
        return models.User.objects.filter(
            Q(is_superuser=True) | Q(askbot_profile__status__in=('m', 'd'))
        ).order_by('id')[0]
    except IndexError:
        raise models.User.DoesNotExist( # pylint: disable=no-member
            """Please add a moderator or an administrator to the forum first
            there don't seem to be any"""
        )
