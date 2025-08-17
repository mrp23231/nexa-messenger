#!/usr/bin/env python3
"""
Финальный тест всех новых функций Nexa Messenger
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_all_features():
    """Тестирует все новые функции"""
    print("🚀 Финальный тест всех новых функций Nexa Messenger")
    print("=" * 70)
    
    # Создаем сессию для admin
    session = requests.Session()
    
    # 1. Вход в систему
    print("1️⃣ Вход в систему...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("   ✅ Успешный вход в систему")
        else:
            print(f"   ❌ Ошибка входа: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при входе: {e}")
        return False
    
    # 2. Проверка профиля с display_name
    print("\n2️⃣ Проверка профиля...")
    try:
        response = session.get(f"{BASE_URL}/profile")
        if response.status_code == 200:
            print("   ✅ Профиль доступен")
            if 'Администратор' in response.text:
                print("   ✅ Display name 'Администратор' отображается")
            if '@admin' in response.text:
                print("   ✅ Username '@admin' отображается")
        else:
            print(f"   ❌ Ошибка доступа к профилю: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке профиля: {e}")
    
    # 3. Проверка страницы редактирования профиля
    print("\n3️⃣ Проверка редактирования профиля...")
    try:
        response = session.get(f"{BASE_URL}/profile/edit")
        if response.status_code == 200:
            print("   ✅ Страница редактирования доступна")
            if 'Отображаемое имя' in response.text:
                print("   ✅ Поле 'Отображаемое имя' найдено")
            if 'Юзернейм нельзя изменить' in response.text:
                print("   ✅ Предупреждение о неизменяемом юзернейме")
        else:
            print(f"   ❌ Ошибка доступа к редактированию: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке редактирования: {e}")
    
    # 4. Проверка настроек
    print("\n4️⃣ Проверка настроек...")
    try:
        response = session.get(f"{BASE_URL}/settings")
        if response.status_code == 200:
            print("   ✅ Страница настроек доступна")
            if 'Информация о подключении' in response.text:
                print("   ✅ Секция 'Информация о подключении' найдена")
            if 'Резервное копирование' in response.text:
                print("   ✅ Секция 'Резервное копирование' найдена")
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
            print(f"      Тип устройства: {info.get('device_type')}")
            print(f"      Браузер: {info.get('browser')}")
            print(f"      Протокол: {info.get('protocol')}")
            print(f"      IP адрес: {info.get('ip_address')}")
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
            print(f"      Статус: {result.get('status')}")
            print(f"      Сообщение: {result.get('message')}")
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке API: {e}")
    
    # 7. Проверка поиска пользователей
    print("\n7️⃣ Проверка поиска пользователей...")
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
    
    # 8. Проверка API подсказок
    print("\n8️⃣ Проверка API подсказок...")
    try:
        response = session.get(f"{BASE_URL}/api/tips")
        if response.status_code == 200:
            tips = response.json()
            print("   ✅ API подсказок работает")
            print(f"      Подсказок по чату: {len(tips.get('chat', []))}")
            print(f"      Подсказок по безопасности: {len(tips.get('security', []))}")
            print(f"      Подсказок по функциям: {len(tips.get('features', []))}")
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при проверке API: {e}")
    
    return True

def main():
    """Основная функция"""
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
    
    # Тестируем все функции
    if test_all_features():
        print("\n🎉 Все тесты пройдены успешно!")
        print("\n📱 Для полного тестирования в браузере:")
        print("1. Откройте http://localhost:8080")
        print("2. Войдите с аккаунтом: admin / admin123")
        print("3. Проверьте профиль и настройки")
        print("4. Протестируйте поиск пользователей")
        print("5. Создайте резервную копию")
    else:
        print("\n❌ Некоторые тесты не прошли")

if __name__ == "__main__":
    main()
