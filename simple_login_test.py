#!/usr/bin/env python3
"""
Простой тест входа в систему
"""

import requests

BASE_URL = "http://localhost:8080"

def test_login():
    """Тестирует простой вход в систему"""
    print("🔑 Простой тест входа в систему")
    print("=" * 50)
    
    # Тестируем вход с admin
    print("1️⃣ Тест входа с пользователем 'admin'...")
    session = requests.Session()
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # Получаем страницу входа
        response = session.get(f"{BASE_URL}/login")
        print(f"   Страница входа: {response.status_code}")
        
        # Пытаемся войти
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"   POST /login: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Редирект после входа (успех)")
            redirect_url = response.headers.get('Location', '')
            print(f"   Редирект на: {redirect_url}")
        else:
            print(f"   ❌ Неожиданный статус: {response.status_code}")
            print(f"   Содержимое ответа: {response.text[:200]}...")
        
        # Проверяем, можем ли мы получить доступ к защищенным страницам
        print("\n2️⃣ Проверка доступа к защищенным страницам...")
        
        # Профиль
        response = session.get(f"{BASE_URL}/profile")
        print(f"   Профиль: {response.status_code}")
        
        # Настройки
        response = session.get(f"{BASE_URL}/settings")
        print(f"   Настройки: {response.status_code}")
        
        # API информация о подключении
        response = session.get(f"{BASE_URL}/api/connection_info")
        print(f"   API connection_info: {response.status_code}")
        
        if response.status_code == 200:
            info = response.json()
            print(f"      Тип устройства: {info.get('device_type')}")
            print(f"      Браузер: {info.get('browser')}")
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n3️⃣ Тест входа с пользователем 'testuser123'...")
    session2 = requests.Session()
    
    login_data2 = {
        'username': 'testuser123',
        'password': 'testpass123'
    }
    
    try:
        response = session2.post(f"{BASE_URL}/login", data=login_data2, allow_redirects=False)
        print(f"   POST /login: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Редирект после входа (успех)")
        else:
            print(f"   ❌ Неожиданный статус: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_login()
