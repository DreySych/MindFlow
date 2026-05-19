API и маршруты
==============

Этот раздел описывает основные HTTP-маршруты проекта. Большая часть действий использует Django session authentication.

Главная страница и поиск
------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET
     - ``/``
     - Главная страница с лентой постов.
   * - GET
     - ``/?q=<query>``
     - Semantic search по постам.
   * - GET
     - ``/?tag=<tag>``
     - Фильтрация постов по тегу.
   * - GET
     - ``/?page=<number>``
     - AJAX-подгрузка следующей страницы постов.
   * - GET
     - ``/sidebar/``
     - Рендер боковой панели.

Посты
-----

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET
     - ``/question/<id>/``
     - Страница поста.
   * - POST
     - ``/question/<id>/``
     - Создание комментария к посту.
   * - GET
     - ``/question/make/``
     - Форма создания поста.
   * - POST
     - ``/question/make/``
     - Создание поста.
   * - GET
     - ``/question/edit/?id=<id>``
     - Форма редактирования поста.
   * - POST
     - ``/question/edit/?id=<id>``
     - Сохранение изменений поста.
   * - POST
     - ``/question/<id>/delete/``
     - Удаление поста с проверкой прав.
   * - GET
     - ``/get_tags/``
     - JSON-список доступных тегов.

Голосование
-----------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET
     - ``/like/?id=<question_id>``
     - Лайк поста.
   * - GET
     - ``/dislike/?id=<question_id>``
     - Дизлайк поста.
   * - GET
     - ``/comment/like/?id=<comment_id>``
     - Лайк комментария.
   * - GET
     - ``/comment/dislike/?id=<comment_id>``
     - Дизлайк комментария.
   * - GET
     - ``/answer/like/?id=<answer_id>``
     - Лайк ответа.
   * - GET
     - ``/answer/dislike/?id=<answer_id>``
     - Дизлайк ответа.

Ответы
------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - POST
     - ``/comment/<comment_id>/answer/``
     - Создание ответа на комментарий.

Пользователи
------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET/POST
     - ``/account/signup/``
     - Регистрация.
   * - GET/POST
     - ``/account/login/``
     - Вход.
   * - GET
     - ``/account/logout/``
     - Выход.
   * - GET
     - ``/profile/``
     - Редирект на профиль текущего пользователя.
   * - GET
     - ``/profile/<username>/``
     - Профиль пользователя.
   * - GET/POST
     - ``/profile/settings``
     - Настройки профиля.
   * - GET
     - ``/profile/<username>/comments/``
     - Комментарии пользователя.
   * - GET
     - ``/profile/<username>/liked/``
     - Понравившиеся материалы.
   * - POST
     - ``/add_friend/<user_id>/``
     - Подписка на пользователя.
   * - POST
     - ``/delete_friend/<user_id>/``
     - Отписка от пользователя.

Жалобы
------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - POST
     - ``/complaint/``
     - Создание жалобы.
   * - GET
     - ``/complaint/panel/users/``
     - Панель жалоб на пользователей.
   * - GET
     - ``/complaint/panel/questions/``
     - Панель жалоб на посты.
   * - GET
     - ``/complaint/panel/comments/``
     - Панель жалоб на комментарии и ответы.
   * - POST
     - ``/accept/?complaint_id=<id>``
     - Принятие жалобы модератором.
   * - POST
     - ``/decline/?complaint_id=<id>``
     - Отклонение жалобы модератором.

AI-поиск
--------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET
     - ``/ai/``
     - Страница AI-поиска.
   * - POST
     - ``/ai/api/``
     - JSON API для AI-поиска.

Пример запроса к AI API:

.. code-block:: json

   {
     "q": "как работает Django ORM"
   }

Пример успешного ответа:

.. code-block:: json

   {
     "answer": "..."
   }

Пример ошибки:

.. code-block:: json

   {
     "error": "Пустой запрос"
   }

Уведомления
-----------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET
     - ``/notifications/list/``
     - Список уведомлений текущего пользователя.
   * - GET
     - ``/notifications/count/``
     - Количество непрочитанных уведомлений.
   * - GET
     - ``/notifications/read/<id>/``
     - Отметка уведомления как прочитанного.

Личные сообщения
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Метод
     - URL
     - Назначение
   * - GET
     - ``/messages/<user_id>/``
     - Страница диалога.
   * - GET
     - ``/messages/<user_id>/messages/?page=<number>``
     - JSON-подгрузка истории сообщений.

WebSocket-маршрут чата:

.. code-block:: text

   /ws/chat/<user_id>/
