#!/usr/bin/env python3
"""
Настройка команд и описаний бота
"""
import requests
import json

# Конфигурация
BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
PLATFORM_URL = "https://ltl-18-33bg.vercel.app"

def set_start_command_description():
    """Настраивает описание команды /start"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    
    commands = [
        {
            "command": "start",
            "description": "🎵 Добро пожаловать в BEATSSUDA Platform"
        },
        {
            "command": "app", 
            "description": "📱 Открыть платформу для покупки/продажи битов"
        },
        {
            "command": "help",
            "description": "❓ Помощь по использованию платформы"
        }
    ]
    
    response = requests.post(url, json={"commands": commands})
    
    if response.status_code == 200:
        result = response.json()
        if result["ok"]:
            print("✅ Команды бота обновлены")
            return True
        else:
            print(f"❌ Ошибка обновления команд: {result}")
            return False
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        return False

def setup_webhook_for_start_message():
    """Настраивает вебхук для обработки сообщений"""
    # Для простого бота будем использовать polling через getUpdates
    # или настроим вебхук на наш сайт
    webhook_url = f"{PLATFORM_URL}/webhook/{BOT_TOKEN}"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    
    response = requests.post(url, json={"url": webhook_url})
    
    if response.status_code == 200:
        result = response.json()
        if result["ok"]:
            print(f"✅ Вебхук настроен: {webhook_url}")
            return True
        else:
            print(f"⚠️ Вебхук не настроен: {result}")
            return False
    else:
        print(f"❌ HTTP ошибка при настройке вебхука: {response.status_code}")
        return False

def send_start_message_example():
    """Показывает пример сообщения для /start"""
    message = """🎵 *Добро пожаловать в LTL18:33BG \- BEATSSUDA Platform*

Приветствуем\\! Мы \- комьюнити битмейкеров и продюсеров\\.
Помогаем друг другу, делаем звук,
продаём / покупаем / делимся китами и пресетами\\.

🔥 *Здесь вы можете:*
• Покупать и продавать биты
• Заказывать мастеринг и сведение  
• Делиться опытом с комьюнити
• Находить нужные киты и пресеты

Нажмите кнопку ниже чтобы открыть платформу:"""
    
    print("📝 Рекомендуемый текст для команды /start:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    return message

def main():
    print("🤖 Настройка команд бота для правильного приветствия")
    print("=" * 60)
    
    # Показываем пример сообщения
    send_start_message_example()
    
    print("\n1️⃣ Обновляем описания команд...")
    if set_start_command_description():
        print("✅ Команды обновлены")
    
    print("\n2️⃣ Настраиваем вебхук (опционально)...")
    setup_webhook_for_start_message()
    
    print("\n🎯 СЛЕДУЮЩИЙ ШАГ:")
    print("Для полной работы команды /start нужно:")
    print("1. Добавить обработчик /webhook в приложение")
    print("2. Или настроить простой polling бот")
    print("3. Добавить отправку приветственного сообщения")
    
    print(f"\n🔗 Протестируй бота: https://t.me/ltl1833bg_bot")
    print("💡 Пока что работает кнопка меню, далее добавим обработку /start")

if __name__ == "__main__":
    main()