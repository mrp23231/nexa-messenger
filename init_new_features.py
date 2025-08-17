#!/usr/bin/env python3
"""
Скрипт для инициализации новых функций в базе данных Nexa Messenger
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Channel, ChannelMember, MessageReaction, Report, ModerationAction

def init_new_features():
    """Инициализирует новые функции в базе данных"""
    
    with app.app_context():
        print("🔧 Инициализация новых функций Nexa Messenger...")
        
        # Создаем все таблицы
        print("📊 Создание таблиц...")
        db.create_all()
        print("✅ Таблицы созданы")
        
        # Проверяем новые таблицы модерации
        print("🛡️ Проверка таблиц модерации...")
        if not Report.query.first():
            print("📝 Таблица жалоб готова")
        
        if not ModerationAction.query.first():
            print("📝 Таблица действий модерации готова")
        
        # Создаем несколько демо-каналов
        print("📢 Создание демо-каналов...")
        
        # Проверяем, есть ли уже каналы
        if Channel.query.count() == 0:
            # Создаем демо-каналы
            channels_data = [
                {
                    'name': 'Общий',
                    'description': 'Общий канал для всех пользователей',
                    'topic': 'Общение и знакомства',
                    'is_public': True
                },
                {
                    'name': 'Технологии',
                    'description': 'Обсуждение новинок в мире технологий',
                    'topic': 'IT, программирование, гаджеты',
                    'is_public': True
                },
                {
                    'name': 'Музыка',
                    'description': 'Любимая музыка, новые релизы, концерты',
                    'topic': 'Музыкальные предпочтения',
                    'is_public': True
                },
                {
                    'name': 'Спорт',
                    'description': 'Спортивные новости и обсуждения',
                    'topic': 'Футбол, хоккей, другие виды спорта',
                    'is_public': True
                },
                {
                    'name': 'Кино',
                    'description': 'Фильмы, сериалы, актеры',
                    'topic': 'Кинематограф и телевидение',
                    'is_public': True
                }
            ]
            
            # Получаем первого пользователя как создателя (если есть)
            first_user = User.query.first()
            
            for channel_data in channels_data:
                channel = Channel(
                    name=channel_data['name'],
                    description=channel_data['description'],
                    topic=channel_data['topic'],
                    is_public=channel_data['is_public'],
                    created_by=first_user.id if first_user else 1
                )
                db.session.add(channel)
            
            db.session.commit()
            print(f"✅ Создано {len(channels_data)} демо-каналов")
        else:
            print("ℹ️ Каналы уже существуют")
        
        # Обновляем существующих пользователей (добавляем новые поля)
        print("👥 Обновление пользователей...")
        users = User.query.all()
        updated_count = 0
        
        for user in users:
            # Устанавливаем значения по умолчанию для новых полей
            if not hasattr(user, 'status') or user.status is None:
                user.status = 'online'
                updated_count += 1
            
            if not hasattr(user, 'custom_status') or user.custom_status is None:
                user.custom_status = ''
                updated_count += 1
            
            if not hasattr(user, 'color_accent') or user.color_accent is None:
                user.color_accent = '#00d4ff'
                updated_count += 1
            
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
        
        # Обновляем настройки пользователей
        print("⚙️ Обновление настроек пользователей...")
        for user in users:
            settings = user.get_settings()
            
            # Добавляем новые настройки
            if not hasattr(settings, 'animations_enabled') or settings.animations_enabled is None:
                settings.animations_enabled = True
            
            if not hasattr(settings, 'compact_mode') or settings.compact_mode is None:
                settings.compact_mode = False
        
        db.session.commit()
        print("✅ Настройки пользователей обновлены")
        
        print("\n🎉 Инициализация завершена успешно!")
        print("\n📋 Созданные функции:")
        print("   • Публичные каналы по интересам")
        print("   • Ответы на сообщения")
        print("   • Редактирование сообщений")
        print("   • Удаление сообщений")
        print("   • Реакции на сообщения (эмодзи)")
        print("   • Темы оформления (светлая/темная)")
        print("   • Кастомные аватары")
        print("   • Статусы пользователей")
        print("   • Цветовые акценты")
        print("   • Анимации и эффекты")
        
        print("\n🚀 Теперь вы можете:")
        print("   • Создавать и присоединяться к каналам")
        print("   • Отвечать на сообщения")
        print("   • Редактировать свои сообщения")
        print("   • Добавлять реакции к сообщениям")
        print("   • Настраивать тему и цвета")
        print("   • Устанавливать статус")

if __name__ == '__main__':
    try:
        init_new_features()
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        sys.exit(1)
