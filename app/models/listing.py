from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()

class Listing(db.Model):
    """Модель для объявлений"""
    __tablename__ = 'listings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Основная информация
    listing_type = db.Column(db.String(10), nullable=False)  # sell, buy, service
    author = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    
    # Информация о товаре/услуге
    item_type = db.Column(db.String(50), nullable=False)  # бит, сведение, мастеринг и т.д.
    genre = db.Column(db.String(50), nullable=False)
    
    # Медиа и контент
    preview_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    # Коммерческая информация
    price = db.Column(db.String(100), nullable=False)
    price_usd = db.Column(db.Float)  # Для фильтрации, конвертированная в USD
    license = db.Column(db.String(50))
    includes = db.Column(db.String(200))
    delivery_time = db.Column(db.String(100))
    
    # Теги
    tags = db.Column(db.Text)  # JSON строка с тегами
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_moderated = db.Column(db.Boolean, default=False)
    
    # Статистика
    views = db.Column(db.Integer, default=0)
    contacts_clicked = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Listing {self.id}: {self.item_type} by {self.author}>'
    
    @property
    def formatted_tags(self):
        """Возвращает список тегов"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split() if tag.strip()]
    
    @property
    def is_preview_safe(self):
        """Проверяет, безопасна ли ссылка на превью"""
        safe_domains = [
            'soundcloud.com',
            'drive.google.com',
            't.me',
            'dropbox.com',
            'mediafire.com',
            'wetransfer.com'
        ]
        return any(domain in self.preview_url.lower() for domain in safe_domains)
    
    def extract_price_usd(self):
        """Извлекает цену в USD для фильтрации"""
        if not self.price:
            return 0
            
        # Ищем числовое значение и валюту
        match = re.search(r'(\d+(?:\.\d+)?)\s*(USD|usd|грн|₽|rub)', self.price, re.IGNORECASE)
        if match:
            amount = float(match.group(1))
            currency = match.group(2).upper()
            
            # Конвертируем в USD (примерные курсы)
            if currency in ['USD']:
                return amount
            elif currency in ['ГРН']:
                return amount / 27  # Примерный курс
            elif currency in ['₽', 'RUB']:
                return amount / 60  # Примерный курс
        
        return 0
    
    def to_dict(self):
        """Преобразует объект в словарь для API"""
        return {
            'id': self.id,
            'listing_type': self.listing_type,
            'author': self.author,
            'contact': self.contact,
            'item_type': self.item_type,
            'genre': self.genre,
            'preview_url': self.preview_url,
            'description': self.description,
            'price': self.price,
            'price_usd': self.price_usd,
            'license': self.license,
            'includes': self.includes,
            'delivery_time': self.delivery_time,
            'tags': self.formatted_tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'is_moderated': self.is_moderated,
            'views': self.views,
            'contacts_clicked': self.contacts_clicked
        }

class ModerationLog(db.Model):
    """Лог модерации"""
    __tablename__ = 'moderation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # approved, rejected, flagged
    reason = db.Column(db.Text)
    moderator = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    listing = db.relationship('Listing', backref=db.backref('moderation_logs', lazy=True))

class ContentFilter(db.Model):
    """Фильтры для модерации контента"""
    __tablename__ = 'content_filters'
    
    id = db.Column(db.Integer, primary_key=True)
    filter_type = db.Column(db.String(50), nullable=False)  # banned_word, banned_domain, etc.
    pattern = db.Column(db.String(200), nullable=False)
    is_regex = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContentFilter {self.filter_type}: {self.pattern}>'

class User(db.Model):
    """Пользователи (для будущей интеграции с ботом)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Статистика
    listings_created = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Настройки
    is_banned = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username or self.first_name}>'

def init_db(app):
    """Инициализация базы данных"""
    db.init_app(app)
    
    with app.app_context():
        # Создаем таблицы
        db.create_all()
        
        # Добавляем базовые фильтры контента
        if ContentFilter.query.count() == 0:
            default_filters = [
                ContentFilter(
                    filter_type='banned_domain',
                    pattern='torrent',
                    is_regex=False
                ),
                ContentFilter(
                    filter_type='banned_domain',
                    pattern='crack',
                    is_regex=False
                ),
                ContentFilter(
                    filter_type='banned_word',
                    pattern=r'\b(бесплатно скачать|даром|free download)\b',
                    is_regex=True
                ),
                ContentFilter(
                    filter_type='banned_word',
                    pattern=r'\b(кряк|crack|keygen)\b',
                    is_regex=True
                )
            ]
            
            for filter_obj in default_filters:
                db.session.add(filter_obj)
            
            db.session.commit()
            print("✅ Базовые фильтры контента добавлены")