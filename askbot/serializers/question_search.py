"""Serializers returning data for the list of questions."""
from rest_framework import serializers
from django.core.paginator import Paginator
from django.http import QueryDict
from django.urls import reverse
from askbot import models
from askbot.conf import settings as askbot_settings
from askbot.search.state_manager import SearchState
from askbot.templatetags import extra_tags
from askbot.utils.functions import get_epoch_seconds

class QuestionSearchSerializer(serializers.Serializer):
    """Base class for the QuestionSearchSerializers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


    def serialize_related_tags(self):
        """Returns list of tags data as dictionary"""
        related_tags = models.Tag.objects.get_related_to_search(
                            threads=self.page.object_list,
                            ignored_tag_names=self.meta_data.get('ignored_tag_names', [])
                        )
        result = list()
        for tag in related_tags:
            result.append({'id': tag.id,
                           'name': tag.name,
                           'used_count': tag.local_used_count})
        return result


    def get_contributors_data(self):
        """Returns the filtered contributors data"""
        users = models.Thread.objects.get_thread_contributors(
                                        thread_list=self.page.object_list
                                    ).only('id', 'username',
                                           'askbot_profile__gravatar')
        data = list()
        for user in users:
            data.append({'id': user.id,
                         'username': user.username,
                         'avatar_url': user.askbot_profile.gravatar})

        return data


    def get_related_tags_data(self):
        """Returns data necessary to render tags related to search."""
        tags_data = self.serialize_related_tags()
        tag_list_type = askbot_settings.TAG_LIST_FORMAT
        if tag_list_type == 'cloud':
            related_tags = sorted(related_tags, key='name')
            font_sizes = extra_tags.get_tag_font_size(related_tags)
            for data in tags_data:
                data['font_size'] = font_sizes[data['name']]

        return tags_data


    def get_threads_data(self):
        """Returns serialized threads data"""
        threads = self.page.object_list
        data = list()
        for thread in threads:
            author_id, author_name, timestamp = thread.get_public_last_activity_info(self.request.user)
            data.append({'id': thread.id,
                         'answer_count': thread.answer_count,
                         'closed': thread.closed,
                         'has_accepted_answer': thread.has_accepted_answer(),
                         'last_activity_at': get_epoch_seconds(timestamp),
                         'last_activity_by_id': author_id,
                         'last_activity_by_username': author_name,
                         'tag_names': thread.get_tag_names(),
                         'title': thread.title,
                         'view_count': thread.view_count,
                         'vote_count': thread._question_post().score
                        })
        return data


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


    def to_representation(self, _):
        """Searches for threads matching the parameters
        and returns instance of page, containing the
        results"""
        return {
            'contributors': self.get_contributors_data(),
            'feed_url': self.get_rss_feed_url(),
            'non_existing_tags': self.meta_data['non_existing_tags'],
            'num_pages': self.paginator.num_pages,
            'num_threads': self.paginator.count,
            'page': self.search_state.page,
            'query_data': self.search_state.as_dict(),
            'query_string': self.search_state.query_string(),
            'related_tags': self.get_related_tags_data(),
            'tag_list_type': askbot_settings.TAG_LIST_FORMAT,
            'threads': self.get_threads_data(),
        }
