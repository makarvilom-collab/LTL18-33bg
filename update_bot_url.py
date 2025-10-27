#!/usr/bin/env python3
"""
Обновление бота с новым URL Vercel
"""
import requests
import json

# Конфигурация
BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
NEW_PLATFORM_URL = "https://ltl-18-33bg.vercel.app"

def update_menu_button():
    """Обновляет кнопку меню бота с новым URL"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton"
    
    menu_button = {
        "type": "web_app",
        "text": "BEATSSUDA Platform",
        "web_app": {
            "url": NEW_PLATFORM_URL
        }
    }
    
    response = requests.post(url, json={"menu_button": menu_button})
    
    if response.status_code == 200:
        result = response.json()
        if result["ok"]:
            print("✅ Кнопка меню обновлена с новым URL")
            return True
        else:
            print(f"❌ Ошибка обновления кнопки меню: {result}")
            return False
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        return False

def test_new_site():
    """Тестирует доступность нового сайта"""
    try:
        response = requests.get(NEW_PLATFORM_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Сайт {NEW_PLATFORM_URL} доступен")
            return True
        else:
            print(f"❌ Сайт возвращает код: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к сайту: {e}")
        return False

def main():
    print("🔄 Обновление бота с новым URL Vercel")
    print("=" * 50)
    print(f"🌐 Новый URL: {NEW_PLATFORM_URL}")
    print()
    
    # Тестируем сайт
    print("1️⃣ Тестируем доступность сайта...")
    if not test_new_site():
        print("❌ Сайт недоступен! Отменяем обновление.")
        return False
    
    # Обновляем кнопку меню
    print("2️⃣ Обновляем кнопку меню бота...")
    if not update_menu_button():
        print("❌ Не удалось обновить кнопку меню!")
        return False
    
    print()
    print("🎉 Успешно обновлено!")
    print(f"🤖 Бот @ltl1833bg_bot теперь использует: {NEW_PLATFORM_URL}")
    print("🔗 Протестируй: https://t.me/ltl1833bg_bot")
    
    return True

if __name__ == "__main__":
    main()