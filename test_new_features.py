#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новых функций Nexa Messenger
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

def test_connection_info():
    """Тестирует API для получения информации о подключении"""
    print("🔍 Тестирование API информации о подключении...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/connection_info")
        if response.status_code == 401:
            print("✅ API работает (требует авторизации)")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def test_backup_api():
    """Тестирует API для создания резервной копии"""
    print("🔍 Тестирование API резервного копирования...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/backup")
        if response.status_code == 401:
            print("✅ API работает (требует авторизации)")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def test_tips_api():
    """Тестирует API для получения подсказок"""
    print("🔍 Тестирование API подсказок...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tips")
        if response.status_code == 200:
            tips = response.json()
            print("✅ API подсказок работает")
            print(f"   - Подсказок по чату: {len(tips.get('chat', []))}")
            print(f"   - Подсказок по безопасности: {len(tips.get('security', []))}")
            print(f"   - Подсказок по функциям: {len(tips.get('features', []))}")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def test_pages():
    """Тестирует доступность основных страниц"""
    print("🔍 Тестирование доступности страниц...")
    
    pages = [
        ("/", "Главная страница"),
        ("/login", "Страница входа"),
        ("/register", "Страница регистрации"),
        ("/help", "Страница помощи")
    ]
    
    for page, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {name}: доступна")
            else:
                print(f"❌ {name}: статус {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: сервер не запущен")
            return False
        except Exception as e:
            print(f"❌ {name}: ошибка {e}")
    
    return True

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование новых функций Nexa Messenger")
    print("=" * 50)
    
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
    
    # Тестируем API
    test_connection_info()
    print()
    
    test_backup_api()
    print()
    
    test_tips_api()
    print()
    
    # Тестируем страницы
    test_pages()
    print()
    
    print("🎉 Тестирование завершено!")
    print("\n📱 Для полного тестирования:")
    print("1. Откройте http://localhost:8080 в браузере")
    print("2. Зарегистрируйте нового пользователя")
    print("3. Проверьте редактирование профиля (display_name)")
    print("4. Проверьте настройки и информацию о подключении")
    print("5. Проверьте создание резервной копии")

if __name__ == "__main__":
    main()
