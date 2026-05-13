Модуль notifications (Уведомления)
==================================

Система уведомлений пользователей о событиях на платформе.

Обзор
-----

Модуль ``notifications`` обеспечивает:

* Создание уведомлений при различных событиях
* Отображение непрочитанных уведомлений
* Автоматическую отметку как прочитанных
* Ссылки на связанные объекты

Модели
------

.. automodule:: notifications.models
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: notifications.views
   :members:
   :undoc-members:
   :show-inheritance:

Apps
----

.. automodule:: notifications.apps
   :members:
   :undoc-members:
   :show-inheritance:

Модель Notification
-------------------

Структура уведомления
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class Notification(models.Model):
       user = models.ForeignKey(User, on_delete=CASCADE)
       text = models.TextField()
       link = models.CharField(max_length=255)
       is_read = models.BooleanField(default=False)
       created_at = models.DateTimeField(auto_now_add=True)

Поля:

* **user** — получатель уведомления
* **text** — текст уведомления
* **link** — ссылка на связанный объект
* **is_read** — прочитано или нет
* **created_at** — время создания

Типы уведомлений
----------------

Платформа создаёт уведомления при следующих событиях:

1. **Новый комментарий к вопросу**

   .. code-block:: python

      Notification.objects.create(
          user=question.author,
          text=f'{comment.author.username} прокомментировал ваш вопрос',
          link=f'/questions/{question.id}/'
      )

2. **Новый ответ на комментарий**

   .. code-block:: python

      Notification.objects.create(
          user=comment.author,
          text=f'{answer.author.username} ответил на ваш комментарий',
          link=f'/questions/{comment.question.id}/'
      )

3. **Новая подписка**

   .. code-block:: python

      Notification.objects.create(
          user=subscribed_to_user,
          text=f'{subscriber.username} подписался на вас',
          link=f'/profile/{subscriber.username}/'
      )

4. **Лайк на вопрос**

   .. code-block:: python

      Notification.objects.create(
          user=question.author,
          text=f'{liker.username} лайкнул ваш вопрос',
          link=f'/questions/{question.id}/'
      )

5. **Новая жалоба (для администраторов)**

   .. code-block:: python

      admins = User.objects.filter(is_staff=True)
      for admin in admins:
          Notification.objects.create(
              user=admin,
              text=f'{complaint.author.username} отправил жалобу',
              link='/complaint/panel/questions/'
          )

Примеры использования
---------------------

Создание уведомления
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from notifications.models import Notification
   from users.models import User

   user = User.objects.get(username='john')

   notification = Notification.objects.create(
       user=user,
       text='У вас новое сообщение',
       link='/messages/inbox/'
   )

Получение уведомлений пользователя
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Все уведомления
   notifications = Notification.objects.filter(user=request.user)

   # Только непрочитанные
   unread = Notification.objects.filter(
       user=request.user,
       is_read=False
   ).order_by('-created_at')

   # Количество непрочитанных
   unread_count = Notification.objects.filter(
       user=request.user,
       is_read=False
   ).count()

Отметка как прочитанное
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Одно уведомление
   notification = Notification.objects.get(id=42)
   notification.is_read = True
   notification.save()

   # Все уведомления пользователя
   Notification.objects.filter(
       user=request.user,
       is_read=False
   ).update(is_read=True)

Удаление старых уведомлений
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import timedelta
   from django.utils import timezone

   # Удаление уведомлений старше 30 дней
   thirty_days_ago = timezone.now() - timedelta(days=30)

   Notification.objects.filter(
       created_at__lt=thirty_days_ago,
       is_read=True
   ).delete()

Views
-----

Страница уведомлений
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth.decorators import login_required
   from django.shortcuts import render
   from notifications.models import Notification

   @login_required
   def notifications_view(request):
       # Получаем все уведомления
       notifications = Notification.objects.filter(
           user=request.user
       ).order_by('-created_at')

       # Отмечаем все как прочитанные
       Notification.objects.filter(
           user=request.user,
           is_read=False
       ).update(is_read=True)

       return render(request, 'notifications.html', {
           'notifications': notifications
       })

Счётчик непрочитанных
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def get_unread_count(request):
       """Context processor для отображения счётчика."""
       if request.user.is_authenticated:
           unread_count = Notification.objects.filter(
               user=request.user,
               is_read=False
           ).count()
           return {'unread_notifications_count': unread_count}
       return {'unread_notifications_count': 0}

   # settings.py
   TEMPLATES = [
       {
           'OPTIONS': {
               'context_processors': [
                   # ...
                   'notifications.context_processors.get_unread_count',
               ],
           },
       },
   ]

Signals для автоматических уведомлений
--------------------------------------

Уведомление при новом комментарии
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from questions.models import Comment
   from notifications.models import Notification

   @receiver(post_save, sender=Comment)
   def notify_on_comment(sender, instance, created, **kwargs):
       """Уведомляет автора вопроса о новом комментарии."""
       if created:
           # Не уведомляем, если автор комментирует свой вопрос
           if instance.author != instance.question.author:
               Notification.objects.create(
                   user=instance.question.author,
                   text=f'{instance.author.username} прокомментировал ваш вопрос "{instance.question.title}"',
                   link=f'/questions/{instance.question.id}/#comment-{instance.id}'
               )

Уведомление при ответе на комментарий
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from questions.models import Answer

   @receiver(post_save, sender=Answer)
   def notify_on_answer(sender, instance, created, **kwargs):
       """Уведомляет автора комментария об ответе."""
       if created:
           # Не уведомляем себя
           if instance.author != instance.comment.author:
               Notification.objects.create(
                   user=instance.comment.author,
                   text=f'{instance.author.username} ответил на ваш комментарий',
                   link=f'/questions/{instance.comment.question.id}/#answer-{instance.id}'
               )

Уведомление при подписке
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from users.models import Subscription

   @receiver(post_save, sender=Subscription)
   def notify_on_subscription(sender, instance, created, **kwargs):
       """Уведомляет пользователя о новом подписчике."""
       if created:
           Notification.objects.create(
               user=instance.user2,  # На кого подписались
               text=f'{instance.user1.username} подписался на вас',
               link=f'/profile/{instance.user1.username}/'
           )

Уведомление при лайке
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from main.models import Like

   @receiver(post_save, sender=Like)
   def notify_on_like(sender, instance, created, **kwargs):
       """Уведомляет автора вопроса о лайке."""
       if created:
           # Не уведомляем о своих лайках
           if instance.user != instance.question.author:
               Notification.objects.create(
                   user=instance.question.author,
                   text=f'{instance.user.username} лайкнул ваш вопрос "{instance.question.title}"',
                   link=f'/questions/{instance.question.id}/'
               )

Шаблоны
-------

Список уведомлений
~~~~~~~~~~~~~~~~~~

.. code-block:: html

   <!-- notifications.html -->
   <div class="notifications-page">
       <h1>Уведомления</h1>

       {% if notifications %}
           <ul class="notifications-list">
               {% for notification in notifications %}
               <li class="notification-item {% if not notification.is_read %}unread{% endif %}">
                   <div class="notification-content">
                       <p>{{ notification.text }}</p>
                       <span class="notification-time">{{ notification.created_at|timesince }} назад</span>
                   </div>
                   <a href="{{ notification.link }}" class="notification-link">
                       Перейти →
                   </a>
               </li>
               {% endfor %}
           </ul>
       {% else %}
           <p class="no-notifications">У вас пока нет уведомлений</p>
       {% endif %}
   </div>

Бейдж непрочитанных
~~~~~~~~~~~~~~~~~~~

.. code-block:: html

   <!-- base.html - навигация -->
   <nav>
       <a href="/notifications/">
           🔔 Уведомления
           {% if unread_notifications_count > 0 %}
               <span class="badge">{{ unread_notifications_count }}</span>
           {% endif %}
       </a>
   </nav>

API для AJAX-запросов
---------------------

Получение новых уведомлений
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.http import JsonResponse

   @login_required
   def notifications_api(request):
       """Возвращает непрочитанные уведомления в JSON."""

       notifications = Notification.objects.filter(
           user=request.user,
           is_read=False
       ).order_by('-created_at')[:10]  # Последние 10

       data = {
           'count': notifications.count(),
           'notifications': [
               {
                   'id': n.id,
                   'text': n.text,
                   'link': n.link,
                   'created_at': n.created_at.isoformat(),
               }
               for n in notifications
           ]
       }

       return JsonResponse(data)

Отметка как прочитанное через AJAX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.views.decorators.http import require_POST

   @login_required
   @require_POST
   def mark_notification_read(request, notification_id):
       """Отмечает уведомление как прочитанное."""

       try:
           notification = Notification.objects.get(
               id=notification_id,
               user=request.user
           )
           notification.is_read = True
           notification.save()

           return JsonResponse({'ok': True})
       except Notification.DoesNotExist:
           return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)

JavaScript для real-time обновлений
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   // Проверка новых уведомлений каждые 30 секунд
   setInterval(async () => {
       const response = await fetch('/notifications/api/');
       const data = await response.json();

       // Обновление бейджа
       const badge = document.querySelector('.notifications-badge');
       if (data.count > 0) {
           badge.textContent = data.count;
           badge.style.display = 'inline';
       } else {
           badge.style.display = 'none';
       }

       // Показ всплывающих уведомлений
       data.notifications.forEach(notif => {
           showToast(notif.text, notif.link);
       });
   }, 30000);

Оптимизация
-----------

Индексы базы данных
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class Notification(models.Model):
       # ...

       class Meta:
           indexes = [
               models.Index(fields=['user', '-created_at']),
               models.Index(fields=['user', 'is_read']),
           ]

Пагинация
~~~~~~~~~

.. code-block:: python

   from django.core.paginator import Paginator

   def notifications_view(request):
       all_notifications = Notification.objects.filter(
           user=request.user
       ).order_by('-created_at')

       paginator = Paginator(all_notifications, 20)  # 20 на страницу
       page_number = request.GET.get('page', 1)
       notifications = paginator.get_page(page_number)

       return render(request, 'notifications.html', {
           'notifications': notifications
       })

Bulk создание
~~~~~~~~~~~~~

.. code-block:: python

   # Вместо цикла с create()
   notifications_to_create = []
   for admin in admins:
       notifications_to_create.append(
           Notification(
               user=admin,
               text='Новая жалоба',
               link='/complaints/'
           )
       )

   Notification.objects.bulk_create(notifications_to_create)

Управление командой
-------------------

Очистка старых уведомлений
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # management/commands/cleanup_notifications.py
   from django.core.management.base import BaseCommand
   from django.utils import timezone
   from datetime import timedelta
   from notifications.models import Notification

   class Command(BaseCommand):
       help = 'Удаляет прочитанные уведомления старше 30 дней'

       def handle(self, *args, **options):
           threshold = timezone.now() - timedelta(days=30)

           deleted, _ = Notification.objects.filter(
               created_at__lt=threshold,
               is_read=True
           ).delete()

           self.stdout.write(
               self.style.SUCCESS(f'Удалено {deleted} уведомлений')
           )

Использование:

.. code-block:: bash

   python manage.py cleanup_notifications

Тестирование
------------

.. code-block:: python

   from django.test import TestCase
   from notifications.models import Notification
   from users.models import User

   class NotificationTest(TestCase):
       def setUp(self):
           self.user = User.objects.create_user(
               username='testuser',
               password='pass'
           )

       def test_create_notification(self):
           notification = Notification.objects.create(
               user=self.user,
               text='Test notification',
               link='/test/'
           )

           self.assertFalse(notification.is_read)
           self.assertEqual(notification.user, self.user)

       def test_mark_as_read(self):
           notification = Notification.objects.create(
               user=self.user,
               text='Test',
               link='/'
           )

           notification.is_read = True
           notification.save()

           updated = Notification.objects.get(id=notification.id)
           self.assertTrue(updated.is_read)

       def test_unread_count(self):
           # Создаём 3 непрочитанных
           for i in range(3):
               Notification.objects.create(
                   user=self.user,
                   text=f'Test {i}',
                   link='/'
               )

           count = Notification.objects.filter(
               user=self.user,
               is_read=False
           ).count()

           self.assertEqual(count, 3)

См. также
---------

* :doc:`users` — подписки и уведомления
* :doc:`questions` — комментарии и уведомления
* :doc:`complains` — жалобы на пользователей