#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Версия на чистом Python без Flask
Максимальная совместимость с любыми системами
"""

import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Простое хранилище данных в памяти
users = {}
messages = []
user_id_counter = 1
message_id_counter = 1
current_user = None

# HTML шаблоны
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

class MessengerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global current_user, users
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            if current_user:
                self.send_response(302)
                self.send_header('Location', '/chat')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.encode('utf-8'))
        
        elif path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode('utf-8'))
        
        elif path == '/register':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(REGISTER_HTML.encode('utf-8'))
        
        elif path == '/chat':
            if not current_user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
            else:
                users_list = ''
                for username, user in users.items():
                    if user['id'] != current_user['id']:
                        users_list += f'<div class="user-item" onclick="selectUser({user["id"]}, \'{user["display_name"]}\')">{user["display_name"]} (@{user["username"]})</div>'
                
                chat_html = CHAT_HTML.format(
                    display_name=current_user['display_name'],
                    users_list=users_list
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(chat_html.encode('utf-8'))
        
        elif path == '/logout':
            global current_user
            current_user = None
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        elif path.startswith('/api/messages/'):
            if not current_user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Не авторизован'}).encode('utf-8'))
            else:
                try:
                    user_id = int(path.split('/')[-1])
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
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(user_messages).encode('utf-8'))
                except:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Неверный ID пользователя'}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Страница не найдена</h1>')
    
    def do_POST(self):
        global current_user, users, user_id_counter, messages, message_id_counter
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)
            
            username = form_data.get('username', [''])[0].strip()
            email = form_data.get('email', [''])[0].strip()
            password = form_data.get('password', [''])[0].strip()
            display_name = form_data.get('display_name', [''])[0].strip()
            
            if not all([username, email, password, display_name]):
                response_html = REGISTER_HTML + '<div class="error">Все поля обязательны для заполнения!</div>'
            elif username in users:
                response_html = REGISTER_HTML + '<div class="error">Пользователь с таким именем уже существует!</div>'
            else:
                user_id = user_id_counter
                user_id_counter += 1
                
                users[username] = {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'password': password,
                    'display_name': display_name
                }
                
                response_html = REGISTER_HTML + '<div class="success">Регистрация успешна! <a href="/login">Войти в систему</a></div>'
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))
        
        elif path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)
            
            username = form_data.get('username', [''])[0].strip()
            password = form_data.get('password', [''])[0].strip()
            
            if not username or not password:
                response_html = LOGIN_HTML + '<div class="error">Введите имя пользователя и пароль!</div>'
            elif username in users and users[username]['password'] == password:
                global current_user
                current_user = users[username]
                self.send_response(302)
                self.send_header('Location', '/chat')
                self.end_headers()
                return
            else:
                response_html = LOGIN_HTML + '<div class="error">Неверное имя пользователя или пароль!</div>'
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))
        
        elif path == '/send_message':
            if not current_user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Не авторизован'}).encode('utf-8'))
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                content = data.get('content', '').strip()
                receiver_id = data.get('receiver_id')
                
                if not content or not receiver_id:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Неверные данные'}).encode('utf-8'))
                    return
                
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
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Неверный JSON'}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Страница не найдена</h1>')

def run_server():
    global users, messages, user_id_counter, message_id_counter
    
    # Создаем тестового пользователя
    users['admin'] = {
        'id': user_id_counter,
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'display_name': 'Администратор'
    }
    user_id_counter += 1
    
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Запуск Nexa Messenger на порту {port}...")
    print(f"📊 Тестовый пользователь: admin / admin123")
    
    server = HTTPServer(('0.0.0.0', port), MessengerHandler)
    print(f"✅ Сервер запущен на http://0.0.0.0:{port}")
    print("🔄 Нажмите Ctrl+C для остановки")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        server.shutdown()

if __name__ == '__main__':
    run_server()
