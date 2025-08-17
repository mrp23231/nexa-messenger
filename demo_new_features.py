#!/usr/bin/env python3
"""
Демонстрация новых функций Nexa Messenger
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def demo_registration_and_profile():
    """Демонстрирует регистрацию и работу с display_name"""
    print("🆕 Демонстрация регистрации и работы с display_name")
    print("=" * 60)
    
    # Создаем сессию для сохранения cookies
    session = requests.Session()
    
    # 1. Регистрация нового пользователя
    print("1️⃣ Регистрация нового пользователя...")
    registration_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    
    try:
        # Получаем страницу регистрации
        response = session.get(f"{BASE_URL}/register")
        if response.status_code == 200:
            print("   ✅ Страница регистрации доступна")
        else:
            print(f"   ❌ Ошибка доступа к странице регистрации: {response.status_code}")
            return False
        
        # Регистрируем пользователя
        response = session.post(f"{BASE_URL}/register", data=registration_data)
        if response.status_code == 302:  # Редирект после успешной регистрации
            print("   ✅ Пользователь успешно зарегистрирован")
        else:
            print(f"   ❌ Ошибка регистрации: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка при регистрации: {e}")
        return False
    
    # 2. Вход в систему
    print("\n2️⃣ Вход в систему...")
    login_data = {
        'username': 'testuser123',
        'password': 'testpass123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 302:  # Редирект после успешного входа
            print("   ✅ Успешный вход в систему")
        else:
            print(f"   ❌ Ошибка входа: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при входе: {e}")
        return False
    
    # 3. Проверка профиля
    print("\n3️⃣ Проверка профиля...")
    try:
        response = session.get(f"{BASE_URL}/profile")
        if response.status_code == 200:
            print("   ✅ Профиль доступен")
            # Проверяем, содержит ли профиль display_name
            if 'testuser123' in response.text:
                print("   ✅ Display name отображается корректно")
            else:
                print("   ⚠️ Display name не найден в профиле")
        else:
            print(f"   ❌ Ошибка доступа к профилю: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке профиля: {e}")
    
    # 4. Проверка настроек
    print("\n4️⃣ Проверка настроек...")
    try:
        response = session.get(f"{BASE_URL}/settings")
        if response.status_code == 200:
            print("   ✅ Страница настроек доступна")
            # Проверяем наличие новых секций
            if 'Информация о подключении' in response.text:
                print("   ✅ Секция информации о подключении найдена")
            if 'Резервное копирование' in response.text:
                print("   ✅ Секция резервного копирования найдена")
        else:
            print(f"   ❌ Ошибка доступа к настройкам: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке настроек: {e}")
    
    # 5. Проверка API информации о подключении
    print("\n5️⃣ Проверка API информации о подключении...")
    try:
        response = session.get(f"{BASE_URL}/api/connection_info")
        if response.status_code == 200:
            info = response.json()
            print("   ✅ API информации о подключении работает")
            print(f"      Тип устройства: {info.get('device_type', 'Неизвестно')}")
            print(f"      Браузер: {info.get('browser', 'Неизвестно')}")
            print(f"      Протокол: {info.get('protocol', 'Неизвестно')}")
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке API: {e}")
    
    # 6. Проверка API резервного копирования
    print("\n6️⃣ Проверка API резервного копирования...")
    try:
        response = session.post(f"{BASE_URL}/api/backup")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ API резервного копирования работает")
            print(f"      Статус: {result.get('status', 'Неизвестно')}")
            print(f"      Сообщение: {result.get('message', 'Нет сообщения')}")
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке API: {e}")
    
    return True

def demo_search_features():
    """Демонстрирует улучшенный поиск пользователей"""
    print("\n🔍 Демонстрация улучшенного поиска")
    print("=" * 60)
    
    session = requests.Session()
    
    # Входим в систему
    login_data = {
        'username': 'testuser123',
        'password': 'testpass123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 302:
            print("✅ Вход в систему для тестирования поиска")
        else:
            print("❌ Не удалось войти в систему")
            return False
    except Exception as e:
        print(f"❌ Ошибка входа: {e}")
        return False
    
    # Тестируем поиск
    print("\n🔍 Тестирование поиска пользователей...")
    try:
        response = session.get(f"{BASE_URL}/search_users?q=test")
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ Поиск работает, найдено пользователей: {len(users)}")
            if users:
                user = users[0]
                print(f"      Первый пользователь:")
                print(f"         ID: {user.get('id')}")
                print(f"         Username: {user.get('username')}")
                print(f"         Display Name: {user.get('display_name', 'Не указан')}")
                print(f"         Статус: {'В сети' if user.get('is_online') else 'Не в сети'}")
        else:
            print(f"   ❌ Ошибка поиска: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при поиске: {e}")

def main():
    """Основная функция демонстрации"""
    print("🚀 Демонстрация новых функций Nexa Messenger")
    print("=" * 70)
    
    # Проверяем, запущен ли сервер
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Сервер не отвечает корректно")
            return
    except:
        print("❌ Сервер не запущен. Запустите app.py")
        return
    
    print("✅ Сервер запущен и отвечает")
    print()
    
    # Демонстрируем основные функции
    if demo_registration_and_profile():
        demo_search_features()
    
    print("\n🎉 Демонстрация завершена!")
    print("\n📱 Для полного тестирования:")
    print("1. Откройте http://localhost:8080 в браузере")
    print("2. Войдите с аккаунтом: testuser123 / testpass123")
    print("3. Проверьте профиль и настройки")
    print("4. Протестируйте поиск пользователей")

if __name__ == "__main__":
    main()
