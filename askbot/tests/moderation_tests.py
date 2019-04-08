import json
from django.conf import settings as django_settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from askbot.tests.utils import AskbotTestCase, with_settings
from askbot.models import (ModerationReason, ModerationQueueItem, PostRevision)

def get_reason_id(reason_title):
    """Returns id of the moderation reason"""
    return ModerationReason.objects.get(title=reason_title).pk

class ModerationTests(AskbotTestCase):

    def setUp(self):
        self.ip_mod_setting_backup = django_settings.ASKBOT_IP_MODERATION_ENABLED
        django_settings.ASKBOT_IP_MODERATION_ENABLED = True

    def tearDown(self):
        django_settings.ASKBOT_IP_MODERATION_ENABLED = self.ip_mod_setting_backup

    @with_settings(MIN_REP_TO_FLAG_OFFENSIVE=0)
    def test_decline_question(self):
        author = self.create_user('author')
        flagger1 = self.create_user('flagger1')
        question = self.post_question(user=author)
        self.assertEqual(question.deleted, False)
        flagger1.flag_post(question)

        admin = self.create_user('admin', status='d')
        self.client.login(method='force', user_id=admin.id)

        mqi_before = ModerationQueueItem.objects.all()
        flag1 = mqi_before[0]

        self.assertEqual(flag1.item.revision, 1)

        data = {'action': 'decline-with-reason',
                'items': ['posts'],
                'reason': get_reason_id('Spam'),
                'item_ids': [flag1.id]}

        self.client.post(
            reverse('moderate_items'), 
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        flag1 = self.reload_object(flag1)

        #1) old flags are resolved
        self.assertEqual(flag1.resolution_status, 'followup')
        self.assertEqual(flag1.resolved_by, admin)
        # old flags have a common followup item
        # the followup item is upheld with reason "Spam"
        mod_item = ModerationQueueItem.objects.order_by('-id')[0]
        self.assertEqual(mod_item.pk, flag1.pk + 1)
        self.assertEqual(mod_item.resolution_status, 'upheld')
        self.assertEqual(mod_item.resolved_by, admin)
        self.assertEqual(mod_item.reason.title, 'Spam')

    @with_settings(CONTENT_MODERATION_MODE='premoderation')
    def test_block_users_and_ips(self):
        user1 = self.create_user('user1', status='w')
        user2 = self.create_user('user2', status='a')
        admin = self.create_user('admin', status='d')
        self.client.login(method='force', user_id=admin.id)
        question1 = self.post_question(user=user1, ip_addr='1.1.1.1')
        question2 = self.post_question(user=user1, ip_addr='2.2.2.2')
        question3 = self.post_question(user=user2, ip_addr='2.2.2.2')
        question4 = self.post_question(user=user2, ip_addr='3.3.3.3')

        # first two questions were put on the queue
        mqi = ModerationQueueItem.objects.order_by('id')
        self.assertEqual(mqi.count(), 2)

        self.assertEqual(mqi[0].item, question1.current_revision)
        self.assertEqual(mqi[1].item, question2.current_revision)

        data = {'action': 'block',
                'items': ['posts', 'users', 'ips'],
                'item_ids': [mqi[0].id]}

        mqi_ids = list(mqi.values_list('pk', flat=True))

        self.client.post(
            reverse('moderate_items'), 
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # original queue items are deleted
        self.assertEqual(ModerationQueueItem.objects.filter(pk__in=mqi_ids).count(), 0)
        self.assertEqual(ModerationQueueItem.objects.count(), 2)
        self.assertEqual(ModerationQueueItem.objects.filter(reason__title='Spam').count(), 2)

        # all questions are deleted
        question1 = self.reload_object(question1)
        self.assertEqual(question1.deleted, True)
        question2 = self.reload_object(question2)
        self.assertEqual(question2.deleted, True)
        question3 = self.reload_object(question3)
        self.assertEqual(question3.deleted, True)
        question4 = self.reload_object(question4)
        self.assertEqual(question4.deleted, True)

        # user1 and user2 are blocked
        user1 = self.reload_object(user1)
        self.assertEqual(user1.askbot_profile.status, 'b')
        user2 = self.reload_object(user2)
        self.assertEqual(user2.askbot_profile.status, 'b')
        # all ips are blocked

        from stopforumspam.models import Cache
        ips = Cache.objects.all()
        self.assertEqual(ips.count(), 3)
        ips = ips.values_list('ip', flat=True)
        self.assertEqual(set(ips), set(['1.1.1.1', '2.2.2.2', '3.3.3.3']))


    @with_settings(
        CONTENT_MODERATION_MODE='premoderation',
        MIN_REP_TO_EDIT_OTHERS_POSTS=0
    )
    def test_decline_new_answer_revision_as_spam(self):
        user1 = self.create_user('user1', status='w')
        user2 = self.create_user('user2', status='w')
        admin = self.create_user('admin', status='d')
        self.client.login(method='force', user_id=admin.id)
        #1) post question and approve it
        question = self.post_question(user=user1)
        self.assertEqual(question.approved, False)
        self.assertEqual(question.thread.approved, False)
        self.assertEqual(question.revisions.count(), 1)
        # first revision has zero number, b/c it is not yet approved
        self.assertEqual(question.revisions.all()[0].revision, 0)

        ct = ContentType.objects.get_for_model(PostRevision)
        mqi = ModerationQueueItem.objects.filter(
            item_content_type=ct,
            item_id=question.revisions.all()[0].id
        )
        self.assertEqual(mqi.count(), 1)
        self.assertEqual(mqi[0].resolution_status, 'waiting')

        item_id = mqi[0].id

        data = {'action': 'approve',
                'items': ['posts', 'users'],
                'item_ids': [item_id]}
        self.client.post(
            reverse('moderate_items'), 
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        mqi = ModerationQueueItem.objects.filter(pk=item_id)
        self.assertEqual(mqi.count(), 0)

        question = self.reload_object(question)
        self.assertEqual(question.approved, True)
        self.assertEqual(question.thread.approved, True)
        self.assertEqual(question.revisions.count(), 1)
        # first revision has non-zero number
        self.assertEqual(question.revisions.all()[0].revision, 1)

        user1 = self.reload_object(user1)
        self.assertEqual(user1.askbot_profile.status, 'a')

        #2) post answer and approve it
        answer = self.post_answer(question=question, user=user1)
        self.assertEqual(answer.approved, False)
        self.assertEqual(answer.revisions.count(), 1)
        # first revision has zero number
        self.assertEqual(answer.revisions.all()[0].revision, 0)

        mqi = ModerationQueueItem.objects.filter(
            item_content_type=ct,
            item_id=answer.revisions.all()[0].id
        )
        self.assertEqual(mqi.count(), 1)
        self.assertEqual(mqi[0].resolution_status, 'waiting')

        item_id = mqi[0].id

        data = {'action': 'approve',
                'items': ['posts'],
                'item_ids': [item_id]}
        self.client.post(
            reverse('moderate_items'), 
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        mqi = ModerationQueueItem.objects.filter(pk=item_id)
        answer = self.reload_object(answer)
        self.assertEqual(answer.approved, True)
        self.assertEqual(answer.revisions.count(), 1)
        # first revision has zero number
        self.assertEqual(answer.revisions.all()[0].revision, 1)

        #3) edit answer
        self.edit_answer(answer=answer, user=user2)
        answer = self.reload_object(answer)
        self.assertEqual(answer.approved, True)
        self.assertEqual(answer.revisions.count(), 2)
        # last revision has zero revision number
        latest_rev = answer.revisions.order_by('-id')[0]
        self.assertEqual(latest_rev.revision, 0)

        mod_item = ModerationQueueItem.objects.get(
            item_content_type=ct,
            item_id=latest_rev.id,
            resolution_status='waiting'
        )
        self.assertEqual(mod_item.reason.title, 'Post edit')

        #4) block latest answer edit as spam
        data = {'action': 'decline-with-reason',
                'items': ['posts'],
                'reason': get_reason_id('Spam'),
                'item_ids': [mod_item.id]}
        self.client.post(
            reverse('moderate_items'), 
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        answer = self.reload_object(answer)
        self.assertTrue(answer.deleted, True)
        self.assertEqual(answer.revisions.count(), 2)
        latest_rev = answer.revisions.order_by('-id')[0]
        self.assertEqual(latest_rev.revision, 0)

        mod_items = ModerationQueueItem.objects.filter(
            item_content_type=ct,
            item_id=latest_rev.id
        )
        self.assertEqual(mod_items.count(), 1)

        self.assertEqual(mod_items[0].resolution_status, 'upheld')
        self.assertEqual(mod_items[0].reason.title, 'Spam')

    @with_settings(MIN_REP_TO_FLAG_OFFENSIVE=0)
    def test_delete_moderation_reason(self):
        user = self.create_user('user', status='w')
        question = self.post_question(user=user)
        admin = self.create_user('admin', status='d')

        reason_params = {'added_by': admin,
                         'reason_type': 'post_moderation',
                         'title': 'blablabla',
                         'description_text': 'blahblah'}

        reason = ModerationReason.objects.create(**reason_params)
        user.flag_post(post=question, reason=reason)
        question = self.reload_object(question)
        self.assertEqual(question.offensive_flag_count, 1)

        self.client.login(method='force', user_id=admin.id)
        response = self.client.post(
            reverse('delete_moderation_reason'), 
            data={'reason_id': reason.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = json.loads(response.content)
        self.assertEqual(data['deleted'], True)
        question = self.reload_object(question)
        self.assertEqual(question.offensive_flag_count, 0)
        reasons = ModerationReason.objects.filter(pk=reason.pk)
        self.assertEqual(reasons.count(), 0)
