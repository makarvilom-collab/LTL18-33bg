import sys
import os

# Добавляем корневую папку в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем приложение
from app import create_app

# Создаем приложение для Vercel
app = create_app()

# Для отладки
if __name__ == "__main__":
    app.run(debug=True)