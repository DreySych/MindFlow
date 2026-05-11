# MindFlow — Платформа для обмена знаний

> MindFlow — это социальная платформа для обмена знаниями и идеями, вдохновлённая концепцией Reddit, но с акцентом на интеллектуальные дискуссии и персонализированный контент. Платформа объединяет классические возможности форумов с современными технологиями искусственного интеллекта для создания уникального опыта взаимодействия.

![Django](https://img.shields.io/badge/django-4.2%2B-092E20?logo=django)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Coverage](https://img.shields.io/badge/coverage-0%25-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

---

## 📋 Описание

- Проект представляет собой веб‑приложение на Django, которое можно быстро развернуть локально и использовать как основу для дальнейшей разработки
- ?

---

## ✨ Возможности

- Готовая структура Django‑проекта с настроенным виртуальным окружением и базой данных SQLite.
- Админ‑панель Django для управления данными через веб‑интерфейс.
- Возможность быстро добавлять новые приложения, модели и API‑эндпоинты.
- Интеграция с внешними сервисами и API через стандартные Django‑модули и сторонние библиотеки.
- ?

---

## 🛠 Технологии

- **Backend**: Python 3.10+, Django 4.2 / FastAPI
- **База данных**: SQLite
- **Фронтенд**: HTML, CSS, JavaScript
- **Дополнительно**: ?
- **AI**: Ollama

---

## 📦 Установка

### Предварительные требования

- Python 3.10 или выше
- ?

### Шаг 1: Клонирование репозитория

```bash
git clone https://gitlab.informatics.ru/Drey_Sych/MindFlow.git
cd project-name
```

### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\\Scripts\\activate   # для Windows
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

### Шаг 6: Создание суперпользователя (для Django)

```bash
python manage.py createsuperuser
```

---

## 🚀 Запуск

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: `http://127.0.0.1:8000/`

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
project-name/
├── ai/                     # Основное приложение
│   ├── migrations/         # Миграции базы данных
│   ├── models.py           # Модели данных
│   ├── views.py            # Views и API endpoints
│   ├── service.py          # Бизнес-логика
│   ├── tests.py            # Юнит-тесты
│   └── urls.py             # URL-маршруты
├── project_name/           # Настройки проекта
│   ├── settings.py         # Конфигурация Django
│   ├── urls.py             # Главные URL
│   └── wsgi.py             # WSGI точка входа
├── ???????????
├── static/                 # Статические файлы
├── .env.example            # Пример файла окружения
├── requirements.txt        # Зависимости Python
├── docker-compose.yml      # Docker Compose
├── manage.py               # Django CLI
└── README.md               # Документация
```

---

## 🏗 Архитектура

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Django View│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │
└─────────────┘
```

Проект следует паттерну **Service Layer**: view отвечает за HTTP, service — за бизнес-логику.

?????????????????

---

## 🔌 API

??????????????????????????????????????

### `POST ai/api/`

Выполняет поиск с использованием AI.

**Request:**

```json
{
  "q": "ваш запрос"
}
```

**Response (успех):**

```json
{
  "query": "ваш запрос",
  "answer": "Ответ системы",
  "error": null
}
```

**Response (ошибка):**

```json
{
  "query": "ваш запрос",
  "answer": null,
  "error": "Описание ошибки"
}
```

**Коды ответа:**
- `200` — Успех
- `400` — Ошибка сервиса
- `405` — Метод не разрешён

---

## 🤝 Контрибуция

Мы приветствуем вклад в проект!

1. Форкните репозиторий
2. Создайте ветку для фичи: `git checkout -b feature/new-feature`
3. Закоммитьте изменения: `git commit -m 'Add new feature'`
4. Запушьте в ветку: `git push origin feature/new-feature`
5. ?

### Правила оформления кода

- Следуйте PEP 8 (pylint coderate >= 8.0/10.0)
- Покрывайте код тестами (coverage > 80%)
- Обновляйте документацию Sphinx
- ?

---

## 👤 Разработчики

Тимлид: **Колесников Андрей**

- GitLab: [@Drey_Sych](https://gitlab.informatics.ru/Drey_Sych)
- Email: andreyakolesnikovg@gmail.com

Ведущий разработчик: **Чуранкин Макар**

- GitLab: [@calalal](https://gitlab.informatics.ru/calalal)
- Email: ?

Фронтенд-лид: **Голубенко Степан**

- GitLab: [@St_Gol](https://gitlab.informatics.ru/St_Gol)
- Email: ?

Бэкенд-лид: **Ткаченко Кирилл**

- GitLab: [@GlupiMakak](https://gitlab.informatics.ru/GlupiMakak)
- Email: ?

Серверный разработчик: **Кокоткин Евгений**

- GitLab: [@Gesha](https://gitlab.informatics.ru/Gesha)
- Email: ?

Клиентский разработчик: **Кочуров Никита**

- GitLab: [@Nekoseko](https://gitlab.informatics.ru/Nekoseko)
- Email: ?

Клиентский разработчик: **Сехин Алексей**

- GitLab: [@azer0](https://gitlab.informatics.ru/azer0)
- Email: ?

---

## 🙏 Благодарности

- [Django](https://www.djangoproject.com/)
- [Ollama](https://ollama.ai/)
- ?


---

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

- Создайте [Issue](https://gitlab.informatics.ru/Drey_Sych/the-final-build/-/issues)
- Email: andreyakolesnikovg@gmail.com
