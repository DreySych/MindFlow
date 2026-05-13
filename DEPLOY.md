## Доставка проекта на VPS через PowerShell

```powershell
scp -r "D:\Desktop\PYCHARM\the-final-build\*" site2@188.127.251.228:/home/site2/app/
```

## Первичный запуск проекта на сервере

```bash
ssh site2@188.127.251.228
cd /home/site2/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
chmod -R o+rX staticfiles media 2>/dev/null
sudo systemctl enable --now site2.service
sudo systemctl status site2.service --no-pager
```

## Обновление проекта

```bash
cd /home/site2/app
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
chmod -R o+rX staticfiles media 2>/dev/null
sudo systemctl restart site2.service
```

## Проверка работы сервиса

```bash
sudo systemctl status site2.service --no-pager
sudo journalctl -u site2.service --no-pager
```