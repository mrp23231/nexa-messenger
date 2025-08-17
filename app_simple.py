#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nexa Messenger - Упрощенная версия для продакшена
Без WebSocket для максимальной совместимости
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3

# Создание Flask приложения
app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nexa-messenger-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nexa_messenger.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(120), default='default.jpg')
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(500))
    ban_until = db.Column(db.DateTime)
    ban_count = db.Column(db.Integer, default=0)
    warnings_count = db.Column(db.Integer, default=0)
    last_warning = db.Column(db.DateTime)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('message.id'))

# Загрузчик пользователей
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Маршруты
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        display_name = request.form['display_name']
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует!')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            display_name=display_name
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите в систему.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_banned:
                flash('Ваш аккаунт заблокирован!')
                return render_template('login.html')
            
            login_user(user)
            user.is_online = True
            user.last_seen = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('chat'))
        else:
            flash('Неверное имя пользователя или пароль!')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    current_user.is_online = False
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))

@app.route('/chat')
@login_required
def chat():
    users = User.query.filter(User.id != current_user.id).all()
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | 
        (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.desc()).limit(50).all()
    
    return render_template('chat_simple.html', users=users, messages=messages)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ запрещен!')
        return redirect(url_for('chat'))
    
    users = User.query.all()
    return render_template('admin_simple.html', users=users)

# API для сообщений
@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    content = data.get('content', '').strip()
    receiver_id = data.get('receiver_id')
    
    if not content:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%H:%M'),
        'sender_name': current_user.display_name
    })

@app.route('/api/messages')
@login_required
def get_messages():
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | 
        (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.desc()).limit(100).all()
    
    return jsonify([{
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'sender_name': User.query.get(msg.sender_id).display_name,
        'is_own': msg.sender_id == current_user.id
    } for msg in messages])

# Главная функция
if __name__ == '__main__':
    try:
        print("🚀 Запуск Nexa Messenger (упрощенная версия)...")
        print(f"📊 FLASK_ENV: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"🔧 FLASK_DEBUG: {os.environ.get('FLASK_DEBUG', '1')}")
        print(f"🌐 PORT: {os.environ.get('PORT', '8080')}")
        
        with app.app_context():
            print("📁 Создание базы данных...")
            db.create_all()
            print("✅ База данных готова")
        
        port = int(os.environ.get('PORT', 8080))
        print(f"🚪 Запуск на порту: {port}")
        
        if os.environ.get('FLASK_ENV') == 'production':
            print("🏭 Продакшен режим")
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            print("🔬 Режим разработки")
            app.run(host='0.0.0.0', port=port, debug=True)
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
