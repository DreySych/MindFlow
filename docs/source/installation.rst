Установка и настройка
=====================

Системные требования
--------------------

Для локального запуска проекта требуется:

* Python 3.12 или совместимая версия;
* Git;
* SQLite для локальной разработки;
* установленный пакетный менеджер ``pip``;
* виртуальное окружение Python;
* доступ к SMTP-почте, если нужно проверять восстановление пароля;
* ключ OpenRouter API, если нужно проверять внешний AI-функционал без fallback.

Клонирование проекта
--------------------

.. code-block:: bash

   git clone <repository-url>
   cd MindFlow

Создание виртуального окружения
-------------------------------

Windows PowerShell:

.. code-block:: powershell

   python -m venv .venv
   .venv\Scripts\activate

Linux/macOS:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate

Установка зависимостей
----------------------

.. code-block:: bash

   pip install -r requirements.txt

Файл окружения
--------------

Создайте файл ``.env`` в корне проекта. В репозиторий должен попадать только ``.env.example``.

Пример переменных:

.. code-block:: bash

   SECRET_KEY=your-secret-key
   DEBUG=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   OPENROUTER_API_KEY=your-openrouter-key

Для production-окружения значение ``DEBUG`` должно быть ``False``.

Миграции
--------

.. code-block:: bash

   python manage.py migrate

Создание администратора
-----------------------

.. code-block:: bash

   python manage.py createsuperuser

Запуск проекта
--------------

.. code-block:: bash

   python manage.py runserver

После запуска сайт будет доступен по адресу:

.. code-block:: text

   http://127.0.0.1:8000/
