# 🚀 Пошаговая настройка Nexa Messenger в Render

## 📋 Шаг 1: Создание веб-сервиса

1. **В Render Dashboard:**
   - Нажмите **"New +"** → **"Web Service"**
   - Подключите GitHub репозиторий: `mrp23231/nexa-messenger`
   - Нажмите **"Connect"**

## ⚙️ Шаг 2: Настройка сервиса

### **Основные настройки:**
- **Name:** `nexa-messenger`
- **Environment:** `Python 3`
- **Region:** выберите ближайший к вам
- **Branch:** `main`
- **Root Directory:** оставьте пустым

### **Build & Deploy:**
- **Build Command:** `pip install -r requirements.minimal.txt` ⭐ **ВАЖНО!**
- **Start Command:** `python app.py` ⭐ **ВАЖНО!**

## 🔧 Шаг 3: Переменные окружения

Добавьте следующие переменные:

| Key | Value | Описание |
|-----|-------|----------|
| `FLASK_ENV` | `production` | Режим продакшена |
| `FLASK_DEBUG` | `0` | Отключить debug |
| `SECRET_KEY` | `любая-случайная-строка` | Секретный ключ |
| `DATABASE_URL` | `sqlite:///nexa_messenger.db` | SQLite база данных |

## 🎯 Шаг 4: Создание базы данных (опционально)

Если хотите PostgreSQL:

1. **Создайте новую базу данных:**
   - **"New +"** → **"PostgreSQL"**
   - Выберите **Free** план
   - Назовите: `nexa-messenger-db`

2. **Обновите DATABASE_URL:**
   - Скопируйте **Internal Database URL**
   - Замените значение `DATABASE_URL` в переменных окружения

## 🚀 Шаг 5: Запуск

1. **Нажмите "Create Web Service"**
2. **Дождитесь завершения сборки** (Build successful 🎉)
3. **Сервис автоматически запустится**

## 🔍 Шаг 6: Проверка

После успешного запуска:
- Ваш мессенджер будет доступен по URL: `https://nexa-messenger.onrender.com`
- Все функции будут работать: регистрация, чат, модерация, рейтинги

## 🆘 Если что-то не работает:

### **Проблема с Gunicorn:**
Измените Start Command на: `python app.py`

### **Проблема с базой данных:**
Убедитесь что `DATABASE_URL` указан правильно

### **Проблема с портом:**
Render автоматически предоставляет переменную `$PORT`

## 📞 Поддержка

Если возникнут проблемы:
1. Проверьте логи в Render Dashboard
2. Убедитесь что все переменные окружения настроены
3. Проверьте что Start Command: `python app.py`
