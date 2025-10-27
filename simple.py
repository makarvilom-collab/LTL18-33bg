from flask import Flask

app = Flask(__name__)

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
        <p>Платформа для продажи и покупки битов</p>
        <p>🔥 Минимал, чисто, по сути</p>
        <a href="/health" class="btn">Проверить статус</a>
        <br><br>
        <p><strong>Статус:</strong> ✅ Работает на Vercel!</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "ok", "platform": "BEATSSUDA", "host": "vercel"}

if __name__ == '__main__':
    app.run(debug=True)