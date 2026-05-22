import datetime

from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from .models import Complaint
from questions.models import Question, Comment


class MessagesTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@abc.abc',
            password='password123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now()
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@abc.abc',
            password='password123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now()
        )

        self.banned = User.objects.create_user(
            username='banned',
            email='banned@abc.abc',
            password='password123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now(),
            active=False
        )

        self.question = Question.objects.create(
            author=self.user2,
            title="вопрос",
            description='.',
            creation_date=datetime.datetime.now(),
            images='.',
            rating=0
        )
        self.comment = Comment.objects.create(author=self.user2, text="комментарий", question=self.question, rating=0,
                                              creation_date=datetime.datetime.now())

        self.client = Client()
        self.client.login(username='user1', password='password123')

        self.url = reverse('complaint')

    def test_complaint_on_question_created(self):
        response = self.client.post(f"{self.url}?question_id={self.question.id}", {
            'description': 'жалоба на пост'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Complaint.objects.filter(
            question=self.question).count(), 1)

    def test_complaint_on_comment_created(self):
        response = self.client.post(f"{self.url}?comment_id={self.comment.id}", {
            'description': 'Оскорбление в комментарии'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Complaint.objects.filter(
            comment=self.comment).count(), 1)

    def test_complaint_on_user_created(self):
        response = self.client.post(f"{self.url}?user_id={self.user2.id}", {
            'description': 'Подозрительный аккаунт'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Complaint.objects.filter(user=self.user2).count(), 1)

    def test_cannot_complain_on_own_question(self):
        own_question = Question.objects.create(
            author=self.user1,
            title="вопрос",
            description='.',
            creation_date=datetime.datetime.now(),
            images='.',
            rating=0
        )
        response = self.client.post(f"{self.url}?question_id={own_question.id}", {
            'description': 'Жалоба на самого себя'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['ok'])
        self.assertEqual(response.json()['error'],
                         'Нельзя жаловаться на свой пост')
        self.assertEqual(Complaint.objects.filter(
            question=own_question).count(), 0)

    def test_cannot_complain_on_own_comment(self):
        own_comment = Comment.objects.create(author=self.user1, text="комментарий", question=self.question, rating=0,
                                             creation_date=datetime.datetime.now())
        response = self.client.post(f"{self.url}?comment_id={own_comment.id}", {
            'description': 'Жалоба на свой коммент'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['ok'])
        self.assertEqual(response.json()['error'],
                         'Нельзя жаловаться на свой комментарий')
        self.assertEqual(Complaint.objects.filter(
            comment=own_comment).count(), 0)

    def test_cannot_complain_on_self(self):
        response = self.client.post(f"{self.url}?user_id={self.user1.id}", {
            'description': 'Я жалуюсь на себя'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['ok'])
        self.assertEqual(response.json()['error'], 'Нельзя жаловаться на себя')
        self.assertEqual(Complaint.objects.filter(user=self.user1).count(), 0)

    def test_banned_user(self):
        self.client.login(username='banned', password='password123')

        response = self.client.post(f"{self.url}?question_id={self.question.id}", {
            'description': 'жалоба на пост'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['ok'])


class ComplaintActionTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@abc.abc',
            password='123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now()
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@abc.abc',
            password='123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now()
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@abc.abc',
            password='123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now()
        )

        self.client.login(username='admin', password='123')

        self.question = Question.objects.create(
            author=self.user2,
            title="вопрос",
            description='.',
            creation_date=datetime.datetime.now(),
            images='.',
            rating=0
        )
        self.comment = Comment.objects.create(author=self.user2, text="комментарий", question=self.question, rating=0,
                                              creation_date=datetime.datetime.now())

        self.accept_url = reverse('accept_complaint')
        self.decline_url = reverse('decline_complaint')

    def test_accept_complaint_deletes_comment(self):
        complaint = Complaint.objects.create(
            author=self.user2, comment=self.comment, description="Test")

        response = self.client.post(
            f"{self.accept_url}?complaint_id={complaint.id}")

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
        self.assertFalse(Complaint.objects.filter(id=complaint.id).exists())

    def test_accept_complaint_bans_user(self):
        complaint = Complaint.objects.create(
            author=self.user2, user=self.user1, description="Test")

        self.client.post(
            f"{self.accept_url}?complaint_id={complaint.id}")

        self.user1.refresh_from_db()
        self.assertFalse(self.user1.active)
        self.assertFalse(Complaint.objects.filter(id=complaint.id).exists())

    def test_decline_complaint_keeps_object(self):
        complaint = Complaint.objects.create(
            author=self.user2, question=self.question, description="Test")

        response = self.client.post(
            f"{self.decline_url}?complaint_id={complaint.id}")

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Complaint.objects.filter(id=complaint.id).exists())
        self.assertTrue(Question.objects.filter(id=self.question.id).exists())

    def test_accept_complaint_deletes_question(self):
        complaint = Complaint.objects.create(
            author=self.user2, question=self.question, description="Test")

        self.client.post(
            f"{self.accept_url}?complaint_id={complaint.id}")

        self.assertFalse(Question.objects.filter(id=self.question.id).exists())
        self.assertFalse(Complaint.objects.filter(id=complaint.id).exists())


class ComplaintPanel(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@abc.abc',
            password='123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now(),
            is_staff=True
        )

        self.client.login(username='admin', password='123')

        self.url1 = reverse('complains_panel_page_u')
        self.url2 = reverse('complains_panel_page_p')
        self.url3 = reverse('complains_panel_page_c')

    def test_complaint_panels_available(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.url3)
        self.assertEqual(response.status_code, 200)
