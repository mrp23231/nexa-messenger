#!/usr/bin/env python3
"""
Скрипт для запуска Nexa Messenger с настройками для интернета
"""

import os
import sys
from app import app, socketio

def main():
    """Запуск сервера"""
    
    # Настройки для доступа из интернета
    host = '0.0.0.0'  # Доступ со всех интерфейсов
    port = 8080
    debug = False  # Отключаем режим отладки для продакшена
    
    print("🚀 Запуск Nexa Messenger для интернета...")
    print(f"   Хост: {host}")
    print(f"   Порт: {port}")
    print(f"   Режим отладки: {'Включен' if debug else 'Выключен'}")
    print(f"   Доступ: http://localhost:{port}")
    print(f"   Админ-панель: http://localhost:{port}/admin")
    print("\n📱 Для доступа из интернета:")
    print(f"   • Настройте проброс порта {port} на роутере")
    print(f"   • Используйте ваш внешний IP адрес")
    print(f"   • Или настройте домен и SSL сертификат")
    print("\n🔐 Данные для входа:")
    print(f"   • Username: admin")
    print(f"   • Пароль: admin123456")
    print("\n⏹️  Для остановки нажмите Ctrl+C")
    
    try:
        # Запускаем приложение
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Отключаем автоперезагрузку
            log_output=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
