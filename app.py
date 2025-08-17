from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import re
from cryptography.fernet import Fernet
import json
import uuid
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexa-messenger-secret-key-2024'
# Конфигурация для продакшена
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///nexa_messenger.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройки безопасности
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nexa-messenger-secret-key-2024')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Настройки для загрузки файлов
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB максимум
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Юзернейм - неизменяемый
    display_name = db.Column(db.String(100), nullable=False)  # Отображаемое имя - можно менять
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200), default='default.jpg')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


    status = db.Column(db.String(50), default='online')  # online, away, busy, dnd
    custom_status = db.Column(db.String(100), default='')  # Кастомный статус
    color_accent = db.Column(db.String(7), default='#00d4ff')  # Цветовой акцент
    is_admin = db.Column(db.Boolean, default=False)  # Права администратора
    is_banned = db.Column(db.Boolean, default=False)  # Заблокирован ли пользователь
    ban_reason = db.Column(db.Text, default='')  # Причина блокировки
    ban_until = db.Column(db.DateTime)  # До когда заблокирован (None = навсегда)
    ban_count = db.Column(db.Integer, default=0)  # Количество блокировок
    warnings_count = db.Column(db.Integer, default=0)  # Количество предупреждений
    last_warning = db.Column(db.DateTime)  # Дата последнего предупреждения
    rating = db.Column(db.Float, default=5.0)  # Рейтинг пользователя (1-5)
    rating_count = db.Column(db.Integer, default=0)  # Количество оценок
    
    # Настройки пользователя
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def get_settings(self):
        if not self.settings:
            self.settings = UserSettings(user_id=self.id)
            db.session.add(self.settings)
            db.session.commit()
        return self.settings

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=True)  # Для каналов
    content = db.Column(db.Text, nullable=False)
    encrypted_content = db.Column(db.Text, nullable=False)  # Зашифрованное содержимое
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)  # Ответ на сообщение
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_for_all = db.Column(db.Boolean, default=False)  # Удалено для всех
    
    # Отношения
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    reply_to = db.relationship('Message', remote_side=[id])
    reactions = db.relationship('MessageReaction', backref='message', cascade='all, delete-orphan')

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    is_public = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(200), default='')
    member_count = db.Column(db.Integer, default=0)
    
    # Отношения
    creator = db.relationship('User', foreign_keys=[created_by])
    members = db.relationship('ChannelMember', backref='channel', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='channel', cascade='all, delete-orphan')

class ChannelMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='member')  # member, moderator, admin
    
    # Отношения
    user = db.relationship('User')

class MessageReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)  # Эмодзи реакция
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    user = db.relationship('User')

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(20), default='light')  # light, dark, auto
    language = db.Column(db.String(10), default='ru')
    notifications_enabled = db.Column(db.Boolean, default=True)
    sound_enabled = db.Column(db.Boolean, default=True)
    auto_save_drafts = db.Column(db.Boolean, default=True)
    privacy_level = db.Column(db.String(20), default='friends')  # public, friends, private
    animations_enabled = db.Column(db.Boolean, default=True)  # Анимации
    compact_mode = db.Column(db.Boolean, default=False)  # Компактный режим
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(db.Model):
    """Модель для жалоб на пользователей"""
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Кто пожаловался
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # На кого пожаловались
    reason = db.Column(db.String(200), nullable=False)  # Причина жалобы
    description = db.Column(db.Text, default='')  # Подробное описание
    evidence = db.Column(db.Text, default='')  # Доказательства (ссылки на сообщения и т.д.)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved, dismissed
    admin_notes = db.Column(db.Text, default='')  # Заметки администратора
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Кто рассмотрел
    
    # Отношения
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class ModerationAction(db.Model):
    """Модель для действий модерации"""
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Кто выполнил действие
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # На кого направлено действие
    action_type = db.Column(db.String(50), nullable=False)  # ban, unban, delete, warn, promote
    reason = db.Column(db.Text, nullable=False)  # Причина действия
    duration = db.Column(db.Integer, default=0)  # Длительность в минутах (0 = навсегда)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=True)  # Связанная жалоба
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    admin = db.relationship('User', foreign_keys=[admin_id])
    target_user = db.relationship('User', foreign_keys=[target_user_id])
    report = db.relationship('Report')

class Warning(db.Model):
    """Модель для предупреждений пользователей"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    user = db.relationship('User', foreign_keys=[user_id])
    admin = db.relationship('User', foreign_keys=[admin_id])

class UserRating(db.Model):
    """Модель для рейтинга пользователей"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    user = db.relationship('User', foreign_keys=[user_id])
    rater = db.relationship('User', foreign_keys=[rater_id])
    
    # Уникальное ограничение - один пользователь может оценить другого только один раз
    __table_args__ = (db.UniqueConstraint('user_id', 'rater_id', name='unique_user_rating'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Роуты
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    device_type = detect_device_type(request.headers.get('User-Agent'))
    return render_template('index.html', device_type=device_type)

@app.route('/register', methods=['GET', 'POST'])
def register():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            # Предлагаем альтернативные юзернеймы
            alternatives = generate_username_alternatives(username)
            flash(f'Пользователь с именем "{username}" уже существует! Попробуйте: {", ".join(alternatives[:3])}')
            return render_template('register.html', alternatives=alternatives, original_username=username, device_type=device_type)
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с такой почтой уже существует!')
            return render_template('register.html', device_type=device_type)
        
        user = User(
            username=username,
            display_name=username,  # Изначально display_name = username
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите в систему.')
        return redirect(url_for('login'))
    
    return render_template('register.html', device_type=device_type)

def generate_username_alternatives(base_username):
    """Генерирует альтернативные юзернеймы"""
    alternatives = []
    
    # Добавляем числа
    for i in range(1, 10):
        alternatives.append(f"{base_username}{i}")
    
    # Добавляем подчеркивания
    alternatives.append(f"{base_username}_")
    alternatives.append(f"_{base_username}")
    
    # Добавляем популярные суффиксы
    suffixes = ['pro', 'dev', 'user', '2024', '2025', 'cool', 'awesome']
    for suffix in suffixes:
        alternatives.append(f"{base_username}_{suffix}")
    
    # Фильтруем уже занятые
    available_alternatives = []
    for alt in alternatives:
        if not User.query.filter_by(username=alt).first():
            available_alternatives.append(alt)
    
    return available_alternatives[:10]  # Возвращаем максимум 10 вариантов

def detect_device_type(user_agent):
    """Определяет тип устройства по User-Agent"""
    if not user_agent:
        return 'desktop'
    
    user_agent = user_agent.lower()
    
    # Мобильные устройства
    mobile_patterns = [
        r'android', r'iphone', r'ipad', r'ipod', r'blackberry',
        r'windows phone', r'mobile', r'tablet'
    ]
    
    # Планшеты
    tablet_patterns = [
        r'ipad', r'android.*tablet', r'kindle', r'playbook'
    ]
    
    # Проверяем планшеты
    for pattern in tablet_patterns:
        if re.search(pattern, user_agent):
            return 'tablet'
    
    # Проверяем мобильные
    for pattern in mobile_patterns:
        if re.search(pattern, user_agent):
            return 'mobile'
    
    return 'desktop'

def get_connection_info(request):
    """Получает информацию о подключении пользователя"""
    info = {
        'device_type': detect_device_type(request.headers.get('User-Agent')),
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Неизвестно'),
        'secure': request.is_secure,
        'protocol': 'HTTPS' if request.is_secure else 'HTTP'
    }
    
    # Определяем тип браузера
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'chrome' in user_agent:
        info['browser'] = 'Chrome'
    elif 'firefox' in user_agent:
        info['browser'] = 'Firefox'
    elif 'safari' in user_agent:
        info['browser'] = 'Safari'
    elif 'edge' in user_agent:
        info['browser'] = 'Edge'
    else:
        info['browser'] = 'Другой'
    
    return info

# Функции шифрования
def generate_encryption_key():
    """Генерирует ключ шифрования для сообщений"""
    return Fernet.generate_key()

def encrypt_message(content, key):
    """Шифрует сообщение"""
    f = Fernet(key)
    return f.encrypt(content.encode()).decode()

def decrypt_message(encrypted_content, key):
    """Расшифровывает сообщение"""
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_content.encode()).decode()
    except:
        return "Сообщение повреждено"

# Генерируем ключ шифрования для приложения
ENCRYPTION_KEY = generate_encryption_key()

# Функция для автоматического резервного копирования
def auto_backup_data():
    """Автоматически создает резервную копию всех данных"""
    try:
        from datetime import datetime
        import os
        
        # Создаем папку для резервных копий
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Имя файла резервной копии
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/nexa_backup_{timestamp}.db'
        
        # Копируем базу данных
        import shutil
        shutil.copy2('nexa_messenger.db', backup_file)
        
        # Удаляем старые резервные копии (оставляем только последние 5)
        backup_files = sorted([f for f in os.listdir(backup_dir) if f.startswith('nexa_backup_')])
        if len(backup_files) > 5:
            for old_file in backup_files[:-5]:
                os.remove(os.path.join(backup_dir, old_file))
        
        print(f'Резервная копия создана: {backup_file}')
        return True
    except Exception as e:
        print(f'Ошибка создания резервной копии: {e}')
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Проверяем, не заблокирован ли пользователь
            if user.is_banned:
                if user.ban_until and user.ban_until < datetime.utcnow():
                    # Блокировка истекла, разблокируем
                    user.is_banned = False
                    user.ban_reason = ''
                    user.ban_until = None
                    db.session.commit()
                else:
                    # Пользователь заблокирован
                    if user.ban_until:
                        ban_time = user.ban_until.strftime('%d.%m.%Y %H:%M')
                        flash(f'Ваш аккаунт заблокирован до {ban_time}. Причина: {user.ban_reason}')
                    else:
                        flash(f'Ваш аккаунт заблокирован навсегда. Причина: {user.ban_reason}')
                    return render_template('login.html', device_type=device_type)
            
            login_user(user)
            user.is_online = True
            user.last_seen = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('chat'))
        else:
            flash('Неверное имя пользователя или пароль!')
    
    return render_template('login.html', device_type=device_type)

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
    device_type = detect_device_type(request.headers.get('User-Agent'))
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('chat.html', users=users, device_type=device_type)

@app.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    if query:
        # Улучшенный поиск: ищем по username и display_name
        exact_match = User.query.filter(
            User.id != current_user.id,
            (User.username == query) | (User.display_name == query)
        ).first()
        
        starts_with = User.query.filter(
            User.id != current_user.id,
            (User.username.ilike(f'{query}%')) | (User.display_name.ilike(f'{query}%'))
        ).limit(10).all()
        
        contains = User.query.filter(
            User.id != current_user.id,
            (User.username.ilike(f'%{query}%')) | (User.display_name.ilike(f'%{query}%'))
        ).limit(10).all()
        
        # Объединяем результаты, убирая дубликаты
        all_users = []
        seen_ids = set()
        
        # Сначала точные совпадения
        if exact_match and exact_match.id not in seen_ids:
            all_users.append(exact_match)
            seen_ids.add(exact_match.id)
        
        # Затем начинающиеся с запроса
        for user in starts_with:
            if user.id not in seen_ids:
                all_users.append(user)
                seen_ids.add(user.id)
        
        # Затем содержащие запрос
        for user in contains:
            if user.id not in seen_ids:
                all_users.append(user)
                seen_ids.add(user.id)
        
        users = all_users[:20]  # Максимум 20 результатов
    else:
        # Если запрос пустой, показываем онлайн пользователей
        online_users = User.query.filter(
            User.id != current_user.id,
            User.is_online == True
        ).limit(10).all()
        
        recent_users = User.query.filter(
            User.id != current_user.id
        ).order_by(User.last_seen.desc()).limit(10).all()
        
        # Объединяем, убирая дубликаты
        all_users = []
        seen_ids = set()
        
        for user in online_users:
            if user.id not in seen_ids:
                all_users.append(user)
                seen_ids.add(user.id)
        
        for user in recent_users:
            if user.id not in seen_ids and len(all_users) < 20:
                all_users.append(user)
                seen_ids.add(user.id)
        
        users = all_users
    
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'display_name': user.display_name,
        'is_online': user.is_online,
        'last_seen': user.last_seen.strftime('%d.%m.%Y в %H:%M') if user.last_seen else 'Неизвестно',
        'match_type': 'exact' if query and user.username == query else 'partial'
    } for user in users])

@app.route('/profile')
@login_required
def profile():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    return render_template('profile.html', device_type=device_type)

@app.route('/profile/<username>')
@login_required
def view_profile(username):
    device_type = detect_device_type(request.headers.get('User-Agent'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('profile'))
    
    return render_template('view_profile.html', user=user, device_type=device_type)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    
    if request.method == 'POST':
        # Можно менять display_name, но не username
        current_user.display_name = request.form['display_name']
        current_user.bio = request.form['bio']
        db.session.commit()
        flash('Профиль обновлен!')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', device_type=device_type)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    user_settings = current_user.get_settings()
    
    if request.method == 'POST':
        user_settings.theme = request.form.get('theme', 'light')
        user_settings.language = request.form.get('language', 'ru')
        user_settings.notifications_enabled = 'notifications_enabled' in request.form
        user_settings.sound_enabled = 'sound_enabled' in request.form
        user_settings.auto_save_drafts = 'auto_save_drafts' in request.form
        user_settings.privacy_level = request.form.get('privacy_level', 'friends')
        
        db.session.commit()
        flash('Настройки сохранены!')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', settings=user_settings, device_type=device_type)

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    if request.method == 'POST':
        data = request.get_json()
        user_settings = current_user.get_settings()
        
        for key, value in data.items():
            if hasattr(user_settings, key):
                setattr(user_settings, key, value)
        
        db.session.commit()
        return jsonify({'status': 'success'})
    
    user_settings = current_user.get_settings()
    return jsonify({
        'theme': user_settings.theme,
        'language': user_settings.language,
        'notifications_enabled': user_settings.notifications_enabled,
        'sound_enabled': user_settings.sound_enabled,
        'auto_save_drafts': user_settings.auto_save_drafts,
        'privacy_level': user_settings.privacy_level
    })

@app.route('/help')
def help():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    return render_template('help.html', device_type=device_type)

@app.route('/rules')
@login_required
def rules_page():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    return render_template('rules.html', device_type=device_type)

@app.route('/api/tips')
def api_tips():
    """API для получения подсказок"""
    tips = {
        'chat': [
            '💡 Нажмите Enter для отправки сообщения',
            '💡 Используйте поиск для быстрого нахождения пользователей',
            '💡 Двойной клик по сообщению для ответа',
            '💡 Все сообщения защищены шифрованием'
        ],
        'security': [
            '🔒 Ваши сообщения зашифрованы и недоступны третьим лицам',
            '🔒 Только вы и получатель можете видеть переписку',
            '🔒 Данные хранятся в зашифрованном виде',
            '🔒 Приложение соответствует стандартам безопасности'
        ],
        'features': [
            '✨ Автоматическое определение устройства',
            '✨ Адаптивный интерфейс для всех экранов',
            '✨ Уведомления в реальном времени',
            '✨ Индикатор "печатает"'
        ]
    }
    return jsonify(tips)

@app.route('/api/connection_info')
@login_required
def api_connection_info():
    """API для получения информации о подключении пользователя"""
    connection_info = get_connection_info(request)
    return jsonify(connection_info)

@app.route('/api/backup', methods=['POST'])
@login_required
def api_backup():
    """API для создания резервной копии данных"""
    if auto_backup_data():
        return jsonify({'status': 'success', 'message': 'Резервная копия создана успешно'})
    else:
        return jsonify({'status': 'error', 'message': 'Ошибка создания резервной копии'}), 500

@app.route('/api/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()
    
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'is_own': msg.sender_id == current_user.id,
        'is_edited': msg.is_edited,
        'edited_at': msg.edited_at.strftime('%H:%M') if msg.edited_at else None,
        'reply_to_id': msg.reply_to_id,
        'reply_to_content': msg.reply_to.content[:50] + '...' if msg.reply_to else None,
        'reactions': [{'emoji': r.emoji, 'count': len([re for re in msg.reactions if re.emoji == r.emoji])} for r in set(r.emoji for r in msg.reactions)]
    } for msg in messages])

# Новые роуты для каналов
@app.route('/channels')
@login_required
def channels():
    device_type = detect_device_type(request.headers.get('User-Agent'))
    public_channels = Channel.query.filter_by(is_public=True).all()
    user_channels = ChannelMember.query.filter_by(user_id=current_user.id).all()
    return render_template('channels.html', 
                         public_channels=public_channels, 
                         user_channels=user_channels, 
                         device_type=device_type)

@app.route('/channel/<int:channel_id>')
@login_required
def channel_chat(channel_id):
    device_type = detect_device_type(request.headers.get('User-Agent'))
    channel = Channel.query.get_or_404(channel_id)
    member = ChannelMember.query.filter_by(channel_id=channel_id, user_id=current_user.id).first()
    
    if not member and not channel.is_public:
        flash('У вас нет доступа к этому каналу')
        return redirect(url_for('channels'))
    
    return render_template('channel_chat.html', channel=channel, device_type=device_type)

@app.route('/api/channels', methods=['GET', 'POST'])
@login_required
def api_channels():
    if request.method == 'POST':
        data = request.get_json()
        channel = Channel(
            name=data['name'],
            description=data.get('description', ''),
            is_public=data.get('is_public', True),
            created_by=current_user.id
        )
        db.session.add(channel)
        db.session.commit()
        
        # Добавляем создателя как участника
        member = ChannelMember(channel_id=channel.id, user_id=current_user.id, role='admin')
        db.session.add(member)
        db.session.commit()
        
        return jsonify({'status': 'success', 'channel_id': channel.id})
    
    channels = Channel.query.filter_by(is_public=True).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'member_count': c.member_count,
        'topic': c.topic
    } for c in channels])

@app.route('/api/channel/<int:channel_id>/join', methods=['POST'])
@login_required
def join_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    existing_member = ChannelMember.query.filter_by(channel_id=channel_id, user_id=current_user.id).first()
    
    if existing_member:
        return jsonify({'status': 'error', 'message': 'Вы уже участник этого канала'})
    
    member = ChannelMember(channel_id=channel_id, user_id=current_user.id)
    db.session.add(member)
    channel.member_count += 1
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/api/channel/<int:channel_id>/messages')
@login_required
def get_channel_messages(channel_id):
    member = ChannelMember.query.filter_by(channel_id=channel_id, user_id=current_user.id).first()
    if not member:
        return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403
    
    messages = Message.query.filter_by(channel_id=channel_id).order_by(Message.timestamp).all()
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'sender_name': msg.sender.display_name,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'is_own': msg.sender_id == current_user.id,
        'is_edited': msg.is_edited,
        'edited_at': msg.edited_at.strftime('%H:%M') if msg.edited_at else None,
        'reply_to_id': msg.reply_to_id,
        'reply_to_content': msg.reply_to.content[:50] + 'chat.html' if msg.reply_to else None,
        'reactions': [{'emoji': r.emoji, 'count': len([re for re in msg.reactions if re.emoji == r.emoji])} for r in set(r.emoji for r in msg.reactions)]
    } for msg in messages])

# Роуты для реакций
@app.route('/api/message/<int:message_id>/react', methods=['POST'])
@login_required
def react_to_message(message_id):
    data = request.get_json()
    emoji = data.get('emoji')
    
    if not emoji:
        return jsonify({'status': 'error', 'message': 'Эмодзи не указан'}), 400
    
    # Убираем существующую реакцию пользователя
    existing_reaction = MessageReaction.query.filter_by(
        message_id=message_id, 
        user_id=current_user.id
    ).first()
    
    if existing_reaction:
        if existing_reaction.emoji == emoji:
            # Убираем реакцию
            db.session.delete(existing_reaction)
        else:
            # Меняем реакцию
            existing_reaction.emoji = emoji
    else:
        # Добавляем новую реакцию
        reaction = MessageReaction(
            message_id=message_id,
            user_id=current_user.id,
            emoji=emoji
        )
        db.session.add(reaction)
    
    db.session.commit()
    return jsonify({'status': 'success'})

# Роуты для редактирования и удаления сообщений
@app.route('/api/message/<int:message_id>/edit', methods=['PUT'])
@login_required
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.sender_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Вы можете редактировать только свои сообщения'}), 403
    
    data = request.get_json()
    new_content = data.get('content', '').strip()
    
    if not new_content:
        return jsonify({'status': 'error', 'message': 'Содержимое не может быть пустым'}), 400
    
    message.content = new_content
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'status': 'success', 'content': new_content})

@app.route('/api/message/<int:message_id>/delete', methods=['DELETE'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    data = request.get_json()
    delete_for_all = data.get('delete_for_all', False)
    
    if message.sender_id != current_user.id and not delete_for_all:
        return jsonify({'status': 'error', 'message': 'Вы можете удалять только свои сообщения'}), 403
    
    if delete_for_all and message.sender_id == current_user.id:
        message.is_deleted = True
        message.deleted_for_all = True
    else:
        message.is_deleted = True
    
    db.session.commit()
    return jsonify({'status': 'success'})

# Роуты для статусов пользователя
@app.route('/api/user/status', methods=['PUT'])
@login_required
def update_user_status():
    data = request.get_json()
    status = data.get('status', 'online')
    custom_status = data.get('custom_status', '')
    
    if status not in ['online', 'away', 'busy', 'dnd']:
        return jsonify({'status': 'error', 'message': 'Неверный статус'}), 400
    
    current_user.status = status
    current_user.custom_status = custom_status
    db.session.commit()
    
    # Уведомляем других пользователей об изменении статуса
    socketio.emit('user_status_changed', {
        'user_id': current_user.id,
        'status': status,
        'custom_status': custom_status
    }, broadcast=True)
    
    return jsonify({'status': 'success'})

# Роут для загрузки аватара
@app.route('/api/user/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не выбран'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Файл не выбран'}), 400
    
    if file:
        # Простая проверка типа файла
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'status': 'error', 'message': 'Неподдерживаемый тип файла'}), 400
        
        # Генерируем уникальное имя файла
        filename = f"avatar_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
        
        # Сохраняем файл
        upload_folder = os.path.join(app.static_folder, 'avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Обновляем профиль пользователя
        current_user.profile_picture = filename
        db.session.commit()
        
        return jsonify({'status': 'success', 'filename': filename})
    
    return jsonify({'status': 'error', 'message': 'Ошибка загрузки файла'}), 500

# Роут для обновления цветового акцента
@app.route('/api/user/color', methods=['PUT'])
@login_required
def update_user_color():
    data = request.get_json()
    color = data.get('color', '#00d4ff')
    
    # Простая проверка цвета
    import re
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return jsonify({'status': 'error', 'message': 'Неверный формат цвета'}), 400
    
    current_user.color_accent = color
    db.session.commit()
    
    return jsonify({'status': 'success', 'color': color})

# Админ-панель для просмотра пользователей
@app.route('/admin')
@login_required
def admin_panel():
    # Проверяем, является ли пользователь админом
    if not current_user.is_admin:
        flash('Доступ запрещен. Требуются права администратора.')
        return redirect(url_for('chat'))
    
    device_type = detect_device_type(request.headers.get('User-Agent'))
    
    # Получаем статистику
    total_users = User.query.count()
    online_users = User.query.filter_by(is_online=True).count()
    total_channels = Channel.query.count()
    total_messages = Message.query.count()
    banned_users = User.query.filter_by(is_banned=True).count()
    pending_reports = Report.query.filter_by(status='pending').count()
    
    # Получаем последних пользователей
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Получаем активные каналы
    active_channels = Channel.query.order_by(Channel.member_count.desc()).limit(5).all()
    
    # Получаем последние жалобы
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
    
    return render_template('admin.html', 
                         total_users=total_users,
                         online_users=online_users,
                         total_channels=total_channels,
                         total_messages=total_messages,
                         banned_users=banned_users,
                         pending_reports=pending_reports,
                         recent_users=recent_users,
                         active_channels=active_channels,
                         recent_reports=recent_reports,
                         device_type=device_type)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            User.username.ilike(f'%{search}%') |
            User.display_name.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%')
        )
    
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'email': user.email,
            'is_online': user.is_online,
            'status': user.status,
            'custom_status': user.custom_status,
            'created_at': user.created_at.strftime('%d.%m.%Y %H:%M'),
            'last_seen': user.last_seen.strftime('%d.%m.%Y %H:%M') if user.last_seen else 'Неизвестно',
            'profile_picture': user.profile_picture,
            'is_admin': user.is_admin,
            'is_banned': user.is_banned,
            'ban_reason': user.ban_reason if user.is_banned else '',
            'ban_until': user.ban_until.strftime('%d.%m.%Y %H:%M') if user.ban_until and user.is_banned else None,
            'ban_count': user.ban_count
        } for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@app.route('/admin/statistics')
@login_required
def admin_statistics():
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403
    
    # Статистика по дням (последние 30 дней)
    from datetime import datetime, timedelta
    
    dates = []
    user_counts = []
    message_counts = []
    report_counts = []
    
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime('%d.%m'))
        
        # Количество новых пользователей за день
        user_count = User.query.filter(
            User.created_at >= date.replace(hour=0, minute=0, second=0, microsecond=0),
            User.created_at < date.replace(hour=23, minute=59, second=59, microsecond=999999)
        ).count()
        user_counts.append(user_count)
        
        # Количество сообщений за день
        message_count = Message.query.filter(
            Message.timestamp >= date.replace(hour=0, minute=0, second=0, microsecond=0),
            Message.timestamp < date.replace(hour=23, minute=59, second=59, microsecond=999999)
        ).count()
        message_counts.append(message_count)
        
        # Количество жалоб за день
        report_count = Report.query.filter(
            Report.created_at >= date.replace(hour=0, minute=0, second=0, microsecond=0),
            Report.created_at < date.replace(hour=23, minute=59, second=59, microsecond=999999)
        ).count()
        report_counts.append(report_count)
    
    # Переворачиваем массивы для правильного порядка
    dates.reverse()
    user_counts.reverse()
    message_counts.reverse()
    report_counts.reverse()
    
    return jsonify({
        'dates': dates,
        'user_counts': user_counts,
        'message_counts': message_counts,
        'report_counts': report_counts,
        'total_users': User.query.count(),
        'online_users': User.query.filter_by(is_online=True).count(),
        'total_channels': Channel.query.count(),
        'total_messages': Message.query.count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'pending_reports': Report.query.filter_by(status='pending').count()
    })

# Функция для проверки админских прав
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# API для изменения прав администратора
@app.route('/api/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin_rights(user_id):
    target_user = User.query.get_or_404(user_id)
    
    if target_user.id == current_user.id:
        return jsonify({'status': 'error', 'message': 'Нельзя изменить свои права'}), 400
    
    target_user.is_admin = not target_user.is_admin
    db.session.commit()
    
    # Создаем запись о действии
    action = ModerationAction(
        admin_id=current_user.id,
        target_user_id=user_id,
        action_type='promote' if target_user.is_admin else 'demote',
        reason=f'Изменение прав администратора на {"предоставлены" if target_user.is_admin else "отозваны"}'
    )
    db.session.add(action)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'is_admin': target_user.is_admin,
        'message': f'Права администратора {"предоставлены" if target_user.is_admin else "отозваны"}'
    })



# API для удаления пользователя
@app.route('/api/user/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    if target_user.id == current_user.id:
        return jsonify({'status': 'error', 'message': 'Нельзя удалить себя'}), 400
    
    if target_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Нельзя удалить администратора'}), 400
    
    # Создаем запись о действии
    action = ModerationAction(
        admin_id=current_user.id,
        target_user_id=user_id,
        action_type='delete',
        reason='Удаление аккаунта администратором'
    )
    db.session.add(action)
    db.session.commit()
    
    # Удаляем пользователя
    db.session.delete(target_user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Пользователь удален'})

# API для создания жалобы
@app.route('/api/report', methods=['POST'])
@login_required
def create_report():
    data = request.get_json()
    reported_user_id = data.get('reported_user_id')
    reason = data.get('reason')
    description = data.get('description', '')
    evidence = data.get('evidence', '')
    
    if not reported_user_id or not reason:
        return jsonify({'status': 'error', 'message': 'Не все поля заполнены'}), 400
    
    if reported_user_id == current_user.id:
        return jsonify({'status': 'error', 'message': 'Нельзя пожаловаться на себя'}), 400
    
    # Проверяем, не жаловался ли уже пользователь
    existing_report = Report.query.filter_by(
        reporter_id=current_user.id,
        reported_user_id=reported_user_id,
        status='pending'
    ).first()
    
    if existing_report:
        return jsonify({'status': 'error', 'message': 'Вы уже жаловались на этого пользователя'}), 400
    
    report = Report(
        reporter_id=current_user.id,
        reported_user_id=reported_user_id,
        reason=reason,
        description=description,
        evidence=evidence
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Жалоба отправлена'})

# API для предупреждения пользователя
@app.route('/api/user/<int:user_id>/warn', methods=['POST'])
@admin_required
def warn_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    if target_user.id == current_user.id:
        return jsonify({'status': 'error', 'message': 'Нельзя предупредить себя'}), 400
    
    if target_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Нельзя предупредить администратора'}), 400
    
    data = request.get_json()
    reason = data.get('reason', 'Нарушение правил')
    
    # Создаем предупреждение
    warning = Warning(
        user_id=target_user.id,
        admin_id=current_user.id,
        reason=reason
    )
    db.session.add(warning)
    
    # Обновляем счетчик предупреждений
    target_user.warnings_count += 1
    target_user.last_warning = datetime.utcnow()
    
    db.session.commit()
    
    # Отправляем уведомление пользователю через WebSocket
    socketio.emit('user_warned', {
        'message': f'Вы получили предупреждение: {reason}',
        'warning_count': target_user.warnings_count
    }, room=f'user_{target_user.id}')
    
    return jsonify({
        'status': 'success',
        'message': 'Предупреждение выдано',
        'warning_count': target_user.warnings_count
    })

# API для блокировки пользователя
@app.route('/api/user/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    if target_user.id == current_user.id:
        return jsonify({'status': 'error', 'message': 'Нельзя заблокировать себя'}), 400
    
    if target_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Нельзя заблокировать администратора'}), 400
    
    data = request.get_json()
    reason = data.get('reason', 'Нарушение правил')
    duration = data.get('duration', 0)  # 0 = навсегда, >0 = в минутах
    
    # Вычисляем дату окончания блокировки
    if duration > 0:
        ban_until = datetime.utcnow() + timedelta(minutes=duration)
    else:
        ban_until = None  # Навсегда
    
    # Блокируем пользователя
    target_user.is_banned = True
    target_user.ban_reason = reason
    target_user.ban_until = ban_until
    target_user.ban_count += 1
    
    # Создаем запись о действии модерации
    action = ModerationAction(
        admin_id=current_user.id,
        target_user_id=target_user.id,
        action_type='ban',
        reason=reason,
        duration=duration
    )
    db.session.add(action)
    
    db.session.commit()
    
    # Отправляем уведомление пользователю через WebSocket
    if duration > 0:
        ban_message = f'Вы заблокированы до {ban_until.strftime("%d.%m.%Y %H:%M")}. Причина: {reason}'
    else:
        ban_message = f'Вы заблокированы навсегда. Причина: {reason}'
    
    socketio.emit('user_banned', {
        'message': ban_message,
        'ban_until': ban_until.isoformat() if ban_until else None
    }, room=f'user_{target_user.id}')
    
    return jsonify({
        'status': 'success',
        'message': 'Пользователь заблокирован',
        'ban_until': ban_until.isoformat() if ban_until else None
    })

# API для разблокировки пользователя
@app.route('/api/user/<int:user_id>/unban', methods=['POST'])
@admin_required
def unban_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    # Разблокируем пользователя
    target_user.is_banned = False
    target_user.ban_reason = None
    target_user.ban_until = None
    
    # Создаем запись о действии модерации
    action = ModerationAction(
        admin_id=current_user.id,
        target_user_id=target_user.id,
        action_type='unban',
        reason='Разблокировка администратором',
        duration=0
    )
    db.session.add(action)
    
    db.session.commit()
    
    # Отправляем уведомление пользователю через WebSocket
    socketio.emit('user_unbanned', {
        'message': 'Ваша блокировка снята. Добро пожаловать обратно!'
    }, room=f'user_{target_user.id}')
    
    return jsonify({'status': 'success', 'message': 'Пользователь разблокирован'})

# API для оценки пользователя
@app.route('/api/user/<int:user_id>/rate', methods=['POST'])
@login_required
def rate_user(user_id):
    if current_user.id == user_id:
        return jsonify({'status': 'error', 'message': 'Нельзя оценить самого себя'}), 400
    
    target_user = User.query.get_or_404(user_id)
    data = request.get_json()
    rating = data.get('rating', 5)
    comment = data.get('comment', '')
    
    # Проверяем, что рейтинг в диапазоне 1-5
    if not 1 <= rating <= 5:
        return jsonify({'status': 'error', 'message': 'Рейтинг должен быть от 1 до 5'}), 400
    
    # Проверяем, не оценивал ли уже этот пользователь
    existing_rating = UserRating.query.filter_by(
        user_id=user_id, 
        rater_id=current_user.id
    ).first()
    
    if existing_rating:
        return jsonify({'status': 'error', 'message': 'Вы уже оценили этого пользователя'}), 400
    
    # Создаем оценку
    user_rating = UserRating(
        user_id=user_id,
        rater_id=current_user.id,
        rating=rating,
        comment=comment
    )
    db.session.add(user_rating)
    
    # Обновляем общий рейтинг пользователя
    target_user.rating_count += 1
    total_rating = target_user.rating * (target_user.rating_count - 1) + rating
    target_user.rating = total_rating / target_user.rating_count
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Оценка добавлена',
        'new_rating': round(target_user.rating, 2),
        'rating_count': target_user.rating_count
    })

# API для получения рейтинга пользователя
@app.route('/api/user/<int:user_id>/rating', methods=['GET'])
def get_user_rating(user_id):
    target_user = User.query.get_or_404(user_id)
    
    # Получаем все оценки пользователя
    ratings = UserRating.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'status': 'success',
        'rating': round(target_user.rating, 2),
        'rating_count': target_user.rating_count,
        'ratings': [{
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat(),
            'rater_username': r.rater.username
        } for r in ratings]
    })

# API для получения жалоб (для админов)
@app.route('/api/reports')
@admin_required
def get_reports():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    
    query = Report.query
    
    if status:
        query = query.filter_by(status=status)
    
    reports = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'reports': [{
            'id': report.id,
            'reporter': {
                'id': report.reporter.id,
                'username': report.reporter.username,
                'display_name': report.reporter.display_name
            },
            'reported_user': {
                'id': report.reported_user.id,
                'username': report.reported_user.username,
                'display_name': report.reported_user.display_name
            },
            'reason': report.reason,
            'description': report.description,
            'evidence': report.evidence,
            'status': report.status,
            'created_at': report.created_at.strftime('%d.%m.%Y %H:%M'),
            'reviewed_at': report.reviewed_at.strftime('%d.%m.%Y %H:%M') if report.reviewed_at else None,
            'reviewer': {
                'id': report.reviewer.id,
                'username': report.reviewer.username
            } if report.reviewer else None,
            'admin_notes': report.admin_notes
        } for report in reports.items],
        'total': reports.total,
        'pages': reports.pages,
        'current_page': page
    })

# API для обработки жалобы
@app.route('/api/report/<int:report_id>/review', methods=['POST'])
@admin_required
def review_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    if report.status != 'pending':
        return jsonify({'status': 'error', 'message': 'Жалоба уже обработана'}), 400
    
    data = request.get_json()
    action = data.get('action')  # resolve, dismiss
    admin_notes = data.get('admin_notes', '')
    
    report.status = action
    report.admin_notes = admin_notes
    report.reviewed_at = datetime.utcnow()
    report.reviewed_by = current_user.id
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Жалоба обработана'})

# API для просмотра профиля пользователя
@app.route('/api/user/<int:user_id>/profile')
@login_required
def get_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    # Проверяем, заблокирован ли пользователь
    if user.is_banned:
        if user.ban_until and user.ban_until < datetime.utcnow():
            # Блокировка истекла, разблокируем
            user.is_banned = False
            user.ban_reason = ''
            user.ban_until = None
            db.session.commit()
        else:
            return jsonify({'status': 'error', 'message': 'Пользователь заблокирован'}), 403
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'display_name': user.display_name,
        'email': user.email if current_user.is_admin else None,
        'profile_picture': user.profile_picture,
        'bio': user.bio,
        'status': user.status,
        'custom_status': user.custom_status,
        'color_accent': user.color_accent,
        'is_online': user.is_online,
        'created_at': user.created_at.strftime('%d.%m.%Y %H:%M'),
        'last_seen': user.last_seen.strftime('%d.%m.%Y %H:%M') if user.last_seen else None,
        'is_admin': user.is_admin,
        'is_banned': user.is_banned,
        'ban_reason': user.ban_reason if current_user.is_admin else None,
        'ban_until': user.ban_until.strftime('%d.%m.%Y %H:%M') if user.ban_until and current_user.is_admin else None,
        'ban_count': user.ban_count if current_user.is_admin else None
    })

# WebSocket события
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        current_user.is_online = True
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        emit('user_status', {'user_id': current_user.id, 'status': 'online'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        current_user.is_online = False
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        emit('user_status', {'user_id': current_user.id, 'status': 'offline'}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    # Проверяем, что сообщение не пустое
    if not data.get('content', '').strip():
        return
    
    content = data['content'].strip()
    
    # Шифруем сообщение
    encrypted_content = encrypt_message(content, ENCRYPTION_KEY)
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=data.get('receiver_id'),
        channel_id=data.get('channel_id'),
        content=content,  # Оригинальное сообщение для отображения
        encrypted_content=encrypted_content,  # Зашифрованное для хранения
        reply_to_id=data.get('reply_to_id')
    )
    db.session.add(message)
    db.session.commit()
    
    # Отправляем сообщение всем подключенным пользователям
    emit('new_message', {
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'channel_id': message.channel_id,
        'content': content,  # Отправляем оригинальное сообщение
        'timestamp': message.timestamp.strftime('%H:%M'),
        'sender_name': current_user.display_name,
        'reply_to_id': message.reply_to_id,
        'reply_to_content': message.reply_to.content[:50] + '...' if message.reply_to else None
    }, broadcast=True)
    
    # Отправляем уведомление получателю
    if message.receiver_id:
        emit('message_notification', {
            'sender_name': current_user.display_name,
            'content': content[:50] + '...' if len(content) > 50 else content
        }, room=message.receiver_id)
    elif message.channel_id:
        # Уведомление для канала
        emit('channel_message_notification', {
            'channel_id': message.channel_id,
            'sender_name': current_user.display_name,
            'content': content[:50] + '...' if len(content) > 50 else content
        }, broadcast=True)

@socketio.on('join_channel')
def handle_join_channel(data):
    channel_id = data.get('channel_id')
    if channel_id:
        join_room(f'channel_{channel_id}')
        emit('user_joined_channel', {
            'user_id': current_user.id,
            'username': current_user.username,
            'display_name': current_user.display_name
        }, room=f'channel_{channel_id}')

@socketio.on('leave_channel')
def handle_leave_channel(data):
    channel_id = data.get('channel_id')
    if channel_id:
        leave_room(f'channel_{channel_id}')
        emit('user_left_channel', {
            'user_id': current_user.id,
            'username': current_user.username,
            'display_name': current_user.display_name
        }, room=f'channel_{channel_id}')

@socketio.on('typing_start')
def handle_typing_start(data):
    emit('typing_start', {
        'user_id': current_user.id,
        'username': current_user.username,
        'display_name': current_user.display_name
    }, broadcast=True)

@socketio.on('typing_stop')
def handle_typing_stop(data):
    emit('typing_stop', {
        'user_id': current_user.id,
        'username': current_user.username,
        'display_name': current_user.display_name
    }, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Получаем порт из переменной окружения (для Render) или используем 8080
    port = int(os.environ.get('PORT', 8080))
    
    # Проверяем, запускаем ли мы в продакшене
    if os.environ.get('FLASK_ENV') == 'production':
        # В продакшене используем простой запуск без debug
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        # В разработке используем debug режим
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
