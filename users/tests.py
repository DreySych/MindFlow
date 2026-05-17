from django.test import TestCase, Client
from django.utils import timezone

# Create your tests here.
from users.models import User, Subscription


class UsersViewsTest(TestCase):
    def setUp(self):
        # Создаём трёх пользователей: автор, другой и заблокированный
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass',
            email='u1@example.com',
            sex=1,
            role='user',
            birth_date='2000-01-01',
            registration_date=timezone.now().date(),
            reputation=0,
            active=True
        )

        self.user2 = User.objects.create_user(
            username='user2',
            password='pass',
            email='u2@example.com',
            sex=1,
            role='user',
            birth_date='2000-01-01',
            registration_date=timezone.now().date(),
            reputation=0,
            active=True
        )

        self.blocked = User.objects.create_user(
            username='blocked',
            password='pass',
            email='blocked@example.com',
            sex=1,
            role='user',
            birth_date='2000-01-01',
            registration_date=timezone.now().date(),
            reputation=0,
            active=False
        )

        self.client = Client()

    def test_registration(self):
        # Тест регистрации: успешная отправка формы создаёт пользователя и делает редирект
        resp = self.client.post('/account/signup/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass',
            'password_confirm': 'newpass',
            'sex': 1,
            'birth_date': '1990-01-01'
        })

        # Проверяем редирект и наличие пользователя в БД
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login(self):
        # Тест логина через форму: POST на /account/login/ должен залогинить пользователя и редиректнуть
        resp = self.client.post('/account/login/', {
            'username': 'user1',
            'password': 'pass'
        })

        self.assertEqual(resp.status_code, 302)

    def test_logout(self):
        # Тест логаута: после выхода в сессии не должно быть user_id
        self.client.login(username='user1', password='pass')
        resp = self.client.get('/account/logout/')
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('user_id', self.client.session)

    def test_subscribe_user(self):
        # Тест подписки: пользователь1 подписывается на пользователь2
        self.client.login(username='user1', password='pass')
        resp = self.client.post(f'/add_friend/{self.user2.id}/')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Subscription.objects.filter(
            user1=self.user1, user2=self.user2).exists())

    def test_unsubscribe_user(self):
        # Тест отписки: сначала создаём подписку, затем удаляем
        Subscription.objects.create(user1=self.user1, user2=self.user2)
        self.client.login(username='user1', password='pass')
        resp = self.client.post(f'/delete_friend/{self.user2.id}/')
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Subscription.objects.filter(
            user1=self.user1, user2=self.user2).exists())

    def test_blocked_user_cannot_edit_profile(self):
        # Забаненный пользователь не может попасть на страницу настроек профиля
        self.client.login(username='blocked', password='pass')
        resp = self.client.get('/profile/settings')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/')

    def test_blocked_user_cannot_subscribe(self):
        # Забаненный пользователь не может подписываться на других
        self.client.login(username='blocked', password='pass')
        resp = self.client.post(f'/add_friend/{self.user1.id}/')
        self.assertEqual(resp.status_code, 200)
        # Подписка не должна быть создана
        self.assertFalse(Subscription.objects.filter(
            user1=self.blocked, user2=self.user1).exists())
