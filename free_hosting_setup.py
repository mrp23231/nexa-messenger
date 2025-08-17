#!/usr/bin/env python3
"""
Настройка бесплатного хостинга для Nexa Messenger
"""

import os
import sys
import subprocess
import json

def show_free_hosting_options():
    """Показывает бесплатные варианты хостинга"""
    print("🌐 Бесплатные варианты хостинга Nexa Messenger")
    print("=" * 60)
    
    options = [
        {
            "name": "🚀 Ngrok (Самый простой)",
            "description": "Создает туннель к вашему компьютеру",
            "pros": ["Мгновенно", "Бесплатно", "Простая настройка"],
            "cons": ["URL меняется при перезапуске", "Требует запущенный компьютер"],
            "setup": "python setup_ngrok.py"
        },
        {
            "name": "☁️ Render (Облачный хостинг)",
            "description": "Бесплатный хостинг приложений",
            "pros": ["Постоянный URL", "Автозапуск", "SSL сертификат"],
            "cons": ["Ограничения бесплатного плана", "Требует GitHub"],
            "setup": "Следуйте инструкциям в DEPLOYMENT_README.md"
        },
        {
            "name": "🌊 Railway (Современный хостинг)",
            "description": "Платформа для развертывания приложений",
            "pros": ["Простая настройка", "Автоматический деплой", "SSL"],
            "cons": ["Ограниченное время работы", "Требует GitHub"],
            "setup": "Следуйте инструкциям в DEPLOYMENT_README.md"
        },
        {
            "name": "🐘 Heroku (Классический выбор)",
            "description": "Платформа для веб-приложений",
            "pros": ["Надежность", "Много документации", "Интеграции"],
            "cons": ["Убрали бесплатный план", "Требует карту"],
            "setup": "Следуйте инструкциям в DEPLOYMENT_README.md"
        }
    ]
    
    for i, option in enumerate(options, 1):
        print(f"\n{i}. {option['name']}")
        print(f"   {option['description']}")
        print(f"   ✅ Плюсы: {', '.join(option['pros'])}")
        print(f"   ❌ Минусы: {', '.join(option['cons'])}")
        print(f"   🔧 Настройка: {option['setup']}")
    
    return options

def setup_ngrok_quick():
    """Быстрая настройка Ngrok"""
    print("\n🚀 Быстрая настройка Ngrok...")
    
    # Проверяем, запущен ли сервер
    try:
        import requests
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code != 200:
            print("❌ Сервер не запущен на порту 8080")
            print("   Сначала запустите: python start_server.py")
            return False
    except:
        print("❌ Сервер не запущен на порту 8080")
        print("   Сначала запустите: python start_server.py")
        return False
    
    print("✅ Сервер запущен")
    
    # Проверяем ngrok
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok уже установлен")
        else:
            print("❌ Ngrok не установлен")
            print("   Запустите: python setup_ngrok.py")
            return False
    except FileNotFoundError:
        print("❌ Ngrok не установлен")
        print("   Запустите: python setup_ngrok.py")
        return False
    
    # Запускаем туннель
    print("🚀 Запуск туннеля...")
    try:
        process = subprocess.Popen(['ngrok', 'http', '8080'], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        
        import time
        time.sleep(3)
        
        # Получаем URL
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            if tunnels:
                public_url = tunnels[0]['public_url']
                print(f"✅ Туннель запущен!")
                print(f"🌐 Публичный URL: {public_url}")
                print(f"📱 Теперь все могут зайти по адресу: {public_url}")
                
                # Сохраняем URL
                with open('public_url.txt', 'w') as f:
                    f.write(public_url)
                
                return True
        
        print("❌ Не удалось запустить туннель")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def create_deployment_files():
    """Создает файлы для развертывания"""
    print("\n📁 Создание файлов для развертывания...")
    
    # Procfile для Heroku
    with open('Procfile', 'w') as f:
        f.write('web: gunicorn app:app')
    
    # runtime.txt для Python версии
    with open('runtime.txt', 'w') as f:
        f.write('python-3.9.18')
    
    # requirements.txt уже есть
    
    print("✅ Файлы для развертывания созданы:")
    print("   • Procfile")
    print("   • runtime.txt")
    print("   • requirements.txt")

def show_github_setup():
    """Показывает инструкции по настройке GitHub"""
    print("\n📚 Настройка GitHub для бесплатного хостинга:")
    print("1. Создайте аккаунт на GitHub.com (бесплатно)")
    print("2. Создайте новый репозиторий")
    print("3. Загрузите код:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit'")
    print("   git remote add origin https://github.com/username/repo.git")
    print("   git push -u origin main")
    print("4. Подключите к выбранному хостингу")

def main():
    """Основная функция"""
    print("🌐 Бесплатная локализация Nexa Messenger")
    print("=" * 60)
    
    while True:
        print("\nВыберите действие:")
        print("1. Показать варианты бесплатного хостинга")
        print("2. Быстрая настройка Ngrok")
        print("3. Создать файлы для развертывания")
        print("4. Инструкции по GitHub")
        print("5. Выход")
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == '1':
            show_free_hosting_options()
        elif choice == '2':
            setup_ngrok_quick()
        elif choice == '3':
            create_deployment_files()
        elif choice == '4':
            show_github_setup()
        elif choice == '5':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == '__main__':
    main()
