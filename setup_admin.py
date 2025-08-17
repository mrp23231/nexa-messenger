#!/usr/bin/env python3
"""
Скрипт для настройки первого администратора Nexa Messenger
"""

import os
import sys
from getpass import getpass

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def setup_admin():
    """Настраивает первого администратора"""
    
    with app.app_context():
        print("🔧 Настройка администратора Nexa Messenger...")
        
        # Проверяем, есть ли уже админы
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"✅ Администратор уже существует: {existing_admin.username}")
            return
        
        print("📝 Создание первого администратора...")
        
        # Запрашиваем данные
        username = input("Введите username: ").strip()
        if not username:
            print("❌ Username не может быть пустым")
            return
        
        # Проверяем, не занят ли username
        if User.query.filter_by(username=username).first():
            print("❌ Пользователь с таким username уже существует")
            return
        
        display_name = input("Введите отображаемое имя (или Enter для username): ").strip()
        if not display_name:
            display_name = username
        
        email = input("Введите email: ").strip()
        if not email:
            print("❌ Email не может быть пустым")
            return
        
        # Проверяем, не занят ли email
        if User.query.filter_by(email=email).first():
            print("❌ Пользователь с таким email уже существует")
            return
        
        password = getpass("Введите пароль: ")
        if len(password) < 6:
            print("❌ Пароль должен содержать минимум 6 символов")
            return
        
        password_confirm = getpass("Подтвердите пароль: ")
        if password != password_confirm:
            print("❌ Пароли не совпадают")
            return
        
        # Создаем администратора
        try:
            from werkzeug.security import generate_password_hash
            
            admin = User(
                username=username,
                display_name=display_name,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True,
                status='online'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Администратор {username} успешно создан!")
            print(f"   Отображаемое имя: {display_name}")
            print(f"   Email: {email}")
            print(f"   Права: Администратор")
            print("\n🚀 Теперь вы можете:")
            print("   • Войти в систему с этими данными")
            print("   • Получить доступ к админ-панели")
            print("   • Управлять пользователями и системой")
            
        except Exception as e:
            print(f"❌ Ошибка при создании администратора: {e}")
            db.session.rollback()

if __name__ == '__main__':
    try:
        setup_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Операция отменена пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
