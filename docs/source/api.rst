API Документация
================

Документация REST API для программного взаимодействия с платформой.

.. note::
   Большинство API требуют аутентификации через Django сессии.

AI Search API
-------------

Интеллектуальный поиск по вопросам с использованием LLM.

Поиск
~~~~~

.. http:post:: /ai/api/

   Выполняет AI-поиск по базе вопросов.

   **Запрос:**

   .. sourcecode:: json

      {
        "q": "как работает Django ORM"
      }

   **Параметры запроса:**

   :q: (string) Поисковый запрос пользователя (обязательный)

   **Ответ при успехе (200 OK):**

   .. sourcecode:: json

      {
        "answer": "Django ORM — это Object-Relational Mapping система..."
      }

   **Ответ при ошибке (400 Bad Request):**

   .. sourcecode:: json

      {
        "error": "Пустой запрос"
      }

   **Возможные ошибки:**

   * ``"Пустой запрос"`` — запрос пустой или содержит только пробелы
   * ``"Подходящих постов не найдено"`` — нет релевантных вопросов
   * ``"Ошибка при обращении к ИИ: ..."`` — проблема с Ollama

   **Пример использования:**

   .. code-block:: javascript

      // JavaScript Fetch API
      fetch('/ai/api/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              q: 'расскажи про Python'
          })
      })
      .then(response => response.json())
      .then(data => {
          if (data.answer) {
              console.log(data.answer);
          } else {
              console.error(data.error);
          }
      });

   .. code-block:: python

      # Python requests
      import requests

      response = requests.post(
          'http://localhost:8000/ai/api/',
          json={'q': 'расскажи про Python'}
      )

      data = response.json()
      if 'answer' in data:
          print(data['answer'])
      else:
          print(f"Ошибка: {data['error']}")

   .. note::
      CSRF защита отключена для этого endpoint (``@csrf_exempt``).
      В production рекомендуется добавить токен-аутентификацию.

Страница AI-поиска
~~~~~~~~~~~~~~~~~~

.. http:get:: /ai/

   Отображает страницу AI-поиска с формой.

   **Query параметры:**

   :q: (string, optional) Предзаполненный поисковый запрос

   **Пример:**

   .. code-block:: http

      GET /ai/?q=Django+ORM HTTP/1.1

Complaints API
--------------

API для создания и обработки жалоб на контент.

Создание жалобы
~~~~~~~~~~~~~~~

.. http:post:: /complaint/

   Создаёт жалобу на контент или пользователя.

   **Query параметры (один обязателен):**

   :question_id: (int) ID вопроса для жалобы
   :user_id: (int) ID пользователя для жалобы
   :comment_id: (int) ID комментария для жалобы
   :answer_id: (int) ID ответа для жалобы

   **POST параметры:**

   :description: (string) Текст жалобы (обязательный, макс. 500 символов)

   **Требования:**

   * Пользователь должен быть авторизован
   * Пользователь не должен быть заблокирован (``active=True``)
   * Нельзя жаловаться на свой контент

   **Ответ при успехе:**

   .. sourcecode:: json

      {
        "ok": true
      }

   **Ответ при ошибке:**

   .. sourcecode:: json

      {
        "ok": false,
        "error": "Описание ошибки"
      }

   **Возможные ошибки:**

   * ``"Требуется авторизация"``
   * ``"Вы заблокированы и не можете отправлять жалобы"``
   * ``"Введите текст жалобы"``
   * ``"Максимум 500 символов"``
   * ``"Нельзя жаловаться на свой пост"``
   * ``"Не указан объект жалобы"``
   * ``"Пост не найден"``

   **Пример:**

   .. code-block:: javascript

      // Жалоба на вопрос
      const formData = new FormData();
      formData.append('description', 'Спам и реклама');

      fetch('/complaint/?question_id=42', {
          method: 'POST',
          body: formData
      })
      .then(r => r.json())
      .then(data => {
          if (data.ok) {
              alert('Жалоба отправлена');
          } else {
              alert(data.error);
          }
      });

   .. warning::
      При создании жалобы всем администраторам отправляется уведомление.

Принять жалобу
~~~~~~~~~~~~~~

.. http:get:: /accept/

   Принимает жалобу и применяет санкции к объекту.

   **Доступ:** только администраторы (``is_staff=True``)

   **Query параметры:**

   :complaint_id: (int) ID жалобы для обработки
   :to: (string, optional) URL для редиректа после обработки

   **Действия:**

   * **Question:** удаляет вопрос
   * **User:** блокирует пользователя (``active=False``)
   * **Comment:** удаляет комментарий
   * **Answer:** удаляет ответ

   После санкции жалоба удаляется.

Отклонить жалобу
~~~~~~~~~~~~~~~~

.. http:get:: /decline/

   Отклоняет жалобу без применения санкций.

   **Доступ:** только администраторы

   **Query параметры:**

   :complaint_id: (int) ID жалобы
   :to: (string, optional) URL для редиректа

   Жалоба просто удаляется из базы.

Likes API
---------

API для лайков и дизлайков вопросов.

Лайк
~~~~

.. http:get:: /like/

   Добавляет лайк вопросу.

   **Query параметры:**

   :question_id: (int) ID вопроса
   :to: (string, optional) URL для редиректа

   **Правила:**

   * Нельзя лайкнуть свой вопрос
   * Если был дизлайк, он удаляется
   * Повторный лайк удаляет предыдущий

Дизлайк
~~~~~~~

.. http:get:: /dislike/

   Добавляет дизлайк вопросу.

   **Query параметры:**

   :question_id: (int) ID вопроса
   :to: (string, optional) URL для редиректа

   **Правила:**

   * Нельзя дизлайкнуть свой вопрос
   * Если был лайк, он удаляется
   * Повторный дизлайк удаляет предыдущий

Notifications API
-----------------

Просмотр уведомлений
~~~~~~~~~~~~~~~~~~~~

.. http:get:: /notifications/

   Отображает страницу с уведомлениями пользователя.

   **Требования:** авторизация

   **Действие:** помечает все непрочитанные уведомления как прочитанные

Subscriptions API
-----------------

Подписка
~~~~~~~~

.. http:get:: /subscribe/

   Подписывается на пользователя.

   **Query параметры:**

   :user_id: (int) ID пользователя для подписки
   :to: (string, optional) URL для редиректа

   **Правила:**

   * Нельзя подписаться на себя
   * Повторная подписка отменяет предыдущую

   **Эффект:** создаёт уведомление у пользователя, на которого подписались

Ограничения и лучшие практики
------------------------------

Rate Limiting
~~~~~~~~~~~~~

В текущей версии rate limiting не реализован. В production рекомендуется:

* Использовать ``django-ratelimit``
* Ограничить AI-поиск: 10 запросов/мин на пользователя
* Ограничить создание жалоб: 5 жалоб/час

Аутентификация
~~~~~~~~~~~~~~

Текущая версия использует Django session auth. Для API-клиентов рекомендуется:

* Использовать Django REST Framework с Token Authentication
* Или OAuth2 через ``django-oauth-toolkit``

Обработка ошибок
~~~~~~~~~~~~~~~~

Всегда проверяйте коды ответов:

.. code-block:: javascript

   fetch('/api/endpoint')
       .then(response => {
           if (!response.ok) {
               throw new Error(`HTTP ${response.status}`);
           }
           return response.json();
       })
       .catch(error => console.error('Ошибка:', error));

См. также
---------

* :doc:`modules/ai` — документация модуля AI-поиска
* :doc:`modules/complains` — система жалоб
* :doc:`quickstart` — быстрый старт для пользователей