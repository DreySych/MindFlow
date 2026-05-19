Модуль ai
=========

Приложение ``ai`` отвечает за AI-поиск по содержимому платформы. Оно собирает контекст из постов, комментариев и ответов, выбирает стратегию получения данных и обращается к внешнему AI API.

Ключевые элементы
-----------------

* ``AiSearchService`` — основной сервис AI-поиска;
* ``SearchStrategy`` — интерфейс стратегий;
* ``AllQuestionsStrategy`` — выбор всех вопросов;
* ``LastNQuestionsStrategy`` — выбор последних N вопросов;
* ``OpenRouterClient`` — адаптер внешнего API;
* ``ai_search_api`` — JSON endpoint для поиска.

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

Clients
-------

.. automodule:: ai.clients
   :members:
   :undoc-members:
   :show-inheritance:
