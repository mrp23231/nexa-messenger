# 🚀 Развертывание Nexa Messenger в интернете

Это руководство поможет вам развернуть Nexa Messenger так, чтобы все пользователи могли заходить со своих устройств и общаться в реальном времени.

## 📋 Требования

- Python 3.9+
- Виртуальное окружение
- База данных (SQLite для начала, PostgreSQL для продакшена)
- Веб-сервер (Nginx + Gunicorn для продакшена)
- SSL сертификат (Let's Encrypt)

## 🏗️ Варианты развертывания

### 1. Локальный хостинг (для тестирования)

#### Запуск на локальном сервере:
```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем переменные окружения
export FLASK_ENV=production
export HOST=0.0.0.0
export PORT=8080

# Запускаем приложение
python run_production.py
```

#### Доступ из интернета:
- Настройте проброс портов на роутере (порт 8080)
- Используйте ваш внешний IP адрес
- **Внимание**: Это небезопасно для продакшена!

### 2. Облачный хостинг (рекомендуется)

#### Heroku:
```bash
# Установите Heroku CLI
# Создайте приложение
heroku create your-messenger-app

# Настройте базу данных
heroku addons:create heroku-postgresql:hobby-dev

# Настройте переменные окружения
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here

# Разверните
git push heroku main
```

#### DigitalOcean App Platform:
- Создайте новое приложение
- Подключите GitHub репозиторий
- Выберите Python runtime
- Настройте переменные окружения

#### VPS (Ubuntu/Debian):
```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python и зависимости
sudo apt install python3 python3-pip python3-venv nginx

# Клонируйте проект
git clone https://github.com/your-username/nexa-messenger.git
cd nexa-messenger

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Настройте базу данных
python init_new_features.py
python setup_admin.py

# Настройте Gunicorn
pip install gunicorn

# Создайте systemd сервис
sudo nano /etc/systemd/system/nexa-messenger.service
```

## 🔧 Настройка базы данных

### SQLite (для разработки):
```python
# В config.py
SQLALCHEMY_DATABASE_URI = 'sqlite:///nexa_messenger.db'
```

### PostgreSQL (для продакшена):
```bash
# Установите PostgreSQL
sudo apt install postgresql postgresql-contrib

# Создайте базу данных
sudo -u postgres psql
CREATE DATABASE nexa_messenger;
CREATE USER nexa_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nexa_messenger TO nexa_user;
\q

# Установите Python драйвер
pip install psycopg2-binary
```

```python
# В config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://nexa_user:your_password@localhost/nexa_messenger'
```

## 🌐 Настройка веб-сервера

### Nginx конфигурация:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/your/project/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Gunicorn конфигурация:
```bash
# Создайте gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

## 🔐 Настройка безопасности

### SSL сертификат (Let's Encrypt):
```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx

# Получите сертификат
sudo certbot --nginx -d your-domain.com

# Автообновление
sudo crontab -e
# Добавьте строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

### Переменные окружения:
```bash
# Создайте .env файл
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/db
SESSION_COOKIE_SECURE=true
```

## 📱 Настройка для мобильных устройств

### PWA (Progressive Web App):
```html
<!-- В base.html -->
<link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
<meta name="theme-color" content="#00d4ff">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
```

### Создайте manifest.json:
```json
{
  "name": "Nexa Messenger",
  "short_name": "Nexa",
  "description": "Современный мессенджер для общения",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#00d4ff",
  "icons": [
    {
      "src": "/static/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

## 🚀 Запуск в продакшене

### 1. Инициализация базы данных:
```bash
python init_new_features.py
python setup_admin.py
```

### 2. Запуск с Gunicorn:
```bash
gunicorn -c gunicorn.conf.py "app:app"
```

### 3. Запуск через systemd:
```bash
sudo systemctl start nexa-messenger
sudo systemctl enable nexa-messenger
```

### 4. Проверка статуса:
```bash
sudo systemctl status nexa-messenger
sudo journalctl -u nexa-messenger -f
```

## 📊 Мониторинг и логи

### Логирование:
```python
# В app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/nexa_messenger.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Nexa Messenger startup')
```

### Мониторинг через админ-панель:
- Откройте `/admin` в браузере
- Просматривайте статистику пользователей
- Мониторьте активность каналов
- Отслеживайте системные метрики

## 🔄 Обновления

### Автоматическое обновление:
```bash
# Создайте скрипт обновления
#!/bin/bash
cd /path/to/your/project
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nexa-messenger
```

### Резервное копирование:
```bash
# Создайте скрипт бэкапа
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/nexa_messenger"
mkdir -p $BACKUP_DIR

# Бэкап базы данных
pg_dump nexa_messenger > $BACKUP_DIR/db_$DATE.sql

# Бэкап файлов
tar -czf $BACKUP_DIR/files_$DATE.tar.gz static/uploads/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## 🆘 Устранение неполадок

### Проблемы с WebSocket:
- Проверьте настройки Nginx для `/socket.io/`
- Убедитесь, что Gunicorn поддерживает WebSocket
- Проверьте логи на ошибки

### Проблемы с базой данных:
- Проверьте права доступа пользователя БД
- Убедитесь, что PostgreSQL запущен
- Проверьте логи PostgreSQL

### Проблемы с производительностью:
- Увеличьте количество workers в Gunicorn
- Настройте кэширование в Nginx
- Оптимизируйте запросы к базе данных

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи приложения и веб-сервера
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки файрвола и роутера
4. Создайте issue в GitHub репозитории

---

**🎉 Поздравляем! Ваш мессенджер теперь доступен в интернете!**

Пользователи смогут:
- Регистрироваться и входить в систему
- Общаться в реальном времени
- Создавать и присоединяться к каналам
- Использовать все функции на любых устройствах
