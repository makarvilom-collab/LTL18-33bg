from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from app.models.listing import db, init_db, Listing
from app.forms import ListingForm, SearchForm
from app.moderation import content_moderator
from app.api.routes import api_bp
from app.telegram_auth import validate_telegram_user_header
import os
from datetime import datetime

def create_app():
    """Создание и настройка Flask приложения"""
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'beatssuda-secret-key-change-in-production')
    
    # Создаем папку для базы данных если её нет
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Путь к базе данных
    db_path = os.path.join(data_dir, 'beatssuda.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация базы данных
    init_db(app)
    
    # Регистрация API blueprint
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

@app.route('/')
def index():
    """Главная страница"""
    # Получаем параметры фильтрации
    listing_type = request.args.get('type')
    genre = request.args.get('genre')
    item_type = request.args.get('item_type')
    
    # Базовый запрос
    query = Listing.query.filter_by(is_active=True, is_moderated=True)
    
    # Применяем фильтры
    if listing_type:
        query = query.filter(Listing.listing_type == listing_type)
    
    if genre:
        query = query.filter(Listing.genre == genre)
    
    if item_type:
        query = query.filter(Listing.item_type == item_type)
    
    # Получаем объявления, отсортированные по дате (новые первыми)
    listings = query.order_by(Listing.created_at.desc()).limit(50).all()
    
    return render_template('index.html', listings=listings)

@app.route('/listings/<listing_type>')
def listings(listing_type):
    """Страница объявлений по типу"""
    if listing_type not in ['sell', 'buy', 'service']:
        return redirect(url_for('index'))
    
    listings = Listing.query.filter_by(
        listing_type=listing_type,
        is_active=True,
        is_moderated=True
    ).order_by(Listing.created_at.desc()).limit(50).all()
    
    return render_template('index.html', listings=listings)

@app.route('/create', methods=['GET', 'POST'])
def create_listing():
    """Создание нового объявления"""
    form = ListingForm()
    
    # Проверяем авторизацию для POST запросов
    if request.method == 'POST':
        user_header = request.headers.get('X-Telegram-User')
        if not user_header:
            flash('❌ Для создания объявлений необходимо войти через Telegram', 'error')
            return redirect(url_for('index'))
        
        # Валидируем Telegram данные
        is_valid, user_data = validate_telegram_user_header(user_header)
        if not is_valid:
            flash(f'❌ Ошибка авторизации: {user_data}', 'error')
            return redirect(url_for('index'))
    
    if form.validate_on_submit():
        try:
            # Собираем данные из формы
            listing_data = {
                'listing_type': form.listing_type.data,
                'author': form.author.data,
                'contact': form.contact.data,
                'item_type': form.item_type.data,
                'genre': form.genre.data,
                'preview_url': form.preview_url.data,
                'price': form.price.data,
                'license': form.license.data,
                'includes': form.includes.data,
                'delivery_time': form.delivery_time.data,
                'description': form.description.data,
                'tags': form.tags.data
            }
            
            # Модерируем контент
            moderation_result = content_moderator.moderate_listing(listing_data)
            
            if not moderation_result['approved']:
                for error in moderation_result['errors']:
                    flash(f'❌ {error}', 'error')
                return render_template('create_listing.html', form=form)
            
            # Создаем объявление
            listing = Listing(
                listing_type=form.listing_type.data,
                author=form.author.data,
                contact=form.contact.data,
                item_type=form.item_type.data,
                genre=form.genre.data,
                preview_url=form.preview_url.data,
                price=form.price.data,
                license=form.license.data if form.license.data else None,
                includes=form.includes.data if form.includes.data else None,
                delivery_time=form.delivery_time.data if form.delivery_time.data else None,
                description=form.description.data if form.description.data else None,
                tags=form.tags.data if form.tags.data else None,
                is_moderated=not moderation_result['needs_review']
            )
            
            # Вычисляем цену в USD
            listing.price_usd = listing.extract_price_usd()
            
            db.session.add(listing)
            db.session.commit()
            
            # Логируем модерацию
            content_moderator.log_moderation(
                listing.id,
                'auto_approved' if listing.is_moderated else 'needs_review',
                f"Warnings: {'; '.join(moderation_result['warnings'])}" if moderation_result['warnings'] else 'Clean'
            )
            
            # Показываем результат
            if moderation_result['needs_review']:
                flash('⚠️ Объявление создано, но требует проверки модератором', 'warning')
                for warning in moderation_result['warnings']:
                    flash(warning, 'info')
            else:
                flash('✅ Объявление успешно создано и опубликовано!', 'success')
            
            return redirect(url_for('view_listing', listing_id=listing.id))
            
        except Exception as e:
            app.logger.error(f"Error creating listing: {str(e)}")
            flash('❌ Произошла ошибка при создании объявления', 'error')
    
    return render_template('create_listing.html', form=form)

@app.route('/listing/<int:listing_id>')
def view_listing(listing_id):
    """Просмотр конкретного объявления"""
    listing = Listing.query.filter_by(id=listing_id, is_active=True).first_or_404()
    
    # Увеличиваем счетчик просмотров
    listing.views += 1
    db.session.commit()
    
    return render_template('view_listing.html', listing=listing)

@app.route('/search')
def search():
    """Поиск объявлений"""
    form = SearchForm()
    listings = []
    
    if request.args.get('query'):
        query_text = request.args.get('query', '').strip()
        listing_type = request.args.get('listing_type', '')
        genre = request.args.get('genre', '')
        item_type = request.args.get('item_type', '')
        
        # Базовый поиск
        query = Listing.query.filter_by(is_active=True, is_moderated=True)
        
        # Текстовый поиск
        if query_text:
            search_filter = db.or_(
                Listing.description.ilike(f'%{query_text}%'),
                Listing.author.ilike(f'%{query_text}%'),
                Listing.item_type.ilike(f'%{query_text}%'),
                Listing.genre.ilike(f'%{query_text}%'),
                Listing.tags.ilike(f'%{query_text}%')
            )
            query = query.filter(search_filter)
        
        # Фильтры
        if listing_type:
            query = query.filter(Listing.listing_type == listing_type)
        if genre:
            query = query.filter(Listing.genre == genre)
        if item_type:
            query = query.filter(Listing.item_type == item_type)
        
        listings = query.order_by(Listing.created_at.desc()).limit(50).all()
    
    return render_template('search.html', form=form, listings=listings)

@app.route('/stats')
def stats():
    """Статистика платформы"""
    total_listings = Listing.query.filter_by(is_active=True).count()
    active_listings = Listing.query.filter_by(is_active=True, is_moderated=True).count()
    
    # Статистика по типам
    sell_count = Listing.query.filter_by(listing_type='sell', is_active=True, is_moderated=True).count()
    buy_count = Listing.query.filter_by(listing_type='buy', is_active=True, is_moderated=True).count()
    service_count = Listing.query.filter_by(listing_type='service', is_active=True, is_moderated=True).count()
    
    # Популярные жанры
    genre_stats = db.session.query(
        Listing.genre,
        db.func.count(Listing.id).label('count')
    ).filter_by(is_active=True, is_moderated=True).group_by(Listing.genre).order_by(db.text('count DESC')).limit(10).all()
    
    moderation_stats = content_moderator.get_moderation_stats()
    
    stats_data = {
        'listings': {
            'total': total_listings,
            'active': active_listings,
            'sell': sell_count,
            'buy': buy_count,
            'service': service_count
        },
        'genres': genre_stats,
        'moderation': moderation_stats
    }
    
    return render_template('stats.html', stats=stats_data)

@app.route('/track-contact/<int:listing_id>')
def track_contact(listing_id):
    """Отслеживание клика по контакту"""
    listing = Listing.query.filter_by(id=listing_id, is_active=True).first_or_404()
    
    # Увеличиваем счетчик кликов по контакту
    listing.contacts_clicked += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'contact': listing.contact,
        'clicks': listing.contacts_clicked
    })

# Обработчики ошибок
@app.errorhandler(404)
def not_found(error):
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

# Создаем экземпляр приложения для хостинга
app = create_app()

if __name__ == '__main__':
    # Создаем таблицы базы данных
    with app.app_context():
        db.create_all()
    
    # Получаем порт от хостинга или используем 5001 для локальной разработки
    import os
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)