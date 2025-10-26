// BEATSSUDA Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeCharacterCounter();
});

// Form validation
function initializeFormValidation() {
    const form = document.querySelector('.create-form');
    if (!form) return;
    
    // Check if user is authorized
    const userData = localStorage.getItem('telegram_user');
    if (!userData) {
        showAuthRequiredMessage();
        return;
    }
    
    const requiredFields = form.querySelectorAll('[required]');
    const previewUrlField = form.querySelector('input[name="preview_url"]');
    const tagsField = form.querySelector('input[name="tags"]');
    
    // Real-time validation
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(field);
        });
        
        field.addEventListener('input', function() {
            clearFieldError(field);
        });
    });
    
    // Preview URL validation
    if (previewUrlField) {
        previewUrlField.addEventListener('blur', function() {
            validatePreviewUrl(this);
        });
    }
    
    // Tags validation
    if (tagsField) {
        tagsField.addEventListener('blur', function() {
            validateTags(this);
        });
    }
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        if (previewUrlField && !validatePreviewUrl(previewUrlField)) {
            isValid = false;
        }
        
        if (tagsField && !validateTags(tagsField)) {
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            scrollToFirstError();
        }
    });
}

function validateField(field) {
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'Это поле обязательно для заполнения');
        return false;
    }
    
    clearFieldError(field);
    return true;
}

function validatePreviewUrl(field) {
    const value = field.value.trim();
    
    if (!value) {
        showFieldError(field, 'Ссылка на превью обязательна');
        return false;
    }
    
    // Basic URL validation
    try {
        new URL(value);
    } catch {
        showFieldError(field, 'Введите корректную ссылку');
        return false;
    }
    
    // Check for common audio/file hosting platforms
    const validPlatforms = [
        'soundcloud.com',
        'drive.google.com',
        't.me',
        'dropbox.com',
        'mediafire.com',
        'wetransfer.com'
    ];
    
    const isValidPlatform = validPlatforms.some(platform => 
        value.toLowerCase().includes(platform)
    );
    
    if (!isValidPlatform) {
        showFieldError(field, 'Рекомендуем использовать SoundCloud, Google Drive или Telegram');
        return false;
    }
    
    clearFieldError(field);
    return true;
}

function validateTags(field) {
    const value = field.value.trim();
    
    if (!value) return true; // Tags are optional
    
    const tags = value.split(/\s+/);
    const invalidTags = tags.filter(tag => !tag.startsWith('#') || tag.length < 2);
    
    if (invalidTags.length > 0) {
        showFieldError(field, 'Каждый тег должен начинаться с # и содержать минимум 1 символ');
        return false;
    }
    
    clearFieldError(field);
    return true;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-errors';
    errorDiv.innerHTML = `<span class="error">${message}</span>`;
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = 'var(--error-color)';
}

function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.form-errors');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.style.borderColor = '';
}

function scrollToFirstError() {
    const firstError = document.querySelector('.form-errors');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Character counter for description
function initializeCharacterCounter() {
    const descriptionField = document.querySelector('textarea[name="description"]');
    if (!descriptionField) return;
    
    const maxLength = parseInt(descriptionField.getAttribute('maxlength')) || 200;
    
    // Create counter element
    const counter = document.createElement('div');
    counter.className = 'character-counter';
    counter.style.cssText = `
        font-size: 11px;
        color: var(--text-muted);
        text-align: right;
        margin-top: 4px;
    `;
    
    descriptionField.parentNode.appendChild(counter);
    
    function updateCounter() {
        const currentLength = descriptionField.value.length;
        counter.textContent = `${currentLength}/${maxLength}`;
        
        if (currentLength > maxLength * 0.9) {
            counter.style.color = 'var(--warning-color)';
        } else if (currentLength >= maxLength) {
            counter.style.color = 'var(--error-color)';
        } else {
            counter.style.color = 'var(--text-muted)';
        }
    }
    
    updateCounter();
    descriptionField.addEventListener('input', updateCounter);
}

// Utility functions
function formatPrice(price) {
    // Extract numeric value and currency
    const match = price.match(/(\d+(?:\.\d+)?)\s*(USD|грн|₽)/i);
    if (match) {
        const amount = parseFloat(match[1]);
        const currency = match[2].toUpperCase();
        
        if (currency === 'USD') return amount;
        if (currency === 'ГРН') return amount / 27; // Approximate conversion
        if (currency === '₽') return amount / 60; // Approximate conversion
    }
    
    return 0;
}

// Smooth animations
function addSmoothAnimations() {
    const cards = document.querySelectorAll('.listing-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Telegram Auth
function telegramLogin() {
    // Check if we're in Telegram Web App environment
    if (window.Telegram && window.Telegram.WebApp) {
        try {
            // Initialize Telegram Web App
            const tg = window.Telegram.WebApp;
            tg.ready();
            
            // Get user data from Telegram
            const initData = tg.initDataUnsafe;
            if (initData && initData.user) {
                handleTelegramAuth(initData.user);
            } else {
                showTelegramError('Не удалось получить данные пользователя из Telegram');
            }
        } catch (error) {
            console.error('Telegram WebApp error:', error);
            showTelegramError('Ошибка при подключении к Telegram');
        }
    } else {
        // Not in Telegram environment - show instruction
        showTelegramInstruction();
    }
}

function showTelegramInstruction() {
    const modal = document.createElement('div');
    modal.className = 'auth-modal';
    modal.innerHTML = `
        <div class="auth-modal-content">
            <h3>� Вход через Telegram</h3>
            <div class="telegram-instruction">
                <div class="instruction-step">
                    <div class="step-number">1</div>
                    <div class="step-text">Откройте этот сайт через Telegram бота</div>
                </div>
                <div class="instruction-step">
                    <div class="step-number">2</div>
                    <div class="step-text">Или добавьте наш бот: <strong>@ltl1833bg_bot</strong></div>
                </div>
                <div class="instruction-step">
                    <div class="step-number">3</div>
                    <div class="step-text">Нажмите "Открыть приложение" в боте</div>
                </div>
            </div>
            <div class="instruction-buttons">
                <a href="https://t.me/ltl1833bg_bot" target="_blank" class="telegram-bot-btn">
                    📱 Открыть Telegram бота
                </a>
                <button onclick="closeAuthModal()" class="close-modal-btn">Закрыть</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function showTelegramError(message) {
    const modal = document.createElement('div');
    modal.className = 'auth-modal';
    modal.innerHTML = `
        <div class="auth-modal-content">
            <h3>❌ Ошибка авторизации</h3>
            <p>${message}</p>
            <p>Попробуйте открыть сайт через Telegram бота.</p>
            <button onclick="closeAuthModal()" class="close-modal-btn">Закрыть</button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function handleTelegramAuth(user) {
    // Save user data to localStorage
    const userData = {
        id: user.id,
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name || '',
        login_time: new Date().toISOString()
    };
    
    localStorage.setItem('telegram_user', JSON.stringify(userData));
    
    // Send to backend
    fetch('/api/v1/auth/telegram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Telegram-User': JSON.stringify(userData)
        },
        body: JSON.stringify(userData)
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              updateAuthUI(userData);
              
              // Show success message
              showSuccessMessage('✅ Вы успешно вошли через Telegram!');
              
              // If we're on create page, reload to show form
              if (window.location.pathname === '/create') {
                  setTimeout(() => {
                      window.location.reload();
                  }, 1500);
              }
          }
      }).catch(error => {
          console.error('Auth error:', error);
          updateAuthUI(userData);
      });
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-toast';
    successDiv.textContent = message;
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

function updateAuthUI(user) {
    const loginBtn = document.getElementById('login-btn');
    const userMenu = document.getElementById('user-menu');
    const userName = document.getElementById('user-name');
    
    if (user && loginBtn && userMenu && userName) {
        loginBtn.style.display = 'none';
        userMenu.style.display = 'flex';
        userName.textContent = `@${user.username}`;
    } else if (loginBtn && userMenu) {
        loginBtn.style.display = 'block';
        userMenu.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('telegram_user');
    updateAuthUI(null);
    showToast('Вы успешно вышли из системы', 'success');
    
    // Redirect to home page if on protected page
    if (window.location.pathname === '/create') {
        window.location.href = '/';
    }
}

function closeAuthModal() {
    const modal = document.querySelector('.auth-modal');
    if (modal) {
        modal.remove();
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    const backgroundColor = type === 'success' ? '#28a745' : 
                          type === 'error' ? '#dc3545' : 
                          type === 'warning' ? '#ffc107' : '#17a2b8';
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${backgroundColor};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showAuthRequiredMessage() {
    const form = document.querySelector('.create-form');
    if (!form) return;
    
    // Hide the form
    form.style.display = 'none';
    
    // Show auth required message
    const authMessage = document.createElement('div');
    authMessage.className = 'auth-required-message';
    authMessage.innerHTML = `
        <div class="auth-required-content">
            <h2>🔐 Требуется авторизация</h2>
            <p>Для создания объявлений необходимо войти через Telegram</p>
            <div class="auth-required-steps">
                <div class="auth-step">
                    <span class="auth-step-icon">📱</span>
                    <span>Откройте наш Telegram бот</span>
                </div>
                <div class="auth-step">
                    <span class="auth-step-icon">🚀</span>
                    <span>Нажмите "Открыть приложение"</span>
                </div>
                <div class="auth-step">
                    <span class="auth-step-icon">✨</span>
                    <span>Создавайте объявления!</span>
                </div>
            </div>
            <div class="auth-required-actions">
                <a href="https://t.me/ltl1833bg_bot" target="_blank" class="telegram-bot-btn">
                    📱 Открыть Telegram бота
                </a>
                <a href="/" class="btn btn-secondary">← На главную</a>
            </div>
        </div>
    `;
    
    form.parentNode.insertBefore(authMessage, form);
}

function checkAuthStatus() {
    // Check if we're in Telegram Web App and auto-login
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        const initData = tg.initDataUnsafe;
        
        if (initData && initData.user && !localStorage.getItem('telegram_user')) {
            // Auto-login from Telegram
            handleTelegramAuth(initData.user);
            return;
        }
    }
    
    // Check existing auth
    const userData = localStorage.getItem('telegram_user');
    if (userData) {
        try {
            const user = JSON.parse(userData);
            updateAuthUI(user);
        } catch (e) {
            localStorage.removeItem('telegram_user');
        }
    }
}

// Initialize animations when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addSmoothAnimations();
        checkAuthStatus();
    });
} else {
    addSmoothAnimations();
    checkAuthStatus();
}