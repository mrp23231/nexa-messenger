#!/usr/bin/env python3
"""
Бесплатная локализация Nexa Messenger через Ngrok
"""

import os
import sys
import subprocess
import time
import requests
import json

def install_ngrok():
    """Устанавливает Ngrok"""
    print("🔧 Установка Ngrok для бесплатного доступа...")
    
    try:
        # Проверяем, установлен ли уже ngrok
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok уже установлен!")
            return True
    except FileNotFoundError:
        pass
    
    print("📥 Скачивание Ngrok...")
    
    # Определяем OS
    import platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-arm64.tgz"
        else:
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.tgz"
    elif system == "linux":
        if "arm" in machine or "aarch64" in machine:
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
        else:
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    elif system == "windows":
        url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    else:
        print("❌ Неподдерживаемая операционная система")
        return False
    
    try:
        # Скачиваем ngrok
        print(f"📥 Скачивание с {url}")
        
        if system == "windows":
            subprocess.run(['curl', '-L', url, '-o', 'ngrok.zip'], check=True)
            subprocess.run(['unzip', 'ngrok.zip'], check=True)
            os.remove('ngrok.zip')
        else:
            subprocess.run(['curl', '-L', url, '-o', 'ngrok.tgz'], check=True)
            subprocess.run(['tar', '-xzf', 'ngrok.tgz'], check=True)
            os.remove('ngrok.tgz')
        
        # Делаем исполняемым
        if system != "windows":
            subprocess.run(['chmod', '+x', 'ngrok'], check=True)
        
        print("✅ Ngrok успешно установлен!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка установки: {e}")
        return False

def setup_ngrok_account():
    """Настраивает аккаунт Ngrok"""
    print("\n🔑 Настройка аккаунта Ngrok...")
    print("📋 Для бесплатного использования:")
    print("   1. Зайдите на https://ngrok.com/signup")
    print("   2. Зарегистрируйтесь (бесплатно)")
    print("   3. Получите authtoken")
    print("   4. Введите его ниже")
    
    authtoken = input("\nВведите ваш authtoken: ").strip()
    
    if not authtoken:
        print("❌ Authtoken не введен")
        return False
    
    try:
        # Настраиваем ngrok
        subprocess.run(['./ngrok', 'config', 'add-authtoken', authtoken], check=True)
        print("✅ Ngrok настроен!")
        return True
    except Exception as e:
        print(f"❌ Ошибка настройки: {e}")
        return False

def start_ngrok_tunnel():
    """Запускает туннель Ngrok"""
    print("\n🚀 Запуск туннеля Ngrok...")
    
    try:
        # Запускаем ngrok в фоне
        process = subprocess.Popen(['./ngrok', 'http', '8080'], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        
        # Ждем запуска
        time.sleep(3)
        
        # Получаем URL туннеля
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    print(f"✅ Туннель запущен!")
                    print(f"🌐 Публичный URL: {public_url}")
                    print(f"🔗 Локальный URL: http://localhost:8080")
                    print(f"\n📱 Теперь все могут зайти по адресу: {public_url}")
                    print(f"\n⏹️  Для остановки нажмите Ctrl+C")
                    
                    # Сохраняем URL в файл
                    with open('public_url.txt', 'w') as f:
                        f.write(public_url)
                    
                    return process, public_url
                else:
                    print("❌ Туннель не создан")
                    process.terminate()
                    return None, None
            else:
                print("❌ Не удалось получить информацию о туннеле")
                process.terminate()
                return None, None
                
        except Exception as e:
            print(f"❌ Ошибка получения URL: {e}")
            process.terminate()
            return None, None
            
    except Exception as e:
        print(f"❌ Ошибка запуска туннеля: {e}")
        return None, None

def main():
    """Основная функция"""
    print("🌐 Бесплатная локализация Nexa Messenger")
    print("=" * 50)
    
    # Проверяем, запущен ли сервер
    try:
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code != 200:
            print("❌ Сервер не запущен на порту 8080")
            print("   Сначала запустите: python start_server.py")
            return
    except:
        print("❌ Сервер не запущен на порту 8080")
        print("   Сначала запустите: python start_server.py")
        return
    
    print("✅ Сервер запущен на порту 8080")
    
    # Устанавливаем ngrok
    if not install_ngrok():
        print("❌ Не удалось установить Ngrok")
        return
    
    # Настраиваем аккаунт
    if not setup_ngrok_account():
        print("❌ Не удалось настроить Ngrok")
        return
    
    # Запускаем туннель
    process, public_url = start_ngrok_tunnel()
    if not process:
        return
    
    try:
        # Ждем завершения
        process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка туннеля...")
        process.terminate()
        print("✅ Туннель остановлен")
        
        # Удаляем временные файлы
        if os.path.exists('public_url.txt'):
            os.remove('public_url.txt')

if __name__ == '__main__':
    main()
