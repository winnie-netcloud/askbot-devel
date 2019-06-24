=================================
Settings for ``settings.py`` file
=================================

* ``ALLOW_UNICODE_SLUGS`` - if ``True``, slugs will use unicode, default - ``False``
* ``ASKBOT_DELAYED_EMAIL_ALERTS_CUTOFF_TIMESTAMP`` - a datetime isnstance, useful
  when enabling email alerts on a site with a lot of existing content.
  This prevents spamming users with update alerts on content created
  long before the perioding email alerts were enabled.

There are more settings that are not documented yet,
but most are described in the ``settings.py`` template:

    askbot/setup_templates/settings.py.mustache

TODO: describe all of them here.
