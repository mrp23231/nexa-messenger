#!/usr/bin/env python3
"""
Проверка содержимого базы данных
"""

from app import app, db, User, UserSettings

def check_database():
    """Проверяет содержимое базы данных"""
    print("🔍 Проверка содержимого базы данных...")
    
    with app.app_context():
        # Проверяем пользователей
        users = User.query.all()
        print(f"👥 Пользователей в базе: {len(users)}")
        
        for user in users:
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Display Name: {user.display_name}")
            print(f"   Email: {user.email}")
            print(f"   Password Hash: {user.password_hash[:50]}...")
            print(f"   Created: {user.created_at}")
            print(f"   Online: {user.is_online}")
            print(f"   Last Seen: {user.last_seen}")
            print("   ---")
        
        # Проверяем настройки
        settings = UserSettings.query.all()
        print(f"⚙️  Настроек в базе: {len(settings)}")
        
        for setting in settings:
            print(f"   ID: {setting.id}")
            print(f"   User ID: {setting.user_id}")
            print(f"   Theme: {setting.theme}")
            print(f"   Language: {setting.language}")
            print("   ---")
        
        # Проверяем конкретного пользователя
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("✅ Пользователь 'admin' найден:")
            print(f"   ID: {admin_user.id}")
            print(f"   Display Name: {admin_user.display_name}")
            print(f"   Password Hash: {admin_user.password_hash[:50]}...")
        else:
            print("❌ Пользователь 'admin' не найден")

if __name__ == "__main__":
    check_database()
