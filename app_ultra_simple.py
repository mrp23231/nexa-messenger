#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Ультра простая надежная версия
С полной обработкой ошибок и отладкой
"""

import os
import traceback
from flask import Flask, request, redirect, url_for

# Создание Flask приложения
app = Flask(__name__)

# Функции для работы с базой данных
def init_db():
    try:
        import sqlite3
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
        print("✅ База данных инициализирована успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        traceback.print_exc()
        return False

def create_user(username, email, password, display_name):
    try:
        import sqlite3
        conn = sqlite3.connect('nexa_messenger.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO users (username, email, password, display_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password, display_name))
        
        conn.commit()
        conn.close()
        print(f"✅ Пользователь {username} создан успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        return False

def get_user_by_username(username):
    try:
        import sqlite3
        conn = sqlite3.connect('nexa_messenger.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"❌ Ошибка получения пользователя: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def get_all_users():
    try:
        import sqlite3
        conn = sqlite3.connect('nexa_messenger.db')
        c = conn.cursor()
        c.execute('SELECT id, username, display_name FROM users')
        users = c.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Ошибка получения пользователей: {e}")
        if 'conn' in locals():
            conn.close()
        return []

def save_message(sender_id, receiver_id, content):
    try:
        import sqlite3
        conn = sqlite3.connect('nexa_messenger.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (?, ?, ?)
        ''', (sender_id, receiver_id, content))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения сообщения: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def get_messages_between_users(user1_id, user2_id):
    try:
        import sqlite3
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
    except Exception as e:
        print(f"❌ Ошибка получения сообщений: {e}")
        if 'conn' in locals():
            conn.close()
        return []

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
                })
                .catch(error => {
                    console.error('Ошибка загрузки сообщений:', error);
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
            }).catch(error => {
                console.error('Ошибка отправки сообщения:', error);
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
    try:
        global current_user
        if current_user:
            return redirect('/chat')
        return LOGIN_HTML
    except Exception as e:
        print(f"❌ Ошибка в index: {e}")
        traceback.print_exc()
        return f"<h1>Ошибка</h1><p>{str(e)}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        global current_user
        
        if request.method == 'POST':
            print("📝 Получен POST запрос на регистрацию")
            
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            display_name = request.form.get('display_name', '').strip()
            
            print(f"📊 Данные: username={username}, email={email}, display_name={display_name}")
            
            if not all([username, email, password, display_name]):
                print("❌ Не все поля заполнены")
                return REGISTER_HTML + '<div class="error">Все поля обязательны для заполнения!</div>'
            
            # Проверяем, существует ли пользователь
            existing_user = get_user_by_username(username)
            if existing_user:
                print(f"❌ Пользователь {username} уже существует")
                return REGISTER_HTML + '<div class="error">Пользователь с таким именем уже существует!</div>'
            
            # Создаем пользователя
            print(f"🔧 Создание пользователя {username}...")
            if create_user(username, email, password, display_name):
                print(f"✅ Пользователь {username} создан успешно")
                return REGISTER_HTML + '<div class="success">Регистрация успешна! <a href="/login">Войти в систему</a></div>'
            else:
                print(f"❌ Ошибка при создании пользователя {username}")
                return REGISTER_HTML + '<div class="error">Ошибка при создании пользователя!</div>'
        
        print("📄 Отображение формы регистрации")
        return REGISTER_HTML
        
    except Exception as e:
        print(f"❌ Критическая ошибка в register: {e}")
        traceback.print_exc()
        return f"<h1>Критическая ошибка</h1><p>{str(e)}<br><a href='/'>Вернуться на главную</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        global current_user
        
        if request.method == 'POST':
            print("🔐 Получен POST запрос на вход")
            
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"📊 Данные входа: username={username}")
            
            if not username or not password:
                print("❌ Не все поля заполнены")
                return LOGIN_HTML + '<div class="error">Введите имя пользователя и пароль!</div>'
            
            user = get_user_by_username(username)
            if user and user[3] == password:  # user[3] - password
                print(f"✅ Успешный вход пользователя {username}")
                current_user = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'display_name': user[4]
                }
                return redirect('/chat')
            else:
                print(f"❌ Неудачная попытка входа для {username}")
                return LOGIN_HTML + '<div class="error">Неверное имя пользователя или пароль!</div>'
        
        print("📄 Отображение формы входа")
        return LOGIN_HTML
        
    except Exception as e:
        print(f"❌ Критическая ошибка в login: {e}")
        traceback.print_exc()
        return f"<h1>Критическая ошибка</h1><p>{str(e)}<br><a href='/'>Вернуться на главную</a>"

@app.route('/logout')
def logout():
    try:
        global current_user
        current_user = None
        print("🚪 Пользователь вышел из системы")
        return redirect('/')
    except Exception as e:
        print(f"❌ Ошибка в logout: {e}")
        return redirect('/')

@app.route('/chat')
def chat():
    try:
        global current_user
        if not current_user:
            print("❌ Попытка доступа к чату без авторизации")
            return redirect('/login')
        
        print(f"💬 Пользователь {current_user['username']} зашел в чат")
        users = get_all_users()
        users_list = ''
        for user in users:
            if user[0] != current_user['id']:
                users_list += f'<div class="user-item" onclick="selectUser({user[0]}, \'{user[2]}\')">{user[2]} (@{user[1]})</div>'
        
        return CHAT_HTML.format(
            display_name=current_user['display_name'],
            users_list=users_list
        )
        
    except Exception as e:
        print(f"❌ Критическая ошибка в chat: {e}")
        traceback.print_exc()
        return f"<h1>Критическая ошибка</h1><p>{str(e)}<br><a href='/'>Вернуться на главную</a>"

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        global current_user
        if not current_user:
            print("❌ Попытка отправки сообщения без авторизации")
            return {'error': 'Не авторизован'}, 401
        
        print(f"📤 Попытка отправки сообщения от {current_user['username']}")
        
        data = request.get_json()
        content = data.get('content', '').strip()
        receiver_id = data.get('receiver_id')
        
        print(f"📊 Данные сообщения: content='{content}', receiver_id={receiver_id}")
        
        if not content or not receiver_id:
            print("❌ Неверные данные сообщения")
            return {'error': 'Неверные данные'}, 400
        
        if save_message(current_user['id'], receiver_id, content):
            print(f"✅ Сообщение от {current_user['username']} сохранено")
            return {'success': True}
        else:
            print(f"❌ Ошибка сохранения сообщения от {current_user['username']}")
            return {'error': 'Ошибка сохранения'}, 500
        
    except Exception as e:
        print(f"❌ Критическая ошибка в send_message: {e}")
        traceback.print_exc()
        return {'error': 'Внутренняя ошибка сервера'}, 500

@app.route('/api/messages/<int:user_id>')
def get_messages(user_id):
    try:
        global current_user
        if not current_user:
            print("❌ Попытка получения сообщений без авторизации")
            return {'error': 'Не авторизован'}, 401
        
        print(f"📥 Запрос сообщений для {current_user['username']} с пользователем {user_id}")
        
        messages = get_messages_between_users(current_user['id'], user_id)
        
        result = []
        for msg in messages:
            result.append({
                'id': msg[0],
                'content': msg[4],
                'timestamp': msg[5],
                'is_own': msg[1] == current_user['id']
            })
        
        print(f"✅ Получено {len(result)} сообщений")
        return result
        
    except Exception as e:
        print(f"❌ Критическая ошибка в get_messages: {e}")
        traceback.print_exc()
        return {'error': 'Внутренняя ошибка сервера'}, 500

# Главная функция
if __name__ == '__main__':
    try:
        print("🚀 Запуск Nexa Messenger (ультра простая версия)...")
        print(f"🌐 PORT: {os.environ.get('PORT', '8080')}")
        
        # Инициализируем базу данных
        print("📁 Инициализация базы данных...")
        if not init_db():
            print("❌ Критическая ошибка: не удалось инициализировать БД")
            exit(1)
        
        port = int(os.environ.get('PORT', 8080))
        print(f"🚪 Запуск на порту: {port}")
        
        print("🏭 Продакшен режим")
        app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"❌ Критическая ошибка запуска: {e}")
        traceback.print_exc()
        exit(1)
