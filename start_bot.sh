#!/bin/bash

# 🤖 Telegram Push Converter Bot - Startup Script
# Скрипт для быстрого запуска бота с проверками

echo "🚀 Запуск Telegram Push Converter Bot..."
echo "========================================="

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "📝 Создайте файл .env на основе env_example.txt"
    echo "💡 Команда: cp env_example.txt .env"
    echo "🔑 Затем добавьте ваш токен бота в .env файл"
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создаю виртуальное окружение..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка создания виртуального окружения"
        exit 1
    fi
fi

# Активируем виртуальное окружение
echo "⚡ Активирую виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Проверяю зависимости..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

# Проверяем токен в .env
if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || grep -q "your_bot_token_here" .env; then
    echo "⚠️  Токен не настроен в .env файле!"
    echo "🔑 Отредактируйте .env файл и добавьте ваш токен бота"
    echo "💡 Получить токен можно у @BotFather в Telegram"
    exit 1
fi

echo "✅ Все проверки пройдены!"
echo "🤖 Запускаю бота..."
echo "========================================="
echo ""

# Загружаем переменные окружения и запускаем бота
set -a
source .env
set +a

python bot.py
