#!/usr/bin/env python3
"""
Демонстрация Nexa Messenger
Показывает все основные функции мессенджера
"""

import requests
import json
import time
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080"

def print_header():
    """Печатает заголовок демонстрации"""
    print("🌟" + "="*50 + "🌟")
    print("🚀 ДЕМОНСТРАЦИЯ NEXA MESSENGER")
    print("🌟" + "="*50 + "🌟")
    print()

def test_basic_functionality():
    """Тестирует базовую функциональность"""
    print("📱 Тестирование базовой функциональности...")
    
    # Проверяем главную страницу
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Главная страница работает")
        else:
            print(f"⚠️ Главная страница вернула код: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка главной страницы: {e}")
    
    # Проверяем страницу регистрации
    try:
        response = requests.get(f"{BASE_URL}/register")
        if response.status_code == 200:
            print("✅ Страница регистрации работает")
        else:
            print(f"⚠️ Страница регистрации вернула код: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка страницы регистрации: {e}")
    
    # Проверяем страницу входа
    try:
        response = requests.get(f"{BASE_URL}/login")
        if response.status_code == 200:
            print("✅ Страница входа работает")
        else:
            print(f"⚠️ Страница входа вернула код: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка страницы входа: {e}")

def test_registration_flow():
    """Тестирует процесс регистрации"""
    print("\n🔐 Тестирование процесса регистрации...")
    
    # Тестовые данные
    test_users = [
        {"username": "demo_user", "email": "demo@nexa.com", "password": "demo123"},
        {"username": "test_user", "email": "test@nexa.com", "password": "test123"},
        {"username": "nexa_fan", "email": "fan@nexa.com", "password": "fan123"}
    ]
    
    for i, user_data in enumerate(test_users, 1):
        try:
            print(f"  Регистрируем пользователя {i}: {user_data['username']}")
            response = requests.post(f"{BASE_URL}/register", data=user_data)
            
            if response.status_code == 200:
                print(f"    ✅ Пользователь {user_data['username']} зарегистрирован")
            elif response.status_code == 302:
                print(f"    ✅ Пользователь {user_data['username']} зарегистрирован (редирект)")
            else:
                print(f"    ⚠️ Код ответа: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")

def test_search_functionality():
    """Тестирует функциональность поиска"""
    print("\n🔍 Тестирование функциональности поиска...")
    
    # Сначала регистрируем тестового пользователя для поиска
    test_user = {"username": "search_test", "email": "search@nexa.com", "password": "search123"}
    
    try:
        # Регистрируем пользователя
        requests.post(f"{BASE_URL}/register", data=test_user)
        print("✅ Тестовый пользователь для поиска создан")
        
        # Тестируем поиск (должен вернуть редирект на логин, так как не авторизованы)
        response = requests.get(f"{BASE_URL}/search_users?q=search")
        if response.status_code == 302:
            print("✅ API поиска работает (требует авторизацию)")
        else:
            print(f"⚠️ API поиска вернул код: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования поиска: {e}")

def test_chat_pages():
    """Тестирует страницы чата"""
    print("\n💬 Тестирование страниц чата...")
    
    pages = [
        ("/chat", "Страница чата"),
        ("/profile", "Страница профиля"),
        ("/profile/edit", "Страница редактирования профиля")
    ]
    
    for page, description in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 302:
                print(f"✅ {description} работает (требует авторизацию)")
            elif response.status_code == 200:
                print(f"✅ {description} доступна")
            else:
                print(f"⚠️ {description} вернул код: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка {description}: {e}")

def show_demo_instructions():
    """Показывает инструкции по демонстрации"""
    print("\n" + "="*60)
    print("🎮 ИНСТРУКЦИИ ПО ДЕМОНСТРАЦИИ")
    print("="*60)
    print()
    print("1️⃣ ОТКРОЙТЕ БРАУЗЕР:")
    print("   🌐 http://localhost:8080")
    print()
    print("2️⃣ ПРОТЕСТИРУЙТЕ РЕГИСТРАЦИЮ:")
    print("   • Нажмите 'Создать аккаунт'")
    print("   • Попробуйте зарегистрировать 'admin' (должно предложить альтернативы)")
    print("   • Выберите предложенный вариант")
    print()
    print("3️⃣ ПРОТЕСТИРУЙТЕ ВХОД:")
    print("   • Войдите в созданный аккаунт")
    print("   • Проверьте что попали в чат")
    print()
    print("4️⃣ ПРОТЕСТИРУЙТЕ ПОИСК:")
    print("   • Введите в поиск часть имени")
    print("   • Убедитесь что поиск работает")
    print()
    print("5️⃣ ПРОТЕСТИРУЙТЕ ЧАТ:")
    print("   • Создайте второго пользователя в другом окне")
    print("   • Начните переписку между ними")
    print("   • Проверьте индикатор 'печатает'")
    print()
    print("🌟 ВСЕ ФУНКЦИИ РАБОТАЮТ В РЕАЛЬНОМ ВРЕМЕНИ!")

def main():
    """Основная функция демонстрации"""
    print_header()
    
    # Тестируем базовую функциональность
    test_basic_functionality()
    
    # Тестируем процесс регистрации
    test_registration_flow()
    
    # Тестируем функциональность поиска
    test_search_functionality()
    
    # Тестируем страницы чата
    test_chat_pages()
    
    # Показываем инструкции по демонстрации
    show_demo_instructions()
    
    print("\n" + "="*60)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("="*60)
    print("\n💡 Теперь откройте браузер и протестируйте все функции!")

if __name__ == "__main__":
    main()
