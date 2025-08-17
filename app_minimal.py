#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Максимально простая версия
Все HTML встроено в код, никаких внешних шаблонов
"""

import os
from flask import Flask, request, redirect, url_for
import sqlite3
from datetime import datetime

# Создание Flask приложения
app = Flask(__name__)

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
            password TEXT NOT NULL,
            display_name TEXT NOT NULL,
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
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, email, password, display_name):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (username, email, password, display_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password, display_name))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_user_by_username(username):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('SELECT id, username, display_name FROM users')
    users = c.fetchall()
    conn.close()
    return users

def save_message(sender_id, receiver_id, content):
    conn = sqlite3.connect('nexa_messenger.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    ''', (sender_id, receiver_id, content))
    conn.commit()
    conn.close()

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

# Глобальная переменная для текущего пользователя
current_user = None

# HTML шаблоны встроены в код
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Messenger - Вход</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; padding: 50px; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .error { color: red; margin: 10px 0; }
        .success { color: green; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 Nexa Messenger</h1>
        <h2>Вход в систему</h2>
        
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Имя пользователя" required>
            <input type="password" name="password" placeholder="Пароль" required>
            <button type="submit">Войти</button>
        </form>
        
        <p><a href="/register">Регистрация</a> | <a href="/">Главная</a></p>
    </div>
</body>
</html>
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Messenger - Регистрация</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; padding: 50px; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .error { color: red; margin: 10px 0; }
        .success { color: green; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 Nexa Messenger</h1>
        <h2>Регистрация</h2>
        
        <form method="POST" action="/register">
            <input type="text" name="username" placeholder="Имя пользователя" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Пароль" required>
            <input type="text" name="display_name" placeholder="Отображаемое имя" required>
            <button type="submit">Зарегистрироваться</button>
        </form>
        
        <p><a href="/login">Вход</a> | <a href="/">Главная</a></p>
    </div>
</body>
</html>
'''

CHAT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Messenger - Чат</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .chat-container { display: grid; grid-template-columns: 300px 1fr; gap: 20px; }
        .users-list { background: white; padding: 20px; border-radius: 10px; }
        .chat-area { background: white; padding: 20px; border-radius: 10px; }
        .user-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
        .user-item:hover { background: #f8f9fa; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .message.own { background: #007bff; color: white; }
        .message.other { background: #e9ecef; }
        input, button { padding: 10px; margin: 5px; }
        .logout { background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 Nexa Messenger</h1>
            <p>Добро пожаловать, {display_name}!</p>
            <a href="/logout" class="logout">Выйти</a>
        </div>
        
        <div class="chat-container">
            <div class="users-list">
                <h3>Пользователи</h3>
                {users_list}
            </div>
            
            <div class="chat-area">
                <h3>Выберите пользователя для чата</h3>
                <div id="messages"></div>
                <div id="message-input" style="display: none;">
                    <input type="text" id="message-text" placeholder="Введите сообщение...">
                    <button onclick="sendMessage()">Отправить</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedUserId = null;
        
        function selectUser(userId, userName) {
            selectedUserId = userId;
            document.getElementById('message-input').style.display = 'block';
            loadMessages(userId);
        }
        
        function loadMessages(userId) {
            fetch('/api/messages/' + userId)
                .then(response => response.json())
                .then(messages => {
                    displayMessages(messages);
                });
        }
        
        function displayMessages(messages) {
            const container = document.getElementById('messages');
            container.innerHTML = '';
            
            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = 'message ' + (msg.is_own ? 'own' : 'other');
                div.innerHTML = msg.content + ' <small>(' + msg.timestamp + ')</small>';
                container.appendChild(div);
            });
        }
        
        function sendMessage() {
            const text = document.getElementById('message-text').value;
            if (!text || !selectedUserId) return;
            
            fetch('/send_message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    content: text,
                    receiver_id: selectedUserId
                })
            }).then(() => {
                document.getElementById('message-text').value = '';
                loadMessages(selectedUserId);
            });
        }
        
        // Автообновление каждые 3 секунды
        setInterval(() => {
            if (selectedUserId) loadMessages(selectedUserId);
        }, 3000);
    </script>
</body>
</html>
'''

# Маршруты
@app.route('/')
def index():
    global current_user
    if current_user:
        return redirect('/chat')
    return LOGIN_HTML

@app.route('/register', methods=['GET', 'POST'])
def register():
    global current_user
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        display_name = request.form.get('display_name', '').strip()
        
        if not all([username, email, password, display_name]):
            return REGISTER_HTML + '<div class="error">Все поля обязательны!</div>'
        
        if get_user_by_username(username):
            return REGISTER_HTML + '<div class="error">Пользователь уже существует!</div>'
        
        if create_user(username, email, password, display_name):
            return REGISTER_HTML + '<div class="success">Регистрация успешна! <a href="/login">Войти</a></div>'
        else:
            return REGISTER_HTML + '<div class="error">Ошибка при создании пользователя!</div>'
    
    return REGISTER_HTML

@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return LOGIN_HTML + '<div class="error">Введите имя пользователя и пароль!</div>'
        
        user = get_user_by_username(username)
        if user and user[3] == password:  # user[3] - password
            current_user = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'display_name': user[4]
            }
            return redirect('/chat')
        else:
            return LOGIN_HTML + '<div class="error">Неверное имя пользователя или пароль!</div>'
    
    return LOGIN_HTML

@app.route('/logout')
def logout():
    global current_user
    current_user = None
    return redirect('/')

@app.route('/chat')
def chat():
    global current_user
    if not current_user:
        return redirect('/login')
    
    users = get_all_users()
    users_list = ''
    for user in users:
        if user[0] != current_user['id']:
            users_list += f'<div class="user-item" onclick="selectUser({user[0]}, \'{user[2]}\')">{user[2]} (@{user[1]})</div>'
    
    return CHAT_HTML.format(
        display_name=current_user['display_name'],
        users_list=users_list
    )

@app.route('/send_message', methods=['POST'])
def send_message():
    global current_user
    if not current_user:
        return {'error': 'Не авторизован'}, 401
    
    data = request.get_json()
    content = data.get('content', '').strip()
    receiver_id = data.get('receiver_id')
    
    if not content or not receiver_id:
        return {'error': 'Неверные данные'}, 400
    
    save_message(current_user['id'], receiver_id, content)
    return {'success': True}

@app.route('/api/messages/<int:user_id>')
def get_messages(user_id):
    global current_user
    if not current_user:
        return {'error': 'Не авторизован'}, 401
    
    messages = get_messages_between_users(current_user['id'], user_id)
    
    result = []
    for msg in messages:
        result.append({
            'id': msg[0],
            'content': msg[4],
            'timestamp': msg[5],
            'is_own': msg[1] == current_user['id']
        })
    
    return result

# Главная функция
if __name__ == '__main__':
    try:
        print("🚀 Запуск Nexa Messenger (минимальная версия)...")
        
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
