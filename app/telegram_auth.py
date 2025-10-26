"""
Telegram Web Apps Authentication Module
"""
import os
import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"

def validate_telegram_auth(init_data):
    """
    Валидация данных авторизации Telegram Web Apps
    """
    try:
        # Парсим init_data
        data = dict(parse_qsl(unquote(init_data)))
        
        # Извлекаем hash для проверки
        received_hash = data.pop('hash', None)
        if not received_hash:
            return False, "No hash provided"
        
        # Создаем строку для проверки подписи
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(data.items())])
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            "WebAppData".encode(),
            TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем hash
        if calculated_hash == received_hash:
            # Извлекаем данные пользователя
            user_data = json.loads(data.get('user', '{}'))
            return True, user_data
        else:
            return False, "Invalid hash"
            
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_telegram_user_header(user_header):
    """
    Простая валидация пользователя из заголовка (для обратной совместимости)
    """
    try:
        user_data = json.loads(user_header)
        required_fields = ['id', 'username', 'first_name']
        
        # Проверяем наличие обязательных полей
        for field in required_fields:
            if field not in user_data:
                return False, f"Missing field: {field}"
        
        # Проверяем, что ID - число
        if not isinstance(user_data['id'], int):
            return False, "Invalid user ID"
            
        return True, user_data
        
    except json.JSONDecodeError:
        return False, "Invalid JSON"
    except Exception as e:
        return False, f"Validation error: {str(e)}")