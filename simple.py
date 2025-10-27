from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

BOT_TOKEN = "8405053839:AAENp9xuJw2HVwF1FWs8Dipwkrur1dqK2Uw"

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LTL18:33bg - BEATSSUDA</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0a0a; color: #ffffff; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        header { background: rgba(0,0,0,0.95); padding: 1rem 0; position: fixed; width: 100%; top: 0; z-index: 1000; backdrop-filter: blur(10px); }
        nav { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #ff6b35; }
        .nav-links { display: flex; list-style: none; gap: 2rem; }
        .nav-links a { color: #ffffff; text-decoration: none; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: #ff6b35; }
        
        main { margin-top: 80px; }
        .hero { text-align: center; padding: 4rem 0; background: linear-gradient(135deg, #1a0a0a 0%, #2a1a1a 100%); }
        .hero h1 { font-size: 3rem; font-weight: 700; margin-bottom: 1rem; background: linear-gradient(135deg, #ff6b35, #ff8c42); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.2rem; color: #cccccc; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto; }
        
        .features { padding: 4rem 0; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem; }
        .feature-card { background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
        .feature-card h3 { color: #ff6b35; margin-bottom: 1rem; }
        
        .cta { background: #ff6b35; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; transition: background 0.3s; }
        .cta:hover { background: #e55a2b; }
        
        .stats { background: rgba(255,107,53,0.05); padding: 3rem 0; text-align: center; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; }
        .stat h3 { font-size: 2rem; color: #ff6b35; }
        
        footer { background: #000000; padding: 2rem 0; text-align: center; margin-top: 4rem; }
        .support { color: #ff6b35; font-weight: 600; }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .nav-links { display: none; }
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">🎵 BEATSSUDA</div>
            <ul class="nav-links">
                <li><a href="#home">Главная</a></li>
                <li><a href="#beats">Биты</a></li>
                <li><a href="#services">Услуги</a></li>
                <li><a href="#community">Комьюнити</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section class="hero" id="home">
            <div class="container">
                <h1>LTL18:33BG - BEATSSUDA Platform</h1>
                <p>Приветствуем! Мы - комьюнити битмейкеров и продюсеров.<br>
                Помогаем друг другу, делаем звук, продаём / покупаем / делимся китами и пресетами.</p>
                <a href="https://t.me/ltl1833bg_bot" class="cta">🚀 Открыть в Telegram</a>
                <a href="#features" class="cta">� Узнать больше</a>
            </div>
        </section>

        <section class="features" id="features">
            <div class="container">
                <h2 style="text-align: center; margin-bottom: 1rem; color: #ff6b35;">�🔥 Здесь вы можете:</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>🎵 Покупать и продавать биты</h3>
                        <p>Размещайте свои треки и находите идеальные биты для ваших проектов</p>
                    </div>
                    <div class="feature-card">
                        <h3>🎚️ Заказывать мастеринг и сведение</h3>
                        <p>Профессиональные услуги по обработке звука от опытных инженеров</p>
                    </div>
                    <div class="feature-card">
                        <h3>🤝 Делиться опытом с комьюнити</h3>
                        <p>Общайтесь с единомышленниками, делитесь советами и получайте фидбек</p>
                    </div>
                    <div class="feature-card">
                        <h3>🎹 Находить киты и пресеты</h3>
                        <p>Огромная библиотека сэмплов, лупов и пресетов для ваших битов</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="stats">
            <div class="container">
                <h2 style="margin-bottom: 2rem; color: #ff6b35;">📊 Статистика платформы</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <h3>50+</h3>
                        <p>Активных битмейкеров</p>
                    </div>
                    <div class="stat">
                        <h3>200+</h3>
                        <p>Опубликованных битов</p>
                    </div>
                    <div class="stat">
                        <h3>24/7</h3>
                        <p>Поддержка комьюнити</p>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>© 2024 LTL18:33BG - BEATSSUDA Platform</p>
            <p>🔥 Минимал, чисто, по сути</p>
            <p class="support">Техподдержка и модерация: <strong>@BeatHavenX</strong></p>
            <p>Все проблемы писать ему!</p>
        </div>
    </footer>
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

*Техподдержка:* @BeatHavenX

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
1\\. Нажмите кнопу меню или используйте /app
2\\. Откроется платформа в Telegram
3\\. Покупайте, продавайте, общайтесь\\!

*Техподдержка и модерация:* @BeatHavenX
*Все проблемы писать ему\\!*"""
    
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