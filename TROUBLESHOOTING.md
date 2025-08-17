# 🆘 Устранение неполадок в Render

## ❌ Ошибка сборки (Build failed)

### **Проблема:** Ошибки компиляции gevent/eventlet
**Решение:** Используйте `requirements.minimal.txt` вместо `requirements.txt`

### **Проблема:** Несовместимость версий Python
**Решение:** Render автоматически выберет совместимую версию

## 🚀 Альтернативные команды запуска

### **Вариант 1 (рекомендуемый):**
```
python app.py
```

### **Вариант 2 (если нужен Gunicorn):**
```
gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app
```

### **Вариант 3 (простой Gunicorn):**
```
gunicorn app:app --bind 0.0.0.0:$PORT
```

## 🔧 Настройка переменных окружения

### **Обязательные:**
```
FLASK_ENV = production
FLASK_DEBUG = 0
SECRET_KEY = ваш-секретный-ключ
```

### **Опциональные:**
```
DATABASE_URL = sqlite:///nexa_messenger.db
```

## 📁 Файлы для разных сценариев

### **Для простого запуска:**
- `Procfile.minimal` → `web: python app.py`
- `requirements.minimal.txt` → минимальные зависимости

### **Для Gunicorn:**
- `Procfile.gunicorn` → `web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class sync app:app`

### **Для максимальной совместимости:**
- `Procfile.simple` → `web: python app.py`

## 🎯 Пошаговое решение проблем

### **Шаг 1:** Проверьте Build Command
```
pip install -r requirements.minimal.txt
```

### **Шаг 2:** Проверьте Start Command
```
python app.py
```

### **Шаг 3:** Проверьте переменные окружения
- `FLASK_ENV = production`
- `FLASK_DEBUG = 0`

### **Шаг 4:** Перезапустите сервис
- Render автоматически пересоберет проект

## 📞 Если ничего не помогает

1. **Используйте минимальную конфигурацию:**
   - Build: `pip install -r requirements.minimal.txt`
   - Start: `python app.py`

2. **Проверьте логи в Render Dashboard**

3. **Убедитесь что все файлы загружены в GitHub**
