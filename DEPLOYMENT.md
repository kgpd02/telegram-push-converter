# 🚀 Деплой и настройка проекта

## 📁 Создание GitHub репозитория

### Вариант 1: Через веб-интерфейс GitHub

1. **Перейдите на [GitHub.com](https://github.com)**
2. **Нажмите "New repository" (зеленая кнопка)**
3. **Заполните форму:**
   - Repository name: `telegram-push-converter`
   - Description: `🤖 Telegram bot for converting Excel push notifications to JSON format`
   - ✅ Public (или Private по желанию)
   - ❌ НЕ инициализируйте с README (у нас уже есть)
   - ❌ НЕ добавляйте .gitignore (у нас уже есть)
4. **Нажмите "Create repository"**

### Вариант 2: Через GitHub CLI (если установлен)

```bash
# Установка GitHub CLI на macOS
brew install gh

# Авторизация
gh auth login

# Создание репозитория
gh repo create telegram-push-converter --public --description "🤖 Telegram bot for converting Excel push notifications to JSON format"
```

## 🔗 Подключение к удаленному репозиторию

После создания репозитория на GitHub, выполните команды:

```bash
# Добавляем удаленный репозиторий
git remote add origin https://github.com/YOUR_USERNAME/telegram-push-converter.git

# Отправляем код на GitHub
git push -u origin main
```

**Замените `YOUR_USERNAME` на ваше имя пользователя GitHub!**

## ⚙️ Настройка для запуска

### 1. Создание .env файла

```bash
# Копируем пример
cp env_example.txt .env

# Редактируем файл (замените токен на свой)
nano .env
```

### 2. Установка зависимостей

```bash
# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 3. Запуск бота

```bash
# Убедитесь, что .env файл настроен с вашим токеном
python bot.py
```

## 🔐 Получение токена Telegram бота

1. **Найдите [@BotFather](https://t.me/BotFather) в Telegram**
2. **Отправьте команду:** `/newbot`
3. **Следуйте инструкциям:**
   - Введите имя бота (например: `Push Converter Bot`)
   - Введите username бота (например: `push_converter_123_bot`)
4. **Скопируйте полученный токен** и добавьте в `.env` файл

## 📦 Структура проекта

```
telegram-push-converter/
├── 📄 README.md              # Основная документация
├── 📄 DEPLOYMENT.md          # Инструкции по деплою
├── 🤖 bot.py                 # Главный файл бота
├── 🧪 test_parser.py         # Тестирование парсера
├── 📋 requirements.txt       # Python зависимости
├── 🔧 env_example.txt        # Пример переменных окружения
├── 📊 push.xlsx              # Пример Excel файла
├── 📄 push.json              # Пример JSON файла
└── 🚫 .gitignore             # Исключения для Git
```

## 🌐 Деплой на сервер (опционально)

### На VPS/Dedicated сервере:

```bash
# Клонируем репозиторий
git clone https://github.com/YOUR_USERNAME/telegram-push-converter.git
cd telegram-push-converter

# Настраиваем окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настраиваем .env
cp env_example.txt .env
nano .env  # Добавляем токен бота

# Запускаем в фоне
nohup python bot.py &
```

### Через systemd (рекомендуется):

```bash
# Создаем сервис
sudo nano /etc/systemd/system/telegram-push-bot.service
```

Содержимое файла сервиса:

```ini
[Unit]
Description=Telegram Push Converter Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/telegram-push-converter
Environment=PATH=/path/to/telegram-push-converter/venv/bin
ExecStart=/path/to/telegram-push-converter/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-push-bot
sudo systemctl start telegram-push-bot
sudo systemctl status telegram-push-bot
```

## 📱 Тестирование бота

1. **Запустите бота локально**
2. **Найдите своего бота в Telegram** (по username)
3. **Отправьте команду** `/start`
4. **Загрузите Excel файл** (можете использовать `push.xlsx` как пример)
5. **Получите JSON файлы** для каждой категории

## 🔧 Troubleshooting

### Проблема: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Проблема: "Invalid token"
- Проверьте токен в .env файле
- Убедитесь, что токен получен от @BotFather
- Проверьте, что нет лишних пробелов

### Проблема: "File too large"
- Максимальный размер файла: 20MB
- Уменьшите размер Excel файла

### Проблема: "Invalid file structure"
- Убедитесь, что первая колонка содержит коды языков
- Убедитесь, что для каждого языка есть две строки (title и message)

## 📞 Поддержка

Если возникли проблемы, создайте [Issue на GitHub](https://github.com/YOUR_USERNAME/telegram-push-converter/issues) с описанием проблемы и логами.
