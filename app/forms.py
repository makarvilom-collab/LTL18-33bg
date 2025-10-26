from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, URLField
from wtforms.validators import DataRequired, Length, URL, Optional, Regexp
import re

class ListingForm(FlaskForm):
    """Форма для создания объявления"""
    
    listing_type = SelectField(
        'Тип объявления',
        choices=[
            ('sell', 'Продажа'),
            ('buy', 'Покупка'),
            ('service', 'Услуга')
        ],
        validators=[DataRequired(message='Выберите тип объявления')]
    )
    
    author = StringField(
        'Ваш ник',
        validators=[
            DataRequired(message='Укажите ваш ник'),
            Length(min=2, max=100, message='Ник должен быть от 2 до 100 символов')
        ]
    )
    
    contact = StringField(
        'Контакт для связи',
        validators=[
            DataRequired(message='Укажите контакт для связи'),
            Length(min=2, max=100, message='Контакт должен быть от 2 до 100 символов')
        ]
    )
    
    item_type = SelectField(
        'Тип товара/услуги',
        choices=[
            ('бит', 'Бит'),
            ('луп', 'Луп'),
            ('драм-кит', 'Драм-кит'),
            ('пресет', 'Пресет'),
            ('сведение', 'Сведение'),
            ('мастеринг', 'Мастеринг'),
            ('проект', 'Проект'),
            ('другое', 'Другое')
        ],
        validators=[DataRequired(message='Выберите тип товара/услуги')]
    )
    
    genre = SelectField(
        'Жанр',
        choices=[
            ('trap', 'Trap'),
            ('drill', 'Drill'),
            ('rnb', 'R&B'),
            ('lo-fi', 'Lo-Fi'),
            ('house', 'House'),
            ('hip-hop', 'Hip-Hop'),
            ('pop', 'Pop'),
            ('electronic', 'Electronic'),
            ('rock', 'Rock'),
            ('любой', 'Любой'),
            ('другой', 'Другой')
        ],
        validators=[DataRequired(message='Выберите жанр')]
    )
    
    preview_url = URLField(
        'Ссылка на превью',
        validators=[
            DataRequired(message='Ссылка на превью обязательна'),
            URL(message='Введите корректную ссылку')
        ]
    )
    
    price = StringField(
        'Цена',
        validators=[
            DataRequired(message='Укажите цену'),
            Length(min=1, max=100, message='Цена должна быть от 1 до 100 символов')
        ]
    )
    
    license = SelectField(
        'Лицензия',
        choices=[
            ('', 'Не указана'),
            ('exclusive', 'Exclusive'),
            ('non-exclusive', 'Non-exclusive'),
            ('lease', 'Lease'),
            ('custom', 'По договору')
        ],
        validators=[Optional()]
    )
    
    includes = StringField(
        'Что включено',
        validators=[
            Optional(),
            Length(max=200, message='Максимум 200 символов')
        ]
    )
    
    delivery_time = StringField(
        'Срок доставки',
        validators=[
            Optional(),
            Length(max=100, message='Максимум 100 символов')
        ]
    )
    
    description = TextAreaField(
        'Описание',
        validators=[
            Optional(),
            Length(max=200, message='Максимум 200 символов')
        ]
    )
    
    tags = StringField(
        'Теги',
        validators=[
            Optional(),
            Length(max=200, message='Максимум 200 символов')
        ]
    )
    
    def validate_preview_url(self, field):
        """Дополнительная валидация ссылки на превью"""
        url = field.data.lower()
        
        # Рекомендуемые платформы
        safe_platforms = [
            'soundcloud.com',
            'drive.google.com',
            't.me',
            'dropbox.com',
            'mediafire.com',
            'wetransfer.com'
        ]
        
        # Проверяем, содержит ли URL одну из безопасных платформ
        if not any(platform in url for platform in safe_platforms):
            # Это предупреждение, но не ошибка
            pass
    
    def validate_author(self, field):
        """Валидация ника автора"""
        author = field.data.strip()
        
        # Проверяем, что ник начинается с @ если это телеграм ник
        if author and not author.startswith('@') and len(author) > 0:
            # Автоматически добавляем @ если это похоже на телеграм ник
            if re.match(r'^[a-zA-Z0-9_]{3,}$', author):
                field.data = '@' + author
    
    def validate_contact(self, field):
        """Валидация контакта"""
        contact = field.data.strip()
        
        # Проверяем, что контакт начинается с @ если это телеграм ник
        if contact and not contact.startswith('@') and len(contact) > 0:
            # Автоматически добавляем @ если это похоже на телеграм ник
            if re.match(r'^[a-zA-Z0-9_]{3,}$', contact):
                field.data = '@' + contact
    
    def validate_tags(self, field):
        """Валидация тегов"""
        if not field.data:
            return
            
        tags_str = field.data.strip()
        if not tags_str:
            return
            
        # Разбиваем теги по пробелам
        tags = tags_str.split()
        
        invalid_tags = []
        for tag in tags:
            # Каждый тег должен начинаться с # и содержать минимум 2 символа
            if not tag.startswith('#') or len(tag) < 2:
                invalid_tags.append(tag)
        
        if invalid_tags:
            raise ValueError(f'Некорректные теги: {", ".join(invalid_tags)}. Каждый тег должен начинаться с # и содержать минимум 1 символ.')
    
    def validate_price(self, field):
        """Валидация цены"""
        price = field.data.strip().lower()
        
        # Проверяем базовые форматы цен
        valid_patterns = [
            r'\d+\s*(usd|долл|доллар)',  # USD
            r'\d+\s*(грн|гривен)',       # Гривны  
            r'\d+\s*₽',                  # Рубли
            r'barter',                   # Бартер
            r'по договору',              # По договору
            r'договор'                   # Договор
        ]
        
        is_valid = any(re.search(pattern, price) for pattern in valid_patterns)
        
        if not is_valid:
            # Это предупреждение, цена может быть в любом формате
            pass

class SearchForm(FlaskForm):
    """Форма для поиска объявлений"""
    
    query = StringField(
        'Поиск',
        validators=[
            Optional(),
            Length(max=100, message='Максимум 100 символов')
        ]
    )
    
    listing_type = SelectField(
        'Тип',
        choices=[
            ('', 'Все'),
            ('sell', 'Продажа'),
            ('buy', 'Покупка'),
            ('service', 'Услуга')
        ],
        validators=[Optional()]
    )
    
    genre = SelectField(
        'Жанр',
        choices=[
            ('', 'Все'),
            ('trap', 'Trap'),
            ('drill', 'Drill'),
            ('rnb', 'R&B'),
            ('lo-fi', 'Lo-Fi'),
            ('house', 'House'),
            ('hip-hop', 'Hip-Hop'),
            ('другой', 'Другой')
        ],
        validators=[Optional()]
    )
    
    item_type = SelectField(
        'Товар/Услуга',
        choices=[
            ('', 'Все'),
            ('бит', 'Бит'),
            ('луп', 'Луп'),
            ('драм-кит', 'Драм-кит'),
            ('пресет', 'Пресет'),
            ('сведение', 'Сведение'),
            ('мастеринг', 'Мастеринг'),
            ('проект', 'Проект')
        ],
        validators=[Optional()]
    )