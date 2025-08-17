#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Pure Python version without Flask
Maximum compatibility with any systems
"""

import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Simple in-memory data storage
users = {}
messages = []
user_id_counter = 1
message_id_counter = 1
current_user = None

# HTML templates
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Messenger - Login</title>
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
        <h2>Login</h2>
        
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        
        <p><a href="/register">Register</a> | <a href="/">Home</a></p>
    </div>
</body>
</html>
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Messenger - Registration</title>
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
                console.error('Error sending message:', error);
            });
        }
        
        // Auto-refresh every 3 seconds
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
            # Check if user is logged in
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
            # Check if user is logged in
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
            # Log out user
            global current_user
            current_user = None
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        elif path.startswith('/api/messages/'):
            # Check if user is authorized
            if not current_user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not authorized'}).encode('utf-8'))
            else:
                try:
                    user_id = int(path.split('/')[-1])
                    # Get messages between users
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
                    # Handle invalid user ID
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid user ID'}).encode('utf-8'))
        
        else:
            # Handle 404 error
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 - Page Not Found</h1>'.encode('utf-8'))
    
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
            
            # Check if all fields are filled
            if not all([username, email, password, display_name]):
                response_html = REGISTER_HTML + '<div class="error">All fields are required!</div>'
            elif username in users:
                # Check if user exists
                response_html = REGISTER_HTML + '<div class="error">User with this name already exists!</div>'
            else:
                # Create user
                user_id = user_id_counter
                user_id_counter += 1
                
                # Create user object
                users[username] = {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'password': password,
                    'display_name': display_name
                }
                
                response_html = REGISTER_HTML + '<div class="success">Registration successful! <a href="/login">Login</a></div>'
            
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
            
            # Check if username and password are provided
            if not username or not password:
                response_html = LOGIN_HTML + '<div class="error">Enter username and password!</div>'
            elif username in users and users[username]['password'] == password:
                # Login successful
                global current_user
                current_user = users[username]
                self.send_response(302)
                self.send_header('Location', '/chat')
                self.end_headers()
                return
            else:
                response_html = LOGIN_HTML + '<div class="error">Invalid username or password!</div>'
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))
        
        elif path == '/send_message':
            # Check if user is authorized
            if not current_user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not authorized'}).encode('utf-8'))
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                content = data.get('content', '').strip()
                receiver_id = data.get('receiver_id')
                
                # Check if message data is valid
                if not content or not receiver_id:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid data'}).encode('utf-8'))
                    return
                
                # Save message
                message = {
                    'id': message_id_counter,
                    'sender_id': current_user['id'],
                    'receiver_id': receiver_id,
                    'content': content,
                    'timestamp': 'Now'
                }
                message_id_counter += 1
                messages.append(message)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                
            except json.JSONDecodeError:
                # Handle JSON decode error
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
        
        else:
            # Handle 404 error
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 - Page Not Found</h1>'.encode('utf-8'))

def run_server():
    global users, messages, user_id_counter, message_id_counter
    
    # Create test user
    users['admin'] = {
        'id': user_id_counter,
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'display_name': 'Administrator'
    }
    user_id_counter += 1
    
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Nexa Messenger on port {port}...")
    print(f"Test user: admin / admin123")
    
    server = HTTPServer(('0.0.0.0', port), MessengerHandler)
    print(f"Server started on http://0.0.0.0:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.shutdown()

if __name__ == '__main__':
    run_server()
