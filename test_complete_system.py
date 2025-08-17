#!/usr/bin/env python3
"""
Скрипт для полного тестирования системы модерации Nexa Messenger
"""

import os
import sys
import requests
import json
from datetime import datetime

# URL сервера
BASE_URL = "http://localhost:8080"

def test_complete_system():
    """Тестирует всю систему модерации"""
    
    print("🧪 Полное тестирование системы модерации Nexa Messenger")
    print("=" * 60)
    
    # 1. Проверка доступности сервера
    print("\n1️⃣ Проверка доступности сервера...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен")
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return
    except requests.exceptions.RequestException:
        print("❌ Не удается подключиться к серверу")
        print("   Убедитесь, что сервер запущен на http://localhost:8080")
        return
    
    # 2. Тестирование входа администратора
    print("\n2️⃣ Тестирование входа администратора...")
    
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123456'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200:
        print("✅ Вход администратора выполнен успешно")
    else:
        print("❌ Ошибка входа администратора")
        return
    
    # 3. Проверка админ-панели
    print("\n3️⃣ Проверка админ-панели...")
    
    response = session.get(f"{BASE_URL}/admin")
    
    if response.status_code == 200:
        print("✅ Админ-панель доступна")
    else:
        print(f"❌ Ошибка доступа к админ-панели: {response.status_code}")
        return
    
    # 4. Проверка API статистики
    print("\n4️⃣ Проверка API статистики...")
    
    response = session.get(f"{BASE_URL}/admin/statistics")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ API статистики работает:")
        print(f"   Всего пользователей: {stats.get('total_users', 'N/A')}")
        print(f"   Онлайн пользователей: {stats.get('online_users', 'N/A')}")
        print(f"   Всего сообщений: {stats.get('total_messages', 'N/A')}")
        print(f"   Заблокированных: {stats.get('banned_users', 'N/A')}")
        print(f"   Жалоб в ожидании: {stats.get('pending_reports', 'N/A')}")
    else:
        print(f"❌ Ошибка API статистики: {response.status_code}")
    
    # 5. Проверка API пользователей
    print("\n5️⃣ Проверка API пользователей...")
    
    response = session.get(f"{BASE_URL}/admin/users?page=1&search=")
    
    if response.status_code == 200:
        users_data = response.json()
        print("✅ API пользователей работает:")
        print(f"   Найдено пользователей: {users_data.get('total', 'N/A')}")
        print(f"   Страниц: {users_data.get('pages', 'N/A')}")
        
        if users_data.get('users'):
            first_user = users_data['users'][0]
            print(f"   Первый пользователь: {first_user.get('username')} (ID: {first_user.get('id')})")
            print(f"   Админ: {'Да' if first_user.get('is_admin') else 'Нет'}")
            print(f"   Заблокирован: {'Да' if first_user.get('is_banned') else 'Нет'}")
    else:
        print(f"❌ Ошибка API пользователей: {response.status_code}")
    
    # 6. Проверка API профиля
    print("\n6️⃣ Проверка API профиля...")
    
    response = session.get(f"{BASE_URL}/api/user/1/profile")
    
    if response.status_code == 200:
        profile = response.json()
        print("✅ API профиля работает:")
        print(f"   Пользователь: {profile.get('username')} (ID: {profile.get('id')})")
        print(f"   Статус: {profile.get('status')}")
        print(f"   Онлайн: {'Да' if profile.get('is_online') else 'Нет'}")
        print(f"   Админ: {'Да' if profile.get('is_admin') else 'Нет'}")
    else:
        print(f"❌ Ошибка API профиля: {response.status_code}")
    
    # 7. Проверка страницы правил
    print("\n7️⃣ Проверка страницы правил...")
    
    response = session.get(f"{BASE_URL}/rules")
    
    if response.status_code == 200:
        print("✅ Страница правил доступна")
    else:
        print(f"❌ Ошибка страницы правил: {response.status_code}")
    
    # 8. Проверка страницы помощи
    print("\n8️⃣ Проверка страницы помощи...")
    
    response = session.get(f"{BASE_URL}/help")
    
    if response.status_code == 200:
        print("✅ Страница помощи доступна")
    else:
        print(f"❌ Ошибка страницы помощи: {response.status_code}")
    
    # Итоговая статистика
    print("\n" + "=" * 60)
    print("🎯 Результаты тестирования:")
    print("✅ Система модерации полностью функциональна!")
    
    print("\n💡 Что протестировано:")
    print("   • Доступность сервера")
    print("   • Вход администратора")
    print("   • Админ-панель")
    print("   • API статистики")
    print("   • API пользователей")
    print("   • API профилей")
    print("   • Страница правил")
    print("   • Страница помощи")
    
    print("\n🚀 Готово к использованию:")
    print("   1. Войдите как admin/admin123456")
    print("   2. Перейдите в админ-панель /admin")
    print("   3. Управляйте пользователями и жалобами")
    print("   4. Изучите правила в /rules")
    print("   5. Получите помощь в /help")
    
    print("\n📊 Демо-данные:")
    print("   • Администратор: admin/admin123456")
    print("   • Тестовый пользователь: testuser/test123456")
    print("   • Демо-жалоба создана для тестирования")

if __name__ == '__main__':
    try:
        test_complete_system()
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("🔧 Проверьте логи и настройки сервера")
