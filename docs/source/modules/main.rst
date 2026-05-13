Модуль main (Главная страница)
==============================

Главное приложение с основной функциональностью платформы.

Обзор
-----

Модуль ``main`` содержит:

* Главную страницу с лентой вопросов
* Систему лайков и дизлайков
* Общие утилиты и вспомогательные функции

Модели
------

.. automodule:: main.models
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: main.views
   :members:
   :undoc-members:
   :show-inheritance:

Apps
----

.. automodule:: main.apps
   :members:
   :undoc-members:
   :show-inheritance:

Модели Like и Dislike
---------------------

Модель Like
~~~~~~~~~~~

.. code-block:: python

   class Like(models.Model):
       user = models.ForeignKey(User, on_delete=CASCADE)
       question = models.ForeignKey(Question, on_delete=CASCADE)

Модель Dislike
~~~~~~~~~~~~~~

.. code-block:: python

   class Dislike(models.Model):
       user = models.ForeignKey(User, on_delete=CASCADE)
       question = models.ForeignKey(Question, on_delete=CASCADE)

Правила:

* Один пользователь может поставить только один лайк/дизлайк на вопрос
* Нельзя лайкнуть/дизлайкнуть свой вопрос
* При лайке удаляется дизлайк (и наоборот)
* Повторный лайк/дизлайк удаляет предыдущий

Главная страница
----------------

View-функция
~~~~~~~~~~~~

.. code-block:: python

   from django.shortcuts import render
   from questions.models import Question
   from users.models import Subscription

   def main_page(request):
       """Отображает главную страницу с лентой вопросов."""

       questions = Question.objects.select_related('author').order_by('-creation_date')

       context = {
           'questions': questions,
           'user': request.user,
       }

       if request.user.is_authenticated:
           context['subscriptions'] = Subscription.objects.filter(
               user1=request.user
           )

       return render(request, 'main.html', context)

Фильтрация и сортировка
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def main_page(request):
       # Получаем параметры
       sort = request.GET.get('sort', 'newest')  # newest, popular, unanswered

       questions = Question.objects.select_related('author')

       # Сортировка
       if sort == 'newest':
           questions = questions.order_by('-creation_date')
       elif sort == 'popular':
           questions = questions.annotate(
               likes_count=Count('like_set')
           ).order_by('-likes_count')
       elif sort == 'unanswered':
           questions = questions.annotate(
               comments_count=Count('comment_set')
           ).filter(comments_count=0).order_by('-creation_date')

       return render(request, 'main.html', {
           'questions': questions,
           'current_sort': sort
       })

Система лайков
--------------

Добавление лайка
~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth.decorators import login_required
   from django.shortcuts import redirect, get_object_or_404
   from main.models import Like, Dislike
   from questions.models import Question

   @login_required
   def like_question(request):
       """Добавляет или удаляет лайк вопроса."""

       question_id = request.GET.get('question_id')
       question = get_object_or_404(Question, id=question_id)

       # Нельзя лайкнуть свой вопрос
       if question.author == request.user:
           return redirect(request.GET.get('to', '/'))

       # Проверяем существующий лайк
       existing_like = Like.objects.filter(
           user=request.user,
           question=question
       ).first()

       if existing_like:
           # Убираем лайк
           existing_like.delete()
       else:
           # Удаляем дизлайк, если был
           Dislike.objects.filter(
               user=request.user,
               question=question
           ).delete()

           # Добавляем лайк
           Like.objects.create(
               user=request.user,
               question=question
           )

           # Уведомление автору (опционально)
           from notifications.models import Notification
           if question.author != request.user:
               Notification.objects.create(
                   user=question.author,
                   text=f'{request.user.username} лайкнул ваш вопрос',
                   link=f'/questions/{question.id}/'
               )

       return redirect(request.GET.get('to', '/'))

Добавление дизлайка
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @login_required
   def dislike_question(request):
       """Добавляет или удаляет дизлайк вопроса."""

       question_id = request.GET.get('question_id')
       question = get_object_or_404(Question, id=question_id)

       # Нельзя дизлайкнуть свой вопрос
       if question.author == request.user:
           return redirect(request.GET.get('to', '/'))

       existing_dislike = Dislike.objects.filter(
           user=request.user,
           question=question
       ).first()

       if existing_dislike:
           # Убираем дизлайк
           existing_dislike.delete()
       else:
           # Удаляем лайк, если был
           Like.objects.filter(
               user=request.user,
               question=question
           ).delete()

           # Добавляем дизлайк
           Dislike.objects.create(
               user=request.user,
               question=question
           )

       return redirect(request.GET.get('to', '/'))

Проверка статуса лайка
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def get_like_status(user, question):
       """Возвращает статус лайка пользователя для вопроса."""

       if not user.is_authenticated:
           return None

       has_like = Like.objects.filter(
           user=user,
           question=question
       ).exists()

       has_dislike = Dislike.objects.filter(
           user=user,
           question=question
       ).exists()

       if has_like:
           return 'liked'
       elif has_dislike:
           return 'disliked'
       else:
           return None

Подсчёт лайков
~~~~~~~~~~~~~~

.. code-block:: python

   def get_question_score(question):
       """Возвращает баланс лайков/дизлайков."""

       likes_count = Like.objects.filter(question=question).count()
       dislikes_count = Dislike.objects.filter(question=question).count()

       return {
           'likes': likes_count,
           'dislikes': dislikes_count,
           'score': likes_count - dislikes_count
       }

Использование в шаблонах
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Context processor для лайков
   def likes_context(request):
       """Добавляет функцию проверки лайков в контекст."""

       def user_liked(question):
           if not request.user.is_authenticated:
               return False
           return Like.objects.filter(
               user=request.user,
               question=question
           ).exists()

       def user_disliked(question):
           if not request.user.is_authenticated:
               return False
           return Dislike.objects.filter(
               user=request.user,
               question=question
           ).exists()

       return {
           'user_liked': user_liked,
           'user_disliked': user_disliked
       }

Template tags
-------------

Кастомные теги для лайков
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # main/templatetags/likes_tags.py
   from django import template
   from main.models import Like, Dislike

   register = template.Library()

   @register.simple_tag
   def likes_count(question):
       """Возвращает количество лайков."""
       return Like.objects.filter(question=question).count()

   @register.simple_tag
   def dislikes_count(question):
       """Возвращает количество дизлайков."""
       return Dislike.objects.filter(question=question).count()

   @register.simple_tag
   def question_score(question):
       """Возвращает баланс лайков-дизлайков."""
       likes = Like.objects.filter(question=question).count()
       dislikes = Dislike.objects.filter(question=question).count()
       return likes - dislikes

   @register.simple_tag(takes_context=True)
   def user_reaction(context, question):
       """Возвращает реакцию пользователя (like/dislike/none)."""
       user = context['user']

       if not user.is_authenticated:
           return 'none'

       if Like.objects.filter(user=user, question=question).exists():
           return 'like'
       elif Dislike.objects.filter(user=user, question=question).exists():
           return 'dislike'
       else:
           return 'none'

Использование в шаблоне:

.. code-block:: html

   {% load likes_tags %}

   <div class="question-votes">
       <a href="/like/?question_id={{ question.id }}&to={{ request.path }}"
          class="vote-btn {% if user_reaction question == 'like' %}active{% endif %}">
           👍 {% likes_count question %}
       </a>

       <span class="score">{{ question_score question }}</span>

       <a href="/dislike/?question_id={{ question.id }}&to={{ request.path }}"
          class="vote-btn {% if user_reaction question == 'dislike' %}active{% endif %}">
           👎 {% dislikes_count question %}
       </a>
   </div>

Оптимизация
-----------

Annotate для подсчёта
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models import Count

   # Вместо отдельных запросов для каждого вопроса
   questions = Question.objects.annotate(
       likes_count=Count('like'),
       dislikes_count=Count('dislike')
   ).select_related('author')

   # Теперь можно использовать question.likes_count без запросов

Prefetch для статуса пользователя
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models import Prefetch

   if request.user.is_authenticated:
       user_likes = Like.objects.filter(user=request.user)
       user_dislikes = Dislike.objects.filter(user=request.user)

       questions = Question.objects.prefetch_related(
           Prefetch('like_set', queryset=user_likes, to_attr='user_likes'),
           Prefetch('dislike_set', queryset=user_dislikes, to_attr='user_dislikes')
       )

Тестирование
------------

.. code-block:: python

   from django.test import TestCase, Client
   from users.models import User
   from questions.models import Question
   from main.models import Like, Dislike

   class LikeDislikeTest(TestCase):
       def setUp(self):
           self.client = Client()
           self.user1 = User.objects.create_user('user1', password='pass')
           self.user2 = User.objects.create_user('user2', password='pass')
           self.question = Question.objects.create(
               author=self.user1,
               title='Test',
               description='Test'
           )

       def test_like_question(self):
           self.client.login(username='user2', password='pass')

           response = self.client.get(f'/like/?question_id={self.question.id}')

           self.assertEqual(Like.objects.filter(question=self.question).count(), 1)

       def test_cannot_like_own_question(self):
           self.client.login(username='user1', password='pass')

           self.client.get(f'/like/?question_id={self.question.id}')

           self.assertEqual(Like.objects.filter(question=self.question).count(), 0)

       def test_like_removes_dislike(self):
           self.client.login(username='user2', password='pass')

           # Сначала дизлайк
           Dislike.objects.create(user=self.user2, question=self.question)

           # Потом лайк
           self.client.get(f'/like/?question_id={self.question.id}')

           self.assertEqual(Like.objects.filter(question=self.question).count(), 1)
           self.assertEqual(Dislike.objects.filter(question=self.question).count(), 0)

URL конфигурация
----------------

.. code-block:: python

   # main/urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path('', views.main_page, name='main'),
       path('like/', views.like_question, name='like'),
       path('dislike/', views.dislike_question, name='dislike'),
   ]

См. также
---------

* :doc:`questions` — модель Question
* :doc:`users` — авторизация
* :doc:`notifications` — уведомления о лайках