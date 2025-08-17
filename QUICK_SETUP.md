# ⚡ БЫСТРАЯ НАСТРОЙКА RENDER

## 🎯 В Render Dashboard:

### **1. New + → Web Service**
### **2. Подключите:** `mrp23231/nexa-messenger`

### **3. Настройки:**
- **Name:** `nexa-messenger`
- **Build Command:** `pip install -r requirements.minimal.txt`
- **Start Command:** `python app_simple.py`

### **4. Переменные окружения:**
```
FLASK_ENV = production
FLASK_DEBUG = 0
SECRET_KEY = nexa-messenger-secret-key-2024
DATABASE_URL = sqlite:///nexa_messenger.db
```

### **5. Create Web Service**

## ✅ Готово! Ваш мессенджер будет доступен по адресу:
`https://nexa-messenger.onrender.com`
