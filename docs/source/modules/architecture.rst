Архитектура проекта
===================

Общая архитектура и дизайн-решения проекта The Final Build.

Обзор системы
-------------

The Final Build — это модульная Django платформа, организованная по принципу разделения ответственности.

.. code-block:: text

   ┌─────────────────────────────────────────────┐
   │           Presentation Layer                │
   │  (Templates, Static Files, JavaScript)      │
   └─────────────────────────────────────────────┘
                        ↓
   ┌─────────────────────────────────────────────┐
   │            Application Layer                │
   │      (Views, Forms, URL Routing)            │
   └─────────────────────────────────────────────┘
                        ↓
   ┌─────────────────────────────────────────────┐
   │            Business Logic Layer             │
   │    (Services, Strategies, Validators)       │
   └─────────────────────────────────────────────┘
                        ↓
   ┌─────────────────────────────────────────────┐
   │              Data Layer                     │
   │       (Models, ORM, Database)               │
   └─────────────────────────────────────────────┘

Структура приложений
--------------------

Проект разделён на 6 Django-приложений:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Приложение
     - Назначение
     - Ключевые компоненты
   * - **ai**
     - AI-поиск
     - AiSearchService, SearchStrategy, Ollama integration
   * - **questions**
     - Q&A система
     - Question, Comment, Answer models
   * - **users**
     - Пользователи
     - User, Subscription, профили
   * - **complaints**
     - Модерация
     - Complaint model, панели администратора
   * - **notifications**
     - Уведомления
     - Notification model, signals
   * - **main**
     - Главная
     - Like/Dislike, главная страница

Паттерны проектирования
-----------------------

Strategy Pattern (AI-поиск)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Используется в модуле ``ai`` для гибкого выбора вопросов:

.. code-block:: python

   # Абстракция
   class SearchStrategy(ABC):
       @abstractmethod
       def get_questions(self, query):
           pass

   # Конкретные стратегии
   class AllQuestionsStrategy(SearchStrategy):
       def get_questions(self, query):
           return Question.objects.all()

   class LastNQuestionsStrategy(SearchStrategy):
       def __init__(self, n):
           self.n = n

       def get_questions(self, query):
           return Question.objects.order_by('-creation_date')[:self.n]

   # Использование
   service = AiSearchService(strategy=LastNQuestionsStrategy(30))
   service.search("Django ORM")

**Преимущества:**

* Легко добавлять новые стратегии
* Динамическое переключение логики
* Тестируемость

Signal-Receiver Pattern
~~~~~~~~~~~~~~~~~~~~~~~

Используется для создания уведомлений:

.. code-block:: python

   @receiver(post_save, sender=Comment)
   def notify_on_comment(sender, instance, created, **kwargs):
       if created:
           Notification.objects.create(
               user=instance.question.author,
               text=f'Новый комментарий от {instance.author.username}',
               link=f'/questions/{instance.question.id}/'
           )

**Преимущества:**

* Слабая связанность модулей
* Расширяемость без изменения существующего кода

Repository Pattern (частично)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django ORM играет роль репозитория:

.. code-block:: python

   # Вместо прямых SQL-запросов
   questions = Question.objects.filter(
       author=user
   ).select_related('author').prefetch_related('comment_set')

Модель данных
-------------

ER-диаграмма
~~~~~~~~~~~~

.. code-block:: text

   User ──┬──< Question ──< Comment ──< Answer
          │
          ├──< Subscription
          ├──< Like
          ├──< Dislike
          ├──< Complaint
          └──< Notification

Ключевые связи:

* **User → Question** (1:N) — автор вопросов
* **Question → Comment** (1:N) — комментарии к вопросу
* **Comment → Answer** (1:N) — ответы на комментарий
* **User ↔ User** (M:N через Subscription) — подписки
* **User ↔ Question** (M:N через Like/Dislike) — голосование

Бизнес-логика
-------------

Workflow создания вопроса
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Пользователь заполняет форму
      ↓
   2. Валидация формы (QuestionForm)
      ↓
   3. Сохранение в БД (Question.objects.create)
      ↓
   4. Редирект на страницу вопроса

Workflow AI-поиска
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Пользователь вводит запрос
      ↓
   2. Выбор стратегии (на основе ключевых слов)
      ↓
   3. Получение вопросов через стратегию
      ↓
   4. Формирование контекста (build_context)
      ↓
   5. Запрос к Ollama LLM
      ↓
   6. Генерация ответа
      ↓
   7. Возврат результата

Workflow модерации
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Пользователь создаёт жалобу
      ↓
   2. Валидация (нельзя жаловаться на свой контент)
      ↓
   3. Сохранение жалобы
      ↓
   4. Уведомление всех администраторов
      ↓
   5. Администратор рассматривает жалобу
      ↓
   6. Решение:
      ├─ Принять → Удаление/блокировка
      └─ Отклонить → Удаление жалобы

Интеграция с внешними сервисами
--------------------------------

Ollama LLM
~~~~~~~~~~

Архитектура интеграции:

.. code-block:: text

   Django App
      ↓
   AskOllamaClient (обёртка)
      ↓
   ollama.Client (библиотека)
      ↓
   HTTP REST API
      ↓
   Ollama Server (localhost:11434)
      ↓
   qwen3:1.7b Model

**Конфигурация:**

.. code-block:: python

   # ai/services.py
   ollama_client = ollama.Client(host="http://127.0.0.1:11434")

   class AskOllamaClient:
       def ask(self, system_prompt, user_prompt, model="qwen3:1.7b"):
           response = self._client.chat(
               model=model,
               messages=[
                   {"role": "system", "content": system_prompt},
                   {"role": "user", "content": user_prompt},
               ],
           )
           return response["message"]["content"].strip()

Безопасность
------------

Защита от основных угроз
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Угроза
     - Защита
   * - **CSRF**
     - Django CSRF middleware (кроме AI API с ``@csrf_exempt``)
   * - **SQL Injection**
     - Django ORM (параметризованные запросы)
   * - **XSS**
     - Django template auto-escaping
   * - **Unauthorized Access**
     - ``@login_required``, ``@user_passes_test``
   * - **Mass Assignment**
     - Явное указание полей в ``ModelForm.Meta.fields``

Проверка прав доступа
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Пример: только администраторы
   @user_passes_test(lambda u: u.is_staff)
   def admin_panel(request):
       pass

   # Пример: только автор может редактировать
   def edit_question(request, question_id):
       question = get_object_or_404(Question, id=question_id)
       if question.author != request.user:
           return HttpResponseForbidden()
       # ...

Производительность
------------------

Оптимизация запросов
~~~~~~~~~~~~~~~~~~~~

**N+1 проблема:**

.. code-block:: python

   # ПЛОХО
   for question in Question.objects.all():
       print(question.author.username)  # N запросов

   # ХОРОШО
   for question in Question.objects.select_related('author').all():
       print(question.author.username)  # 1 запрос

**Prefetch для связанных коллекций:**

.. code-block:: python

   questions = Question.objects.prefetch_related(
       'comment_set__author',
       'comment_set__answer_set'
   )

Индексы БД
~~~~~~~~~~

.. code-block:: python

   class Question(models.Model):
       # ...
       class Meta:
           indexes = [
               models.Index(fields=['-creation_date']),
               models.Index(fields=['author', '-creation_date']),
           ]

Кеширование
~~~~~~~~~~~

.. code-block:: python

   from django.core.cache import cache

   def get_popular_questions():
       cache_key = 'popular_questions'
       questions = cache.get(cache_key)

       if questions is None:
           questions = Question.objects.annotate(
               likes_count=Count('like')
           ).order_by('-likes_count')[:10]

           cache.set(cache_key, questions, timeout=300)  # 5 минут

       return questions

Масштабируемость
----------------

Горизонтальное масштабирование
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Load Balancer (Nginx)
          ↓
   ┌──────┼──────┐
   │      │      │
   App1  App2  App3  (Gunicorn workers)
   │      │      │
   └──────┼──────┘
          ↓
   PostgreSQL (master-slave)
          ↓
   Redis (cache, sessions)

Асинхронные задачи
~~~~~~~~~~~~~~~~~~

Для тяжёлых операций (будущее развитие):

.. code-block:: python

   # Используя Celery
   @app.task
   def process_ai_search(user_id, query):
       service = AiSearchService(...)
       result = service.search(query)
       # Сохранить результат
       return result.answer

Мониторинг и логирование
-------------------------

Логирование
~~~~~~~~~~~

.. code-block:: python

   import logging

   logger = logging.getLogger('project')

   # В views
   logger.info('User %s created question', request.user.username)
   logger.error('AI search failed: %s', error)

Настройка:

.. code-block:: python

   # settings.py
   LOGGING = {
       'version': 1,
       'handlers': {
           'file': {
               'class': 'logging.FileHandler',
               'filename': 'logs/project.log',
           },
       },
       'loggers': {
           'project': {
               'handlers': ['file'],
               'level': 'INFO',
           },
       },
   }

Развёртывание
-------------

Production stack
~~~~~~~~~~~~~~~~

.. code-block:: text

   Client
      ↓
   Nginx (reverse proxy, static files)
      ↓
   Gunicorn (WSGI server)
      ↓
   Django Application
      ↓
   PostgreSQL Database

**Конфигурация Gunicorn:**

.. code-block:: bash

   gunicorn The_Final_Build.wsgi:application \
       --bind 0.0.0.0:8000 \
       --workers 4 \
       --timeout 120

Будущие улучшения
-----------------

Планируемые функции:

1. **WebSocket для real-time уведомлений** (Django Channels)
2. **Полнотекстовый поиск** (PostgreSQL Full-Text Search или Elasticsearch)
3. **Рекомендательная система** (на основе ML)
4. **API на REST/GraphQL** (Django REST Framework)
5. **Мобильное приложение** (React Native)

См. также
---------

* :doc:`index` — детальная документация модулей
* :doc:`../api` — API документация
* :doc:`../installation` — руководство по установке