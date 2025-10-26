#!/usr/bin/env python3
"""
Тестовый скрипт для API BEATSSUDA Platform
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_get_listings():
    """Тест получения всех объявлений"""
    print("🔍 Тестируем получение объявлений...")
    response = requests.get(f"{BASE_URL}/api/v1/listings")
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Количество объявлений: {len(data.get('data', []))}")
        print("✅ Тест пройден")
    else:
        print("❌ Тест не пройден")
    print()

def test_search_listings():
    """Тест поиска объявлений"""
    print("🔍 Тестируем поиск объявлений...")
    response = requests.get(f"{BASE_URL}/api/v1/listings/search", params={"q": "trap"})
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Найдено объявлений: {len(data.get('data', []))}")
        print("✅ Тест пройден")
    else:
        print("❌ Тест не пройден")
    print()

def test_get_stats():
    """Тест получения статистики"""
    print("📊 Тестируем получение статистики...")
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Статистика: {data.get('data', {})}")
        print("✅ Тест пройден")
    else:
        print("❌ Тест не пройден")
    print()

def test_create_listing():
    """Тест создания объявления"""
    print("📝 Тестируем создание объявления...")
    
    listing_data = {
        "listing_type": "sell",
        "author": "@test_user",
        "contact": "@test_user",
        "item_type": "бит",
        "genre": "trap",
        "preview_url": "https://soundcloud.com/test/track",
        "price": "50 USD",
        "license": "non-exclusive",
        "includes": "wav, stems",
        "delivery_time": "24 часа",
        "description": "Тестовый трап бит для проверки API",
        "tags": "#бит #продам #trap #test"
    }
    
    # Имитация Telegram пользователя
    headers = {
        "Content-Type": "application/json",
        "X-Telegram-User": json.dumps({
            "id": 12345,
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User"
        })
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/listings", 
                           json=listing_data, 
                           headers=headers)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        listing_id = data.get('data', {}).get('id')
        print(f"Создано объявление с ID: {listing_id}")
        print("✅ Тест пройден")
        return listing_id
    else:
        print(f"Ошибка: {response.text}")
        print("❌ Тест не пройден")
        return None
    print()

def test_get_single_listing(listing_id):
    """Тест получения одного объявления"""
    if not listing_id:
        print("⏭️ Пропускаем тест получения объявления - нет ID")
        return
        
    print(f"📄 Тестируем получение объявления {listing_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/listings/{listing_id}")
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Объявление: {data.get('data', {}).get('item_type')} - {data.get('data', {}).get('price')}")
        print("✅ Тест пройден")
    else:
        print("❌ Тест не пройден")
    print()

def test_get_formatted_listing(listing_id):
    """Тест получения отформатированного объявления"""
    if not listing_id:
        print("⏭️ Пропускаем тест форматирования - нет ID")
        return
        
    print(f"📝 Тестируем форматирование объявления {listing_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/listings/{listing_id}/formatted")
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        formatted_text = data.get('data', {}).get('formatted_text', '')
        print(f"Отформатированный текст (первые 100 символов):\n{formatted_text[:100]}...")
        print("✅ Тест пройден")
    else:
        print("❌ Тест не пройден")
    print()

def main():
    """Запуск всех тестов"""
    print("🚀 Запуск тестов API BEATSSUDA Platform\n")
    
    # Базовые тесты
    test_get_listings()
    test_search_listings()
    test_get_stats()
    
    # Тесты создания и получения
    listing_id = test_create_listing()
    test_get_single_listing(listing_id)
    test_get_formatted_listing(listing_id)
    
    print("🏁 Тестирование завершено!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения!")
        print("Убедитесь, что Flask сервер запущен на http://127.0.0.1:5001")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")