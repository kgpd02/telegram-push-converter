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
                
                # ID пуша для каждой категории
                push_id = 1
                
                # Создаем пуши для каждого языка в данной категории
                for lang in languages:
                    # Находим строки для текущего языка
                    lang_mask = df.iloc[:, 0] == lang
                    lang_indices = df.index[lang_mask].tolist()
                    
                    title = ""
                    message = ""
                    
                    # Если есть строка с языком
                    if len(lang_indices) > 0:
                        lang_row_idx = lang_indices[0]
                        title = df.loc[lang_row_idx, category] if category in df.columns else ""
                        
                        # Проверяем следующую строку (должна быть с NaN в первой колонке)
                        next_idx = lang_row_idx + 1
                        if next_idx < len(df) and pd.isna(df.iloc[next_idx, 0]):
                            message = df.iloc[next_idx][category] if category in df.columns else ""
                    
                    # Создаем пуш для текущего языка
                    push_data = {
                        "id": f"push_{str(push_id).zfill(3)}",
                        "translations": {
                            lang: {
                                "title": str(title) if pd.notna(title) else "",
                                "message": str(message) if pd.notna(message) else ""
                            }
                        }
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
