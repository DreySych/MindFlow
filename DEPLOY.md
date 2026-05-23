# MindFlow Deployment Guide

## Production environment

Проект развёрнут на VPS Ubuntu.

Public URL:

http://mindflow-2026.duckdns.org:8082

Backup URL:

http://188.127.251.228:8082

---

# Technology stack

- Python 3.12
- Django 5
- Django Channels
- Daphne
- nginx
- SQLite
- GitLab CI/CD
- Sphinx
- WebSocket

---

## Server information

- VPS OS: Ubuntu
- User: site2
- Project directory: /home/site2/app
- Django type: ASGI
- Web server: nginx
- ASGI server: Daphne

Ports:

- nginx: 8082
- Daphne: 8002

---

## Real-time functionality

Проект использует Django Channels и WebSocket для:

- личных сообщений
- комментариев
- уведомлений

Это позволяет обновлять данные без перезагрузки страницы.

---

## Deployment workflow

1. Push changes to GitLab
2. CI/CD pipeline validates project
3. Upload changed files to VPS
4. Restart Daphne
5. Verify server status

---

## Important

Проект использует Django Channels и WebSocket, поэтому production deployment выполняется через Daphne.

`runserver` используется только для локальной разработки.

Gunicorn для данного проекта не используется.

---

## Connect to server

```bash
ssh site2@188.127.251.228
```

---

## Activate virtual environment

```bash
cd /home/site2/app
source venv/bin/activate
```

---

## Stop old processes

```bash
pkill gunicorn
pkill -f daphne
pkill -f "manage.py runserver"
```

---

## Start Daphne

```bash
nohup env DJANGO_SETTINGS_MODULE=The_Final_Build.settings /home/site2/app/venv/bin/daphne -b 127.0.0.1 -p 8002 The_Final_Build.asgi:application > logs/server.log 2>&1 &
```

---

## Quick restart

```bash
cd /home/site2/app
source venv/bin/activate

pkill -f daphne

nohup env DJANGO_SETTINGS_MODULE=The_Final_Build.settings \
/home/site2/app/venv/bin/daphne \
-b 127.0.0.1 \
-p 8002 \
The_Final_Build.asgi:application \
> logs/server.log 2>&1 &
```

---

## Check server status

Check Daphne:

```bash
curl -I http://127.0.0.1:8002
```

Check nginx proxy:

```bash
curl -I http://127.0.0.1:8082
```

Expected result:

```bash
HTTP/1.1 200 OK
```

---

## If 502 Bad Gateway appears

Это означает:

- nginx работает
- Daphne/Django не поднялся

Check logs:

```bash
tail -n 100 logs/server.log
```

Check processes:

```bash
ps aux | grep daphne
```

```bash
ps aux | grep manage.py
```

После этого необходимо заново запустить Daphne.

---

## Static files

STATIC_ROOT:

```text
/home/site2/app/staticfiles
```

nginx отдаёт статику из:

```text
/home/site2/app/static
```

---

## Update static files

### Upload file

Example:

```bash
scp ./static_src/css/theme.css site2@188.127.251.228:/home/site2/app/static_src/css/theme.css
```

### Collect static

```bash
cd /home/site2/app
source venv/bin/activate

python manage.py collectstatic --noinput

rm -rf static
mkdir static
cp -r staticfiles/* static/

chmod -R o+rX static staticfiles media 2>/dev/null
```

Перезапуск Daphne после изменения CSS не требуется.

---

## Environment variables

`.env` хранится только на сервере:

```text
/home/site2/app/.env
```

Файл не хранится в Git-репозитории.

Example:

```env
CSRF_TRUSTED_ORIGINS=http://mindflow-2026.duckdns.org:8082,http://188.127.251.228:8082
```

---

## Allowed hosts

```python
ALLOWED_HOSTS = [
    "188.127.251.228",
    "mindflow-2026.duckdns.org",
]
```

---

## Security

- CSRF protection enabled
- Environment variables stored outside Git
- Sensitive data excluded from repository

---

## Monitoring

Для мониторинга uptime используется UptimeRobot.

Monitoring URL:

http://mindflow-2026.duckdns.org:8082

---

## CI/CD

GitLab Runner работает в user-mode.

Runner directory:

```text
~/gitlab-runner
```

Start runner:

```bash
cd ~/gitlab-runner
nohup ./gitlab-runner run > runner.log 2>&1 &
```

Check runner:

```bash
ps aux | grep gitlab-runner
```

```bash
tail -n 50 ~/gitlab-runner/runner.log
```

Если VPS перезагрузится:

- runner нужно запускать вручную
- Daphne тоже нужно запускать вручную

---

## CI optimization

Для CI используется:

```text
requirements-ci.txt
```

Это позволяет не устанавливать тяжёлые AI-зависимости в pipeline.

---

## AI fallback logic

Если `sentence-transformers` недоступен, проект продолжает работать без AI-поиска.

В этом случае:

- `get_model()` возвращает `None`
- основной функционал проекта продолжает работать

На production-сервере используется полный `requirements.txt`.

---

## Logs

Main log:

```text
logs/server.log
```

View logs:

```bash
tail -f logs/server.log
```