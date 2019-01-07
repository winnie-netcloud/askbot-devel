from askbot.utils import decorators
from askbot.utils.html import sanitize_html
from askbot.utils.functions import decode_and_loads
from askbot import const
from askbot.conf import settings as askbot_settings
from askbot import models
from askbot import mail
from django.http import Http404
from django.utils.translation import string_concat
from django.utils.translation import ungettext
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.encoding import force_text
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators import csrf
from django.utils.encoding import force_text
from django.utils import timezone
from django.core import exceptions
import simplejson

#some utility functions
def get_object(mod_item):
    item = mod_item.item
    if isinstance(item, models.PostRevision):
        return item.post
    return item

def get_queue_items_for_user(user):
    """Returns moderation queue items matching
    the user's languages"""
    return models.ModerationQueueItem.objects.filter(
        language_code__in=user.get_languages(),
        resolution_status='waiting'
    )


def get_revision_set(item_set):
    """returns revisions given the item_set"""
    rev_ids = set()
    for item in item_set:
        obj = item.item
        if isinstance(obj, models.PostRevision):
            rev_ids.add(obj.id)
    return models.PostRevision.objects.filter(id__in=rev_ids)


def expand_revision_set(revs):
    """returns expanded set of post revisions,
    seeded by the list of ips and user ids
    received from the `revs` revision set"""
    #1) get post edits and ips from them
    ips, user_ids = get_revision_ips_and_author_ids(revs)
    #2) get revs by those ips and users
    revs_filter = Q(ip_addr__in=ips) | Q(author_id__in=user_ids)
    more_revs = models.PostRevision.objects.filter(revs_filter)

    #return ips and users when number of revisions loaded by
    #users and ip addresses stops growing
    diff_count = more_revs.count() - revs.count()
    if diff_count == 0:
        return revs
    elif diff_count > 0:
        return expand_revision_set(more_revs)
    else:
        raise ValueError('expanded revisions set smaller then the original')


def get_revision_ips_and_author_ids(revs):
    """returns sets of ips and users from revisions"""
    ips = set(revs.values_list('ip_addr', flat=True))
    user_ids = set(revs.values_list('author_id', flat=True))
    return ips, user_ids 


def get_queue_item_ids_for_revisions(revs, user):
    rev_ct = ContentType.objects.get_for_model(models.PostRevision)
    rev_ids = revs.values_list('id', flat=True)
    mod_items = models.ModerationQueueItem.objects.filter(
        language_code__in=user.get_languages(),
        resolution_status='waiting',
        item_content_type=rev_ct,
        item_id__in=rev_ids
    )
    return list(mod_items.values_list('pk', flat=True))


MOD_IDS = set()
def get_mod_ids():
    """Returns user ids of moderators
    and administrators"""
    mods = models.UserProfile.objects.filter(status__in=('d', 'm'))
    return set(mods.values_list('pk', flat=True))


def exclude_admins(user_ids):
    """Returns set of user ids excluding ids
    of admins or moderators"""
    global MOD_IDS
    if not MOD_IDS:
        MOD_IDS = get_mod_ids()
    return set(user_ids) - MOD_IDS


def get_author_ids(items):
    """Returns user ids of the item authors"""
    return items.values_list('item_author_id', flat=True)


def concat_messages(message1, message2):
    if message1:
        message = string_concat(message1, ', ')
        return string_concat(message, message2)
    else:
        return message2


def approve_posts(admin, mod_items):
    """mod approves revisions in mod_items
    and returns number of approved posts.
    At the same time removes all other flags on the post.
    """
    num_posts = 0
    for item in mod_items:
        if not isinstance(item.item, models.PostRevision):
            continue
        admin.approve_post_revision(item.item)
        admin.flag_post(item.item.post, cancel_all=True, force=True)
        num_posts += 1

    return num_posts


def handle_decline_action(admin, item_set, reason_id):
    """Declines posts with a reason"""
    reason = models.ModerationReason.objects.get(pk=reason_id)
    # get unique posts from the mod queue items
    posts = set([get_object(item) for item in item_set])
    from askbot.mail.messages import RejectedPost
    result = {'declined_posts': 0,
              'item_ids': list()}
    for post in posts:
        admin.delete_post(post)
        #todo: bunch notifications - one per recipient
        email = RejectedPost({
                    'post': post.html,
                    'reject_reason': reason.description_html
                })
        email.send([post.author.email,])
        result['declined_posts'] += 1

    for item in item_set:
        result['item_ids'].append(item.pk)
        followup_item = item.create_resolved_item(admin, reason)
        if item.reason.is_manually_assignable:
            item.resolution_status = 'followup'
            item.resolved_at = timezone.now()
            item.resolved_by = admin
            item.followup_item = followup_item
            item.save()
        else:
            # system-assigned original items are deleted
            item.delete()

    return result


def handle_block_ips_action(admin, item_set, remote_addr):
    """Blocks the ip addresses"""
    revs = get_revision_set(item_set)
    # expand set of revisions via the set of the ip addresses
    revs = expand_revision_set(revs)

    ips, user_ids = get_revision_ips_and_author_ids(revs)

    result = dict()
    result['blocked_ips'] = block_ips(ips, remote_addr)
    result['item_ids'] = get_queue_item_ids_for_revisions(revs, admin)

    user_ids -= set([admin.pk])
    result['blocked_users'] = models.UserProfile.objects.filter(pk__in=user_ids).update(status='b')

    post_count = 0
    for user in models.User.objects.filter(pk__in=user_ids):
        #delete all content by the user
        post_count += admin.delete_users_content(user, mark_spam=True)

    result['deleted_posts'] = post_count
    return result


def handle_block_users_action(admin, item_set):
    result = {'blocked_users': 0,
              'deleted_posts': 0,
              'item_ids': list(item_set.values_list('pk', flat=True))}
    set_users_statuses(admin, item_set, 'b')
    author_ids = exclude_admins(get_author_ids(item_set))
    for user in models.User.objects.filter(pk__in=author_ids):
        #delete all content by the user
        result['deleted_posts'] += admin.delete_users_content(user, mark_spam=True)
        result['blocked_users'] += 1

    #todo: create blocked user moderation items
    return result


def handle_block_action(admin, item_set, item_types, remote_addr):
    moderate_ips = django_settings.ASKBOT_IP_MODERATION_ENABLED
    # If we block by IPs we always block users and posts
    # so we use a "spider" algorithm to find posts, users and IPs to block.
    # once we find users, posts and IPs, we block all of them summarily.
    if moderate_ips and 'ips' in item_types:
        assert('users' in item_types)
        assert('posts' in item_types)
        assert(len(item_types) == 3)
        return handle_block_ips_action(admin, item_set, remote_addr)

    if 'users' in item_types:
        return handle_block_users_action(admin, item_set)

    raise ValueError('unexpected item types {}'.format(str(item_set)))


def block_ips(ips, current_ip):
    #to make sure to not block the admin and
    #in case REMOTE_ADDR is a proxy server - not
    #block access to the site
    good_ips = set(django_settings.ASKBOT_WHITELISTED_IPS)
    good_ips.add(current_ip)
    ips = ips - good_ips

    #block IPs
    from stopforumspam.models import Cache
    already_blocked = Cache.objects.filter(ip__in=ips)
    already_blocked.update(permanent=True)
    already_blocked_ips = already_blocked.values_list('ip', flat=True)
    ips = ips - set(already_blocked_ips)
    for ip in ips:
        cache = Cache(ip=ip, permanent=True)
        cache.save()

    return len(ips)


def set_users_statuses(admin, item_set, status):
    user_ids = exclude_admins(get_author_ids(item_set))
    user_ids -= set([admin.pk])
    return models.UserProfile.objects.filter(pk__in=user_ids).update(status=status)


@login_required
def moderation_queue(request):
    """Lists moderation queue items"""
    if not request.user.is_administrator_or_moderator():
        raise Http404

    #1) get queue items
    queue_items = get_queue_items_for_user(request.user)
    queue_items = queue_items.order_by('-added_at')

    #3) "package" data for the output
    queue = list()
    for queue_item in queue_items:
        if queue_item.item is None:
            queue_item.delete()
            continue#a temp plug due to a bug in the comment deletion

        queue.append(queue_item)

    moderation_reasons = models.ModerationReason.objects.filter_as_dicts(
        reason_type='post_moderation',
        is_manually_assignable=True,
        order_by='title'
    )

    data = {
        'active_tab': 'users',
        'page_class': 'moderation-queue-page',
        'moderation_reasons': list(moderation_reasons),
        'queue_items' : queue,
    }
    return render(request, 'moderation/queue.html', data)


def check_permissions(request):
    if request.user.is_anonymous():
        raise exceptions.PermissionDenied()
    if not request.user.is_administrator_or_moderator():
        raise exceptions.PermissionDenied()


def expand_item_set(item_set):
    author_ids = exclude_admins(get_author_ids(item_set))
    # get moderation queue items corresponding to
    # the authors of the ModerationQueueItem.item
    items_filter = {'item_author_id__in': author_ids, 'resolution_status': 'waiting'}
    return item_set | models.ModerationQueueItem.objects.filter(**items_filter)


# not a view function
def handle_approve_action(admin, item_set, item_types):
    """Approves posts or users"""
    result = dict()
    if 'posts' in item_types:
        # approve all unapproved posts
        result['approved_posts'] = approve_posts(admin, item_set)

    if 'users' in item_types:
        result['approved_users'] = set_users_statuses(admin, item_set, 'a')

    result['item_ids'] = list(item_set.values_list('pk', flat=True))
            
    # manually assigned items are marked as dismissed
    manually_assigned_items = item_set.filter(reason__is_manually_assignable=True)
    manually_assigned_items.update(resolution_status='dismissed',
                                   resolved_by=admin,
                                   resolved_at=timezone.now())

    # delete system assigned items like new post/revisions
    system_assigned_items = item_set.filter(reason__is_manually_assignable=False)
    system_assigned_items.delete()
    return result


def format_message(result):
    """Returns message to be displayed to the moderator"""
    message = ''
    deleted_posts = result.get('deleted_posts', 0)
    if deleted_posts:
        message = ungettext('%d post deleted', '%d posts deleted', deleted_posts) % deleted_posts 

    approved_posts = result.get('approved_posts', 0)
    if approved_posts:
        msg = ungettext('%d post approved', '%d posts approved', approved_posts) % approved_posts 
        message = concat_messages(message, msg)

    approved_users = result.get('approved_users', 0)
    if approved_users:
        msg = ungettext('%d user approved', '%d users approved', approved_users) % approved_users
        message = concat_messages(message, msg)

    blocked_ips = result.get('blocked_ips', 0)
    if blocked_ips:
        msg = ungettext('%d ip blocked', '%d ips blocked', blocked_ips) % blocked_ips
        message = concat_messages(message, msg)

    blocked_users = result.get('blocked_users', 0)
    if blocked_users:
        msg = ungettext('%d user blocked', '%d users blocked', blocked_users) % blocked_users
        message = concat_messages(message, msg)

    return force_text(message)


@csrf.csrf_protect
@decorators.post_only
@decorators.ajax_only
def moderate_items(request):
    check_permissions(request)

    #{'action': 'decline-with-reason', 'items': ['posts'], 'reason': 1, 'edit_ids': [827]}
    post_data = decode_and_loads(request.body)
    item_set = models.ModerationQueueItem.objects.filter(id__in=post_data['item_ids'])

    if post_data['action'] in ('block', 'approve') and 'users' in post_data['items']:
        # if we are approving or declining users we need to expand the item_set
        # to all of their content
        item_set = expand_item_set(item_set)

    action = post_data['action']
    if action == 'approve':
        result = handle_approve_action(request.user, item_set, post_data['items'])

    elif action == 'decline-with-reason':
        result = handle_decline_action(request.user, item_set, post_data['reason'])

    elif action == 'block':
        remote_addr = request.META['REMOTE_ADDR']
        result = handle_block_action(request.user, item_set, post_data['items'], remote_addr)

    else:
        raise ValueError('unexpected action {}'.format(action))

    result['message'] = format_message(result)

    #delete items from the moderation queue
    request.user.update_response_counts()
    result['item_count'] = request.user.get_notifications(const.MODERATED_ACTIVITY_TYPES).count()
    return result
