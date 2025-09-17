#!/bin/bash

# 🚀 Скрипт для развертывания Telegram Push Converter Bot на продакшн сервере
# Автор: Telegram Push Converter Bot Team

set -e  # Останавливаться при ошибках

echo "🚀 Развертывание Telegram Push Converter Bot на сервере"
echo "====================================================="

# Проверяем, что скрипт запущен не от root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Не запускайте этот скрипт от root!"
    echo "💡 Создайте обычного пользователя и запустите от его имени"
    exit 1
fi

# Проверяем наличие необходимых команд
echo "🔍 Проверяю системные требования..."

commands=("git" "python3" "pip3")
for cmd in "${commands[@]}"; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ Команда $cmd не найдена!"
        echo "💡 Установите: sudo apt update && sudo apt install git python3 python3-pip python3-venv"
        exit 1
    fi
done

echo "✅ Системные требования выполнены"

# Переходим в домашнюю директорию
cd ~

# Удаляем старую версию если есть
if [ -d "telegram-push-converter" ]; then
    echo "🗑️  Удаляю старую версию..."
    rm -rf telegram-push-converter
fi

# Клонируем репозиторий
echo "📥 Клонирую репозиторий с GitHub..."
if ! git clone https://github.com/kgpd02/telegram-push-converter.git; then
    echo "❌ Не удалось клонировать репозиторий!"
    echo "💡 Проверьте интернет соединение и доступность GitHub"
    exit 1
fi

cd telegram-push-converter

# Создаем виртуальное окружение
echo "📦 Создаю виртуальное окружение..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "⚡ Активирую виртуальное окружение..."
source venv/bin/activate

# Обновляем pip
echo "🔄 Обновляю pip..."
pip install --upgrade pip

# Очищаем возможные конфликты
echo "🧹 Очищаю возможные конфликты пакетов..."
pip uninstall telegram python-telegram-bot -y 2>/dev/null || true

# Устанавливаем зависимости
echo "📦 Устанавливаю зависимости..."
pip install -r requirements.txt

# Проверяем установку
echo "✅ Проверяю корректность установки..."
python3 -c "from telegram import Update; print('✅ python-telegram-bot установлен корректно')" || {
    echo "❌ Ошибка импорта telegram библиотеки!"
    echo "💡 Попробуйте вручную: pip uninstall telegram python-telegram-bot -y && pip install python-telegram-bot==20.7"
    exit 1
}

# Создаем .env файл если его нет
if [ ! -f ".env" ]; then
    echo "📝 Создаю файл конфигурации .env..."
    cp env_example.txt .env
    
    echo ""
    echo "⚠️  ВАЖНО: Настройте токен бота!"
    echo "📝 Отредактируйте файл .env и добавьте ваш токен:"
    echo "   nano .env"
    echo ""
    echo "🔑 Получить токен можно у @BotFather в Telegram:"
    echo "   1. Найдите @BotFather в Telegram"
    echo "   2. Отправьте /newbot"
    echo "   3. Следуйте инструкциям"
    echo "   4. Скопируйте токен в .env файл"
    echo ""
else
    echo "✅ Файл .env уже существует"
fi

# Делаем скрипт запуска исполняемым
chmod +x start_bot.sh

echo ""
echo "🎉 Развертывание завершено успешно!"
echo "=====================================

📁 Расположение: ~/telegram-push-converter
🔧 Конфигурация: ~/telegram-push-converter/.env

📝 Следующие шаги:
1. Настройте токен бота в .env файле:
   cd ~/telegram-push-converter
   nano .env

2. Запустите бота:
   ./start_bot.sh

3. Для автозапуска создайте systemd сервис:
   sudo nano /etc/systemd/system/telegram-push-bot.service

📚 Подробная документация: README.md и DEPLOYMENT.md
🐛 Проблемы? Смотрите раздел Troubleshooting в DEPLOYMENT.md

🚀 Удачного использования!"

echo ""
