import re
import validators
from urllib.parse import urlparse
from app.models.listing import ContentFilter, ModerationLog, db

class ContentModerator:
    """Класс для модерации контента"""
    
    def __init__(self):
        self.banned_domains = [
            'torrent', 'pirate', 'crack', 'keygen', 'warez',
            'rutracker', 'thepiratebay', 'kickass'
        ]
        
        self.suspicious_patterns = [
            r'\b(бесплатно скачать|даром|free download)\b',
            r'\b(кряк|crack|keygen|серийник)\b',
            r'\b(пиратка|пират|взлом)\b',
            r'\b(телефон|номер телефона|\+\d{10,})\b',
            r'\b(карта|банк|счет|перевод|paypal)\b'
        ]
        
        self.safe_domains = [
            'soundcloud.com',
            'drive.google.com',
            't.me',
            'dropbox.com',
            'mediafire.com',
            'wetransfer.com',
            'youtube.com',
            'youtu.be',
            'bandcamp.com',
            'spotify.com'
        ]
    
    def moderate_listing(self, listing_data):
        """
        Модерирует объявление
        
        Returns:
            dict: {
                'approved': bool,
                'warnings': list,
                'errors': list,
                'needs_review': bool
            }
        """
        result = {
            'approved': True,
            'warnings': [],
            'errors': [],
            'needs_review': False
        }
        
        # Проверяем превью URL
        preview_check = self._check_preview_url(listing_data.get('preview_url', ''))
        if preview_check['error']:
            result['errors'].append(preview_check['message'])
            result['approved'] = False
        elif preview_check['warning']:
            result['warnings'].append(preview_check['message'])
            result['needs_review'] = True
        
        # Проверяем текстовый контент
        text_fields = [
            listing_data.get('description', ''),
            listing_data.get('author', ''),
            listing_data.get('contact', ''),
            listing_data.get('tags', ''),
            listing_data.get('price', '')
        ]
        
        text_content = ' '.join(text_fields).lower()
        
        # Проверяем на запрещенные слова и паттерны
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                result['warnings'].append(f'Обнаружен подозрительный контент: {pattern}')
                result['needs_review'] = True
        
        # Проверяем фильтры из базы данных
        db_filters = ContentFilter.query.filter_by(is_active=True).all()
        for filter_obj in db_filters:
            if filter_obj.is_regex:
                if re.search(filter_obj.pattern, text_content, re.IGNORECASE):
                    if filter_obj.filter_type == 'banned_word':
                        result['errors'].append(f'Обнаружено запрещенное содержимое')
                        result['approved'] = False
                    else:
                        result['warnings'].append(f'Подозрительное содержимое')
                        result['needs_review'] = True
            else:
                if filter_obj.pattern.lower() in text_content:
                    if filter_obj.filter_type == 'banned_domain':
                        result['errors'].append(f'Обнаружен запрещенный домен')
                        result['approved'] = False
                    else:
                        result['warnings'].append(f'Подозрительное содержимое')
                        result['needs_review'] = True
        
        # Проверяем контактную информацию
        contact_check = self._check_contact_info(
            listing_data.get('contact', ''), 
            listing_data.get('description', '')
        )
        if contact_check['warnings']:
            result['warnings'].extend(contact_check['warnings'])
            result['needs_review'] = True
        
        return result
    
    def _check_preview_url(self, url):
        """Проверяет безопасность URL превью"""
        result = {'error': False, 'warning': False, 'message': ''}
        
        if not url:
            result['error'] = True
            result['message'] = 'Отсутствует ссылка на превью'
            return result
        
        # Валидируем URL
        if not validators.url(url):
            result['error'] = True
            result['message'] = 'Некорректная ссылка на превью'
            return result
        
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc
            
            # Проверяем на запрещенные домены
            for banned in self.banned_domains:
                if banned in domain:
                    result['error'] = True
                    result['message'] = f'Запрещенный домен: {domain}'
                    return result
            
            # Проверяем, является ли домен безопасным
            is_safe = any(safe_domain in domain for safe_domain in self.safe_domains)
            
            if not is_safe:
                result['warning'] = True
                result['message'] = f'[ТРЕБУЕТ ПРОВЕРКИ] Неизвестный домен: {domain}'
            
        except Exception as e:
            result['error'] = True
            result['message'] = 'Ошибка при проверке ссылки'
        
        return result
    
    def _check_contact_info(self, contact, description):
        """Проверяет контактную информацию на безопасность"""
        result = {'warnings': []}
        
        text = f"{contact} {description}".lower()
        
        # Проверяем на личные данные
        personal_data_patterns = [
            r'\b\d{10,}\b',  # Телефоны
            r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b',  # Карты
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'  # Email
        ]
        
        for pattern in personal_data_patterns:
            if re.search(pattern, text):
                result['warnings'].append('Возможна утечка личных данных')
                break
        
        return result
    
    def log_moderation(self, listing_id, action, reason, moderator='system'):
        """Записывает лог модерации"""
        log_entry = ModerationLog(
            listing_id=listing_id,
            action=action,
            reason=reason,
            moderator=moderator
        )
        db.session.add(log_entry)
        db.session.commit()
    
    def format_listing_beatssuda_style(self, listing_data):
        """
        Форматирует объявление в стиле BEATSSUDA
        
        Returns:
            str: Отформатированное объявление
        """
        # Определяем эмодзи для типа
        type_emoji = {
            'sell': '🔥 SELL',
            'buy': '💎 BUY', 
            'service': '🛠 SERVICE'
        }
        
        # Формируем красивый блок
        formatted = f"""
{type_emoji.get(listing_data['listing_type'], '📦')} — {listing_data['item_type']}
🧑 Автор: {listing_data['author']}
🎵 Жанр: {listing_data['genre']}"""
        
        if listing_data.get('license'):
            formatted += f"    📌 Лицензия: {listing_data['license']}"
        
        formatted += f"""
🔗 Превью: {listing_data['preview_url']}
💸 Цена: {listing_data['price']}"""
        
        if listing_data.get('includes'):
            formatted += f"""
📦 Что включено: {listing_data['includes']}"""
        
        if listing_data.get('delivery_time'):
            formatted += f"""
⏱ Срок: {listing_data['delivery_time']}"""
        
        if listing_data.get('description'):
            formatted += f"""
✍️ Описание: {listing_data['description']}"""
        
        formatted += f"""
📩 Контакт: {listing_data['contact']}"""
        
        if listing_data.get('tags'):
            tags = [tag.strip() for tag in listing_data['tags'].split() if tag.strip()]
            if tags:
                formatted += f"""
🏷 Теги: {' '.join(tags)}"""
        
        # Добавляем дисклеймер
        formatted += """

⚠️ Администрация LTL18:33bg не несёт ответственности за сделки между пользователями.
Рекомендуем использовать безопасные способы расчёта или предоплату через эскроу."""
        
        return formatted.strip()
    
    def get_moderation_stats(self):
        """Возвращает статистику модерации"""
        from app.models.listing import Listing
        
        total_listings = Listing.query.count()
        approved_listings = Listing.query.filter_by(is_moderated=True, is_active=True).count()
        pending_listings = Listing.query.filter_by(is_moderated=False).count()
        
        return {
            'total': total_listings,
            'approved': approved_listings,
            'pending': pending_listings,
            'approval_rate': (approved_listings / total_listings * 100) if total_listings else 0
        }

# Глобальный экземпляр модератора
content_moderator = ContentModerator()