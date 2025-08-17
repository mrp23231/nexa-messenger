#!/usr/bin/env python3
"""
Скрипт для инициализации системы модерации
"""

import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Report, ModerationAction

def init_moderation_system():
    """Инициализирует систему модерации"""
    
    print("🛡️ Инициализация системы модерации")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Проверяем существование таблиц
            print("📊 Проверка таблиц...")
            
            # Создаем таблицы если их нет
            db.create_all()
            print("✅ Таблицы созданы/проверены")
            
            # Проверяем таблицу жалоб
            if not Report.query.first():
                print("📝 Таблица жалоб готова")
            else:
                print("ℹ️ Таблица жалоб уже содержит данные")
            
            # Проверяем таблицу действий модерации
            if not ModerationAction.query.first():
                print("📝 Таблица действий модерации готова")
            else:
                print("ℹ️ Таблица действий модерации уже содержит данные")
            
            # Обновляем существующих пользователей
            print("\n👥 Обновление пользователей...")
            users = User.query.all()
            updated_count = 0
            
            for user in users:
                # Добавляем новые поля модерации
                if not hasattr(user, 'is_banned') or user.is_banned is None:
                    user.is_banned = False
                    updated_count += 1
                
                if not hasattr(user, 'ban_reason') or user.ban_reason is None:
                    user.ban_reason = ''
                    updated_count += 1
                
                if not hasattr(user, 'ban_until') or user.ban_until is None:
                    user.ban_until = None
                    updated_count += 1
                
                if not hasattr(user, 'ban_count') or user.ban_count is None:
                    user.ban_count = 0
                    updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                print(f"✅ Обновлено {updated_count} полей пользователей")
            else:
                print("ℹ️ Пользователи уже обновлены")
            
            # Создаем демо-жалобу для тестирования
            print("\n🚩 Создание демо-жалобы...")
            
            if Report.query.count() == 0:
                # Находим первого пользователя (не админа)
                demo_user = User.query.filter_by(is_admin=False).first()
                
                if demo_user:
                    # Создаем демо-жалобу
                    demo_report = Report(
                        reporter_id=demo_user.id,
                        reported_user_id=demo_user.id,  # Жалуемся на самого себя для демо
                        reason='Демо-жалоба для тестирования',
                        description='Это тестовая жалоба для проверки системы модерации',
                        evidence='Создана автоматически при инициализации',
                        status='pending'
                    )
                    
                    db.session.add(demo_report)
                    db.session.commit()
                    print("✅ Демо-жалоба создана")
                else:
                    print("ℹ️ Нет пользователей для создания демо-жалобы")
            else:
                print("ℹ️ Жалобы уже существуют")
            
            # Проверяем статистику
            print("\n📈 Статистика системы:")
            total_users = User.query.count()
            admin_users = User.query.filter_by(is_admin=True).count()
            banned_users = User.query.filter_by(is_banned=True).count()
            total_reports = Report.query.count()
            pending_reports = Report.query.filter_by(status='pending').count()
            total_actions = ModerationAction.query.count()
            
            print(f"   👥 Всего пользователей: {total_users}")
            print(f"   👑 Администраторов: {admin_users}")
            print(f"   🚫 Заблокированных: {banned_users}")
            print(f"   🚩 Всего жалоб: {total_reports}")
            print(f"   ⏳ Жалоб в ожидании: {pending_reports}")
            print(f"   📝 Действий модерации: {total_actions}")
            
            print("\n" + "=" * 50)
            print("🎯 Система модерации готова к работе!")
            print("\n💡 Что можно делать:")
            print("   1. Создавать жалобы на пользователей")
            print("   2. Блокировать нарушителей")
            print("   3. Управлять правами администраторов")
            print("   4. Просматривать профили пользователей")
            print("   5. Отслеживать статистику в админ-панели")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    success = init_moderation_system()
    
    if success:
        print("\n✅ Инициализация завершена успешно!")
        print("🚀 Теперь можно запускать приложение")
    else:
        print("\n❌ Инициализация завершилась с ошибками")
        print("🔧 Проверьте логи и попробуйте снова")
