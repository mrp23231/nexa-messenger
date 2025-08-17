// Основной JavaScript файл для мессенджера

document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления элементов
    animateElements();
    
    // Обработка форм
    setupFormValidation();
    
    // Уведомления
    setupNotifications();
});

// Анимация появления элементов
function animateElements() {
    const elements = document.querySelectorAll('.form-container, .profile-container, .chat-container');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Валидация форм
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    showError(input, 'Это поле обязательно для заполнения');
                    isValid = false;
                } else {
                    clearError(input);
                }
            });
            
            // Специальная валидация для email
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && emailInput.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailInput.value)) {
                    showError(emailInput, 'Введите корректный email адрес');
                    isValid = false;
                }
            }
            
            // Валидация пароля
            const passwordInput = form.querySelector('input[type="password"]');
            if (passwordInput && passwordInput.value) {
                if (passwordInput.value.length < 6) {
                    showError(passwordInput, 'Пароль должен содержать минимум 6 символов');
                    isValid = false;
                }
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

// Показать ошибку валидации
function showError(input, message) {
    clearError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.parentNode.appendChild(errorDiv);
    input.style.borderColor = '#dc3545';
}

// Очистить ошибку валидации
function clearError(input) {
    const existingError = input.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    input.style.borderColor = '#e9ecef';
}

// Функция для просмотра профиля пользователя
function viewUserProfile(username) {
    if (username && username !== getCurrentUsername()) {
        window.open(`/profile/${username}`, '_blank');
    }
}

// Получить имя текущего пользователя
function getCurrentUsername() {
    // Попытка получить из meta тега
    const metaUsername = document.querySelector('meta[name="current-user"]');
    if (metaUsername) {
        return metaUsername.getAttribute('content');
    }
    
    // Попытка получить из данных пользователя
    const userData = document.querySelector('[data-username]');
    if (userData) {
        return userData.getAttribute('data-username');
    }
    
    return null;
}

// Система уведомлений
function setupNotifications() {
    // Создаем контейнер для уведомлений
    const notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
    `;
    document.body.appendChild(notificationContainer);
}

// Показать уведомление
function showNotification(message, type = 'info', duration = 5000) {
    const notificationContainer = document.getElementById('notification-container');
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-left: 4px solid;
        animation: slideIn 0.3s ease;
        max-width: 100%;
    `;
    
    // Цвета для разных типов уведомлений
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.borderLeftColor = colors[type] || colors.info;
    
    notification.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                <div style="font-weight: 600; margin-bottom: 0.25rem;">
                    ${type.charAt(0).toUpperCase() + type.slice(1)}
                </div>
                <div style="color: #666; font-size: 0.9rem;">${message}</div>
            </div>
            <button onclick="this.parentNode.parentNode.remove()" style="
                background: none;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                color: #999;
                padding: 0;
                margin-left: 1rem;
            ">&times;</button>
        </div>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Автоматическое удаление
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, duration);
}

// Анимации для уведомлений
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Функции для использования в других частях приложения
window.showNotification = showNotification;
window.showSuccess = (message) => showNotification(message, 'success');
window.showError = (message) => showNotification(message, 'error');
window.showWarning = (message) => showNotification(message, 'warning');
window.showInfo = (message) => showNotification(message, 'info');

// Улучшение UX для чата
function enhanceChatExperience() {
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        // Автоматическое увеличение высоты поля ввода
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Отправка по Enter
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                document.getElementById('message-form').dispatchEvent(new Event('submit'));
            }
        });
    }
}

// Инициализация улучшений чата
if (document.getElementById('message-input')) {
    enhanceChatExperience();
}

// Функция для проверки онлайн статуса
function checkOnlineStatus() {
    // Проверяем подключение к интернету
    if (!navigator.onLine) {
        showWarning('Нет подключения к интернету');
    }
    
    // Периодическая проверка каждые 30 секунд
    setInterval(() => {
        if (navigator.onLine) {
            // Можно добавить ping к серверу для проверки соединения
        }
    }, 30000);
}

// Инициализация проверки статуса
checkOnlineStatus();

// Обработка ошибок сети
window.addEventListener('online', () => {
    showSuccess('Подключение восстановлено');
});

window.addEventListener('offline', () => {
    showWarning('Потеряно подключение к интернету');
});
