# MindFlow — Платформа для обмена знаний

> MindFlow — это социальная платформа для обмена знаниями и идеями, вдохновлённая концепцией Reddit, но с акцентом на интеллектуальные дискуссии и персонализированный контент. Платформа объединяет классические возможности форумов с современными технологиями искусственного интеллекта для создания уникального опыта взаимодействия.

![Django](https://img.shields.io/badge/django-4.2%2B-092E20?logo=django)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Coverage](https://img.shields.io/badge/coverage-78%25-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

---

## 📋 Описание

MindFlow — это веб-платформа для обмена знаниями, созданная студенческой командой как дипломный проект. Платформа объединяет функционал форумов с современным AI-поиском на базе Ollama для интеллектуальных дискуссий.

**Ключевые особенности:**
- Система вопросов и ответов с рейтингом и модерацией
- AI-powered поиск на базе Ollama для персонализированных ответов
- Система уведомлений в реальном времени
- Модуль жалоб и модерации контента
- REST API для интеграции с внешними сервисами
- Полная документация на Sphinx

---

## ✨ Возможности

### Для пользователей
- 📝 Публикация вопросов с изображениями и тегами
- 💬 Комментирование и ответы на вопросы
- ⭐ Система рейтингов и репутации
- 🔔 Уведомления о новых ответах и комментариях
- 🔍 AI-поиск с использованием Ollama LLM
- 👤 Персональные профили с историей активности
- 📊 Подписки на других пользователей

### Для модераторов
- 🚨 Система жалоб и модерации контента
- 🛡️ Блокировка пользователей и удаление контента
- 📈 Статистика активности платформы

### Технические возможности
- 🔌 REST API для всех основных операций
- 📚 Автоматически генерируемая Sphinx документация
- 🧪 Покрытие тестами > 78%

---

## 🛠 Технологии

- **Backend**: Python 3.10+, Django 4.2
- **API**: Django REST Framework, FastAPI (для AI-сервисов)
- **База данных**: SQLite
- **Фронтенд**: HTML, CSS, JavaScript
- **AI/ML**: Ollama
- **Документация**: Sphinx с Read the Docs темой
- **Тестирование**: Django Test Suite, Coverage.py
- **CI/CD**: GitLab CI/CD (pipeline настроен)
- **Версионирование**: Git, GitLab

---

## 📦 Установка

### Предварительные требования

- Python 3.10 или выше
- Git
- Ollama (для AI-функционала)

### Шаг 1: Клонирование репозитория

```bash
git clone https://gitlab.informatics.ru/Drey_Sych/MindFlow.git
cd MindFlow
```

### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate   # для Windows
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

Создайте файл `.env` в корне проекта для хранения конфиденциальных настроек.

#### Генерация SECRET_KEY

Выполните команду для создания уникального секретного ключа:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Скопируйте полученную строку.

#### Создание файла .env

Создайте файл `.env` в корневой папке проекта со следующим содержимым:

```env
SECRET_KEY=django-insecure-ваш-сгенерированный-ключ
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Шаг 5: Применение миграций

```bash
python manage.py migrate
```

### Шаг 6: Создание суперпользователя

```bash
python manage.py createsuperuser
```

---

## 🚀 Запуск

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: `http://127.0.0.1:8000/`

**Админ-панель**: `http://127.0.0.1:8000/admin/`

---

## ⚙️ Конфигурация

### Переменные окружения

| Переменная       | Описание                        | Обязательна | Значение по умолчанию |
|------------------|---------------------------------|-------------|-----------------------|
| `SECRET_KEY`     | Секретный ключ Django           | Да          | —                     |
| `DEBUG`          | Режим отладки                   | Нет         | `False`               |
| `DATABASE_URL`   | URL подключения к базе данных   | Да          | —                     |
| `ALLOWED_HOSTS`  | Разрешённые хосты               | Нет         | `localhost`           |

---

## 🧪 Тестирование

### Запуск всех тестов

```bash
python manage.py test
```

### Запуск конкретного теста

```bash
python manage.py test ai.tests.test_service
```

### Запуск с покрытием

```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # HTML-отчёт в htmlcov/index.html
```

---

## 📁 Структура проекта

```
MindFlow/
├── ai/ # AI-поиск и интеграция с Ollama
│ ├── services.py # Бизнес-логика AI-сервисов
│ ├── strategies.py # Стратегии поиска
│ ├── views.py # API endpoints
│ └── tests/ # Юнит-тесты модуля
├── questions/ # Основной модуль вопросов/ответов
│ ├── models.py # Модели Question, Answer, Comment, Like
│ ├── views.py # Views для отображения и CRUD
│ ├── forms.py # Формы создания/редактирования
│ └── tests/ # Тесты модуля
├── users/ # Пользователи и аутентификация
│ ├── models.py # Расширенная модель User
│ ├── views.py # Регистрация, профили, подписки
│ └── tests/ # Тесты пользователей
├── notifications/ # Система уведомлений
│ ├── models.py # Модель Notification
│ ├── views.py # API уведомлений
│ └── tests/ # Тесты уведомлений
├── complains/ # Модуль жалоб и модерации
│ ├── models.py # Модель Complain
│ ├── views.py # Обработка жалоб
│ └── tests/ # Тесты модерации
├── main/ # Главная страница и общие views
├── The_Final_Build/ # Настройки проекта Django
│ ├── settings.py # Конфигурация Django
│ ├── urls.py # Главный роутинг
│ └── wsgi.py / asgi.py # WSGI/ASGI точки входа
├── docs/ # Sphinx документация
│ ├── source/ # Исходники документации
│ └── build/html/ # Собранная HTML-документация
├── static/ # Статические файлы (CSS, JS, изображения)
├── media/ # Загруженные пользователями файлы
├── templates/ # HTML-шаблоны
├── .env.example # Пример файла окружения
├── requirements.txt # Python-зависимости
├── docker-compose.yml # Docker Compose конфигурация
├── Dockerfile # Docker образ приложения
├── .gitlab-ci.yml # CI/CD pipeline
├── manage.py # Django CLI
└── README.md # Документация проекта
```
---

## 🏗 Архитектура

Проект построен по **MVT (Model-View-Template)** паттерну Django с дополнительным **Service Layer** для бизнес-логики.

### Архитектурные принципы

- **Separation of Concerns**: каждое приложение отвечает за свою доменную область
- **Service Layer Pattern**: сложная логика вынесена в `services.py`
- **Repository Pattern**: работа с БД инкапсулирована в моделях
- **API-First**: все функции доступны через REST API


### Модульная структура

- **ai**: AI-интеграция, изолирована от остальной логики
- **questions**: ядро платформы (вопросы, ответы, комментарии)
- **users**: управление пользователями и профилями
- **notifications**: асинхронные уведомления
- **complains**: модерация и жалобы

---

## 🔌 API

Полная документация API доступна в [Sphinx Docs](docs/build/html/api.html).

### Основные эндпоинты

#### AI-поиск

**`POST /ai/api/`**

Выполняет интеллектуальный поиск с использованием Ollama LLM.

**Request:**
```json
{
  "q": "Как работает Django ORM?"
}
```

**Response (200 OK):**
```json
{
  "query": "Как работает Django ORM?",
  "answer": "Django ORM (Object-Relational Mapping) — это...",
  "error": null
}
```

**Response (400 Bad Request):**
```json
{
  "query": "Как работает Django ORM?",
  "answer": null,
  "error": "Сервис AI недоступен"
}
```

**Коды ответа:**
- `200` — Успех
- `400` — Ошибка сервиса
- `405` — Метод не разрешён

#### Вопросы

- **`GET /questions/api/`** — список всех вопросов
- **`POST /questions/api/create/`** — создать вопрос
- **`GET /questions/api/<id>/`** — детали вопроса
- **`PUT /questions/api/<id>/update/`** — обновить вопрос
- **`DELETE /questions/api/<id>/delete/`** — удалить вопрос

#### Уведомления

- **`GET /notifications/api/`** — список уведомлений
- **`POST /notifications/api/<id>/read/`** — отметить прочитанным

> Полный список эндпоинтов см. в документации Sphinx.

---

## 🤝 Контрибуция

Мы приветствуем вклад в развитие проекта! 🎉

### Быстрый старт

1. Форкните репозиторий
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Внесите изменения и закоммитьте: `git commit -m 'Add amazing feature'`
4. Запушьте ветку: `git push origin feature/amazing-feature`
5. Создайте Merge Request

### Требования к коду

- ✅ Следуйте **PEP 8** (используйте `pylint`, рейтинг ≥ 8.0/10)
- ✅ Покрывайте код **тестами** (coverage ≥ 80%)
- ✅ Обновляйте **Sphinx документацию** в docstrings
- ✅ Убедитесь, что **все тесты проходят**: `python manage.py test`
- ✅ Пройдите **CI/CD pipeline** перед MR

Подробнее см. [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 👤 Разработчики

**Тимлид**: Колесников Андрей  
- GitLab: [@Drey_Sych](https://gitlab.informatics.ru/Drey_Sych)  
- Email: [andreyakolesnikovg@gmail.com](mailto:andreyakolesnikovg@gmail.com)

**Ведущий разработчик**: Чуранкин Макар  
- GitLab: [@calalal](https://gitlab.informatics.ru/calalal)  
- Email: [добавить email]

**Фронтенд-лид**: Голубенко Степан  
- GitLab: [@St_Gol](https://gitlab.informatics.ru/St_Gol)  
- Email: [добавить email]

**Бэкенд-лид**: Ткаченко Кирилл  
- GitLab: [@GlupiMakak](https://gitlab.informatics.ru/GlupiMakak)  
- Email: [добавить email]

**Серверный разработчик**: Кокоткин Евгений  
- GitLab: [@Gesha](https://gitlab.informatics.ru/Gesha)  
- Email: [добавить email]

**Клиентский разработчик**: Кочуров Никита  
- GitLab: [@Nekoseko](https://gitlab.informatics.ru/Nekoseko)  
- Email: [добавить email]

**Клиентский разработчик**: Сехин Алексей  
- GitLab: [@azer0](https://gitlab.informatics.ru/azer0)  
- Email: [добавить email]

---

## 🙏 Благодарности

- [Django](https://www.djangoproject.com/) — мощный веб-фреймворк
- [Ollama](https://ollama.ai/) — локальный AI inference
- [Sphinx](https://www.sphinx-doc.org/) — документация проекта
- [Read the Docs](https://readthedocs.org/) — тема документации

Наставникам и преподавателям за поддержку проекта:
- Волкова Наталья Игоревна
- Опришко Владислав Дмитриевич

---

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

### Баг-репорты и предложения
- 🐛 [Создайте Issue](https://gitlab.informatics.ru/Drey_Sych/the-final-build/-/issues)
- 💡 [Обсудите в Discussions](https://gitlab.informatics.ru/Drey_Sych/the-final-build/-/issues)

### Связь с командой
- 📧 Email тимлида: [andreyakolesnikovg@gmail.com](mailto:andreyakolesnikovg@gmail.com)
- 💬 GitLab: [@Drey_Sych](https://gitlab.informatics.ru/Drey_Sych)

### Документация
- 📚 [Sphinx Docs](docs/build/html/index.html) — полная техническая документация

---


