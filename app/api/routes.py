from flask import Blueprint, request, jsonify, current_app
from app.models.listing import Listing, db
from app.moderation import content_moderator
from datetime import datetime
import re

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/listings', methods=['GET'])
def get_listings():
    """Получить список объявлений с фильтрацией"""
    try:
        # Параметры фильтрации
        listing_type = request.args.get('type')
        genre = request.args.get('genre')
        item_type = request.args.get('item_type')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Базовый запрос
        query = Listing.query.filter_by(is_active=True, is_moderated=True)
        
        # Применяем фильтры
        if listing_type:
            query = query.filter(Listing.listing_type == listing_type)
        
        if genre:
            query = query.filter(Listing.genre == genre)
        
        if item_type:
            query = query.filter(Listing.item_type == item_type)
        
        # Сортировка по дате создания (новые первыми)
        query = query.order_by(Listing.created_at.desc())
        
        # Пагинация
        listings = query.paginate(
            page=page, 
            per_page=per_page, 
            max_per_page=100,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'listings': [listing.to_dict() for listing in listings.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': listings.total,
                    'pages': listings.pages,
                    'has_next': listings.has_next,
                    'has_prev': listings.has_prev
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting listings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения объявлений'
        }), 500

@api_bp.route('/listings', methods=['POST'])
def create_listing():
    """Создать новое объявление"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Данные не предоставлены'
            }), 400
        
        # Валидация обязательных полей
        required_fields = ['listing_type', 'author', 'contact', 'item_type', 'genre', 'preview_url', 'price']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
            }), 400
        
        # Модерация контента
        moderation_result = content_moderator.moderate_listing(data)
        
        if not moderation_result['approved']:
            return jsonify({
                'success': False,
                'error': 'Объявление не прошло модерацию',
                'details': moderation_result['errors']
            }), 400
        
        # Создаем новое объявление
        listing = Listing(
            listing_type=data['listing_type'],
            author=data['author'],
            contact=data['contact'],
            item_type=data['item_type'],
            genre=data['genre'],
            preview_url=data['preview_url'],
            price=data['price'],
            license=data.get('license'),
            includes=data.get('includes'),
            delivery_time=data.get('delivery_time'),
            description=data.get('description'),
            tags=data.get('tags'),
            is_moderated=not moderation_result['needs_review']
        )
        
        # Вычисляем цену в USD для фильтрации
        listing.price_usd = listing.extract_price_usd()
        
        db.session.add(listing)
        db.session.commit()
        
        # Логируем модерацию
        content_moderator.log_moderation(
            listing.id,
            'auto_approved' if listing.is_moderated else 'needs_review',
            f"Warnings: {'; '.join(moderation_result['warnings'])}" if moderation_result['warnings'] else 'Clean'
        )
        
        response_data = {
            'success': True,
            'data': {
                'listing': listing.to_dict(),
                'moderation': {
                    'approved': moderation_result['approved'],
                    'needs_review': moderation_result['needs_review'],
                    'warnings': moderation_result['warnings']
                }
            }
        }
        
        if moderation_result['needs_review']:
            response_data['message'] = 'Объявление создано, но требует проверки модератором'
        
        return jsonify(response_data), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating listing: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка создания объявления'
        }), 500

@api_bp.route('/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Получить конкретное объявление"""
    try:
        listing = Listing.query.filter_by(id=listing_id, is_active=True).first()
        
        if not listing:
            return jsonify({
                'success': False,
                'error': 'Объявление не найдено'
            }), 404
        
        # Увеличиваем счетчик просмотров
        listing.views += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'listing': listing.to_dict()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting listing {listing_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения объявления'
        }), 500

@api_bp.route('/listings/<int:listing_id>/contact', methods=['POST'])
def track_contact_click(listing_id):
    """Отследить клик по контакту"""
    try:
        listing = Listing.query.filter_by(id=listing_id, is_active=True).first()
        
        if not listing:
            return jsonify({
                'success': False,
                'error': 'Объявление не найдено'
            }), 404
        
        # Увеличиваем счетчик кликов по контакту
        listing.contacts_clicked += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'contact': listing.contact,
                'clicks': listing.contacts_clicked
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error tracking contact click for listing {listing_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка отслеживания'
        }), 500

@api_bp.route('/listings/<int:listing_id>/formatted', methods=['GET'])
def get_formatted_listing(listing_id):
    """Получить объявление в отформатированном виде для бота"""
    try:
        listing = Listing.query.filter_by(id=listing_id, is_active=True).first()
        
        if not listing:
            return jsonify({
                'success': False,
                'error': 'Объявление не найдено'
            }), 404
        
        # Форматируем в стиле BEATSSUDA
        formatted_text = content_moderator.format_listing_beatssuda_style(listing.to_dict())
        
        return jsonify({
            'success': True,
            'data': {
                'listing_id': listing.id,
                'formatted_text': formatted_text,
                'raw_data': listing.to_dict()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error formatting listing {listing_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка форматирования объявления'
        }), 500

@api_bp.route('/listings/search', methods=['GET'])
def search_listings():
    """Поиск объявлений по тексту"""
    try:
        query_text = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Поисковый запрос не указан'
            }), 400
        
        # Поиск по нескольким полям
        search_filter = db.or_(
            Listing.description.ilike(f'%{query_text}%'),
            Listing.author.ilike(f'%{query_text}%'),
            Listing.item_type.ilike(f'%{query_text}%'),
            Listing.genre.ilike(f'%{query_text}%'),
            Listing.tags.ilike(f'%{query_text}%')
        )
        
        query = Listing.query.filter(
            search_filter,
            Listing.is_active == True,
            Listing.is_moderated == True
        ).order_by(Listing.created_at.desc())
        
        listings = query.paginate(
            page=page,
            per_page=per_page,
            max_per_page=100,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'query': query_text,
                'listings': [listing.to_dict() for listing in listings.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': listings.total,
                    'pages': listings.pages,
                    'has_next': listings.has_next,
                    'has_prev': listings.has_prev
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error searching listings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка поиска'
        }), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Получить статистику платформы"""
    try:
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
        ).filter_by(is_active=True, is_moderated=True).group_by(Listing.genre).order_by(db.text('count DESC')).limit(5).all()
        
        moderation_stats = content_moderator.get_moderation_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'listings': {
                    'total': total_listings,
                    'active': active_listings,
                    'by_type': {
                        'sell': sell_count,
                        'buy': buy_count,
                        'service': service_count
                    }
                },
                'popular_genres': [{'genre': genre, 'count': count} for genre, count in genre_stats],
                'moderation': moderation_stats
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения статистики'
        }), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'success': False,
        'error': 'API endpoint не найден'
    }), 404

@api_bp.route('/auth/telegram', methods=['POST'])
def telegram_auth():
    """Авторизация через Telegram"""
    try:
        data = request.get_json()
        
        if not data or not data.get('id'):
            return jsonify({
                'success': False,
                'error': 'Данные пользователя не предоставлены'
            }), 400
        
        from app.models.listing import User, db
        
        # Ищем пользователя или создаем нового
        user = User.query.filter_by(telegram_id=data['id']).first()
        
        if not user:
            user = User(
                telegram_id=data['id'],
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            db.session.add(user)
        else:
            # Обновляем данные пользователя
            user.username = data.get('username')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.last_activity = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'telegram_id': user.telegram_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_premium': user.is_premium,
                    'listings_created': user.listings_created
                }
            },
            'message': 'Авторизация успешна'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in telegram auth: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка авторизации'
        }), 500

@api_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Проверка статуса авторизации"""
    try:
        # В реальном приложении здесь была бы проверка JWT токена или сессии
        # Пока возвращаем базовый ответ
        return jsonify({
            'success': True,
            'data': {
                'authenticated': False,
                'message': 'Система авторизации работает в демо-режиме'
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error checking auth status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка проверки авторизации'
        }), 500

@api_bp.errorhandler(500)
def api_server_error(error):
    current_app.logger.error(f"API Server Error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Внутренняя ошибка сервера'
    }), 500