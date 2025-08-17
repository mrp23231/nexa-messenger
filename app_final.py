#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Финальная максимально простая версия
Только базовый Python и Flask, никаких внешних модулей
"""

import os
from flask import Flask, request, redirect

# Создание Flask приложения
app = Flask(__name__)

# Простое хранилище данных в памяти (вместо базы данных)
users = {}
messages = []
user_id_counter = 1
message_id_counter = 1

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

# Глобальная переменная для текущего пользователя
current_user = None

# Маршруты
@app.route('/')
def index():
    global current_user
    if current_user:
        return redirect('/chat')
    return LOGIN_HTML

@app.route('/register', methods=['GET', 'POST'])
def register():
    global current_user, users, user_id_counter
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        display_name = request.form.get('display_name', '').strip()
        
        if not all([username, email, password, display_name]):
            return REGISTER_HTML + '<div class="error">Все поля обязательны для заполнения!</div>'
        
        # Проверяем, существует ли пользователь
        if username in users:
            return REGISTER_HTML + '<div class="error">Пользователь с таким именем уже существует!</div>'
        
        # Создаем пользователя
        user_id = user_id_counter
        user_id_counter += 1
        
        users[username] = {
            'id': user_id,
            'username': username,
            'email': email,
            'password': password,
            'display_name': display_name
        }
        
        return REGISTER_HTML + '<div class="success">Регистрация успешна! <a href="/login">Войти в систему</a></div>'
    
    return REGISTER_HTML

@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user, users
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return LOGIN_HTML + '<div class="error">Введите имя пользователя и пароль!</div>'
        
        if username in users and users[username]['password'] == password:
            current_user = users[username]
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
    global current_user, users
    
    if not current_user:
        return redirect('/login')
    
    users_list = ''
    for username, user in users.items():
        if user['id'] != current_user['id']:
            users_list += f'<div class="user-item" onclick="selectUser({user["id"]}, \'{user["display_name"]}\')">{user["display_name"]} (@{user["username"]})</div>'
    
    return CHAT_HTML.format(
        display_name=current_user['display_name'],
        users_list=users_list
    )

@app.route('/send_message', methods=['POST'])
def send_message():
    global current_user, messages, message_id_counter
    
    if not current_user:
        return {'error': 'Не авторизован'}, 401
    
    data = request.get_json()
    content = data.get('content', '').strip()
    receiver_id = data.get('receiver_id')
    
    if not content or not receiver_id:
        return {'error': 'Неверные данные'}, 400
    
    # Сохраняем сообщение
    message = {
        'id': message_id_counter,
        'sender_id': current_user['id'],
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': 'Сейчас'
    }
    message_id_counter += 1
    messages.append(message)
    
    return {'success': True}

@app.route('/api/messages/<int:user_id>')
def get_messages(user_id):
    global current_user, messages
    
    if not current_user:
        return {'error': 'Не авторизован'}, 401
    
    # Получаем сообщения между пользователями
    user_messages = []
    for msg in messages:
        if (msg['sender_id'] == current_user['id'] and msg['receiver_id'] == user_id) or \
           (msg['sender_id'] == user_id and msg['receiver_id'] == current_user['id']):
            user_messages.append({
                'id': msg['id'],
                'content': msg['content'],
                'timestamp': msg['timestamp'],
                'is_own': msg['sender_id'] == current_user['id']
            })
    
    return user_messages

# Главная функция
if __name__ == '__main__':
    try:
        print("🚀 Запуск Nexa Messenger (финальная версия)...")
        print(f"🌐 PORT: {os.environ.get('PORT', '8080')}")
        
        port = int(os.environ.get('PORT', 8080))
        print(f"🚪 Запуск на порту: {port}")
        
        print("🏭 Продакшен режим")
        app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
