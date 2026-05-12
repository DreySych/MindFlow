import datetime

from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from .models import Message


class MessagesTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='user1@abc.abc',
            password='password123',
            reputation=0,
            role='',
            registration_date=datetime.datetime.now()
        )
        self.receiver = User.objects.create_user(
            username='receiver',
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

        self.client = Client()
        self.client.login(username='sender', password='password123')

        self.url = reverse('chat_page', kwargs={'user_id': self.receiver.id})

    def test_message_creation_on_post(self):
        data = {'text': 'some text'}

        response = self.client.post(self.url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(Message.objects.filter(text=data['text']).exists())

        message = Message.objects.get(text=data['text'])
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)

    def test_empty_message_not_created(self):
        data = {'text': ''}

        self.client.post(self.url, data=data)

        self.assertEqual(Message.objects.count(), 0)

    def test_right_data_about_message(self):
        test_text = "some text"

        self.client.post(self.url, {'text': test_text})

        message = Message.objects.last()

        self.assertEqual(message.text, test_text)

        self.assertEqual(message.sender.id, self.sender.id)
        self.assertEqual(message.sender.username, 'sender')

        self.assertEqual(message.receiver.id, self.receiver.id)
        self.assertEqual(message.receiver.username, 'receiver')

    def test_banned_user(self):
        self.client.login(username='banned', password='password123')

        data = {'text': 'some text'}

        self.client.post(self.url, data=data)

        self.assertEqual(Message.objects.count(), 0)
