from flask import Flask, render_template_string
import os

# Создаем простое Flask приложение для Vercel
app = Flask(__name__)

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LTL18:33BG - BEATSSUDA Platform</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            .logo {
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 20px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .features {
                text-align: left;
                margin: 30px 0;
            }
            .feature {
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
                transition: transform 0.2s;
            }
            .btn:hover {
                transform: translateY(-2px);
            }
            .status {
                background: #d4edda;
                color: #155724;
                padding: 10px;
                border-radius: 10px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎵 BEATSSUDA</div>
            <div class="subtitle">LTL18:33BG - Platform для битмейкеров</div>
            
            <div class="features">
                <div class="feature">🎤 Покупайте и продавайте биты</div>
                <div class="feature">🎛️ Заказывайте мастеринг и сведение</div>
                <div class="feature">💬 Делитесь опытом с комьюнити</div>
                <div class="feature">🎹 Находите нужные киты и пресеты</div>
            </div>
            
            <div class="status">
                ✅ Платформа успешно развернута на Vercel!
            </div>
            
            <a href="/webhook/test" class="btn">Проверить API</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/health')
def health():
    return {
        "status": "ok",
        "message": "BEATSSUDA Platform is running!",
        "version": "1.0.0"
    }

# Вебхук для Telegram бота
@app.route('/webhook/<token>', methods=['POST', 'GET'])  
def webhook(token):
    """Обработчик вебхука от Telegram"""
    BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
    
    if token != BOT_TOKEN and token != "test":
        return {"error": "Unauthorized"}, 403
    
    if token == "test":
        return {
            "status": "ok",
            "message": "Webhook endpoint is working!",
            "bot_token_valid": len(BOT_TOKEN) > 0
        }
    
    try:
        from flask import request
        import requests
        
        if request.method == 'GET':
            return {"status": "webhook_ready", "method": "GET"}
        
        update = request.get_json()
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text == '/start':
                send_start_message(chat_id)
            elif text == '/app':
                send_app_message(chat_id)
            elif text == '/help':
                send_help_message(chat_id)
        
        return {"status": "ok"}, 200
        
    except Exception as e:
        return {"error": str(e)}, 500

def send_start_message(chat_id):
    """Отправляет приветственное сообщение"""
    import requests
    
    BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
    message = """🎵 *Добро пожаловать в LTL18:33BG \\- BEATSSUDA Platform*

Приветствуем\\! Мы \\- комьюнити битмейкеров и продюсеров\\.
Помогаем друг другу, делаем звук,
продаём / покупаем / делимся китами и пресетами\\.

🔥 *Здесь вы можете:*
• Покупать и продавать биты
• Заказывать мастеринг и сведение  
• Делиться опытом с комьюнити
• Находить нужные киты и пресеты

*Техподдержка:* @BeatHavenX

Нажмите кнопку ниже чтобы открыть платформу:"""
    
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🚀 Открыть BEATSSUDA Platform",
                "web_app": {"url": "https://bot-5xnok2krw-kanufuewfs-projects.vercel.app"}
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
                "web_app": {"url": "https://bot-5xnok2krw-kanufuewfs-projects.vercel.app"}
            }
        ]]
    }
    
    send_telegram_message(chat_id, message, keyboard)

def send_help_message(chat_id):
    """Отправляет справочное сообщение"""
    message = """❓ *Помощь по BEATSSUDA Platform*

*Команды:*
/start \\- Главное меню
/app \\- Открыть платформу  
/help \\- Эта справка

*Как пользоваться:*
1\\. Нажмите кнопку меню или используйте /app
2\\. Откроется платформа в Telegram
3\\. Покупайте, продавайте, общайтесь\\!

*Техподдержка и модерация:* @BeatHavenX
*Все проблемы писать ему\\!*"""
    
    send_telegram_message(chat_id, message)

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправляет сообщение через Telegram Bot API"""
    import requests
    
    BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"
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

# Экспорт для Vercel
if __name__ == "__main__":
    app.run(debug=True)