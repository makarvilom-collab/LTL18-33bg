#!/usr/bin/env python3
"""
Автоматическая настройка Telegram бота @ltl1833bg_bot для Web App
"""
import requests
import json

BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
WEBSITE_URL = "https://ltl18-33bg.onrender.com"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def setup_bot_commands():
    """Настраиваем команды бота"""
    commands = [
        {"command": "start", "description": "Запустить платформу BEATSSUDA"},
        {"command": "app", "description": "Открыть LTL18:33BG Platform"},
        {"command": "help", "description": "Помощь по использованию"}
    ]
    
    response = requests.post(f"{BASE_URL}/setMyCommands", json={
        "commands": commands
    })
    
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print("✅ Команды бота настроены:")
            for cmd in commands:
                print(f"  /{cmd['command']} - {cmd['description']}")
        else:
            print(f"❌ Ошибка настройки команд: {result}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")

def setup_bot_description():
    """Настраиваем описание бота"""
    description = """🎵 LTL18:33BG - BEATSSUDA Community Platform

Платформа для продажи и покупки битов, услуг сведения и мастеринга.

Минимал, чисто, по сути.

Нажмите /start чтобы открыть платформу."""
    
    response = requests.post(f"{BASE_URL}/setMyDescription", json={
        "description": description
    })
    
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print("✅ Описание бота настроено")
        else:
            print(f"❌ Ошибка настройки описания: {result}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")

def setup_bot_short_description():
    """Настраиваем короткое описание"""
    short_description = "🎵 BEATSSUDA Platform - биты, сведение, мастеринг"
    
    response = requests.post(f"{BASE_URL}/setMyShortDescription", json={
        "short_description": short_description
    })
    
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print("✅ Короткое описание настроено")
        else:
            print(f"❌ Ошибка настройки короткого описания: {result}")

def setup_menu_button():
    """Настраиваем кнопку меню с Web App"""
    menu_button = {
        "type": "web_app",
        "text": "🎵 Открыть BEATSSUDA Platform",
        "web_app": {
            "url": WEBSITE_URL
        }
    }
    
    response = requests.post(f"{BASE_URL}/setChatMenuButton", json={
        "menu_button": menu_button
    })
    
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print(f"✅ Кнопка меню настроена: {WEBSITE_URL}")
        else:
            print(f"❌ Ошибка настройки кнопки меню: {result}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")

def get_bot_info():
    """Получаем информацию о боте"""
    response = requests.get(f"{BASE_URL}/getMe")
    
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            bot_info = result['result']
            print("\n🤖 Информация о боте:")
            print(f"  Имя: {bot_info['first_name']}")
            print(f"  Username: @{bot_info['username']}")
            print(f"  ID: {bot_info['id']}")
            print(f"  Поддерживает Web Apps: {bot_info.get('supports_web_apps', 'Неизвестно')}")
            return bot_info
        else:
            print(f"❌ Ошибка получения информации: {result}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
    return None

def create_start_message():
    """Создаем приветственное сообщение для команды /start"""
    return f"""🎵 *LTL18:33BG - BEATSSUDA Platform*

Добро пожаловать на платформу для продажи и покупки битов, услуг сведения и мастеринга\!

🔥 *Что можно делать:*
• Продавать и покупать биты
• Заказывать сведение и мастеринг
• Находить нужные услуги

Нажмите кнопку ниже или команду /app чтобы открыть платформу:

[Открыть BEATSSUDA Platform]({WEBSITE_URL})

_Минимал, чисто, по сути\\._"""

def main():
    """Основная функция настройки бота"""
    print("🚀 Настройка Telegram бота для BEATSSUDA Platform")
    print("=" * 60)
    
    # Получаем информацию о боте
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Не удалось получить информацию о боте")
        return
    
    print(f"\n🔧 Настройка бота @{bot_info['username']}...")
    print(f"📱 URL платформы: {WEBSITE_URL}")
    print()
    
    # Настраиваем команды
    setup_bot_commands()
    
    # Настраиваем описания
    setup_bot_description()
    setup_bot_short_description()
    
    # Настраиваем кнопку меню
    setup_menu_button()
    
    # Выводим приветственное сообщение
    print(f"\n📝 Рекомендуемый текст для команды /start:")
    print("-" * 40)
    print(create_start_message())
    print("-" * 40)
    
    print(f"\n✅ Настройка завершена!")
    print(f"🤖 Бот @{bot_info['username']} готов к работе!")
    print(f"🌐 Откройте бота и нажмите /start для тестирования")
    
    print(f"\n🔗 Ссылка на бота: https://t.me/{bot_info['username']}")

if __name__ == "__main__":
    main()