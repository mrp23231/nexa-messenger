#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Nexa Messenger
"""

from app import app, db, User, UserSettings
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Инициализирует базу данных"""
    print("🚀 Инициализация базы данных Nexa Messenger...")
    
    with app.app_context():
        # Удаляем все существующие таблицы
        print("🗑️  Удаление существующих таблиц...")
        db.drop_all()
        
        # Создаем новые таблицы
        print("🏗️  Создание новых таблиц...")
        db.create_all()
        
        # Создаем тестового пользователя
        print("👤 Создание тестового пользователя...")
        test_user = User(
            username='admin',
            display_name='Администратор',
            email='admin@nexa.com',
            password_hash=generate_password_hash('admin123'),
            bio='Тестовый пользователь для демонстрации функций',
            created_at=datetime.utcnow(),
            is_online=False,
            last_seen=datetime.utcnow()
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        # Создаем настройки для пользователя
        print("⚙️  Создание настроек пользователя...")
        user_settings = UserSettings(
            user_id=test_user.id,
            theme='light',
            language='ru',
            notifications_enabled=True,
            sound_enabled=True,
            auto_save_drafts=True,
            privacy_level='public',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(user_settings)
        db.session.commit()
        
        print("✅ База данных успешно инициализирована!")
        print(f"   Тестовый пользователь: admin / admin123")
        print(f"   ID пользователя: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print(f"   Display Name: {test_user.display_name}")
        print(f"   Username: {test_user.username}")
        
        # Проверяем структуру таблиц
        print("\n📊 Проверка структуры таблиц...")
        try:
            # Проверяем таблицу User
            user = User.query.first()
            if user and hasattr(user, 'display_name'):
                print("   ✅ Таблица User содержит поле display_name")
            else:
                print("   ❌ Таблица User не содержит поле display_name")
            
            # Проверяем таблицу UserSettings
            settings = UserSettings.query.first()
            if settings:
                print("   ✅ Таблица UserSettings создана")
            else:
                print("   ❌ Таблица UserSettings не создана")
                
        except Exception as e:
            print(f"   ❌ Ошибка при проверке структуры: {e}")

if __name__ == "__main__":
    init_database()
