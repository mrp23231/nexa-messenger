#!/usr/bin/env python3
"""
Скрипт для проверки внешнего IP адреса
"""

import requests
import socket

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        # Создаем сокет для получения локального IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Не удалось определить"

def get_external_ip():
    """Получает внешний IP адрес"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except Exception:
        return "Не удалось определить"

def main():
    """Основная функция"""
    print("🌐 Проверка IP адресов для Nexa Messenger...")
    print()
    
    local_ip = get_local_ip()
    external_ip = get_external_ip()
    
    print(f"📍 Локальный IP: {local_ip}")
    print(f"🌍 Внешний IP: {external_ip}")
    print()
    
    if local_ip != "Не удалось определить":
        print("🔗 Для локального доступа:")
        print(f"   http://{local_ip}:8080")
        print()
    
    if external_ip != "Не удалось определить":
        print("🌐 Для доступа из интернета:")
        print(f"   http://{external_ip}:8080")
        print("   ⚠️  Убедитесь, что порт 8080 открыт на роутере!")
        print()
    
    print("📋 Инструкции по настройке:")
    print("   1. Настройте проброс порта 8080 на роутере")
    print("   2. Убедитесь, что файрвол разрешает подключения")
    print("   3. Для продакшена настройте домен и SSL")
    print()
    print("🔐 Данные для входа:")
    print("   Username: admin")
    print("   Пароль: admin123456")

if __name__ == '__main__':
    main()
