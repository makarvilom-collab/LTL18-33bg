# LTL18:33bg - BEATSSUDA Community Platform

🔥 **Веб-платформа для комьюнити BEATSSUDA** - место для продажи и покупки битов, услуг сведения, мастеринга и всего, что связано с продакшеном.

## ✨ Особенности

- **Минималистичный дизайн** в стиле BEATSSUDA
- **Telegram авторизация** через Web Apps API
- **Автоматическая модерация** контента с системой фильтров  
- **REST API** для интеграции с Telegram ботом
- **Адаптивный дизайн** для всех устройств
- **Система безопасности** с проверкой ссылок и контента
- **Защищённые формы** - только авторизованные пользователи могут создавать объявления
- **Статистика** и аналитика платформы

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd bot

# Создайте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка

```bash
# Скопируйте файл конфигурации
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

### 3. Запуск

```bash
# Запустите приложение
python app.py
```

Откройте http://localhost:5000 в браузере.

## 📁 Структура проекта

```
bot/
├── app/                    # Основное приложение
│   ├── __init__.py
│   ├── forms.py           # Формы WTF
│   ├── moderation.py      # Система модерации
│   ├── api/               # REST API
│   │   ├── __init__.py
│   │   └── routes.py      # API endpoints
│   ├── models/            # Модели базы данных
│   │   ├── __init__.py
│   │   └── listing.py     # Модель объявлений
│   ├── static/            # Статические файлы
│   │   ├── css/
│   │   │   └── style.css  # Стили BEATSSUDA
│   │   └── js/
│   │       └── main.js    # JavaScript функциональность
│   └── templates/         # HTML шаблоны
│       ├── base.html      # Базовый шаблон
│       ├── index.html     # Главная страница
│       ├── create_listing.html
│       ├── view_listing.html
│       └── error.html
├── data/                  # База данных SQLite
├── app.py                # Главный файл приложения
├── requirements.txt      # Python зависимости
├── .env.example         # Пример конфигурации
└── README.md           # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
# Flask настройки
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///data/beatssuda.db
FLASK_ENV=development
FLASK_DEBUG=True

# Будущая интеграция с ботом
TELEGRAM_BOT_TOKEN=your-bot-token
WEBHOOK_URL=https://your-domain.com/webhook
```

## 📝 API Documentation

### Endpoints

#### Получить объявления
```http
GET /api/v1/listings
```

Параметры:
- `type` - тип объявления (sell, buy, service)
- `genre` - жанр (trap, drill, rnb, etc.)
- `item_type` - тип товара (бит, сведение, etc.)
- `page` - номер страницы
- `per_page` - количество на странице

#### Создать объявление
```http
POST /api/v1/listings
Content-Type: application/json

{
    "listing_type": "sell",
    "author": "@username",
    "contact": "@username",
    "item_type": "бит",
    "genre": "trap",
    "preview_url": "https://soundcloud.com/...",
    "price": "50 USD",
    "license": "non-exclusive",
    "includes": "wav, stems",
    "delivery_time": "24 часа",
    "description": "Атмосферный трап бит",
    "tags": "#бит #продам #trap"
}
```

#### Получить объявление
```http
GET /api/v1/listings/{id}
```

#### Получить отформатированное объявление
```http
GET /api/v1/listings/{id}/formatted
```

#### Поиск объявлений
```http
GET /api/v1/listings/search?q=trap
```

#### Статистика
```http
GET /api/v1/stats
```

## 🛡️ Модерация

Система автоматической модерации проверяет:

- **Запрещенные домены** (торренты, пиратские сайты)
- **Подозрительный контент** (кряки, пиратка)
- **Личные данные** (телефоны, карты)
- **Безопасность ссылок** (проверка доменов)

### Рекомендуемые платформы для превью:
- SoundCloud
- Google Drive
- Telegram
- Dropbox
- MediaFire
- WeTransfer

## 🎨 Стиль BEATSSUDA

Дизайн выполнен в минималистичном стиле:
- **Минимал, чисто, по сути**
- Монохромная палитра с акцентом
- Четкая типографика Inter
- Карточная система отображения
- Адаптивный дизайн

### Цветовая схема:
- Основной: `#000000`
- Вторичный: `#333333`
- Акцент: `#ff6b35`
- Фон: `#ffffff`
- Поверхность: `#f8f9fa`

## 🔗 Telegram Web Apps авторизация

Платформа интегрирована с Telegram через Web Apps API для безопасной авторизации:

### Настройка (подробности в TELEGRAM_SETUP.md):
1. Создайте бота через @BotFather
2. Настройте Web App для бота  
3. Обновите конфигурацию в коде
4. Задеплойте на HTTPS сервер

### Функциональность:
- Автоматическая авторизация при открытии через Telegram бота
- Защита форм - только авторизованные пользователи могут создавать объявления
- Сохранение сессии в localStorage
- Красивые модальные окна с инструкциями для веб-пользователей

## 🔗 Интеграция с Telegram ботом

API готов для подключения Telegram бота:

```python
import requests

# Получить объявления
response = requests.get('http://your-domain.com/api/v1/listings')
listings = response.json()

# Создать объявление через бота
listing_data = {
    "listing_type": "sell",
    "author": "@user",
    # ... другие поля
}
response = requests.post('http://your-domain.com/api/v1/listings', json=listing_data)

# Получить отформатированное объявление для отправки в Telegram
response = requests.get(f'http://your-domain.com/api/v1/listings/{listing_id}/formatted')
formatted_text = response.json()['data']['formatted_text']
```

## 📊 Мониторинг

Доступная статистика:
- Общее количество объявлений
- Объявления по типам (продажа/покупка/услуги)
- Популярные жанры
- Статистика модерации
- Просмотры и клики по объявлениям

## 🚀 Деплой в продакшн

### 1. Настройте переменные окружения:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=strong-secret-key
DATABASE_URL=postgresql://user:pass@localhost/beatssuda
```

### 2. Используйте Gunicorn:
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 app:app
```

### 3. Настройте Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/bot/app/static;
    }
}
```

## 🔧 Разработка

### Добавление новых фильтров модерации:
```python
from app.models.listing import ContentFilter, db

# Добавить новый фильтр
new_filter = ContentFilter(
    filter_type='banned_word',
    pattern=r'\b(spam|scam)\b',
    is_regex=True
)
db.session.add(new_filter)
db.session.commit()
```

### Кастомизация дизайна:
Отредактируйте `/app/static/css/style.css` для изменения стилей.

### Добавление новых полей:
1. Обновите модель в `app/models/listing.py`
2. Добавьте поля в форму `app/forms.py`
3. Обновите шаблоны в `app/templates/`
4. Создайте миграцию базы данных

## 📞 Поддержка

Для вопросов и предложений:
- GitHub Issues
- Telegram: @your-support-contact

## 📄 Лицензия

MIT License - можете использовать код для своих проектов.

---

**LTL18:33bg - BEATSSUDA Community Platform** 🔥
*Минимал, чисто, по сути*