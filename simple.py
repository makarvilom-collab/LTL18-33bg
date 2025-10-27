from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BEATSSUDA Platform</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Inter, sans-serif; background: #0a0a0a; color: white; text-align: center; padding: 50px; }
            h1 { color: #ff6b35; }
            .btn { background: #ff6b35; color: white; padding: 15px 30px; border: none; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px; }
        </style>
    </head>
    <body>
        <h1>🎵 LTL18:33BG - BEATSSUDA Platform</h1>
        <p>Приветствуем! Мы - комьюнити битмейкеров и продюсеров.</p>
        <p>Помогаем друг другу, делаем звук,<br>продаём / покупаем / делимся китами и пресетами.</p>
        <p>🔥 Здесь вы можете покупать и продавать биты, заказывать мастеринг и остальное</p>
        <a href="/health" class="btn">Проверить статус</a>
        <br><br>
        <p><strong>Статус:</strong> ✅ Работает на Vercel!</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "ok", "platform": "BEATSSUDA", "host": "vercel"}

@app.route('/webhook/<token>', methods=['POST'])
def webhook(token):
    """Обработчик вебхука от Telegram"""
    if token != BOT_TOKEN:
        return "Unauthorized", 403
    
    try:
        update = request.get_json()
        
        # Проверяем есть ли сообщение
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Обрабатываем команду /start
            if text == '/start':
                send_start_message(chat_id)
            elif text == '/app':
                send_app_message(chat_id)
            elif text == '/help':
                send_help_message(chat_id)
        
        return "OK", 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Error", 500

def send_start_message(chat_id):
    """Отправляет приветственное сообщение"""
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
    
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🚀 Открыть BEATSSUDA Platform",
                "web_app": {"url": "https://ltl-18-33bg.vercel.app"}
            }
        ]]
    }
    
    send_telegram_message(chat_id, message, keyboard)

def send_app_message(chat_id):
    """Отправляет сообщение с кнопкой приложения"""
    message = "🚀 *Откройте BEATSSUDA Platform*"
    
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "📱 Открыть платформу",
                "web_app": {"url": "https://ltl-18-33bg.vercel.app"}
            }
        ]]
    }
    
    send_telegram_message(chat_id, message, keyboard)

def send_help_message(chat_id):
    """Отправляет справочное сообщение"""
    message = """❓ *Помощь по BEATSSUDA Platform*

*Команды:*
/start \- Главное меню
/app \- Открыть платформу
/help \- Эта справка

*Как пользоваться:*
1\\. Нажмите кнопку меню или используйте /app
2\\. Откроется платформа в Telegram
3\\. Покупайте, продавайте, общайтесь\\!

*Поддержка:* @ltl1833bg\_bot"""
    
    send_telegram_message(chat_id, message)

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправляет сообщение через Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2"
    }
    
    if reply_markup:
        data["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True)