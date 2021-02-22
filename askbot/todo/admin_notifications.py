"""Bits of code sending notifications to the admin"""

def domain_is_bad():
    from askbot.conf import settings as askbot_settings
    parsed = urlparse(askbot_settings.APP_URL)
    if parsed.netloc == '':
        return True
    if parsed.scheme not in ('http', 'https'):
        return True
    return False


# notify admin to set the domain name if necessary
# todo: move this out to a separate middleware
if request.user.is_authenticated and request.user.is_administrator():
    if domain_is_bad():
        url = askbot_settings.get_setting_url(('QA_SITE_SETTINGS', 'APP_URL'))
        msg = _(
            'Please go to Settings -> %s '
            'and set the base url for your site to function properly'
        ) % url
        request.user.message_set.create(message=msg)
