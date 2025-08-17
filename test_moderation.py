#!/usr/bin/env python3
"""
Скрипт для тестирования системы модерации
"""

import requests
import json
import time

# URL сервера
BASE_URL = "http://localhost:8080"

def test_moderation_system():
    """Тестирует основные функции модерации"""
    
    print("🧪 Тестирование системы модерации")
    print("=" * 50)
    
    # 1. Создаем тестового пользователя
    print("\n1️⃣ Создание тестового пользователя...")
    
    test_user_data = {
        'username': 'test_moderator',
        'display_name': 'Тест Модератор',
        'email': 'moderator@test.com',
        'password': 'test123456'
    }
    
    response = requests.post(f"{BASE_URL}/register", data=test_user_data)
    if response.status_code == 200:
        print("✅ Тестовый пользователь создан")
    else:
        print("❌ Ошибка создания пользователя")
        return
    
    # 2. Входим в систему
    print("\n2️⃣ Вход в систему...")
    
    login_data = {
        'username': 'test_moderator',
        'password': 'test123456'
    }
    
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200:
        print("✅ Вход выполнен успешно")
    else:
        print("❌ Ошибка входа")
        return
    
    # 3. Создаем жалобу
    print("\n3️⃣ Создание жалобы...")
    
    report_data = {
        'reported_user_id': 1,  # Предполагаем, что есть пользователь с ID 1
        'reason': 'Спам',
        'description': 'Пользователь отправляет рекламные сообщения',
        'evidence': 'Сообщения в чате #1, #5, #12'
    }
    
    response = session.post(
        f"{BASE_URL}/api/report",
        json=report_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("✅ Жалоба создана успешно")
        else:
            print(f"❌ Ошибка создания жалобы: {result.get('message')}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
    
    # 4. Проверяем профиль пользователя
    print("\n4️⃣ Проверка профиля пользователя...")
    
    response = session.get(f"{BASE_URL}/api/user/1/profile")
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Профиль получен: {profile['username']} (ID: {profile['id']})")
        print(f"   Статус: {profile['status']}")
        print(f"   Онлайн: {'Да' if profile['is_online'] else 'Нет'}")
    else:
        print(f"❌ Ошибка получения профиля: {response.status_code}")
    
    # 5. Проверяем статистику админ-панели
    print("\n5️⃣ Проверка статистики админ-панели...")
    
    response = session.get(f"{BASE_URL}/admin/statistics")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Статистика получена:")
        print(f"   Всего пользователей: {stats.get('total_users', 'N/A')}")
        print(f"   Онлайн пользователей: {stats.get('online_users', 'N/A')}")
        print(f"   Всего сообщений: {stats.get('total_messages', 'N/A')}")
        print(f"   Заблокированных: {stats.get('banned_users', 'N/A')}")
        print(f"   Жалоб в ожидании: {stats.get('pending_reports', 'N/A')}")
    else:
        print(f"❌ Ошибка получения статистики: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 Тестирование завершено!")
    print("\n💡 Для полного тестирования модерации:")
    print("   1. Создайте администратора через create_admin_auto.py")
    print("   2. Войдите как администратор")
    print("   3. Перейдите в админ-панель")
    print("   4. Протестируйте функции блокировки и управления")

if __name__ == '__main__':
    try:
        test_moderation_system()
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("   Убедитесь, что сервер запущен на http://localhost:8080")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
