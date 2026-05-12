Модуль users (Пользователи)
===========================

Модуль управления пользователями, профилями и подписками.

Обзор
-----

Модуль ``users`` обеспечивает:

* **User** — расширенная модель пользователя
* **Subscription** — система подписок между пользователями
* Аутентификация и регистрация
* Профили пользователей

Модели
------

.. automodule:: users.models
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: users.views
   :members:
   :undoc-members:
   :show-inheritance:

Forms
-----

.. automodule:: users.forms
   :members:
   :undoc-members:
   :show-inheritance:

Apps
----

.. automodule:: users.apps
   :members:
   :undoc-members:
   :show-inheritance:

Модель User
-----------

Расширение стандартной модели Django User.

Дополнительные поля:

.. code-block:: python

   class User(AbstractUser):
       avatar = models.ImageField(upload_to='avatars/')
       bio = models.TextField(max_length=500)
       active = models.BooleanField(default=True)  # Для блокировки

Примеры использования
---------------------

Регистрация пользователя
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth import get_user_model

   User = get_user_model()

   user = User.objects.create_user(
       username='john',
       email='john@example.com',
       password='securepassword123'
   )

Обновление профиля
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   user = User.objects.get(username='john')
   user.bio = 'Python разработчик из Москвы'
   user.save()

Загрузка аватара
~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.core.files.uploadedfile import SimpleUploadedFile

   with open('photo.jpg', 'rb') as f:
       user.avatar = SimpleUploadedFile('photo.jpg', f.read())
       user.save()

Блокировка пользователя
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Администратор блокирует пользователя
   user.active = False
   user.save()

   # Проверка в views
   if not request.user.active:
       return HttpResponseForbidden('Вы заблокированы')

Система подписок
----------------

Модель Subscription
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class Subscription(models.Model):
       user1 = models.ForeignKey(User, on_delete=CASCADE, related_name='user1')
       user2 = models.ForeignKey(User, on_delete=CASCADE, related_name='user2')

Подписка на пользователя
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from users.models import Subscription

   # Пользователь user1 подписывается на user2
   subscription = Subscription.objects.create(
       user1=current_user,
       user2=target_user
   )

Проверка подписки
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Проверка, подписан ли user1 на user2
   is_subscribed = Subscription.objects.filter(
       user1=current_user,
       user2=target_user
   ).exists()

Получение подписчиков
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Подписчики пользователя (кто подписан на меня)
   followers = Subscription.objects.filter(user2=user).select_related('user1')

   for sub in followers:
       print(f"{sub.user1.username} подписан на меня")

Получение подписок
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Подписки пользователя (на кого я подписан)
   following = Subscription.objects.filter(user1=user).select_related('user2')

   for sub in following:
       print(f"Я подписан на {sub.user2.username}")

Отписка
~~~~~~~

.. code-block:: python

   # Отписаться от пользователя
   Subscription.objects.filter(
       user1=current_user,
       user2=target_user
   ).delete()

Аутентификация
--------------

Вход (Login)
~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth import authenticate, login

   def login_view(request):
       if request.method == 'POST':
           username = request.POST['username']
           password = request.POST['password']

           user = authenticate(request, username=username, password=password)

           if user is not None and user.active:
               login(request, user)
               return redirect('home')
           else:
               return render(request, 'login.html', {
                   'error': 'Неверные данные или пользователь заблокирован'
               })

Выход (Logout)
~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth import logout

   def logout_view(request):
       logout(request)
       return redirect('login')

Смена пароля
~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth import update_session_auth_hash

   def change_password(request):
       if request.method == 'POST':
           old_password = request.POST['old_password']
           new_password = request.POST['new_password']

           user = request.user

           if user.check_password(old_password):
               user.set_password(new_password)
               user.save()

               # Обновление сессии
               update_session_auth_hash(request, user)

               return redirect('profile')

Декораторы для защиты views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth.decorators import login_required, user_passes_test

   @login_required
   def profile_view(request):
       # Только для авторизованных
       pass

   def is_active(user):
       return user.is_authenticated and user.active

   @user_passes_test(is_active)
   def protected_view(request):
       # Только для активных пользователей
       pass

   def is_staff(user):
       return user.is_authenticated and user.is_staff

   @user_passes_test(is_staff)
   def admin_view(request):
       # Только для администраторов
       pass

Профили пользователей
---------------------

Страница профиля
~~~~~~~~~~~~~~~~

.. code-block:: python

   def profile_view(request, username):
       user = get_object_or_404(User, username=username)

       # Вопросы пользователя
       questions = Question.objects.filter(author=user).order_by('-creation_date')

       # Подписчики
       followers_count = Subscription.objects.filter(user2=user).count()

       # Подписки
       following_count = Subscription.objects.filter(user1=user).count()

       # Проверка подписки текущего пользователя
       is_subscribed = False
       if request.user.is_authenticated:
           is_subscribed = Subscription.objects.filter(
               user1=request.user,
               user2=user
           ).exists()

       context = {
           'profile_user': user,
           'questions': questions,
           'followers_count': followers_count,
           'following_count': following_count,
           'is_subscribed': is_subscribed,
       }

       return render(request, 'profile.html', context)

Редактирование профиля
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @login_required
   def edit_profile(request):
       if request.method == 'POST':
           form = ProfileForm(request.POST, request.FILES, instance=request.user)

           if form.is_valid():
               form.save()
               return redirect('profile', username=request.user.username)
       else:
           form = ProfileForm(instance=request.user)

       return render(request, 'edit_profile.html', {'form': form})

Статистика пользователя
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models import Count

   def user_stats(user):
       stats = {
           'questions_count': Question.objects.filter(author=user).count(),
           'comments_count': Comment.objects.filter(author=user).count(),
           'answers_count': Answer.objects.filter(author=user).count(),
           'likes_received': Like.objects.filter(question__author=user).count(),
           'followers_count': Subscription.objects.filter(user2=user).count(),
           'following_count': Subscription.objects.filter(user1=user).count(),
       }

       return stats

Загрузка аватаров
-----------------

Настройка media файлов
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings.py
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

   # urls.py (для development)
   from django.conf import settings
   from django.conf.urls.static import static

   urlpatterns = [
       # ...
   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Форма загрузки
~~~~~~~~~~~~~~

.. code-block:: python

   from django import forms

   class AvatarForm(forms.ModelForm):
       class Meta:
           model = User
           fields = ['avatar']

       def clean_avatar(self):
           avatar = self.cleaned_data.get('avatar')

           if avatar:
               # Проверка размера (макс. 2MB)
               if avatar.size > 2 * 1024 * 1024:
                   raise forms.ValidationError('Размер файла не должен превышать 2MB')

               # Проверка формата
               if not avatar.content_type.startswith('image/'):
                   raise forms.ValidationError('Загрузите изображение')

           return avatar

Отображение в шаблоне
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

   {% if user.avatar %}
       <img src="{{ user.avatar.url }}" alt="{{ user.username }}">
   {% else %}
       <img src="{% static 'images/default-avatar.png' %}" alt="Default">
   {% endif %}

Signals
-------

Создание профиля при регистрации
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models.signals import post_save
   from django.dispatch import receiver

   @receiver(post_save, sender=User)
   def create_user_profile(sender, instance, created, **kwargs):
       if created:
           # Инициализация дополнительных данных
           print(f"Создан новый пользователь: {instance.username}")

Тестирование
------------

.. code-block:: python

   from django.test import TestCase, Client
   from django.contrib.auth import get_user_model

   User = get_user_model()

   class UserTest(TestCase):
       def setUp(self):
           self.client = Client()
           self.user = User.objects.create_user(
               username='testuser',
               password='testpass123'
           )

       def test_login(self):
           response = self.client.post('/login/', {
               'username': 'testuser',
               'password': 'testpass123'
           })

           self.assertEqual(response.status_code, 302)  # Redirect
           self.assertTrue(response.wsgi_request.user.is_authenticated)

       def test_subscription(self):
           user2 = User.objects.create_user(username='user2', password='pass')

           subscription = Subscription.objects.create(
               user1=self.user,
               user2=user2
           )

           self.assertEqual(Subscription.objects.filter(user1=self.user).count(), 1)

См. также
---------

* :doc:`questions` — вопросы пользователей
* :doc:`notifications` — уведомления о подписках
* :doc:`complains` — система жалоб на вопросы