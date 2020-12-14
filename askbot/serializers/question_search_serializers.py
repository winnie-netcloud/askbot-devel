"""Serializers returning data for the list of questions."""
import operator
from rest_framework import serializers
from django.contrib.humanize.templatetags import humanize
from django.core.paginator import Paginator
from django.http import QueryDict
from django.urls import reverse
from django.utils import translation
from django.template.loader import get_template
from askbot import conf, models
from askbot.conf import settings as askbot_settings
from askbot.search.state_manager import SearchState
from askbot.templatetags import extra_tags
from askbot.views import context

class BaseQuestionSearchSerializer(serializers.Serializer):
    """Base class for the QuestionSearchSerializers"""

    def __init__(self, *args, **kwargs):
        super(BaseQuestionSearchSerializer, self).__init__(*args, **kwargs)
        self.request = kwargs['context']['request']
        self.user = self.request.user
        self.search_state = SearchState(user_logged_in=self.user.is_authenticated,
                                        **args[0])
        manager = models.Thread.objects
        threads, meta_data = manager.run_advanced_search(request_user=self.user,
                                                     search_state=self.search_state)
        self.meta_data = meta_data

        if meta_data['non_existing_tags']:
            self.search_state = self.search_state.remove_tags(meta_data['non_existing_tags'])

        self.paginator = Paginator(threads, self.search_state.page_size)
        if self.paginator.num_pages < self.search_state.page:
            self.search_state.page = 1
        self.page = self.paginator.page(self.search_state.page)
        self.page.object_list = list(self.page.object_list) # evaluate the queryset

        # INFO: Because for the time being we need question posts and thread authors
        #       down the pipeline, we have to precache them in thread objects
        manager.precache_view_data_hack(threads=self.page.object_list)


    def get_related_tags_data(self):
        """Returns data for the related tags"""
        related_tags = models.Tag.objects.get_related_to_search(
                            threads=self.page.object_list,
                            ignored_tag_names=self.meta_data.get('ignored_tag_names', [])
                        )
        tag_list_type = askbot_settings.TAG_LIST_FORMAT
        if tag_list_type == 'cloud': #force cloud to sort by name
            related_tags = sorted(related_tags, key=operator.attrgetter('name'))

        return related_tags


    def get_contributors_data(self):
        """Returns the filtered contributors data"""
        contributors = models.Thread.objects.get_thread_contributors(
                                        thread_list=self.page.object_list
                                    ).only('id', 'username',
                                           'askbot_profile__gravatar')
        return list(contributors)


    def get_paginator_context(self):
        """Returns context necessary to render the questions paginator."""
        return {
            'is_paginated' : (self.paginator.count > self.search_state.page_size),
            'pages': self.paginator.num_pages,
            'current_page_number': self.search_state.page,
            'page_object': self.page,
            'base_url' : self.search_state.query_string(),
            'page_size' : self.search_state.page_size
        }


    def get_rss_feed_url(self):
        """Returns url for the RSS feed"""
        #get url for the rss feed
        feed_url = reverse('latest_questions_feed')
        # We need to pass the rss feed url based
        # on the search state to the template.
        # We use QueryDict to get a querystring
        # from dicts and arrays. Much cleaner
        # than parsing and string formating.
        rss_query_dict = QueryDict("").copy()
        if self.search_state.query:
            # We have search string in session - pass it to
            # the QueryDict
            rss_query_dict.update({"q": self.search_state.query})

        if self.search_state.tags:
            # We have tags in session - pass it to the
            # QueryDict but as a list - we want tags+
            rss_query_dict.setlist('tags', self.search_state.tags)
            feed_url += '?' + rss_query_dict.urlencode()

        return feed_url


    def get_reset_method_count(self):
        """Returns number of search methods used (???)"""
        methods = [self.search_state.query,
                   self.search_state.tags,
                   self.meta_data.get('author_name', None)]

        return len([method for method in methods if method])


class PjaxQuestionSearchSerializer(BaseQuestionSearchSerializer):
    """Serializer for the data returned with the PJAX method
    In the older Jinja2 templates implementation.
    """
    def render_paginator_html(self):
        """Returns HTML of the questions paginator"""
        if self.paginator.count <= self.search_state.page_size:
            return ''

        paginator_tpl = get_template('main_page/paginator.html')
        return paginator_tpl.render({'context': self.get_paginator_context(),
                                     'questions_count': self.paginator.count,
                                     'page_size' : self.search_state.page_size,
                                     'search_state': self.search_state},
                                    self.request)


    def render_questions_html(self):
        """Returns HTML for the questions list"""
        questions_tpl = get_template('main_page/questions_loop.html')
        return questions_tpl.render({'threads': self.page,
                                     'search_state': self.search_state,
                                     'reset_method_count': self.get_reset_method_count(),
                                     'request': self.request},
                                    self.request)


    def render_related_tags_html(self, related_tags):
        """Returns HTML for the related tags snippet"""
        related_tags_tpl = get_template('widgets/related_tags.html')
        tag_list_type = askbot_settings.TAG_LIST_FORMAT
        related_tags_data = {
            'tags': related_tags,
            'tag_list_type': tag_list_type,
            'query_string': self.search_state.query_string(),
            'search_state': self.search_state,
            'language_code': translation.get_language(),
        }
        if tag_list_type == 'cloud':
            related_tags_data['font_size'] = extra_tags.get_tag_font_size(related_tags)

        return related_tags_tpl.render(related_tags_data, self.request)


    def get_humanized_question_count(self):
        """Text for the questions count"""
        count = self.paginator.count
        #todo: used customized words
        question_counter = translation.ungettext('%(q_num)s question', '%(q_num)s questions', count)
        return question_counter % {'q_num': humanize.intcomma(count),}


    def to_representation(self, _):
        """Searches for threads matching the parameters
        and returns instance of page, containing the
        results"""
        #contributors = self.get_contributors_data(self.page.object_list)
        ajax_data = {
            'query_data': {
                'tags': self.search_state.tags,
                'sort_order': self.search_state.sort,
                'ask_query_string': self.search_state.ask_query_string(),
            },
            'paginator': self.render_paginator_html(),
            'question_counter': self.get_humanized_question_count(),
            #'faces': [extra_tags.gravatar(contributor, 48) for contributor in contributors],
            'faces': [],
            'feed_url': self.get_rss_feed_url(),
            'query_string': self.search_state.query_string(),
            'page_size' : self.search_state.page_size,
            'questions': self.render_questions_html(),
            'non_existing_tags': self.meta_data['non_existing_tags'],
        }

        related_tags = self.get_related_tags_data()
        ajax_data['related_tags_html'] = self.render_related_tags_html(related_tags)

        #here we add and then delete some items
        #to allow extra context processor to work
        ajax_data['tags'] = related_tags
        ajax_data['interesting_tag_names'] = None
        ajax_data['threads'] = self.page
        extra_context = context.get_extra('ASKBOT_QUESTIONS_PAGE_EXTRA_CONTEXT',
                                          self.request,
                                          ajax_data)
        del ajax_data['tags']
        del ajax_data['interesting_tag_names']
        del ajax_data['threads']
        ajax_data.update(extra_context)
        return ajax_data


class Jinja2QuestionSearchSerializer(BaseQuestionSearchSerializer):
    """Question search serializer for the responses rendered
    into the Jinja2 templates."""

    def to_representation(self, *args, **kwargs):
        """Searches for threads matching the parameters
        and returns instance of page, containing the
        results"""
        related_tags = self.get_related_tags_data()
        template_data = {
            'active_tab': 'questions',
            'author_name' : self.meta_data.get('author_name', None),
            'contributors' : self.get_contributors_data(),
            'context' : self.get_paginator_context(),
            'is_unanswered' : False,#remove this from template
            'interesting_tag_names': self.meta_data.get('interesting_tag_names', None),
            'ignored_tag_names': self.meta_data.get('ignored_tag_names', None),
            'subscribed_tag_names': self.meta_data.get('subscribed_tag_names', None),
            'language_code': translation.get_language(),
            'name_of_anonymous_user' : models.get_name_of_anonymous_user(),
            'page_class': 'main-page',
            'page_size': self.search_state.page_size,
            'query': self.search_state.query,
            'threads' : self.page,
            'questions_count' : self.paginator.count,
            'reset_method_count': self.get_reset_method_count(),
            'scope': self.search_state.scope,
            'show_sort_by_relevance': conf.should_show_sort_by_relevance(),
            'search_tags' : self.search_state.tags,
            'sort': self.search_state.sort,
            'tab_id' : self.search_state.sort,
            'tags': self.get_related_tags_data(),
            'tag_list_type' : askbot_settings.TAG_LIST_FORMAT,
            'font_size' : extra_tags.get_tag_font_size(related_tags),
            'display_tag_filter_strategy_choices': conf.get_tag_display_filter_strategy_choices(),
            'email_tag_filter_strategy_choices': conf.get_tag_email_filter_strategy_choices(),
            'query_string': self.search_state.query_string(),
            'search_state': self.search_state,
            'feed_url': self.get_rss_feed_url()
        }

        extra_context = context.get_extra('ASKBOT_QUESTIONS_PAGE_EXTRA_CONTEXT',
                                          self.request,
                                          template_data)

        template_data.update(extra_context)
        template_data.update(context.get_for_tag_editor())
        return template_data
