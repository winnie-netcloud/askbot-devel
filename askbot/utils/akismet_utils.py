from akismet import Akismet, APIKeyError, AkismetError
from askbot.conf import settings as askbot_settings
from askbot import get_version
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from askbot.utils.html import site_url
from django.core.urlresolvers import reverse
import logging

def get_user_param(user, request, param_name):
    """Returns param name from user or request
    in that order of priority.
    Returns `None` if user is `None` and request.user is anonymous.
    """
    if user:
        return getattr(user, param_name)
    if request.user.is_anonymous():
        return None
    return getattr(request.user, param_name)

def akismet_check_spam(text, request, author=None):
    """Returns True if spam found, false if not,
    May raise exceptions if something is not right with
    the Akismet account/service/setup"""
    if not askbot_settings.USE_AKISMET:
        return False
    try:
        if askbot_settings.AKISMET_API_KEY.strip() == "":
            raise ImproperlyConfigured('You have not set AKISMET_API_KEY')

        data = {'comment_content': text}
        username = get_user_param(author, request, 'username')
        if username:
            data['comment_author'] = smart_str(username)

        email = get_user_param(author, request, 'email')
        if email:
            data['comment_author_email'] = email

        api = Akismet(key=askbot_settings.AKISMET_API_KEY,
                      blog_url=smart_str(site_url(reverse('questions'))))

        user_ip = request.META.get('REMOTE_ADDR')
        user_agent = request.environ['HTTP_USER_AGENT']
        return api.comment_check(user_ip, user_agent, **data)
    except APIKeyError:
        logging.critical('Akismet Key is missing')
    except AkismetError:
        logging.critical('Akismet error: Invalid Akismet key or Akismet account issue!')
    except Exception, e:
        logging.critical((u'Akismet error: %s' % unicode(e)).encode('utf-8'))
    return False
