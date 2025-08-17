#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Social Network - Full social network like VKontakte
Complete redesign with modern UI and full social features
"""

import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Global data storage
users = {}
posts = []
messages = []
friendships = []
user_id_counter = 1
post_id_counter = 1
message_id_counter = 1
friendship_id_counter = 1
current_user = None

# HTML Templates
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexa Social Network - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .login-btn {
            width: 100%;
            padding: 15px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .login-btn:hover {
            background: #5a6fd8;
        }
        .register-link {
            margin-top: 20px;
            color: #666;
        }
        .register-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #fcc;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">💬 Nexa</div>
        <h2>Welcome Back</h2>
        <p style="color: #666; margin-bottom: 30px;">Sign in to your account</p>
        
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        
        <div class="register-link">
            Don't have an account? <a href="/register">Sign Up</a>
        </div>
    </div>
</body>
</html>
'''

class NexaSocialHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global current_user, users, posts, friendships
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            if not current_user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            # Simple home page for now
            home_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nexa Social Network - Home</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background: #667eea; color: white; padding: 20px; border-radius: 10px; }}
                    .content {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>💬 Welcome to Nexa Social Network!</h1>
                    <p>Hello, {current_user['display_name']}!</p>
                </div>
                <div class="content">
                    <h2>Your Social Network is Ready!</h2>
                    <p>This is a completely new social network built from scratch.</p>
                    <p><a href="/logout">Logout</a></p>
                </div>
            </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(home_html.encode('utf-8'))
        
        elif path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode('utf-8'))
        
        elif path == '/register':
            # Simple register page for now
            register_html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nexa Social Network - Register</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .form-group { margin: 20px 0; }
                    input { padding: 10px; margin: 5px; width: 300px; }
                    button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>💬 Nexa Social Network - Register</h1>
                <form method="POST" action="/register">
                    <div class="form-group">
                        <input type="text" name="username" placeholder="Username" required>
                    </div>
                    <div class="form-group">
                        <input type="email" name="email" placeholder="Email" required>
                    </div>
                    <div class="form-group">
                        <input type="password" name="password" placeholder="Password" required>
                    </div>
                    <div class="form-group">
                        <input type="text" name="display_name" placeholder="Full Name" required>
                    </div>
                    <button type="submit">Create Account</button>
                </form>
                <p><a href="/login">Already have an account? Login</a></p>
            </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(register_html.encode('utf-8'))
        
        elif path == '/logout':
            current_user = None
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 - Page Not Found</h1>'.encode('utf-8'))
    
    def do_POST(self):
        global current_user, users, user_id_counter
        
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
                response_html = '<h1>Error: All fields are required!</h1><a href="/register">Go back</a>'
            elif username in users:
                response_html = '<h1>Error: User already exists!</h1><a href="/register">Go back</a>'
            else:
                user_id = user_id_counter
                user_id_counter += 1
                
                users[username] = {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'password': password,
                    'display_name': display_name,
                    'created_at': datetime.now().strftime('%B %Y')
                }
                
                response_html = '<h1>Registration successful!</h1><a href="/login">Login now</a>'
            
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
                response_html = '<h1>Error: Enter username and password!</h1><a href="/login">Go back</a>'
            elif username in users and users[username]['password'] == password:
                current_user = users[username]
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return
            else:
                response_html = '<h1>Error: Invalid username or password!</h1><a href="/login">Go back</a>'
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 - Page Not Found</h1>'.encode('utf-8'))

def run_server():
    global users, user_id_counter
    
    # Create test user
    users['admin'] = {
        'id': user_id_counter,
        'username': 'admin',
        'email': 'admin@nexa.com',
        'password': 'admin123',
        'display_name': 'Admin User',
        'created_at': 'December 2024'
    }
    user_id_counter += 1
    
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Nexa Social Network on port {port}...")
    print(f"📊 Test user: admin / admin123")
    
    server = HTTPServer(('0.0.0.0', port), NexaSocialHandler)
    print(f"✅ Server started on http://0.0.0.0:{port}")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.shutdown()

if __name__ == '__main__':
    run_server()
