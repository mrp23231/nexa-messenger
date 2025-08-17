# 🚀 Развертывание Nexa Messenger

## Обзор

Nexa Messenger - это веб-приложение, которое можно развернуть на различных платформах. В этом руководстве описаны способы развертывания для локальной разработки, production серверов и облачных платформ.

## 📋 Требования

### Системные требования

- **Python**: 3.8 или выше
- **Память**: Минимум 512MB RAM
- **Дисковое пространство**: Минимум 100MB
- **Сеть**: Доступ к интернету для установки зависимостей

### Зависимости

Все необходимые зависимости указаны в `requirements.txt`:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7
Flask-SocketIO==5.3.6
python-socketio==5.9.0
bcrypt==4.0.1
email-validator==2.0.0
cryptography==41.0.7
```

## 🏠 Локальное развертывание

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/nexa-messenger.git
cd nexa-messenger
```

### 2. Создание виртуального окружения

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корневой директории:

```bash
# .env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///nexa_messenger.db
```

### 5. Инициализация базы данных

```bash
python3 app.py
```

База данных будет создана автоматически при первом запуске.

### 6. Запуск приложения

```bash
python3 app.py
```

Приложение будет доступно по адресу: `http://localhost:8080`

## 🌐 Production развертывание

### 1. Подготовка сервера

#### Ubuntu/Debian

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv nginx -y

# Установка SSL сертификатов
sudo apt install certbot python3-certbot-nginx -y
```

#### CentOS/RHEL

```bash
# Установка Python
sudo yum install python3 python3-pip nginx -y

# Установка EPEL репозитория
sudo yum install epel-release -y
```

### 2. Настройка пользователя

```bash
# Создание пользователя для приложения
sudo useradd -m -s /bin/bash nexa
sudo passwd nexa

# Добавление в группу sudo
sudo usermod -aG sudo nexa
```

### 3. Развертывание приложения

```bash
# Переключение на пользователя nexa
sudo su - nexa

# Клонирование репозитория
git clone https://github.com/your-username/nexa-messenger.git
cd nexa-messenger

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание директории для логов
mkdir logs
```

### 4. Настройка systemd сервиса

Создайте файл `/etc/systemd/system/nexa-messenger.service`:

```ini
[Unit]
Description=Nexa Messenger
After=network.target

[Service]
Type=simple
User=nexa
WorkingDirectory=/home/nexa/nexa-messenger
Environment=PATH=/home/nexa/nexa-messenger/venv/bin
ExecStart=/home/nexa/nexa-messenger/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/nexa-messenger`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Активация конфигурации

```bash
# Создание символической ссылки
sudo ln -s /etc/nginx/sites-available/nexa-messenger /etc/nginx/sites-enabled/

# Проверка конфигурации Nginx
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx

# Запуск сервиса
sudo systemctl start nexa-messenger
sudo systemctl enable nexa-messenger
```

### 7. Настройка SSL

```bash
# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## ☁️ Облачное развертывание

### Heroku

#### 1. Создание Procfile

```bash
# Procfile
web: gunicorn --worker-class eventlet -w 1 app:app
```

#### 2. Настройка requirements.txt

Добавьте в `requirements.txt`:
```
gunicorn==20.1.0
eventlet==0.33.3
```

#### 3. Развертывание

```bash
# Установка Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Логин в Heroku
heroku login

# Создание приложения
heroku create your-nexa-app

# Настройка переменных окружения
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Развертывание
git push heroku main
```

### Docker

#### 1. Создание Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
```

#### 2. Создание docker-compose.yml

```yaml
version: '3.8'

services:
  nexa-messenger:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

#### 3. Запуск

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `FLASK_ENV` | Окружение Flask | `development` |
| `SECRET_KEY` | Секретный ключ | `nexa-messenger-secret-key-2024` |
| `DATABASE_URL` | URL базы данных | `sqlite:///nexa_messenger.db` |
| `HOST` | Хост для привязки | `0.0.0.0` |
| `PORT` | Порт для привязки | `8080` |

### Настройка базы данных

#### SQLite (по умолчанию)

```python
# app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexa_messenger.db'
```

#### PostgreSQL

```bash
# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib

# Создание базы данных
sudo -u postgres createdb nexa_messenger
sudo -u postgres createuser nexa_user

# Установка Python драйвера
pip install psycopg2-binary
```

```python
# app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nexa_user:password@localhost/nexa_messenger'
```

#### MySQL

```bash
# Установка MySQL
sudo apt install mysql-server

# Создание базы данных
mysql -u root -p
CREATE DATABASE nexa_messenger;
CREATE USER 'nexa_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON nexa_messenger.* TO 'nexa_user'@'localhost';
FLUSH PRIVILEGES;
```

```python
# app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://nexa_user:password@localhost/nexa_messenger'
```

## 📊 Мониторинг и логирование

### Настройка логирования

```python
# app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/nexa.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Nexa Messenger startup')
```

### Мониторинг производительности

```bash
# Установка инструментов мониторинга
pip install flask-monitoring

# Настройка мониторинга
from flask_monitoring import Monitor
monitor = Monitor(app)
```

## 🔒 Безопасность production

### 1. Настройка файрвола

```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# iptables (CentOS)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### 2. Настройка SSL/TLS

```bash
# Получение бесплатного SSL сертификата
sudo certbot --nginx -d your-domain.com

# Принудительное перенаправление на HTTPS
# Добавьте в Nginx конфигурацию:
# return 301 https://$server_name$request_uri;
```

### 3. Настройка заголовков безопасности

```python
# app.py
from flask_talisman import Talisman

Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self' https:",
    }
)
```

## 🚀 Масштабирование

### Горизонтальное масштабирование

```yaml
# docker-compose.yml
version: '3.8'

services:
  nexa-messenger:
    build: .
    ports:
      - "8080"
    environment:
      - FLASK_ENV=production
    deploy:
      replicas: 3
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - nexa-messenger
```

### Load Balancer

```nginx
# nginx.conf
upstream nexa_backend {
    server nexa-messenger:8080;
    server nexa-messenger:8080;
    server nexa-messenger:8080;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://nexa_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📝 Чек-лист развертывания

- [ ] Установлены все зависимости
- [ ] Настроены переменные окружения
- [ ] Создана и настроена база данных
- [ ] Настроен веб-сервер (Nginx/Apache)
- [ ] Настроен SSL сертификат
- [ ] Настроен файрвол
- [ ] Настроено логирование
- [ ] Настроен мониторинг
- [ ] Протестирована функциональность
- [ ] Настроено резервное копирование
- [ ] Документированы настройки

## 🆘 Устранение неполадок

### Частые проблемы

1. **Порт занят**
   ```bash
   sudo lsof -i :8080
   sudo kill -9 <PID>
   ```

2. **Проблемы с правами доступа**
   ```bash
   sudo chown -R nexa:nexa /home/nexa/nexa-messenger
   sudo chmod -R 755 /home/nexa/nexa-messenger
   ```

3. **Проблемы с базой данных**
   ```bash
   # Проверка подключения
   python3 -c "from app import db; print(db.engine.execute('SELECT 1').scalar())"
   ```

4. **Проблемы с WebSocket**
   ```bash
   # Проверка логов
   sudo journalctl -u nexa-messenger -f
   ```

---

**🚀 Успешного развертывания!**

Если у вас возникли вопросы, обратитесь к документации или создайте Issue в репозитории.
