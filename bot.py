#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для конвертации Excel файлов с пуш-уведомлениями в JSON формат.
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, List
import pandas as pd
from telegram import Update, Document
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Экранирует специальные символы для Markdown."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

class PushExcelConverter:
    """Класс для конвертации Excel файлов с пуш-уведомлениями в JSON."""
    
    @staticmethod
    def parse_excel_to_categories(file_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Конвертирует Excel файл в JSON формат с отдельными файлами для каждой категории.
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            Dict с категориями и их данными
        """
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path)
            
            # Получаем список языков (уникальные значения в первой колонке, исключая NaN)
            languages = df.iloc[:, 0].dropna().unique().tolist()
            
            # Получаем названия категорий (колонки кроме первой)
            categories = df.columns[1:].tolist()
            
            # Результат - словарь с данными для каждой категории
            categories_data = {}
            
            # Создаем данные для каждой категории отдельно
            for category in categories:
                # Структура для текущей категории
                category_result = {
                    "languages": languages,
                    "pushes": []
                }
                
                # Группируем строки по пушам
                push_groups = []
                current_group = []
                
                # Проходим по всем строкам и группируем по языкам
                for i, row in df.iterrows():
                    lang = row.iloc[0]
                    
                    if pd.notna(lang):  # Начало нового языка
                        if lang == languages[0] and current_group:  # Если это первый язык и уже есть группа
                            push_groups.append(current_group)
                            current_group = []
                        current_group.append(i)
                    else:  # Строка с сообщением (NaN в первой колонке)
                        if current_group:
                            current_group.append(i)
                
                # Добавляем последнюю группу
                if current_group:
                    push_groups.append(current_group)
                
                # Создаем пуши из групп
                push_id = 1
                for group in push_groups:
                    # Проверяем, что в группе есть все языки
                    push_translations = {}
                    
                    i = 0
                    while i < len(group):
                        row_idx = group[i]
                        lang = df.iloc[row_idx, 0]
                        
                        if pd.notna(lang) and lang in languages:
                            title = df.loc[row_idx, category] if category in df.columns else ""
                            message = ""
                            
                            # Проверяем следующую строку для сообщения
                            if i + 1 < len(group):
                                next_row_idx = group[i + 1]
                                if pd.isna(df.iloc[next_row_idx, 0]):
                                    message = df.iloc[next_row_idx][category] if category in df.columns else ""
                                    i += 1  # Пропускаем строку с сообщением
                            
                            push_translations[lang] = {
                                "title": str(title) if pd.notna(title) else "",
                                "message": str(message) if pd.notna(message) else ""
                            }
                        
                        i += 1
                    
                    # Добавляем пуш только если есть хотя бы один перевод
                    if push_translations:
                        push_data = {
                            "id": f"push_{str(push_id).zfill(3)}",
                            "translations": push_translations
                        }
                        category_result["pushes"].append(push_data)
                        push_id += 1
                
                # Сохраняем данные категории
                categories_data[category] = category_result
            
            return categories_data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге Excel файла: {e}")
            raise
    
    @staticmethod
    def validate_excel_structure(file_path: str) -> bool:
        """
        Проверяет структуру Excel файла.
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            True если структура корректна, иначе False
        """
        try:
            df = pd.read_excel(file_path)
            
            # Проверяем, что файл не пустой
            if df.empty:
                return False
            
            # Проверяем, что есть хотя бы 2 колонки
            if len(df.columns) < 2:
                return False
            
            # Проверяем, что в первой колонке есть языки
            languages = df.iloc[:, 0].dropna().unique()
            if len(languages) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при валидации файла: {e}")
            return False

class TelegramBot:
    """Основной класс Telegram бота."""
    
    def __init__(self, token: str):
        """Инициализация бота."""
        self.token = token
        self.application = Application.builder().token(token).build()
        self.converter = PushExcelConverter()
        
        # Добавляем обработчики
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), self.handle_excel_file))
        self.application.add_handler(MessageHandler(filters.Document.FileExtension("xls"), self.handle_excel_file))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start.""" 
        welcome_message = (
            "**🎯 Push Notifications Converter Bot**\n\n"
            "*Привет! Я помогу тебе конвертировать Excel файлы с пуш-уведомлениями в JSON формат.*\n\n"
            "**📋 Как использовать:**\n"
            "1️⃣ *Загрузи Excel файл (.xlsx или .xls)*\n"
            "2️⃣ *Получи JSON файл в ответ* ✨\n\n"
            "**📁 Структура Excel файла:**\n"
            "• *Первая колонка* - коды языков (en, ar, de, es и т.д.)\n"
            "• *Остальные колонки* - категории пушей\n"
            "• *Каждый язык* должен иметь 2 строки: заголовок и сообщение\n\n"
            "**🔧 Команды:**\n"
            "/help - *Показать справку*\n\n"
            "*Просто отправь мне Excel файл и получи JSON!* 🚀"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help."""
        help_message = (
            "**📖 Справка по использованию бота**\n\n"
            "**🎯 Назначение:**\n"
            "*Конвертация Excel файлов с пуш-уведомлениями в JSON формат*\n\n"
            "**📋 Поддерживаемые форматы:**\n"
            "• Excel файлы (.xlsx, .xls)\n\n"
            "**📁 Требования к структуре файла:**\n\n"
            "**Колонка A (Языки):**\n"
            "• en (английский)\n"
            "• ar (арабский) \n"
            "• de (немецкий)\n"
            "• es (испанский)\n"
            "• fr (французский)\n"
            "• и другие...\n\n"
            "**Остальные колонки (Категории):**\n"
            "• Betting (ставки)\n"
            "• Gambling (азартные игры)\n"
            "• Dating (знакомства)\n"
            "• Dating Adult (взрослые знакомства)\n"
            "• Webcam (веб-камеры)\n"
            "• Subscription (подписки)\n"
            "• и другие...\n\n"
            "**📝 Формат данных:**\n"
            "*Для каждого языка должно быть 2 строки:*\n"
            "1️⃣ *Заголовок пуш-уведомления*\n"
            "2️⃣ *Текст сообщения*\n\n"
            "**💡 Пример использования:**\n"
            "*Просто отправь Excel файл в чат, и бот автоматически конвертирует его в JSON!*\n\n"
            "**⚠️ Возможные ошибки:**\n"
            "• Неверный формат файла\n"
            "• Пустой файл\n"
            "• Некорректная структура данных\n\n"
            "*В случае ошибки бот сообщит об этом и поможет исправить проблему.* 🔧"
        )
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_excel_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик Excel файлов."""
        try:
            document: Document = update.message.document
            
            # Проверяем размер файла (максимум 20MB)
            if document.file_size > 20 * 1024 * 1024:
                await update.message.reply_text(
                    "**❌ Ошибка**\n\n"
                    "*Файл слишком большой!* 📁\n"
                    "*Максимальный размер: 20MB*",
                    parse_mode='Markdown'
                )
                return
            
            # Отправляем сообщение о начале обработки
            processing_msg = await update.message.reply_text(
                "**🔄 Обработка файла...**\n\n"
                "*Загружаю и конвертирую Excel файл в JSON*\n"
                "*Это может занять несколько секунд* ⏳",
                parse_mode='Markdown'
            )
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                # Скачиваем файл
                file = await document.get_file()
                await file.download_to_drive(temp_file.name)
                
                try:
                    # Валидируем структуру файла
                    if not self.converter.validate_excel_structure(temp_file.name):
                        await processing_msg.edit_text(
                            "**❌ Ошибка в структуре файла**\n\n"
                            "*Файл не соответствует ожидаемой структуре!*\n\n"
                            "**📋 Требования:**\n"
                            "• *Первая колонка* - коды языков\n"
                            "• *Остальные колонки* - категории\n"
                            "• *Минимум 2 колонки*\n\n"
                            "*Используй /help для получения подробной информации* 💡",
                            parse_mode='Markdown'
                        )
                        return
                    
                    # Конвертируем в JSON (получаем данные для каждой категории)
                    categories_data = self.converter.parse_excel_to_categories(temp_file.name)
                    
                    # Создаем отдельные JSON файлы для каждой категории
                    json_files_paths = []
                    json_filenames = []
                    
                    base_filename = document.file_name.split('.')[0]
                    
                    for category, category_data in categories_data.items():
                        # Создаем имя файла для категории
                        safe_category = category.lower().replace(' ', '_').replace('&', 'and')
                        json_filename = f"{safe_category}_{base_filename}.json"
                        
                        # Создаем временный JSON файл
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as json_file:
                            json.dump(category_data, json_file, ensure_ascii=False, indent=2)
                            json_files_paths.append(json_file.name)
                            json_filenames.append(json_filename)
                    
                    # Отправляем информационное сообщение
                    total_languages = len(list(categories_data.values())[0]['languages'])
                    total_categories = len(categories_data)
                    
                    # Экранируем специальные символы для Markdown
                    safe_filename = escape_markdown(document.file_name)
                    
                    info_message = (
                        "**✅ Конвертация завершена!**\n\n"
                        f"**📁 Исходный файл:** {safe_filename}\n"
                        f"**📊 Найдено языков:** {total_languages}\n"
                        f"**📋 Найдено категорий:** {total_categories}\n\n"
                        f"**🌍 Языки:** {', '.join(list(categories_data.values())[0]['languages'])}\n\n"
                        f"**📦 Создано файлов:** {len(json_files_paths)}\n"
                        "*Отправляю отдельные JSON файлы для каждой категории\\.\\.\\. 🚀*"
                    )
                    
                    await processing_msg.edit_text(info_message, parse_mode='Markdown')
                    
                    # Отправляем каждый JSON файл отдельно
                    for i, (json_file_path, json_filename) in enumerate(zip(json_files_paths, json_filenames)):
                        category_name = list(categories_data.keys())[i]
                        category_data = list(categories_data.values())[i]
                        
                        with open(json_file_path, 'rb') as json_file:
                            # Экранируем название категории
                            safe_category = escape_markdown(category_name)
                            
                            caption = (
                                f"**📋 Категория:** {safe_category}\n\n"
                                f"**🎯 Пушей в категории:** {len(category_data['pushes'])}\n"
                                f"**🌍 Языков:** {len(category_data['languages'])}\n\n"
                                "*Файл готов к использованию\\!* ✨"
                            )
                            
                            await update.message.reply_document(
                                document=json_file,
                                filename=json_filename,
                                caption=caption,
                                parse_mode='Markdown'
                            )
                    
                    # Удаляем временные файлы
                    for json_file_path in json_files_paths:
                        os.unlink(json_file_path)
                    
                except Exception as e:
                    logger.error(f"Ошибка при конвертации файла: {e}")
                    await processing_msg.edit_text(
                        "**❌ Ошибка при обработке файла**\n\n"
                        f"*Произошла ошибка:* `{str(e)}`\n\n"
                        "*Убедись, что файл имеет правильную структуру*\n"
                        "*Используй /help для получения помощи* 💡",
                        parse_mode='Markdown'
                    )
                
                finally:
                    # Удаляем временный файл
                    os.unlink(temp_file.name)
        
        except Exception as e:
            logger.error(f"Общая ошибка при обработке файла: {e}")
            await update.message.reply_text(
                "**❌ Произошла непредвиденная ошибка**\n\n"
                "*Попробуй отправить файл еще раз*\n"
                "*Если проблема повторится, обратись к администратору* 🛠️",
                parse_mode='Markdown'
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений."""
        message = (
            "**📤 Отправь Excel файл**\n\n"
            "*Для конвертации пуш-уведомлений в JSON отправь Excel файл (.xlsx или .xls)*\n\n"
            "**💡 Нужна помощь?**\n"
            "*Используй команду /help для получения подробных инструкций*"
        )
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    def run(self) -> None:
        """Запуск бота."""
        logger.info("Запуск Telegram бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Главная функция."""
    # Получаем токен из переменной окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Ошибка: Не найден TELEGRAM_BOT_TOKEN в переменных окружения!")
        print("📝 Создай .env файл или установи переменную окружения:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # Создаем и запускаем бота
    bot = TelegramBot(token)
    bot.run()

if __name__ == '__main__':
    main()
