from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
import simplejson
from django.db.models import Q
from django.urls import reverse
from askbot import models
from askbot.models import User, UserProfile
from askbot.conf import settings as askbot_settings
from askbot.search.state_manager import SearchState
from askbot.utils.html import site_url
from askbot.utils.functions import get_epoch_str

def get_user_data(user):
    """get common data about the user"""
    avatar_url = user.get_avatar_url()
    if not ('gravatar.com' in avatar_url):
        avatar_url = site_url(avatar_url)

    return {
        'id': user.id,
        'avatar': avatar_url,
        'username': user.username,
        'joined_at': get_epoch_str(user.date_joined),
        'last_seen_at': get_epoch_str(user.last_seen),
        'reputation': user.reputation,
        'gold': user.gold,
        'silver': user.silver,
        'bronze': user.bronze,
    }

def get_question_data(thread):
    """returns data dictionary for a given thread"""
    question_post = thread._question_post()
    datum = {
        'added_at': get_epoch_str(thread.added_at),
        'id': question_post.id,
        'answer_count': thread.answer_count,
        'answer_ids': thread.get_answer_ids(),
        'accepted_answer_id': thread.accepted_answer_id,
        'view_count': thread.view_count,
        'score': thread.score,
        'last_activity_at': get_epoch_str(thread.last_activity_at),
        'title': thread.title,
        'summary': question_post.summary,
        'tags': thread.tagnames.strip().split(),
        'url': site_url(thread.get_absolute_url()),
    }
    datum['author'] = {
        'id': thread._question_post().author.id,
        'username': thread._question_post().author.username
    }
    datum['last_activity_by'] = {
        'id': thread.last_activity_by.id,
        'username': thread.last_activity_by.username
    }
    return datum

def info(request):
    '''
       Returns general data about the forum
    '''
    data = {}
    posts = models.Post.objects.filter(deleted=False)
    data['answers'] = posts.filter(post_type='answer').count()
    data['questions'] = posts.filter(post_type='question').count()
    data['comments'] = posts.filter(post_type='comment').count()
    data['users'] = User.objects.filter(is_active=True).count()

    if askbot_settings.GROUPS_ENABLED:
        data['groups'] = models.Group.objects.exclude_personal().count()
    else:
        data['groups'] = 0

    json_string = simplejson.dumps(data)
    return HttpResponse(json_string, content_type='application/json')

def user(request, user_id):
    '''
       Returns data about one user
    '''
    user = get_object_or_404(User, pk=user_id)
    data = get_user_data(user)
    posts = models.Post.objects.filter(author=user, deleted=False)
    data['answers'] = posts.filter(post_type='answer').count()
    data['questions'] = posts.filter(post_type='question').count()
    data['comments'] = posts.filter(post_type='comment').count()
    json_string = simplejson.dumps(data)
    return HttpResponse(json_string, content_type='application/json')


def users(request):
    '''
       Returns data of the most active or latest users.
    '''
    allowed_sort_map = { #GET value -> Django query
      'recent'    : '-pk__date_joined',
      'oldest'    : 'pk__date_joined',
      'reputation': '-reputation',
      'username'  : 'pk__username'
    }

    page = request.GET.get("page", '1')
    sort = request.GET.get('sort', 'reputation')

    try:
        page = int(page)
        order_by = allowed_sort_map[sort]
    except ValueError: # cast failed
        page = 1
    except KeyError:   # lookup failed
        raise Http404

    profiles = UserProfile.objects.exclude(status='b').order_by('-reputation')

    #FIXME: Shouldn't we reuse profiles here?
    #FIXME: Does this cause 2 DB querys? Should we merge the following 2 lines?
    user_ids = UserProfile.objects.values_list('pk', flat=True)
    users = User.objects.filter(id__in=user_ids).order_by('id')

    paginator = Paginator(users, 10)

    try:
        user_objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        user_objects = paginator.page(paginator.num_pages)

    user_list = []
    #serializing to json
    for user in user_objects:
        user_dict = get_user_data(user)
        user_list.append(dict.copy(user_dict))

    response_dict = {
                'pages': paginator.num_pages,
                'count': paginator.count,
                'users': user_list
            }
    json_string = simplejson.dumps(response_dict)

    return HttpResponse(json_string, content_type='application/json')


def question(request, question_id):
    '''
    Gets a single question
    '''
    #we retrieve question by post id, b/c that's what is in the url,
    #not thread id (currently)
    post = get_object_or_404(
        models.Post, id=question_id,
        post_type='question', deleted=False
    )
    datum = get_question_data(post.thread)
    json_string = simplejson.dumps(datum)
    return HttpResponse(json_string, content_type='application/json')


def questions(request):
    """
    List of Questions, Tagged questions, and Unanswered questions.
    matching search query or user selection
    """
    try:
        author_id = int(request.GET.get("author"))
    except (ValueError, TypeError):
        author_id = None

    try:
        page = int(request.GET.get("page"))
    except (ValueError, TypeError):
        page = None

    search_state = SearchState(
                scope=request.GET.get('scope', 'all'),
                sort=request.GET.get('sort', 'activity-desc'),
                query=request.GET.get('query', None),
                tags=request.GET.get('tags', None),
                author=author_id,
                page=page,
                user_logged_in=request.user.is_authenticated,
            )

    qs, meta_data = models.Thread.objects.run_advanced_search(
                        request_user=request.user, search_state=search_state
                    )
    if meta_data['non_existing_tags']:
        search_state = search_state.remove_tags(meta_data['non_existing_tags'])

    #exludes the question from groups
    #global_group = models.Group.objects.get_global_group()
    #qs = qs.exclude(~Q(groups__id=global_group.id))

    page_size = askbot_settings.DEFAULT_QUESTIONS_PAGE_SIZE
    paginator = Paginator(qs, page_size)
    if paginator.num_pages < search_state.page:
        search_state.page = 1
    page = paginator.page(search_state.page)

    question_list = list()
    for thread in page.object_list:
        datum = get_question_data(thread)
        question_list.append(datum)

    ajax_data = {
        'count': paginator.count,
        'pages' : paginator.num_pages,
        'questions': question_list
    }
    response_data = simplejson.dumps(ajax_data)
    return HttpResponse(response_data, content_type='application/json')
