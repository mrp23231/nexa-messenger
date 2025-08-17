#!/usr/bin/env python3
"""
Скрипт для обновления структуры базы данных
Добавляет новые колонки для системы модерации и рейтинга
"""

import sqlite3
import os
from datetime import datetime

def update_database():
    """Обновляет структуру базы данных"""
    db_path = "instance/nexa_messenger.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    print("🔍 Обновляю структуру базы данных...")
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существующие колонки в таблице user
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Существующие колонки: {columns}")
        
        # Добавляем недостающие колонки
        new_columns = [
            ('warnings_count', 'INTEGER DEFAULT 0'),
            ('last_warning', 'DATETIME'),
            ('rating', 'FLOAT DEFAULT 5.0'),
            ('rating_count', 'INTEGER DEFAULT 0')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"➕ Добавляю колонку: {column_name}")
                cursor.execute(f"ALTER TABLE user ADD COLUMN {column_name} {column_type}")
            else:
                print(f"✅ Колонка уже существует: {column_name}")
        
        # Создаем новые таблицы
        print("\n🗄️ Создаю новые таблицы...")
        
        # Таблица для предупреждений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                admin_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (admin_id) REFERENCES user (id)
            )
        """)
        print("✅ Таблица warning создана/проверена")
        
        # Таблица для рейтингов пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_rating (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rater_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (rater_id) REFERENCES user (id),
                UNIQUE(user_id, rater_id)
            )
        """)
        print("✅ Таблица user_rating создана/проверена")
        
        # Таблица для действий модерации
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moderation_action (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                reason TEXT,
                duration INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES user (id),
                FOREIGN KEY (target_user_id) REFERENCES user (id)
            )
        """)
        print("✅ Таблица moderation_action создана/проверена")
        
        # Обновляем существующих пользователей
        print("\n👥 Обновляю существующих пользователей...")
        cursor.execute("""
            UPDATE user SET 
                warnings_count = 0,
                rating = 5.0,
                rating_count = 0
            WHERE warnings_count IS NULL OR rating IS NULL OR rating_count IS NULL
        """)
        
        updated_rows = cursor.rowcount
        print(f"✅ Обновлено пользователей: {updated_rows}")
        
        # Сохраняем изменения
        conn.commit()
        print("💾 Изменения сохранены в базе данных")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(user)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"\n📋 Финальная структура таблицы user:")
        for column in final_columns:
            print(f"   - {column}")
        
        conn.close()
        print("\n🎉 База данных успешно обновлена!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Запускаю обновление базы данных")
    print("=" * 50)
    
    if update_database():
        print("\n✅ Обновление завершено успешно!")
        print("🚀 Теперь можно запускать сервер")
    else:
        print("\n❌ Обновление не удалось")
        print("🔧 Проверьте права доступа к файлу базы данных")

if __name__ == "__main__":
    main()
