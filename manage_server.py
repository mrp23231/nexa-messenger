#!/usr/bin/env python3
"""
Скрипт управления сервером Nexa Messenger
"""

import os
import sys
import subprocess
import signal
import time

def check_server_status():
    """Проверяет статус сервера"""
    try:
        result = subprocess.run(['curl', '-s', 'http://localhost:8080'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "Сервер работает"
        else:
            return False, "Сервер не отвечает"
    except Exception as e:
        return False, f"Ошибка проверки: {e}"

def start_server():
    """Запускает сервер"""
    print("🚀 Запуск Nexa Messenger...")
    
    # Проверяем, не запущен ли уже сервер
    is_running, status = check_server_status()
    if is_running:
        print("✅ Сервер уже запущен!")
        return
    
    try:
        # Запускаем сервер в фоне
        process = subprocess.Popen([sys.executable, 'start_server.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        
        # Ждем немного для запуска
        time.sleep(3)
        
        # Проверяем статус
        is_running, status = check_server_status()
        if is_running:
            print("✅ Сервер успешно запущен!")
            print("   Локальный доступ: http://localhost:8080")
            print("   Админ-панель: http://localhost:8080/admin")
            print("   PID процесса:", process.pid)
        else:
            print("❌ Ошибка запуска сервера")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def stop_server():
    """Останавливает сервер"""
    print("🛑 Остановка Nexa Messenger...")
    
    try:
        # Ищем процессы Python с start_server.py
        result = subprocess.run(['pkill', '-f', 'start_server.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Сервер остановлен")
        else:
            print("ℹ️  Сервер не был запущен")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def restart_server():
    """Перезапускает сервер"""
    print("🔄 Перезапуск Nexa Messenger...")
    stop_server()
    time.sleep(2)
    start_server()

def show_status():
    """Показывает статус сервера"""
    print("📊 Статус Nexa Messenger...")
    
    is_running, status = check_server_status()
    
    if is_running:
        print("✅ Сервер работает")
        print("   URL: http://localhost:8080")
        print("   Админ: http://localhost:8080/admin")
        
        # Показываем IP адреса
        try:
            result = subprocess.run([sys.executable, 'check_external_ip.py'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("\n🌐 IP адреса:")
                for line in result.stdout.split('\n'):
                    if 'IP:' in line or 'http://' in line:
                        print(f"   {line.strip()}")
        except:
            pass
            
    else:
        print("❌ Сервер не работает")
        print("   Статус:", status)

def show_help():
    """Показывает справку"""
    print("""
🔧 Управление сервером Nexa Messenger

Использование: python manage_server.py [команда]

Команды:
  start     - Запустить сервер
  stop      - Остановить сервер
  restart   - Перезапустить сервер
  status    - Показать статус
  help      - Показать эту справку

Примеры:
  python manage_server.py start
  python manage_server.py status
  python manage_server.py stop

🔐 Данные для входа:
  Username: admin
  Пароль: admin123456
""")

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_server()
    elif command == 'stop':
        stop_server()
    elif command == 'restart':
        restart_server()
    elif command == 'status':
        show_status()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Неизвестная команда: {command}")
        show_help()

if __name__ == '__main__':
    main()
