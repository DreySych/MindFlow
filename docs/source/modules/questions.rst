Модуль questions (Вопросы и ответы)
===================================

Основной модуль системы вопросов, комментариев и ответов.

Обзор
-----

Модуль ``questions`` реализует ядро платформы Q&A:

* **Question** — вопросы пользователей
* **Comment** — комментарии к вопросам
* **Answer** — ответы на комментарии

Модели базы данных
------------------

.. automodule:: questions.models
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: questions.views
   :members:
   :undoc-members:
   :show-inheritance:

Forms
-----

.. automodule:: questions.forms
   :members:
   :undoc-members:
   :show-inheritance:

Apps
----

.. automodule:: questions.apps
   :members:
   :undoc-members:
   :show-inheritance:

Структура данных
----------------

Иерархия объектов::

   Question (Вопрос)
   └── Comment (Комментарий)
       └── Answer (Ответ на комментарий)

Связи между моделями:

.. code-block:: text

   Question
   ├── author: ForeignKey(User)
   ├── comments: OneToMany(Comment)
   └── likes/dislikes: ManyToMany(User)

   Comment
   ├── author: ForeignKey(User)
   ├── question: ForeignKey(Question)
   └── answers: OneToMany(Answer)

   Answer
   ├── author: ForeignKey(User)
   └── comment: ForeignKey(Comment)

Примеры использования
---------------------

Создание вопроса
~~~~~~~~~~~~~~~~

.. code-block:: python

   from questions.models import Question
   from users.models import User

   # Получение пользователя
   user = User.objects.get(username='john')

   # Создание вопроса
   question = Question.objects.create(
       author=user,
       title='Как работает Django ORM?',
       description='Подробное описание вопроса...'
   )

Добавление комментария
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from questions.models import Comment

   comment = Comment.objects.create(
       author=user,
       question=question,
       text='Отличный вопрос! Вот мой комментарий...'
   )

Ответ на комментарий
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from questions.models import Answer

   answer = Answer.objects.create(
       author=user,
       comment=comment,
       answer='Спасибо за комментарий! Вот мой ответ...'
   )

Получение всех комментариев вопроса
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Через related manager
   comments = question.comment_set.all()

   # С оптимизацией запросов
   comments = question.comment_set.select_related('author').all()

Получение ответов на комментарий
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   answers = comment.answer_set.all()

   # С автором
   answers = comment.answer_set.select_related('author').all()

Подсчёт лайков
~~~~~~~~~~~~~~

.. code-block:: python

   from main.models import Like, Dislike

   likes_count = Like.objects.filter(question=question).count()
   dislikes_count = Dislike.objects.filter(question=question).count()

   total_score = likes_count - dislikes_count

Фильтрация вопросов
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Последние 10 вопросов
   recent = Question.objects.order_by('-creation_date')[:10]

   # Вопросы пользователя
   user_questions = Question.objects.filter(author=user)

   # Вопросы с комментариями
   with_comments = Question.objects.annotate(
       num_comments=Count('comment_set')
   ).filter(num_comments__gt=0)

Поиск по тексту
~~~~~~~~~~~~~~~

.. code-block:: python

   # Поиск в заголовке
   results = Question.objects.filter(title__icontains='Django')

   # Поиск в заголовке или описании
   from django.db.models import Q

   results = Question.objects.filter(
       Q(title__icontains='Django') |
       Q(description__icontains='Django')
   )

URL маршруты
------------

Основные endpoints:

.. code-block:: python

   # questions/urls.py
   urlpatterns = [
       path('', views.questions_list, name='questions_list'),
       path('create/', views.create_question, name='create_question'),
       path('<int:question_id>/', views.question_detail, name='question_detail'),
       path('<int:question_id>/edit/', views.edit_question, name='edit_question'),
       path('<int:question_id>/delete/', views.delete_question, name='delete_question'),
   ]

Templates
---------

Основные шаблоны:

* ``questions_list.html`` — список вопросов
* ``question_detail.html`` — страница вопроса с комментариями
* ``create_question.html`` — форма создания вопроса
* ``edit_question.html`` — форма редактирования

Валидация
---------

Валидация на уровне модели
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.core.exceptions import ValidationError

   class Question(models.Model):
       # ...

       def clean(self):
           if len(self.title) < 10:
               raise ValidationError('Заголовок должен быть минимум 10 символов')

           if self.title == self.description:
               raise ValidationError('Заголовок и описание не должны совпадать')

Валидация в формах
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django import forms

   class QuestionForm(forms.ModelForm):
       class Meta:
           model = Question
           fields = ['title', 'description']

       def clean_title(self):
           title = self.cleaned_data['title']

           # Проверка на дубликаты
           if Question.objects.filter(title=title).exists():
               raise forms.ValidationError('Вопрос с таким заголовком уже существует')

           return title

Права доступа
-------------

Проверка прав в views
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.shortcuts import get_object_or_404
   from django.http import HttpResponseForbidden

   def edit_question(request, question_id):
       question = get_object_or_404(Question, id=question_id)

       # Только автор может редактировать
       if question.author != request.user:
           return HttpResponseForbidden('Вы не можете редактировать этот вопрос')

       # ...

Использование декораторов
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth.decorators import login_required

   @login_required
   def create_question(request):
       # Только авторизованные пользователи
       pass

Сигналы
-------

Создание уведомлений при комментарии
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from notifications.models import Notification

   @receiver(post_save, sender=Comment)
   def create_comment_notification(sender, instance, created, **kwargs):
       if created:
           # Уведомление автору вопроса
           Notification.objects.create(
               user=instance.question.author,
               text=f'{instance.author.username} прокомментировал ваш вопрос',
               link=f'/questions/{instance.question.id}/'
           )

Оптимизация запросов
--------------------

Избегайте N+1 проблемы
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ПЛОХО: N+1 запросы
   questions = Question.objects.all()
   for q in questions:
       print(q.author.username)  # Запрос для каждого автора!

   # ХОРОШО: один дополнительный JOIN
   questions = Question.objects.select_related('author').all()
   for q in questions:
       print(q.author.username)  # Без дополнительных запросов

Префетч связанных объектов
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Вопросы с комментариями и их авторами
   questions = Question.objects.prefetch_related(
       'comment_set',
       'comment_set__author',
       'comment_set__answer_set'
   ).all()

Агрегация
~~~~~~~~~

.. code-block:: python

   from django.db.models import Count, Avg

   # Вопросы с количеством комментариев
   questions = Question.objects.annotate(
       comments_count=Count('comment_set'),
       answers_count=Count('comment_set__answer_set')
   )

   for q in questions:
       print(f"{q.title}: {q.comments_count} комментариев, {q.answers_count} ответов")

Тестирование
------------

Пример тестов
~~~~~~~~~~~~~

.. code-block:: python

   from django.test import TestCase
   from questions.models import Question, Comment
   from users.models import User

   class QuestionModelTest(TestCase):
       def setUp(self):
           self.user = User.objects.create_user(
               username='testuser',
               password='12345'
           )

       def test_create_question(self):
           question = Question.objects.create(
               author=self.user,
               title='Test Question',
               description='Test Description'
           )

           self.assertEqual(question.title, 'Test Question')
           self.assertEqual(question.author, self.user)

       def test_add_comment(self):
           question = Question.objects.create(
               author=self.user,
               title='Test',
               description='Test'
           )

           comment = Comment.objects.create(
               author=self.user,
               question=question,
               text='Test comment'
           )

           self.assertEqual(question.comment_set.count(), 1)
           self.assertEqual(comment.question, question)

Запуск тестов:

.. code-block:: bash

   python manage.py test questions

См. также
---------

* :doc:`users` — модуль пользователей
* :doc:`complains` — система жалоб на вопросы
* :doc:`complains` — жалобы на пользователей