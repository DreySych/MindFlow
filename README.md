# MindFlow — Платформа для обмена знаний

> MindFlow — это социальная платформа для обмена знаниями и идеями, вдохновлённая концепцией Reddit, но с акцентом на интеллектуальные дискуссии и персонализированный контент. Платформа объединяет классические возможности форумов с современными технологиями искусственного интеллекта для создания уникального опыта взаимодействия

![Django](https://img.shields.io/badge/django-4.2%2B-092E20?logo=django)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Coverage](https://img.shields.io/badge/coverage-78%25-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

---

## 📋 Описание

MindFlow — это веб-платформа для обмена знаниями, созданная студенческой командой как дипломный проект. Платформа объединяет функционал форумов с современным AI-поиском на базе Ollama

**Ключевые особенности:**

- Система вопросов и ответов с рейтингом и модерацией
- Система уведомлений в реальном времени
- Модуль жалоб и модерации контента
- Семантический поиск на основе векторных эмбеддингов для поиска по смыслу
- AI-ассистент на базе **OpenRouter** для интеллектуальных ответов на вопросы
- Автоматически генерируемая документация на **Sphinx**

---

## ✨ Возможности

### Для пользователей
- 📝 Публикация вопросов с изображениями и тегами
- 💬 Комментирование и ответы на вопросы
- ⭐ Система рейтингов и репутации
- 🔔 Уведомления о новых ответах и комментариях
- 🔍 Семантический поиск по смыслу через векторные эмбеддинги
- 🤖 AI-ассистент на базе OpenRouter для интеллектуальных ответов
- 👤 Персональные профили с историей активности
- 📊 Подписки на других пользователей

### Для модераторов
- 🚨 Система жалоб и модерации контента
- 🛡️ Блокировка пользователей и удаление контента

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
- **AI/ML**: OpenRouter
- **Real-time**: Django Channels (WebSocket для уведомлений, чата и комментариев)
- **Документация**: Sphinx
- **Тестирование**: Django Test Suite, Coverage.py
- **CI/CD**: GitLab CI/CD (pipeline настроен)
- **Версионирование**: Git, GitLab

---

## 📦 Установка

### Предварительные требования

- Python 3.10 или выше
- Git

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

Создайте файл `.env` в корне проекта для хранения конфиденциальных настроек

#### Генерация SECRET_KEY

Выполните команду для создания уникального секретного ключа:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Скопируйте полученную строку

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
```

---

## 📁 Структура проекта

```
MindFlow/
├── ai/ # AI-поиск и интеграция с OpenRouter
│ ├── templates/ # HTML-шаблоны
│ ├── services.py # Бизнес-логика AI-сервисов
│ ├── strategies.py # Стратегии поиска
│ ├── views.py # API endpoints
│ └── tests.py # Юнит-тесты модуля
├── questions/ # Основной модуль вопросов/ответов
│ ├── templates/ # HTML-шаблоны
│ ├── models.py # Модели Question, Answer, Comment, Like
│ ├── views.py # Views для отображения и CRUD
│ ├── forms.py # Формы создания/редактирования
│ ├── consumers.py # real-time обновления вопросов и комментариев
│ ├── routing.py # WebSocket маршруты
│ └── tests.py # Тесты модуля
├── users/ # Пользователи и аутентификация
│ ├── templates/ # HTML-шаблоны
│ ├── models.py # Расширенная модель User
│ ├── views.py # Регистрация, профили, подписки
│ ├── utils.py # Восстановление пароля
│ └── tests.py # Тесты пользователей
├── notifications/ # Система уведомлений
│ ├── templates/ # HTML-шаблоны
│ ├── models.py # Модель Notification
│ ├── views.py # API уведомлений
│ └── tests.py # Тесты уведомлений
├── complains/ # Модуль панели жалоб
│ ├── templates/ # HTML-шаблоны
│ └── views.py # Обработка жалоб
├── complaints/ # Модуль жалоб и модерации
│ ├── templates/ # HTML-шаблоны
│ ├── models.py # Модель Complain
│ ├── views.py # Обработка жалоб
│ ├── forms.py # Формы для жалоб
│ └── tests.py # Тесты модерации
├── private_messages/ # Модуль ЛС
│ ├── templates/ # HTML-шаблоны
│ ├── models.py # Модель ЛС
│ ├── views.py # Обработка ЛС
│ ├── urls.py # Роутинги ЛС
│ ├── consumers.py # real-time обновления вопросов и комментариев
│ ├── routing.py # WebSocket маршруты
│ └── tests.py # Тесты ЛС
├── main/ # Главная страница и общие views
│ ├── templates/ # HTML-шаблоны
│ ├── views.py # Обработчики запросов (главная страница, поиск)
│ ├── forms.py # Формы для пользовательского ввода
│ └── tests.py # Тесты для views и форм
├── The_Final_Build/ # Настройки проекта Django
│ ├── settings.py # Конфигурация Django
│ ├── urls.py # Главный роутинг
│ └── wsgi.py / asgi.py # WSGI/ASGI точки входа
├── docs/ # Sphinx документация
│ ├── source/ # Исходники документации
│ └── build/html/ # Собранная HTML-документация
├── static/ # Статические файлы (CSS, JS, изображения)
├── basic_elements/ # Базовые шаблоны
├── .env.example # Пример файла окружения
├── requirements.txt # Python-зависимости
├── .gitlab-ci.yml # CI/CD pipeline
├── .coverage # Файл с данными о покрытии
├── .pylintrc # Файл конфигурации для Pylint
├── .gitignore # Исключения из репозитория
├── LICENSE # Лицензия
├── DEPLOY.md # Инструкция по развёртыванию 
├── manage.py # Django CLI
├── patterns.txt # Обоснование использования паттернов 
├── CONTRIBUTING.md # Информация для разработчиков
└── README.md # Документация проекта
```
---

## 🏗 Архитектура

Проект построен по **MVT (Model-View-Template)** паттерну Django с дополнительным **Service Layer** для бизнес-логики

### Архитектурные принципы

- **Separation of Concerns**: каждое приложение отвечает за свою доменную область
- **Service Layer Pattern**: сложная логика вынесена в `services.py`
- **Repository Pattern**: работа с БД инкапсулирована в моделях
- **API-First**: все функции доступны через REST API


### Модульная структура

- **main**: рекомендации, подписки, лайки
- **questions**: ядро платформы (вопросы, ответы, комментарии)
- **users**: управление пользователями и профилями
- **notifications**: асинхронные уведомления
- **complaints**: модерация и жалобы
- **complains**: панель жалоб
- **private_messages**: ЛС
- **ai**: AI-интеграция, изолирована от остальной логики

---

## 🔌 API

### Основные эндпоинты

#### AI-поиск

**`POST /ai/api/`**

Выполняет интеллектуальный поиск с использованием OpenRouter LLM

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

> Полный список эндпоинтов см. в документации Sphinx

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
- ✅ Покрывайте код **тестами** (coverage ≥ 70%)
- ✅ Обновляйте **Sphinx документацию** в docstrings
- ✅ Убедитесь, что **все тесты проходят**: `python manage.py test`
- ✅ Пройдите **CI/CD pipeline** перед Merge Request

Подробнее см. [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 👤 Разработчики

**Тимлид**: Колесников Андрей  
- GitLab: [@Drey_Sych](https://gitlab.informatics.ru/Drey_Sych)  
- Email: [andreyakolesnikovg@gmail.com](mailto:andreyakolesnikovg@gmail.com)

**Ведущий разработчик**: Чуранкин Макар  
- GitLab: [@calalal](https://gitlab.informatics.ru/calalal)  
- Email: [calalcalalx2@gmail.com](mailto:calalcalalx2@gmail.com)

**Фронтенд-лид**: Голубенко Степан  
- GitLab: [@St_Gol](https://gitlab.informatics.ru/St_Gol)  
- Email: [stepangolubenko77@gmail.com](mailto:stepangolubenko77@gmail.com)

**Бэкенд-лид**: Ткаченко Кирилл  
- GitLab: [@GlupiMakak](https://gitlab.informatics.ru/GlupiMakak)  
- Email: [glupimakak@gmail.com](mailto:glupimakak@gmail.com)

**Серверный разработчик**: Кокоткин Евгений  
- GitLab: [@Gesha](https://gitlab.informatics.ru/Gesha)  
- Email: [zhenechka.ko@mail.ru](mailto:zhenechka.ko@mail.ru)

**Клиентский разработчик**: Кочуров Никита  
- GitLab: [@Nekoseko](https://gitlab.informatics.ru/Nekoseko)  
- Email: [nekokrator@mail.ru](mailto:nekokrator@mail.ru)

**Клиентский разработчик**: Сехин Алексей  
- GitLab: [@azer0](https://gitlab.informatics.ru/azer0)  
- Email: [sigmaalfamale123@gmail.com](mailto:sigmaalfamale123@gmail.com)

---

## 🙏 Благодарности

- [Django](https://www.djangoproject.com/) — мощный веб-фреймворк
- [OpenRouter](https://openrouter.ai/) — AI интерфейс
- [Sphinx](https://www.sphinx-doc.org/) — документация проекта
- [Read the Docs](https://readthedocs.org/) — тема документации

Наставникам и преподавателям за поддержку проекта:
- Волкова Наталья Игоревна
- Опришко Владислав Дмитриевич

---

## 📄 Лицензия

Этот проект создан в образовательных целях. Все права защищены © 2026 MindFlow Team

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
- 📚 Sphinx Docs — полная техническая документация (см. `docs/build/html/index.html`)

---
