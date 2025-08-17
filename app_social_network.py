#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Social Network - Full social network like VKontakte
With profiles, posts, friends, news feed and messenger
"""

import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Simple in-memory data storage
users = {}
posts = []
messages = []
friendships = []
user_id_counter = 1
post_id_counter = 1
message_id_counter = 1
friendship_id_counter = 1
current_user = None

# HTML templates
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Social Network - Login</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); width: 400px; }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        input:focus { border-color: #667eea; outline: none; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 20px; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .error { color: #e74c3c; margin: 10px 0; text-align: center; }
        .success { color: #27ae60; margin: 10px 0; text-align: center; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
        .links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 Nexa Social Network</h1>
        <h2 style="text-align: center; color: #666;">Login to your account</h2>
        
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        
        <div class="links">
            <a href="/register">Register</a> | <a href="/">Home</a>
        </div>
    </div>
</body>
</html>
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Social Network - Registration</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); width: 400px; }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        input:focus { border-color: #667eea; outline: none; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 20px; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .error { color: #e74c3c; margin: 10px 0; text-align: center; }
        .success { color: #27ae60; margin: 10px 0; text-align: center; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
        .links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 Nexa Social Network</h1>
        <h2 style="text-align: center; color: #666;">Create your account</h2>
        
        <form method="POST" action="/register">
            <input type="text" name="username" placeholder="Username" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="text" name="display_name" placeholder="Full Name" required>
            <input type="text" name="bio" placeholder="Bio (optional)">
            <button type="submit">Create Account</button>
        </form>
        
        <div class="links">
            <a href="/login">Login</a> | <a href="/">Home</a>
        </div>
    </div>
</body>
</html>
'''

MAIN_PAGE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Social Network - Home</title>
    <style>
        body { font-family: Arial; background: #f0f2f5; margin: 0; padding: 0; }
        .header { background: white; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #666; text-decoration: none; padding: 10px 15px; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover { background: #f0f2f5; }
        .nav a.active { background: #667eea; color: white; }
        .user-menu { display: flex; align-items: center; gap: 15px; }
        .user-avatar { width: 40px; height: 40px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .logout-btn { background: #e74c3c; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; }
        
        .main-content { max-width: 1200px; margin: 20px auto; display: grid; grid-template-columns: 250px 1fr 300px; gap: 20px; padding: 0 20px; }
        
        .sidebar { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .sidebar h3 { margin-top: 0; color: #333; }
        .sidebar-item { padding: 10px 0; border-bottom: 1px solid #eee; cursor: pointer; }
        .sidebar-item:hover { background: #f8f9fa; border-radius: 6px; padding-left: 10px; }
        
        .feed { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .post-form { margin-bottom: 20px; }
        .post-input { width: 100%; padding: 15px; border: 2px solid #e1e5e9; border-radius: 8px; resize: vertical; min-height: 80px; font-family: inherit; }
        .post-input:focus { border-color: #667eea; outline: none; }
        .post-btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; float: right; margin-top: 10px; }
        
        .post { border: 1px solid #e1e5e9; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .post-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
        .post-avatar { width: 50px; height: 50px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .post-info h4 { margin: 0; color: #333; }
        .post-info small { color: #666; }
        .post-content { color: #333; line-height: 1.6; margin-bottom: 15px; }
        .post-actions { display: flex; gap: 20px; border-top: 1px solid #eee; padding-top: 15px; }
        .post-action { color: #666; text-decoration: none; display: flex; align-items: center; gap: 5px; }
        .post-action:hover { color: #667eea; }
        
        .right-sidebar { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .friends-list h3 { margin-top: 0; color: #333; }
        .friend-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #eee; }
        .friend-avatar { width: 40px; height: 40px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .friend-info h4 { margin: 0; font-size: 14px; color: #333; }
        .friend-info small { color: #666; font-size: 12px; }
        
        .clearfix::after { content: ""; display: table; clear: both; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">💬 Nexa Social Network</div>
            <div class="nav">
                <a href="/" class="active">Home</a>
                <a href="/profile">Profile</a>
                <a href="/friends">Friends</a>
                <a href="/messages">Messages</a>
            </div>
            <div class="user-menu">
                <div class="user-avatar">{user_initial}</div>
                <span>{user_name}</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="sidebar">
            <h3>Menu</h3>
            <div class="sidebar-item" onclick="location.href='/'">🏠 Home</div>
            <div class="sidebar-item" onclick="location.href='/profile'">👤 My Profile</div>
            <div class="sidebar-item" onclick="location.href='/friends'">👥 Friends</div>
            <div class="sidebar-item" onclick="location.href='/messages'">💬 Messages</div>
            <div class="sidebar-item" onclick="location.href='/photos'">📷 Photos</div>
            <div class="sidebar-item" onclick="location.href='/videos'">🎥 Videos</div>
            <div class="sidebar-item" onclick="location.href='/groups'">👥 Groups</div>
        </div>
        
        <div class="feed">
            <div class="post-form">
                <textarea class="post-input" id="post-content" placeholder="What's on your mind?"></textarea>
                <button class="post-btn" onclick="createPost()">Post</button>
                <div class="clearfix"></div>
            </div>
            
            <div id="posts-container">
                {posts_html}
            </div>
        </div>
        
        <div class="right-sidebar">
            <div class="friends-list">
                <h3>Friends Online</h3>
                {friends_html}
            </div>
        </div>
    </div>
    
    <script>
        function createPost() {
            const content = document.getElementById('post-content').value;
            if (!content.trim()) return;
            
            fetch('/api/create_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            }).then(() => {
                document.getElementById('post-content').value = '';
                location.reload();
            }).catch(error => {
                console.error('Error creating post:', error);
            });
        }
        
        function likePost(postId) {
            fetch('/api/like_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({post_id: postId})
            }).then(() => {
                location.reload();
            }).catch(error => {
                console.error('Error liking post:', error);
            });
        }
        
        function commentPost(postId) {
            const comment = prompt('Enter your comment:');
            if (!comment) return;
            
            fetch('/api/comment_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({post_id: postId, comment: comment})
            }).then(() => {
                location.reload();
            }).catch(error => {
                console.error('Error commenting post:', error);
            });
        }
        
        function sharePost(postId) {
            fetch('/api/share_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({post_id: postId})
            }).then(() => {
                location.reload();
            }).catch(error => {
                console.error('Error sharing post:', error);
            });
        }
    </script>
</body>
</html>
'''

PROFILE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Nexa Social Network - Profile</title>
    <style>
        body { font-family: Arial; background: #f0f2f5; margin: 0; padding: 0; }
        .header { background: white; padding: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #666; text-decoration: none; padding: 10px 15px; border-radius: 8px; transition: background 0.3s; }
        .nav a:hover { background: #f0f2f5; }
        .nav a.active { background: #667eea; color: white; }
        .user-menu { display: flex; align-items: center; gap: 15px; }
        .user-avatar { width: 40px; height: 40px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .logout-btn { background: #e74c3c; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; }
        
        .profile-header { background: white; margin: 20px auto; max-width: 1200px; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .cover-photo { height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .profile-info { padding: 20px; display: flex; align-items: flex-end; gap: 20px; }
        .profile-avatar { width: 120px; height: 120px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 48px; border: 5px solid white; margin-top: -60px; }
        .profile-details h1 { margin: 0; color: #333; }
        .profile-details p { color: #666; margin: 5px 0; }
        .profile-actions { margin-left: auto; }
        .edit-btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; }
        
        .profile-content { max-width: 1200px; margin: 20px auto; display: grid; grid-template-columns: 300px 1fr; gap: 20px; padding: 0 20px; }
        
        .profile-sidebar { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .profile-sidebar h3 { margin-top: 0; color: #333; }
        .profile-sidebar-item { padding: 10px 0; border-bottom: 1px solid #eee; }
        .profile-sidebar-item:last-child { border-bottom: none; }
        
        .profile-posts { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .profile-posts h3 { margin-top: 0; color: #333; }
        
        .post { border: 1px solid #e1e5e9; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .post-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
        .post-avatar { width: 50px; height: 50px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .post-info h4 { margin: 0; color: #333; }
        .post-info small { color: #666; }
        .post-content { color: #333; line-height: 1.6; margin-bottom: 15px; }
        .post-actions { display: flex; gap: 20px; border-top: 1px solid #eee; padding-top: 15px; }
        .post-action { color: #666; text-decoration: none; display: flex; align-items: center; gap: 5px; }
        .post-action:hover { color: #667eea; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">💬 Nexa Social Network</div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/profile" class="active">Profile</a>
                <a href="/friends">Friends</a>
                <a href="/messages">Messages</a>
            </div>
            <div class="user-menu">
                <div class="user-avatar">{user_initial}</div>
                <span>{user_name}</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="profile-header">
        <div class="cover-photo"></div>
        <div class="profile-info">
            <div class="profile-avatar">{user_initial}</div>
            <div class="profile-details">
                <h1>{user_name}</h1>
                <p>@{username}</p>
                <p>{bio}</p>
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
                <strong>Username:</strong> @{username}
            </div>
            <div class="profile-sidebar-item">
                <strong>Email:</strong> {email}
            </div>
            <div class="profile-sidebar-item">
                <strong>Bio:</strong> {bio}
            </div>
            <div class="profile-sidebar-item">
                <strong>Member since:</strong> {created_at}
            </div>
            <div class="profile-sidebar-item">
                <strong>Posts:</strong> {posts_count}
            </div>
            <div class="profile-sidebar-item">
                <strong>Friends:</strong> {friends_count}
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

class SocialNetworkHandler(BaseHTTPRequestHandler):
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
            
            main_html = MAIN_PAGE_HTML.format(
                user_initial=current_user['display_name'][0].upper(),
                user_name=current_user['display_name'],
                posts_html=posts_html,
                friends_html=friends_html
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(main_html.encode('utf-8'))
        
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
        
        elif path == '/profile':
            if not current_user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            # Get user's posts
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
            
            profile_html = PROFILE_HTML.format(
                user_initial=current_user['display_name'][0].upper(),
                user_name=current_user['display_name'],
                username=current_user['username'],
                email=current_user['email'],
                bio=current_user.get('bio', 'No bio yet'),
                created_at=current_user.get('created_at', 'Unknown'),
                posts_count=len(user_posts),
                friends_count=len(user_friends),
                posts_html=posts_html
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(profile_html.encode('utf-8'))
        
        elif path == '/logout':
            current_user = None
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        elif path.startswith('/api/'):
            # Handle API requests
            if not current_user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not authorized'}).encode('utf-8'))
                return
            
            if path == '/api/posts':
                user_posts = [p for p in posts if p['user_id'] == current_user['id']]
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(user_posts).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'API endpoint not found'}).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>404 - Page Not Found</h1>'.encode('utf-8'))
    
    def do_POST(self):
        global current_user, users, posts, post_id_counter, friendships, friendship_id_counter
        
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
            bio = form_data.get('bio', [''])[0].strip()
            
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
                    'display_name': display_name,
                    'bio': bio,
                    'created_at': datetime.now().strftime('%B %Y')
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
                current_user = users[username]
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return
            else:
                response_html = LOGIN_HTML + '<div class="error">Invalid username or password!</div>'
            
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
                
                # Check if post content is valid
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
                post_id_counter += 1
                posts.append(post)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'post_id': post['id']}).encode('utf-8'))
                
            except json.JSONDecodeError:
                # Handle JSON decode error
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
        
        elif path == '/api/comment_post':
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
                comment = data.get('comment', '').strip()
                
                if not comment:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Comment is required'}).encode('utf-8'))
                    return
                
                # Find and comment post
                for post in posts:
                    if post['id'] == post_id:
                        if 'comments' not in post:
                            post['comments'] = []
                        post['comments'].append({
                            'user_id': current_user['id'],
                            'username': current_user['username'],
                            'display_name': current_user['display_name'],
                            'comment': comment,
                            'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
                        })
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
        
        elif path == '/api/share_post':
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
                
                # Find and share post
                for post in posts:
                    if post['id'] == post_id:
                        post['shares'] = post.get('shares', 0) + 1
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
    global users, posts, friendships, user_id_counter, post_id_counter, friendship_id_counter
    
    # Create test user
    users['admin'] = {
        'id': user_id_counter,
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'display_name': 'Administrator',
        'bio': 'Welcome to Nexa Social Network!',
        'created_at': 'December 2024'
    }
    user_id_counter += 1
    
    # Create test post
    posts.append({
        'id': post_id_counter,
        'user_id': 1,
        'content': 'Welcome to Nexa Social Network! This is your first post. Share your thoughts, connect with friends, and enjoy the social experience! 🎉',
        'timestamp': 'December 15, 2024 at 2:30 PM',
        'likes': 5,
        'comments': [],
        'shares': 2
    })
    post_id_counter += 1
    
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Nexa Social Network on port {port}...")
    print(f"Test user: admin / admin123")
    
    server = HTTPServer(('0.0.0.0', port), SocialNetworkHandler)
    print(f"Server started on http://0.0.0.0:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.shutdown()

if __name__ == '__main__':
    run_server()
