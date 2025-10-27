#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
from datetime import datetime

# Добавляем текущую папку в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импорты наших модулей
try:
    from app.models.listing import db, init_db, Listing
    from app.forms import ListingForm, SearchForm
    from app.moderation import content_moderator
    from app.api.routes import api_bp
    from app.telegram_auth import validate_telegram_user_header
except ImportError as e:
    print(f"Import error: {e}")
    # Простая заглушка для тестирования
    db = None

# Создаем Flask приложение
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# Конфигурация
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'beatssuda-secret-key-change-in-production')

# Простой роут для тестирования
@app.route('/')
def index():
    """Главная страница"""
    try:
        return render_template('index.html', 
                             listings=[],
                             recent_listings=[],
                             stats={'total': 0, 'today': 0})
    except Exception as e:
        return f"""
        <html>
        <head><title>BEATSSUDA Platform</title></head>
        <body>
            <h1>🎵 LTL18:33BG - BEATSSUDA Platform</h1>
            <p>Платформа для продажи и покупки битов</p>
            <p>Status: Loading... ({str(e)})</p>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Проверка работоспособности"""
    return jsonify({"status": "ok", "platform": "BEATSSUDA"})

# Настройка базы данных если модули загрузились
if db is not None:
    try:
        # Создаем папку для базы данных
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Путь к базе данных
        database_path = os.path.join(data_dir, 'beatssuda.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Инициализация базы данных
        init_db(app)
        
        # Регистрация API Blueprint
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # Создание таблиц
        with app.app_context():
            db.create_all()
            
    except Exception as e:
        print(f"Database setup error: {e}")

# Для локального запуска
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)