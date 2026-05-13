# CONTRIBUTING.md

Спасибо, что хотите помочь MindFlow! Ниже — минимальные правила для быстрого старта

---

## 🐛 Как сообщить об ошибке

1. Проверьте существующие [Issues](https://gitlab.informatics.ru/Drey_Sych/MindFlow/-/issues).
2. Если нет похожего — создайте новый Issue с:
   - Понятным заголовком
   - Шагами для воспроизведения
   - Ожидаемым и фактическим результатом

---

## 🔀 Как предложить изменение (Merge Request)

1. Создайте ветку от `main` (учтите правила оформления веток ниже)
2. Сделайте небольшие и атомарные изменения
3. Добавьте тесты и/или обновите документацию, если меняете поведение
4. Перед Merge Request:
   - Обновите `main`: `git pull origin main`
   - Прогоните тесты: `python manage.py test`
   - Проверьте покрытие: `coverage run --source='.' manage.py test && coverage report`
5. Откройте Merge Request с описанием и ссылкой на Issue (если есть)

---

## 💻 Локально

```bash
# Клонируйте репозиторий
git clone https://gitlab.informatics.ru/Drey_Sych/MindFlow.git
cd MindFlow

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Примените миграции
python manage.py migrate

# Запустите тесты
python manage.py test

# Проверьте покрытие тестами
coverage run --source='.' manage.py test
coverage report
```

---

## 📝 Правила оформления коммитов

Используйте следующие префиксы для сообщений коммитов (на английском):

### `Add` — добавление нового функционала
Используйте, когда добавляете новый код, файлы или компоненты

**Примеры:**
- `Add main app`
- `Add index page template`
- `Add profile view function`

### `Fix` — исправление ошибок
Используйте для багфиксов и исправлений некорректного поведения

**Примеры:**
- `Fix models in main`
- `Fix comments page template`
- `Fix password_restore view function`

### `Update` — обновление/изменение существующего
Используйте для изменения или улучшения существующего функционала

**Примеры:**
- `Update README`
- `Update urls list`
- `Update index view function`

### `Remove` — удаление кода/функционала
Используйте, когда удаляете файлы, функции или компоненты

**Примеры:**
- `Remove login button from profile page`
- `Remove birth date field from main/models.py`

### `Refactor` — рефакторинг кода
Используйте для улучшения читаемости и структуры без изменения функциональности

**Примеры:**
- `Refactor complaints page template`
- `Refactor user authentication logic`

---

## 🌿 Правила оформления веток

### Формат

<тип>/<краткое-описание>

### Требования
- ✅ **Язык**: только английский
- ✅ **Разделитель**: дефис `-` (kebab-case)
- ✅ **Регистр**: только строчные буквы
- ✅ **Длина**: 2–5 слов, достаточно для понимания цели
- ✅ **Префикс**: `feature/`, `fix/` или другие (со слешем)

### Типы веток

| Префикс    | Назначение                           | Пример                        |
|------------|--------------------------------------|-------------------------------|
| `feature/` | Новая функциональность               | `feature/ai-search-cache`     |
| `fix/`     | Исправление бага                     | `fix/login-redirect-error`    |
| `refactor/`| Рефакторинг без изменения логики     | `refactor/user-model-cleanup` |
| `docs/`    | Обновление документации              | `docs/update-readme`          |
| `test/`    | Добавление или исправление тестов    | `test/add-api-coverage`       |

### Примеры

- feature/add-notifications-api
- fix/profile-image-upload
- refactor/question-model
- docs/contributing-guide
- test/coverage-improvement

---

## ✅ Требования к коду

- Следуйте **PEP 8**
- Добавляйте **docstrings** для публичных функций/классов
- Используйте понятные имена переменных
- Все тесты должны проходить: `python manage.py test`
- **Покрытие тестами** должно быть ≥ 70% (проверяйте через `coverage report`)
- Не коммитьте секреты (используйте `.env`)

---

## Контакты
Если не уверены — создайте Issue с пометкой `question` или напишите тимлиду: andreyakolesnikovg@gmail.com

Спасибо за вклад! ❤️

---