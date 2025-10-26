# BEATSSUDA Platform - Deployment Guide

## 🚀 Быстрый деплой на Railway

### 1. Подготовка
- ✅ Все файлы готовы
- ✅ requirements.txt создан
- ✅ Procfile создан  
- ✅ Код адаптирован для продакшена

### 2. Деплой на Railway
1. Иди на [railway.app](https://railway.app)
2. Войди через GitHub
3. Нажми "New Project"
4. Выбери "Deploy from GitHub repo"
5. Выбери этот репозиторий
6. Railway автоматически задеплоит

### 3. После деплоя
1. Получишь домен типа `beatssuda-bot-production.railway.app`
2. Обнови настройки Telegram бота:
   - Замени все ссылки на `@BEATSSUDA_bot` на своего бота
   - Настрой Web App с новым доменом
3. Протестируй авторизацию через Telegram

### 4. Настройка Telegram Web App
1. Открой @BotFather
2. Отправь `/newapp`
3. Выбери своего бота
4. Введи URL: `https://your-domain.railway.app`
5. Добавь описание и иконку

## 📝 Environment Variables
Railway автоматически установит:
- `PORT` - порт сервера
- `FLASK_ENV=production` - режим продакшена

## 🔧 Локальная разработка
```bash
source venv/bin/activate
python app.py
```

## 📱 Тестирование
После деплоя:
1. Открой свой домен в браузере
2. Проверь что сайт работает
3. Протестируй авторизацию через Telegram бота
4. Создай тестовое объявление

## 🆘 Troubleshooting
- Если сайт не открывается - проверь логи в Railway
- Если авторизация не работает - убедись что домен HTTPS
- Если база не создается - проверь permissions

---
**BEATSSUDA - минимал, чисто, по сути** 🔥