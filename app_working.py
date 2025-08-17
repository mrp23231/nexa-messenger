#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Максимально простая рабочая версия
Только базовый Flask, никаких сложных расширений
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3

# Создание Flask приложения
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nexa-messenger-secret-key-2024')

# Функции для работы с базой данных
def init_db():
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    
    # Создаем таблицу пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            is_online BOOLEAN DEFAULT 0,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем таблицу сообщений
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    # Простое хеширование для демонстрации
    return str(hash(password) % 1000000)

def verify_password(password, password_hash):
    return str(hash(password) % 1000000) == password_hash

def get_user_by_username(username):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, email, password, display_name):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash, display_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hash_password(password), display_name))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_all_users():
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('SELECT id, username, display_name, is_online, last_seen FROM users')
    users = c.fetchall()
    conn.close()
    return users

def get_messages_between_users(user1_id, user2_id):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
        OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    ''', (user1_id, user2_id, user2_id, user1_id))
    messages = c.fetchall()
    conn.close()
    return messages

def save_message(sender_id, receiver_id, content):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    ''', (sender_id, receiver_id, content))
    conn.commit()
    conn.close()

# Глобальная переменная для текущего пользователя
current_user = None

# Маршруты
@app.route('/')
def index():
    global current_user
    if current_user:
        return redirect('/chat')
    return render_template('login_simple.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    global current_user
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        display_name = request.form.get('display_name', '').strip()
        
        if not all([username, email, password, display_name]):
            flash('Все поля обязательны для заполнения!')
            return render_template('register_simple.html')
        
        # Проверяем, существует ли пользователь
        if get_user_by_username(username):
            flash('Пользователь с таким именем уже существует!')
            return render_template('register_simple.html')
        
        # Создаем пользователя
        if create_user(username, email, password, display_name):
            flash('Регистрация успешна! Теперь войдите в систему.')
            return redirect('/login')
        else:
            flash('Ошибка при создании пользователя!')
            return render_template('register_simple.html')
    
    return render_template('register_simple.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Введите имя пользователя и пароль!')
            return render_template('login_simple.html')
        
        user = get_user_by_username(username)
        if user and verify_password(password, user[3]):  # user[3] - password_hash
            current_user = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'display_name': user[4],
                'is_admin': user[7]
            }
            flash(f'Добро пожаловать, {current_user["display_name"]}!')
            return redirect('/chat')
        else:
            flash('Неверное имя пользователя или пароль!')
            return render_template('login_simple.html')
    
    return render_template('login_simple.html')

@app.route('/logout')
def logout():
    global current_user
    current_user = None
    flash('Вы вышли из системы!')
    return redirect('/')

@app.route('/chat')
def chat():
    global current_user
    if not current_user:
        return redirect('/login')
    
    users = get_all_users()
    return render_template('chat_simple.html', users=users, current_user=current_user)

@app.route('/chat/<int:user_id>')
def chat_with_user(user_id):
    global current_user
    if not current_user:
        return redirect('/login')
    
    # Получаем информацию о пользователе
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    other_user = c.fetchone()
    conn.close()
    
    if not other_user:
        flash('Пользователь не найден!')
        return redirect('/chat')
    
    # Получаем сообщения
    messages = get_messages_between_users(current_user['id'], user_id)
    
    return render_template('chat_conversation_simple.html', 
                         other_user=other_user, 
                         messages=messages, 
                         current_user=current_user)

@app.route('/send_message', methods=['POST'])
def send_message():
    global current_user
    if not current_user:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.get_json()
    content = data.get('content', '').strip()
    receiver_id = data.get('receiver_id')
    
    if not content or not receiver_id:
        return jsonify({'error': 'Неверные данные'}), 400
    
    save_message(current_user['id'], receiver_id, content)
    
    return jsonify({
        'success': True,
        'message': 'Сообщение отправлено'
    })

@app.route('/api/messages/<int:user_id>')
def get_messages(user_id):
    global current_user
    if not current_user:
        return jsonify({'error': 'Не авторизован'}), 401
    
    messages = get_messages_between_users(current_user['id'], user_id)
    
    # Получаем имена пользователей
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    
    result = []
    for msg in messages:
        c.execute('SELECT display_name FROM users WHERE id = ?', (msg[1],))
        sender_name = c.fetchone()[0]
        
        result.append({
            'id': msg[0],
            'content': msg[4],
            'timestamp': msg[5],
            'sender_name': sender_name,
            'is_own': msg[1] == current_user['id']
        })
    
    conn.close()
    return jsonify(result)

# Главная функция
if __name__ == '__main__':
    try:
        print("🚀 Запуск Nexa Messenger (простая рабочая версия)...")
        print(f"📊 SECRET_KEY: {app.secret_key[:20]}...")
        print(f"🌐 PORT: {os.environ.get('PORT', '8080')}")
        
        # Инициализируем базу данных
        print("📁 Инициализация базы данных...")
        init_db()
        print("✅ База данных готова")
        
        port = int(os.environ.get('PORT', 8080))
        print(f"🚪 Запуск на порту: {port}")
        
        print("🏭 Продакшен режим")
        app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
