Модуль ai (AI-поиск)
====================

Модуль интеллектуального поиска по вопросам с использованием LLM.

Обзор
-----

Модуль ``ai`` реализует систему AI-поиска, которая использует:

* **Ollama** — локальный сервер LLM
* **qwen3:1.7b** — компактная модель для генерации ответов
* **Strategy Pattern** — гибкая стратегия выборки вопросов

Архитектура
-----------

.. code-block:: text

   User Query
      ↓
   AiSearchService
      ↓
   SearchStrategy ───→ get_questions()
      ↓
   build_context() ───→ форматирование контекста
      ↓
   AskOllamaClient ───→ запрос к LLM
      ↓
   Answer

Views
-----

.. automodule:: ai.views
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: ai.services
   :members:
   :undoc-members:
   :show-inheritance:

Strategies
----------

.. automodule:: ai.strategies
   :members:
   :undoc-members:
   :show-inheritance:

Apps
----

.. automodule:: ai.apps
   :members:
   :undoc-members:
   :show-inheritance:

Примеры использования
---------------------

Базовый поиск
~~~~~~~~~~~~~

.. code-block:: python

   from ai.services import AiSearchService
   from ai.strategies import LastNQuestionsStrategy

   # Создание сервиса
   strategy = LastNQuestionsStrategy(30)
   service = AiSearchService(strategy=strategy)

   # Выполнение поиска
   result = service.search("как работает Django ORM")

   if result.error:
       print(f"Ошибка: {result.error}")
   else:
       print(f"Ответ: {result.answer}")

Смена стратегии
~~~~~~~~~~~~~~~

.. code-block:: python

   from ai.strategies import AllQuestionsStrategy

   # Переключение на поиск по всем вопросам
   service.set_strategy(AllQuestionsStrategy())
   result = service.search("все вопросы о Python")

Кастомная стратегия
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai.strategies import SearchStrategy
   from questions.models import Question

   class TagBasedStrategy(SearchStrategy):
       """Поиск вопросов по тегу."""

       def __init__(self, tag_name):
           self.tag_name = tag_name

       def get_questions(self, query):
           return Question.objects.filter(tags__name=self.tag_name)

   # Использование
   strategy = TagBasedStrategy("python")
   service.set_strategy(strategy)

Настройка
---------

Переменные окружения
~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   # Адрес Ollama сервера
   OLLAMA_HOST=http://127.0.0.1:11434

   # Используемая модель
   OLLAMA_MODEL=qwen3:1.7b

Изменение системного промпта
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Отредактируйте ``ai/services.py``:

.. code-block:: python

   SYSTEM_PROMPT = """Ты — ассистент для работы с постами...

   Правила:
   1. ...
   2. ...
   """

Тестирование
------------

Запуск тестов модуля:

.. code-block:: bash

   python manage.py test ai

Производительность
------------------

Оптимизация запросов
~~~~~~~~~~~~~~~~~~~~

Используйте ``select_related`` и ``prefetch_related``:

.. code-block:: python

   def build_context(questions):
       questions = questions.select_related('author').prefetch_related(
           'comment_set__author',
           'comment_set__answer_set__author'
       )
       # ...

Кеширование
~~~~~~~~~~~

Добавьте кеширование результатов:

.. code-block:: python

   from django.core.cache import cache

   def search(self, user_query):
       cache_key = f"ai_search:{hash(user_query)}"
       cached = cache.get(cache_key)

       if cached:
           return cached

       result = # ... выполнение поиска
       cache.set(cache_key, result, timeout=3600)  # 1 час
       return result

Устранение проблем
------------------

Ollama не отвечает
~~~~~~~~~~~~~~~~~~

1. Проверьте, что Ollama запущен:

   .. code-block:: bash

      ollama serve

2. Проверьте доступность:

   .. code-block:: bash

      curl http://127.0.0.1:11434/api/tags

3. Проверьте модель:

   .. code-block:: bash

      ollama list

Медленные ответы
~~~~~~~~~~~~~~~~

* Уменьшите количество вопросов: ``LastNQuestionsStrategy(10)``
* Используйте более быструю модель (если доступна)
* Добавьте кеширование

См. также
---------

* :doc:`../api` — REST API документация
* :doc:`../quickstart` — быстрый старт