#!/usr/bin/env python3
"""
Скрипт для создания демо-жалобы для тестирования системы модерации
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Report

def create_demo_report():
    """Создает демо-жалобу для тестирования"""
    
    print("🚩 Создание демо-жалобы для тестирования")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Проверяем, есть ли уже жалобы
            if Report.query.count() > 0:
                print("ℹ️ Жалобы уже существуют")
                return
            
            # Находим первого пользователя (не админа)
            demo_user = User.query.filter_by(is_admin=False).first()
            
            if not demo_user:
                print("❌ Нет пользователей для создания демо-жалобы")
                return
            
            print(f"👤 Найден пользователь: {demo_user.username} (ID: {demo_user.id})")
            
            # Создаем демо-жалобу
            demo_report = Report(
                reporter_id=demo_user.id,
                reported_user_id=demo_user.id,  # Жалуемся на самого себя для демо
                reason='Спам и реклама',
                description='Пользователь отправляет рекламные сообщения в общий чат',
                evidence='Сообщения в чате #1, #5, #12. Скриншот прилагается.',
                status='pending'
            )
            
            db.session.add(demo_report)
            db.session.commit()
            
            print("✅ Демо-жалоба создана успешно!")
            print(f"   ID жалобы: {demo_report.id}")
            print(f"   От: @{demo_report.reporter.username}")
            print(f"   На: @{demo_report.reported_user.username}")
            print(f"   Причина: {demo_report.reason}")
            print(f"   Статус: {demo_report.status}")
            print(f"   Время: {demo_report.created_at.strftime('%d.%m.%Y %H:%M')}")
            
            # Проверяем статистику
            total_reports = Report.query.count()
            pending_reports = Report.query.filter_by(status='pending').count()
            
            print(f"\n📊 Статистика жалоб:")
            print(f"   Всего жалоб: {total_reports}")
            print(f"   В ожидании: {pending_reports}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    success = create_demo_report()
    
    if success:
        print("\n🎯 Демо-жалоба готова!")
        print("💡 Теперь вы можете:")
        print("   1. Войти как администратор (admin/admin123456)")
        print("   2. Перейти в админ-панель")
        print("   3. Увидеть жалобу в разделе 'Последние жалобы'")
        print("   4. Протестировать функции модерации")
    else:
        print("\n❌ Создание демо-жалобы завершилось с ошибками")
