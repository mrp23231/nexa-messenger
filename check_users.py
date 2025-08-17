#!/usr/bin/env python3
"""
Скрипт для проверки пользователей в базе данных
"""

import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Report

def check_users():
    """Проверяет пользователей в базе данных"""
    
    print("👥 Проверка пользователей в базе данных")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Получаем всех пользователей
            users = User.query.all()
            
            if not users:
                print("❌ В базе нет пользователей")
                return
            
            print(f"✅ Найдено пользователей: {len(users)}")
            print()
            
            for user in users:
                print(f"👤 ID: {user.id}")
                print(f"   Username: @{user.username}")
                print(f"   Display Name: {user.display_name}")
                print(f"   Email: {user.email}")
                print(f"   Админ: {'Да' if user.is_admin else 'Нет'}")
                print(f"   Заблокирован: {'Да' if user.is_banned else 'Нет'}")
                if user.is_banned:
                    print(f"   Причина блокировки: {user.ban_reason}")
                print(f"   Дата регистрации: {user.created_at.strftime('%d.%m.%Y %H:%M')}")
                print()
            
            # Проверяем жалобы
            reports = Report.query.all()
            print(f"🚩 Жалоб в базе: {len(reports)}")
            
            if reports:
                for report in reports:
                    print(f"   ID: {report.id}")
                    print(f"   От: @{report.reporter.username}")
                    print(f"   На: @{report.reported_user.username}")
                    print(f"   Причина: {report.reason}")
                    print(f"   Статус: {report.status}")
                    print()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    check_users()
