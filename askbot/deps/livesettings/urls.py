try:
    from django.conf.urls import *
except ImportError:
    from django.conf.urls.defaults import *

from askbot.deps.livesettings import views as LivesettingsViews

urlpatterns = [
    url(r'^$', LivesettingsViews.site_settings, {}, name='site_settings'),
    url(r'^export/$', LivesettingsViews.export_as_python, {}, name='settings_export'),
    url(r'^(?P<group>[^/]+)/$', LivesettingsViews.group_settings, name='group_settings'),
]
