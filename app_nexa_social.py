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
notifications = []
groups = []
user_id_counter = 1
post_id_counter = 1
message_id_counter = 1
friendship_id_counter = 1
notification_id_counter = 1
group_id_counter = 1
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
            
            # Get user's posts and friends
            user_posts = [p for p in posts if p['user_id'] == current_user['id']]
            user_friends = [f for f in friendships if f['user1_id'] == current_user['id'] or f['user2_id'] == current_user['id']]
            
            # Generate posts HTML
            posts_html = ''
            for post in user_posts:
                posts_html += f'''
                <div class="post">
                    <div class="post-header">
                        <div class="post-avatar">{current_user['display_name'][0].upper()}</div>
                        <div class="post-info">
                            <h4>{current_user['display_name']}</h4>
                            <small>{post['timestamp']}</small>
                        </div>
                    </div>
                    <div class="post-content">{post['content']}</div>
                    <div class="post-actions">
                        <a href="#" class="post-action" onclick="likePost({post['id']})">👍 Like ({post.get('likes', 0)})</a>
                        <a href="#" class="post-action" onclick="commentPost({post['id']})">💬 Comment</a>
                        <a href="#" class="post-action" onclick="sharePost({post['id']})">📤 Share</a>
                    </div>
                </div>
                '''
            
            # Generate friends HTML
            friends_html = ''
            for friendship in user_friends:
                friend_id = friendship['user2_id'] if friendship['user1_id'] == current_user['id'] else friendship['user1_id']
                friend = users.get(friend_id)
                if friend:
                    friends_html += f'''
                    <div class="friend-item">
                        <div class="friend-avatar">{friend['display_name'][0].upper()}</div>
                        <div class="friend-info">
                            <h4>{friend['display_name']}</h4>
                            <small>@{friend['username']}</small>
                        </div>
                    </div>
                    '''
            
            home_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nexa Social Network - Home</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: #f0f2f5;
                        color: #333;
                    }}
                    .header {{
                        background: white;
                        border-bottom: 1px solid #e1e5e9;
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }}
                    .header-content {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 0 20px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        height: 60px;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #667eea;
                    }}
                    .nav {{
                        display: flex;
                        gap: 30px;
                    }}
                    .nav a {{
                        color: #666;
                        text-decoration: none;
                        font-weight: 500;
                        transition: color 0.3s;
                    }}
                    .nav a:hover, .nav a.active {{
                        color: #667eea;
                    }}
                    .user-menu {{
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }}
                    .user-avatar {{
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: #667eea;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 18px;
                    }}
                    .logout-btn {{
                        color: #666;
                        text-decoration: none;
                        font-weight: 500;
                        transition: color 0.3s;
                    }}
                    .logout-btn:hover {{
                        color: #c33;
                    }}
                    
                    .main-content {{
                        max-width: 1200px;
                        margin: 20px auto;
                        padding: 0 20px;
                        display: grid;
                        grid-template-columns: 1fr 2fr 1fr;
                        gap: 20px;
                    }}
                    
                    .sidebar {{
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        height: fit-content;
                    }}
                    .sidebar h3 {{
                        margin-bottom: 20px;
                        color: #333;
                        font-size: 18px;
                    }}
                    
                    .feed {{
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    
                    .create-post {{
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .create-post textarea {{
                        width: 100%;
                        padding: 15px;
                        border: 2px solid #e1e5e9;
                        border-radius: 10px;
                        font-size: 16px;
                        resize: vertical;
                        min-height: 100px;
                        font-family: inherit;
                        margin-bottom: 15px;
                    }}
                    .create-post textarea:focus {{
                        outline: none;
                        border-color: #667eea;
                    }}
                    .post-btn {{
                        background: #667eea;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.3s;
                    }}
                    .post-btn:hover {{
                        background: #5a6fd8;
                    }}
                    
                    .post {{
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .post-header {{
                        display: flex;
                        align-items: center;
                        gap: 15px;
                        margin-bottom: 15px;
                    }}
                    .post-avatar {{
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        background: #667eea;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 20px;
                    }}
                    .post-info h4 {{
                        margin: 0;
                        color: #333;
                        font-size: 16px;
                    }}
                    .post-info small {{
                        color: #666;
                        font-size: 14px;
                    }}
                    .post-content {{
                        color: #333;
                        line-height: 1.6;
                        margin-bottom: 20px;
                        font-size: 16px;
                    }}
                    .post-actions {{
                        display: flex;
                        gap: 20px;
                        border-top: 1px solid #eee;
                        padding-top: 15px;
                    }}
                    .post-action {{
                        color: #666;
                        text-decoration: none;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        font-weight: 500;
                        transition: color 0.3s;
                        cursor: pointer;
                    }}
                    .post-action:hover {{
                        color: #667eea;
                    }}
                    
                    .friend-item {{
                        display: flex;
                        align-items: center;
                        gap: 15px;
                        padding: 15px 0;
                        border-bottom: 1px solid #eee;
                    }}
                    .friend-item:last-child {{
                        border-bottom: none;
                    }}
                    .friend-avatar {{
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: #667eea;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                    }}
                    .friend-info h4 {{
                        margin: 0;
                        color: #333;
                        font-size: 16px;
                    }}
                    .friend-info small {{
                        color: #666;
                        font-size: 14px;
                    }}
                    
                    @media (max-width: 768px) {{
                        .main-content {{
                            grid-template-columns: 1fr;
                        }}
                        .nav {{
                            display: none;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="header-content">
                        <div class="logo">💬 Nexa</div>
                        <div class="nav">
                            <a href="/" class="active">Home</a>
                            <a href="/profile">Profile</a>
                            <a href="/friends">Friends</a>
                            <a href="/messages">Messages</a>
                        </div>
                        <div class="user-menu">
                            <div class="user-avatar">{current_user['display_name'][0].upper()}</div>
                            <span>{current_user['display_name']}</span>
                            <a href="/logout" class="logout-btn">Logout</a>
                        </div>
                    </div>
                </div>
                
                <div class="main-content">
                    <div class="sidebar">
                        <h3>Friends</h3>
                        {friends_html}
                    </div>
                    
                    <div class="feed">
                        <div class="create-post">
                            <h3>Create Post</h3>
                            <textarea id="postContent" placeholder="What's on your mind?"></textarea>
                            <button class="post-btn" onclick="createPost()">Post</button>
                        </div>
                        
                        <div class="posts">
                            {posts_html}
                        </div>
                    </div>
                    
                    <div class="sidebar">
                        <h3>Trending</h3>
                        <p style="color: #666; font-size: 14px;">Popular topics and hashtags will appear here</p>
                    </div>
                </div>
                
                <script>
                    function createPost() {{
                        const content = document.getElementById('postContent').value;
                        if (!content.trim()) return;
                        
                        fetch('/api/create_post', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{ content: content }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                location.reload();
                            }}
                        }});
                    }}
                    
                    function likePost(postId) {{
                        fetch('/api/like_post', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{ post_id: postId }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                location.reload();
                            }}
                        }});
                    }}
                </script>
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
        
        elif path == '/profile':
            if not current_user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            # Get user's posts
            user_posts = [p for p in posts if p['user_id'] == current_user['id']]
            
            # Generate posts HTML
            posts_html = ''
            for post in user_posts:
                posts_html += f'''
                <div class="post">
                    <div class="post-header">
                        <div class="post-avatar">{current_user['display_name'][0].upper()}</div>
                        <div class="post-info">
                            <h4>{current_user['display_name']}</h4>
                            <small>{post['timestamp']}</small>
                        </div>
                    </div>
                    <div class="post-content">{post['content']}</div>
                    <div class="post-actions">
                        <a href="#" class="post-action" onclick="likePost({post['id']})">👍 Like ({post.get('likes', 0)})</a>
                        <a href="#" class="post-action" onclick="commentPost({post['id']})">💬 Comment</a>
                        <a href="#" class="post-action" onclick="sharePost({post['id']})">📤 Share</a>
                    </div>
                </div>
                '''
            
            profile_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nexa Social Network - Profile</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: #f0f2f5;
                        color: #333;
                    }}
                    .header {{
                        background: white;
                        border-bottom: 1px solid #e1e5e9;
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }}
                    .header-content {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 0 20px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        height: 60px;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #667eea;
                    }}
                    .nav {{
                        display: flex;
                        gap: 30px;
                    }}
                    .nav a {{
                        color: #666;
                        text-decoration: none;
                        font-weight: 500;
                        transition: color 0.3s;
                    }}
                    .nav a:hover, .nav a.active {{
                        color: #667eea;
                    }}
                    .user-menu {{
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }}
                    .user-avatar {{
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: #667eea;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 18px;
                    }}
                    .logout-btn {{
                        color: #666;
                        text-decoration: none;
                        font-weight: 500;
                        transition: color 0.3s;
                    }}
                    .logout-btn:hover {{
                        color: #c33;
                    }}
                    
                    .profile-header {{
                        background: white;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .cover-photo {{
                        height: 200px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 0 0 20px 20px;
                    }}
                    .profile-info {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 0 20px;
                        display: flex;
                        align-items: flex-end;
                        gap: 30px;
                        margin-top: -60px;
                        margin-bottom: 30px;
                    }}
                    .profile-avatar {{
                        width: 120px;
                        height: 120px;
                        border-radius: 50%;
                        background: #667eea;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 48px;
                        border: 5px solid white;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    }}
                    .profile-details h1 {{
                        margin: 0;
                        color: #333;
                        font-size: 32px;
                        margin-bottom: 10px;
                    }}
                    .profile-details p {{
                        margin: 0;
                        color: #666;
                        font-size: 18px;
                        margin-bottom: 5px;
                    }}
                    .profile-actions {{
                        margin-left: auto;
                    }}
                    .edit-btn {{
                        background: #667eea;
                        color: white;
                        text-decoration: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-weight: 600;
                        transition: background 0.3s;
                    }}
                    .edit-btn:hover {{
                        background: #5a6fd8;
                    }}
                    
                    .profile-content {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 0 20px;
                        display: grid;
                        grid-template-columns: 1fr 2fr;
                        gap: 20px;
                    }}
                    
                    .profile-sidebar {{
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        height: fit-content;
                    }}
                    .profile-sidebar h3 {{
                        margin-bottom: 20px;
                        color: #333;
                        font-size: 18px;
                    }}
                    .profile-sidebar-item {{
                        padding: 15px 0;
                        border-bottom: 1px solid #eee;
                    }}
                    .profile-sidebar-item:last-child {{
                        border-bottom: none;
                    }}
                    .profile-sidebar-item strong {{
                        color: #333;
                    }}
                    
                    .profile-posts {{
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .profile-posts h3 {{
                        margin-bottom: 20px;
                        color: #333;
                        font-size: 18px;
                    }}
                    
                    .post {{
                        border: 1px solid #e1e5e9;
                        border-radius: 15px;
                        padding: 20px;
                        margin-bottom: 20px;
                    }}
                    .post-header {{
                        display: flex;
                        align-items: center;
                        gap: 15px;
                        margin-bottom: 15px;
                    }}
                    .post-avatar {{
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        background: #667eea;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 20px;
                    }}
                    .post-info h4 {{
                        margin: 0;
                        color: #333;
                        font-size: 16px;
                    }}
                    .post-info small {{
                        color: #666;
                        font-size: 14px;
                    }}
                    .post-content {{
                        color: #333;
                        line-height: 1.6;
                        margin-bottom: 15px;
                        font-size: 16px;
                    }}
                    .post-actions {{
                        display: flex;
                        gap: 20px;
                        border-top: 1px solid #eee;
                        padding-top: 15px;
                    }}
                    .post-action {{
                        color: #666;
                        text-decoration: none;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        font-weight: 500;
                        transition: color 0.3s;
                        cursor: pointer;
                    }}
                    .post-action:hover {{
                        color: #667eea;
                    }}
                    
                    @media (max-width: 768px) {{
                        .profile-content {{
                            grid-template-columns: 1fr;
                        }}
                        .profile-info {{
                            flex-direction: column;
                            align-items: center;
                            text-align: center;
                        }}
                        .profile-actions {{
                            margin-left: 0;
                            margin-top: 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="header-content">
                        <div class="logo">💬 Nexa</div>
                        <div class="nav">
                            <a href="/">Home</a>
                            <a href="/profile" class="active">Profile</a>
                            <a href="/friends">Friends</a>
                            <a href="/messages">Messages</a>
                        </div>
                        <div class="user-menu">
                            <div class="user-avatar">{current_user['display_name'][0].upper()}</div>
                            <span>{current_user['display_name']}</span>
                            <a href="/logout" class="logout-btn">Logout</a>
                        </div>
                    </div>
                </div>
                
                <div class="profile-header">
                    <div class="cover-photo"></div>
                    <div class="profile-info">
                        <div class="profile-avatar">{current_user['display_name'][0].upper()}</div>
                        <div class="profile-details">
                            <h1>{current_user['display_name']}</h1>
                            <p>@{current_user['username']}</p>
                            <p>Member since {current_user['created_at']}</p>
                        </div>
                        <div class="profile-actions">
                            <a href="/edit_profile" class="edit-btn">Edit Profile</a>
                        </div>
                    </div>
                </div>
                
                <div class="profile-content">
                    <div class="profile-sidebar">
                        <h3>Profile Info</h3>
                        <div class="profile-sidebar-item">
                            <strong>Username:</strong> @{current_user['username']}
                        </div>
                        <div class="profile-sidebar-item">
                            <strong>Email:</strong> {current_user['email']}
                        </div>
                        <div class="profile-sidebar-item">
                            <strong>Member since:</strong> {current_user['created_at']}
                        </div>
                        <div class="profile-sidebar-item">
                            <strong>Posts:</strong> {len(user_posts)}
                        </div>
                    </div>
                    
                    <div class="profile-posts">
                        <h3>My Posts</h3>
                        {posts_html}
                    </div>
                </div>
            </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(profile_html.encode('utf-8'))
        
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
        
        elif path == '/api/create_post':
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
                
                if not content:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Post content is required'}).encode('utf-8'))
                    return
                
                # Create post
                post = {
                    'id': post_id_counter,
                    'user_id': current_user['id'],
                    'content': content,
                    'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                    'likes': 0,
                    'comments': [],
                    'shares': 0
                }
                
                posts.append(post)
                post_id_counter += 1
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'post_id': post['id']}).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
        
        elif path == '/api/like_post':
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
                post_id = data.get('post_id')
                
                # Find and like post
                for post in posts:
                    if post['id'] == post_id:
                        post['likes'] = post.get('likes', 0) + 1
                        break
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 - Page Not Found</h1>'.encode('utf-8'))

def run_server():
    global users, posts, user_id_counter, post_id_counter
    
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
    
    # Create test post
    posts.append({
        'id': post_id_counter,
        'user_id': 1,
        'content': 'Welcome to Nexa Social Network! This is your first post. Share your thoughts with the world! 🌟',
        'timestamp': 'December 15, 2024 at 12:00 PM',
        'likes': 5,
        'comments': [],
        'shares': 2
    })
    post_id_counter += 1
    
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
