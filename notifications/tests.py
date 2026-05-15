from django.test import TestCase, Client
from django.utils import timezone
from users.models import User
from notifications.models import Notification
from django.utils import timezone
from questions.models import Question, Comment


class NotificationsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='notify_user',
            password='pass',
            email='n@example.com',
            sex=1,
            role='user',
            birth_date='2000-01-01',
            registration_date=timezone.now().date(),
            reputation=0,
            active=True
        )
        self.author = User.objects.create_user(
            username='author',
            password='pass',
            email='author@example.com',
            sex=1,
            role='user',
            birth_date='2000-01-01',
            registration_date=timezone.now().date(),
            reputation=0,
            active=True
        )

        self.other = User.objects.create_user(
            username='other',
            password='pass',
            email='other@example.com',
            sex=1,
            role='user',
            birth_date='2000-01-01',
            registration_date=timezone.now().date(),
            reputation=0,
            active=True
        )
        Notification.objects.create(
            user=self.user,
            text='Test notification',
            link='/',
            is_read=False,
            created_at=timezone.now()
        )
        self.question = Question.objects.create(
            title='Test post',
            description='Test description',
            author=self.author,
            rating=0,
            creation_date=timezone.now(),
        )

        self.comment = Comment.objects.create(
            text='Test comment',
            author=self.author,
            question=self.question,
            rating=0,
            creation_date=timezone.now(),
        )

    try:
        from notifications.models import Notification
        NOTIFICATIONS_ENABLED = True
    except ImportError:
        NOTIFICATIONS_ENABLED = False

    def test_notification_list(self):
        self.client.login(username='notify_user', password='pass')
        response = self.client.get(
            '/notifications/list/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('notifications', data)

    def test_notification_on_comment_to_others_post(self):
        self.client.login(username='other', password='pass')
        self.client.post(
            f'/question/{self.question.id}/', {'text': 'Test comment'})
        self.assertTrue(Notification.objects.filter(
            user=self.author,
            text__contains='комментарий'
        ).exists())

    def test_notification_on_reply_to_comment(self):
        self.client.login(username='other', password='pass')
        self.client.post(
            f'/comment/{self.comment.id}/answer/', {'text': 'Reply'})
        self.assertTrue(Notification.objects.filter(
            user=self.author,
            text__contains='ответил'
        ).exists())
