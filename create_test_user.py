#!/usr/bin/env python3
"""
Скрипт для создания тестового пользователя
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def create_test_user():
    """Создает тестового пользователя"""
    
    print("👤 Создание тестового пользователя")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Проверяем, есть ли уже тестовый пользователь
            test_user = User.query.filter_by(username='testuser').first()
            
            if test_user:
                print("ℹ️ Тестовый пользователь уже существует")
                return test_user
            
            # Создаем тестового пользователя
            test_user = User(
                username='testuser',
                display_name='Тестовый Пользователь',
                email='test@example.com',
                password_hash=generate_password_hash('test123456'),
                profile_picture='default.jpg',
                bio='Тестовый пользователь для демонстрации функций',
                created_at=datetime.utcnow(),
                is_online=False,
                status='online',
                custom_status='',
                color_accent='#00d4ff',
                is_admin=False,
                is_banned=False,
                ban_reason='',
                ban_until=None,
                ban_count=0
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Тестовый пользователь создан успешно!")
            print(f"   Username: @{test_user.username}")
            print(f"   Пароль: test123456")
            print(f"   Email: {test_user.email}")
            print(f"   ID: {test_user.id}")
            
            return test_user
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            return None

if __name__ == '__main__':
    user = create_test_user()
    
    if user:
        print("\n🎯 Тестовый пользователь готов!")
        print("💡 Теперь вы можете:")
        print("   1. Войти как testuser/test123456")
        print("   2. Создать жалобу на другого пользователя")
        print("   3. Протестировать систему модерации")
    else:
        print("\n❌ Создание пользователя завершилось с ошибками")
