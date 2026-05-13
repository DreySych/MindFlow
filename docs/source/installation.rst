Установка и настройка
=====================

Это руководство поможет вам установить и настроить проект для локальной разработки.

Системные требования
--------------------

Минимальные требования:

* **Операционная система:** Linux, macOS или Windows 10/11
* **RAM:** 4 GB (рекомендуется 8 GB)
* **Свободное место:** 10 GB
* **Python:** 3.10 или выше
* **PostgreSQL:** 13+ (опционально для разработки)
* **Ollama:** последняя версия

Предварительная установка
-------------------------

Python
~~~~~~

Проверьте установленную версию Python:

.. code-block:: bash

   python --version

Если Python не установлен, скачайте с `python.org <https://python.org>`_.

Git
~~~

.. code-block:: bash

   git --version

Установка Git:

* **Ubuntu/Debian:** ``sudo apt install git``
* **macOS:** ``brew install git``
* **Windows:** скачайте с `git-scm.com <https://git-scm.com>`_

Ollama
~~~~~~

**Linux:**

.. code-block:: bash

   curl https://ollama.ai/install.sh | sh

**macOS:**

.. code-block:: bash

   brew install ollama

**Windows:**

Скачайте установщик с `ollama.ai <https://ollama.ai/download>`_

После установки загрузите модель:

.. code-block:: bash

   ollama pull qwen3:1.7b
   ollama serve

Установка проекта
-----------------

Шаг 1: Клонирование репозитория
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone <repository-url>
   cd The_Final_Build

Шаг 2: Виртуальное окружение
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Linux/macOS:**

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

**Windows:**

.. code-block:: bash

   python -m venv venv
   venv\Scripts\activate

Шаг 3: Установка зависимостей
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install --upgrade pip
   pip install -r requirements.txt

Шаг 4: Настройка переменных окружения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Создайте файл ``.env`` в корне проекта:

.. code-block:: bash

   cp .env.example .env

Пример содержимого ``.env``:

.. code-block:: ini

   # Django
   SECRET_KEY=django-insecure-change-me
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database (SQLite)
   DB_ENGINE=django.db.backends.sqlite3
   DB_NAME=db.sqlite3

   # Ollama
   OLLAMA_HOST=http://127.0.0.1:11434
   OLLAMA_MODEL=qwen3:1.7b

Шаг 5: Миграции базы данных
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py makemigrations
   python manage.py migrate

Шаг 6: Создание суперпользователя
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py createsuperuser

Введите имя пользователя, email и пароль.

Шаг 7: Сбор статических файлов (опционально)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py collectstatic

Шаг 8: Запуск сервера разработки
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py runserver

Откройте в браузере: http://127.0.0.1:8000

Проверка установки
------------------

После запуска сервера проверьте:

1. **Главная страница:** http://127.0.0.1:8000/
2. **Админ-панель:** http://127.0.0.1:8000/admin/
3. **AI-поиск:** http://127.0.0.1:8000/ai/

Убедитесь, что Ollama запущен:

.. code-block:: bash

   curl http://127.0.0.1:11434/api/tags

Вы должны увидеть список моделей, включая ``qwen3:1.7b``.

Устранение проблем
------------------

Ошибка импорта Django
~~~~~~~~~~~~~~~~~~~~~

Если видите ``ImportError: No module named django``:

.. code-block:: bash

   pip install Django

Ошибка подключения к Ollama
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Если AI-поиск не работает:

1. Проверьте, что Ollama запущен: ``ollama serve``
2. Проверьте адрес в ``.env``: ``OLLAMA_HOST=http://127.0.0.1:11434``
3. Убедитесь, что модель загружена: ``ollama list``

Ошибки миграций
~~~~~~~~~~~~~~~

Если миграции не применяются:

.. code-block:: bash

   python manage.py migrate --run-syncdb

Следующие шаги
--------------

После успешной установки:

* Изучите :doc:`quickstart` для быстрого старта
* Прочитайте :doc:`api` для работы с API
* См. :doc:`modules/index` для документации модулей