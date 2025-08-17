#!/usr/bin/env python3
"""
Тестирование входа с существующим пользователем
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_existing_user():
    """Тестирует вход с существующим пользователем"""
    print("🔑 Тестирование входа с существующим пользователем")
    print("=" * 60)
    
    session = requests.Session()
    
    # Вход с существующим пользователем
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 302:  # Редирект после успешного входа
            print("✅ Успешный вход в систему")
        else:
            print(f"❌ Ошибка входа: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при входе: {e}")
        return False
    
    # Проверка профиля
    print("\n👤 Проверка профиля...")
    try:
        response = session.get(f"{BASE_URL}/profile")
        if response.status_code == 200:
            print("   ✅ Профиль доступен")
            # Проверяем наличие display_name
            if 'Администратор' in response.text:
                print("   ✅ Display name отображается корректно")
            if 'admin' in response.text:
                print("   ✅ Username отображается корректно")
        else:
            print(f"   ❌ Ошибка доступа к профилю: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке профиля: {e}")
    
    # Проверка настроек
    print("\n⚙️  Проверка настроек...")
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
    
    # Проверка API информации о подключении
    print("\n🌐 Проверка API информации о подключении...")
    try:
        response = session.get(f"{BASE_URL}/api/connection_info")
        if response.status_code == 200:
            info = response.json()
            print("   ✅ API информации о подключении работает")
            print(f"      Тип устройства: {info.get('device_type', 'Неизвестно')}")
            print(f"      Браузер: {info.get('browser', 'Неизвестно')}")
            print(f"      Протокол: {info.get('protocol', 'Неизвестно')}")
            print(f"      IP адрес: {info.get('ip_address', 'Неизвестно')}")
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке API: {e}")
    
    # Проверка API резервного копирования
    print("\n💾 Проверка API резервного копирования...")
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
    
    # Проверка поиска пользователей
    print("\n🔍 Проверка поиска пользователей...")
    try:
        response = session.get(f"{BASE_URL}/search_users?q=admin")
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
    
    return True

def main():
    """Основная функция"""
    print("🚀 Тестирование существующего пользователя")
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
    
    # Тестируем существующего пользователя
    test_existing_user()
    
    print("\n🎉 Тестирование завершено!")
    print("\n📱 Для полного тестирования:")
    print("1. Откройте http://localhost:8080 в браузере")
    print("2. Войдите с аккаунтом: admin / admin123")
    print("3. Проверьте профиль и настройки")
    print("4. Протестируйте поиск пользователей")

if __name__ == "__main__":
    main()
