import sys
import os

# Добавляем корневую папку в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Импортируем основное приложение
try:
    from app import create_app
    app = create_app()
    
    # Инициализируем базу данных при первом запуске
    with app.app_context():
        from app.models.listing import db
        db.create_all()
        
except Exception as e:
    # Fallback для отладки
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return f"Error importing app: {str(e)}"
    
    @app.route('/health')
    def health():
        return {"status": "error", "message": str(e)}

# Это необходимо для Vercel
if __name__ == "__main__":
    app.run()