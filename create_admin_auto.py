#!/usr/bin/env python3
"""
Автоматическое создание администратора Nexa Messenger
"""

import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_auto():
    """Автоматически создает администратора"""
    
    with app.app_context():
        print("🔧 Автоматическое создание администратора...")
        
        # Проверяем, есть ли уже админы
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"✅ Администратор уже существует: {existing_admin.username}")
            return
        
        # Данные администратора по умолчанию
        admin_data = {
            'username': 'admin',
            'display_name': 'Администратор',
            'email': 'admin@nexa-messenger.com',
            'password': 'admin123456',
            'is_admin': True,
            'status': 'online'
        }
        
        # Проверяем, не занят ли username
        if User.query.filter_by(username=admin_data['username']).first():
            print(f"❌ Пользователь с username '{admin_data['username']}' уже существует")
            return
        
        # Проверяем, не занят ли email
        if User.query.filter_by(email=admin_data['email']).first():
            print(f"❌ Пользователь с email '{admin_data['email']}' уже существует")
            return
        
        try:
            admin = User(
                username=admin_data['username'],
                display_name=admin_data['display_name'],
                email=admin_data['email'],
                password_hash=generate_password_hash(admin_data['password']),
                is_admin=True,
                status='online'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Администратор успешно создан!")
            print(f"   Username: {admin_data['username']}")
            print(f"   Пароль: {admin_data['password']}")
            print(f"   Email: {admin_data['email']}")
            print(f"   Права: Администратор")
            print("\n🚀 Теперь вы можете:")
            print("   • Войти в систему с этими данными")
            print("   • Получить доступ к админ-панели по адресу /admin")
            print("   • Управлять пользователями и системой")
            print("\n⚠️  ВАЖНО: Измените пароль после первого входа!")
            
        except Exception as e:
            print(f"❌ Ошибка при создании администратора: {e}")
            db.session.rollback()

if __name__ == '__main__':
    try:
        create_admin_auto()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
