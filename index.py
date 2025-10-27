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
    
    # Создаем Flask приложение
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'beatssuda-secret-key-change-in-production')
    
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
    
    @app.route('/')
    def index():
        """Главная страница"""
        try:
            # Получаем все объявления
            all_listings = Listing.query.order_by(Listing.created_at.desc()).all()
            
            # Последние 6 объявлений для главной страницы
            recent_listings = all_listings[:6]
            
            # Статистика
            stats = {
                'total': len(all_listings),
                'today': len([l for l in all_listings if l.created_at.date() == datetime.now().date()])
            }
            
            return render_template('index.html', 
                                 listings=all_listings,
                                 recent_listings=recent_listings,
                                 stats=stats)
        except Exception as e:
            # Fallback если что-то не работает
            return render_template('index.html', 
                                 listings=[],
                                 recent_listings=[],
                                 stats={'total': 0, 'today': 0})

    @app.route('/create', methods=['GET', 'POST'])
    def create_listing():
        """Создание нового объявления"""
        form = ListingForm()
        
        if form.validate_on_submit():
            # Проверяем авторизацию через Telegram
            telegram_user = validate_telegram_user_header(request.headers)
            if not telegram_user:
                flash('Необходима авторизация через Telegram', 'error')
                return redirect(url_for('create_listing'))
            
            # Модерация контента
            title_check = content_moderator.check_text(form.title.data)
            description_check = content_moderator.check_text(form.description.data)
            
            if not title_check['is_appropriate'] or not description_check['is_appropriate']:
                flash('Контент не прошел модерацию', 'error')
                return render_template('create_listing.html', form=form)
            
            # Создаем объявление
            listing = Listing(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                category=form.category.data,
                contact_info=form.contact_info.data,
                user_id=telegram_user.get('id'),
                username=telegram_user.get('username', 'Anonymous')
            )
            
            try:
                db.session.add(listing)
                db.session.commit()
                flash('Объявление успешно создано!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при создании объявления', 'error')
        
        return render_template('create_listing.html', form=form)

    @app.route('/view/<int:listing_id>')
    def view_listing(listing_id):
        """Просмотр объявления"""
        listing = Listing.query.get_or_404(listing_id)
        return render_template('view_listing.html', listing=listing)

    @app.route('/search')
    def search_listings():
        """Поиск объявлений"""
        form = SearchForm()
        listings = []
        
        if request.args.get('query'):
            query = request.args.get('query')
            category = request.args.get('category', '')
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            
            # Базовый поиск
            search = Listing.query.filter(
                Listing.title.contains(query) | 
                Listing.description.contains(query)
            )
            
            # Фильтры
            if category:
                search = search.filter(Listing.category == category)
            if min_price is not None:
                search = search.filter(Listing.price >= min_price)
            if max_price is not None:
                search = search.filter(Listing.price <= max_price)
            
            listings = search.order_by(Listing.created_at.desc()).all()
        
        return render_template('search.html', form=form, listings=listings)

    @app.route('/stats')
    def show_stats():
        """Статистика платформы"""
        try:
            total_listings = Listing.query.count()
            categories_stats = db.session.query(
                Listing.category, 
                db.func.count(Listing.id)
            ).group_by(Listing.category).all()
            
            # Статистика по дням
            from sqlalchemy import func, extract
            daily_stats = db.session.query(
                func.date(Listing.created_at),
                func.count(Listing.id)
            ).group_by(func.date(Listing.created_at)).order_by(func.date(Listing.created_at).desc()).limit(7).all()
            
            stats = {
                'total_listings': total_listings,
                'categories': dict(categories_stats),
                'daily_stats': daily_stats
            }
            
            return render_template('stats.html', stats=stats)
        except Exception as e:
            return render_template('stats.html', stats={'total_listings': 0, 'categories': {}, 'daily_stats': []})

    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html',
                             title='Страница не найдена',
                             message='Извините, запрашиваемая страница не существует.'), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f"Server Error: {str(error)}")
        return render_template('error.html',
                             title='Ошибка сервера',
                             message='Произошла внутренняя ошибка сервера.'), 500

    # Контекстные процессоры
    @app.context_processor
    def inject_globals():
        """Глобальные переменные для шаблонов"""
        return {
            'current_year': datetime.now().year,
            'site_name': 'LTL18:33bg - BEATSSUDA'
        }

    # Вебхук для Telegram бота
    @app.route('/webhook/<token>', methods=['POST'])
    def webhook(token):
        """Обработчик вебхука от Telegram"""
        import requests
        
        BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
        
        if token != BOT_TOKEN:
            return "Unauthorized", 403
        
        try:
            update = request.get_json()
            
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')
                
                if text == '/start':
                    send_telegram_start_message(chat_id)
                elif text == '/app':
                    send_telegram_app_message(chat_id)
                elif text == '/help':
                    send_telegram_help_message(chat_id)
            
            return "OK", 200
            
        except Exception as e:
            app.logger.error(f"Webhook error: {e}")
            return "Error", 500

    def send_telegram_start_message(chat_id):
        """Отправляет приветственное сообщение"""
        import requests
        
        BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
        message = """🎵 *Добро пожаловать в LTL18:33BG \- BEATSSUDA Platform*

Приветствуем\\! Мы \- комьюнити битмейкеров и продюсеров\\.
Помогаем друг другу, делаем звук,
продаём / покупаем / делимся китами и пресетами\\.

🔥 *Здесь вы можете:*
• Покупать и продавать биты
• Заказывать мастеринг и сведение  
• Делиться опытом с комьюнити
• Находить нужные киты и пресеты

*Техподдержка:* @BeatHavenX

Нажмите кнопку ниже чтобы открыть платформу:"""
        
        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "🚀 Открыть BEATSSUDA Platform",
                    "web_app": {"url": "https://ltl-18-33bg.vercel.app"}
                }
            ]]
        }
        
        send_telegram_message_helper(chat_id, message, keyboard)

    def send_telegram_app_message(chat_id):
        """Отправляет сообщение с кнопкой приложения"""
        message = "🚀 *Откройте BEATSSUDA Platform*"
        
        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "📱 Открыть платформу",
                    "web_app": {"url": "https://ltl-18-33bg.vercel.app"}
                }
            ]]
        }
        
        send_telegram_message_helper(chat_id, message, keyboard)

    def send_telegram_help_message(chat_id):
        """Отправляет справочное сообщение"""
        message = """❓ *Помощь по BEATSSUDA Platform*

*Команды:*
/start \- Главное меню
/app \- Открыть платформу
/help \- Эта справка

*Как пользоваться:*
1\\. Нажмите кнопку меню или используйте /app
2\\. Откроется платформа в Telegram
3\\. Покупайте, продавайте, общайтесь\\!

*Техподдержка и модерация:* @BeatHavenX
*Все проблемы писать ему\\!*"""
        
        send_telegram_message_helper(chat_id, message)

    def send_telegram_message_helper(chat_id, text, reply_markup=None):
        """Отправляет сообщение через Telegram Bot API"""
        import requests
        
        BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "MarkdownV2"
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        try:
            response = requests.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    # Создание таблиц
    with app.app_context():
        db.create_all()

except ImportError as e:
    print(f"Import error: {e}")
    # Создаем простое приложение если модули не загрузились
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return '''
        <html>
        <head><title>BEATSSUDA Platform</title></head>
        <body>
            <h1>🎵 LTL18:33BG - BEATSSUDA Platform</h1>
            <p>Платформа для продажи и покупки битов</p>
            <p>Status: Import error - contact @BeatHavenX</p>
        </body>
        </html>
        '''

@app.route('/health')
def health():
    """Проверка работоспособности"""
    return jsonify({"status": "ok", "platform": "BEATSSUDA"})

# Для локального запуска
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)