#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый файл для парсера Excel файлов.
"""

import json
import pandas as pd
from typing import Dict, Any

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
            print(f"Ошибка при парсинге Excel файла: {e}")
            raise

def main():
    """Тестирование парсера."""
    print("=== ТЕСТИРОВАНИЕ НОВОГО ПАРСЕРА EXCEL ===\n")
    
    # Создаем экземпляр конвертера
    converter = PushExcelConverter()
    
    try:
        # Парсим файл (получаем данные для каждой категории отдельно)
        categories_data = converter.parse_excel_to_categories('push.xlsx')
        
        print(f"✅ Парсинг завершен успешно!")
        print(f"📊 Найдено категорий: {len(categories_data)}")
        print(f"🌍 Языки: {', '.join(list(categories_data.values())[0]['languages'])}")
        print()
        
        # Сохраняем отдельные JSON файлы для каждой категории
        for category, category_data in categories_data.items():
            safe_category = category.lower().replace(' ', '_').replace('&', 'and')
            filename = f"test_{safe_category}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(category_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 {category}: сохранен в {filename}")
        
        print()
        
        # Выводим статистику по категориям
        print("=== СТАТИСТИКА ПО КАТЕГОРИЯМ ===")
        for i, (category, category_data) in enumerate(categories_data.items()):
            print(f"\n{i+1}. **{category}**")
            print(f"   🎯 Пушей в категории: {len(category_data['pushes'])}")
            print(f"   🌍 Языков: {len(category_data['languages'])}")
            
            # Показываем пример для английского языка
            if category_data['pushes'] and 'en' in category_data['pushes'][0]['translations']:
                en_data = category_data['pushes'][0]['translations']['en']
                print(f"   📝 Пример (EN): \"{en_data['title']}\"")
                print(f"                   \"{en_data['message']}\"")
        
        # Показываем пример структуры для первой категории
        print("\n=== ПРИМЕР СТРУКТУРЫ JSON (первая категория) ===")
        first_category = list(categories_data.keys())[0]
        first_category_data = categories_data[first_category]
        
        # Показываем только первый пуш для краткости
        example_data = {
            "languages": first_category_data["languages"],
            "pushes": first_category_data["pushes"][:1]  # Только первый пуш
        }
        
        print(f"Категория: {first_category}")
        print(json.dumps(example_data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
