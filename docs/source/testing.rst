Тестирование
============

Общее описание
--------------

Проект использует стандартные средства тестирования Django. Тесты проверяют основные сценарии работы приложений: создание постов, комментарии, ответы, лайки, жалобы, пользователей, уведомления и AI-поиск.

Запуск всех тестов
------------------

.. code-block:: bash

   python manage.py test

Запуск тестов одного приложения
-------------------------------

.. code-block:: bash

   python manage.py test questions
   python manage.py test users
   python manage.py test complaints
   python manage.py test notifications
   python manage.py test ai

Покрытие тестами
----------------

Для проверки coverage:

.. code-block:: bash

   coverage run manage.py test
   coverage report

HTML-отчёт coverage:

.. code-block:: bash

   coverage html

После этого отчёт будет доступен в папке:

.. code-block:: text

   htmlcov/

Что проверяют тесты
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Блок
     - Проверяемые сценарии
   * - Посты
     - Создание, редактирование, удаление, отображение страницы поста.
   * - Комментарии
     - Создание комментария авторизованным пользователем и запрет для неавторизованных/заблокированных.
   * - Ответы
     - Создание ответа на комментарий и проверки доступа.
   * - Лайки
     - Лайк, дизлайк, повторное нажатие, переключение лайк/дизлайк.
   * - Пользователи
     - Регистрация, вход, профиль, настройки, подписка и отписка.
   * - Жалобы
     - Создание жалобы, принятие, отклонение, блокировка пользователя, удаление объекта.
   * - Уведомления
     - Создание и отображение уведомлений.
   * - AI
     - Работа AI-поиска и обработка ошибок.

CI/CD для тестов
----------------

Для автоматического запуска тестов можно использовать ``.gitlab-ci.yml``:

.. code-block:: yaml

   stages:
     - test
     - docs

   test:
     image: python:3.12
     script:
       - pip install -r requirements.txt
       - python manage.py test

   docs:
     image: python:3.12
     script:
       - pip install -r requirements.txt
       - pip install sphinx
       - sphinx-build -b html docs/source docs/build/html
     artifacts:
       paths:
         - docs/build/html
