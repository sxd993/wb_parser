import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from loghandler import logger

def save_to_excel(data, output_file):
    """Сохранение данных в Excel файл с отдельными столбцами для всех полей."""
    try:
        # Преобразуем данные в список словарей с плоской структурой
        flat_data = []
        for product in data:
            flat_product = {
                "ID": product["id"],
                "Название": product["name"],
                "Бренд": product["brand"],
                "URL": product["url"],
                "Обычная цена": product["price"]["basic"],
                "Цена по ВБ Карте": product["price"]["product"],
                "Цена без ВБ Карты": product["price"]["total"],
                "Артикул": product["article"],
                "Отзывы": product["feedbacks"],
                "Рейтинг": product["rating"],
                "Поставщик(продавец)": product["supplier"],
                "ID продавца": product["supplierId"],
                "Рейтинг продавца": product["supplierRating"]
            }
            flat_data.append(flat_product)
        
        # Создаем DataFrame
        df = pd.DataFrame(flat_data)
        
        # Сохраняем в Excel
        df.to_excel(output_file, index=False, engine='openpyxl')
        
        # Открываем Excel-файл для настройки ширины столбцов
        workbook = load_workbook(output_file)
        worksheet = workbook.active
        
        # Определяем столбцы, которые нужно сделать шире
        columns_to_widen_one = ["ID", "Артикул", "Бренд", "Обычная цена", "Цена по ВБ Карте", "Цена без ВБ Карты"]
        columns_to_widen_two = ["Поставщик(продавец)"]
        columns_to_widen_three = ["Название", "URL"]
        default_width = 8.43  # Стандартная ширина столбца в openpyxl
        first_width = float(default_width * 1.3)  # Увеличиваем ширину в 1.3 раза
        second_width = float(default_width * 3)  # Увеличиваем ширину в 3 раза
        third_width = float(default_width * 6)  # Увеличиваем ширину в 6 раз
        
        # Логируем значения ширин
        logger.debug(f"1st_width: {first_width}, 2nd_width: {second_width}, 3rd_width: {third_width}")
        
        # Проходим по столбцам DataFrame
        for col_idx, col_name in enumerate(df.columns, start=1):
            column_letter = get_column_letter(col_idx)
            if col_name in columns_to_widen_one:
                worksheet.column_dimensions[column_letter].width = first_width
                logger.debug(f"Установлена ширина {first_width} для столбца {col_name} ({column_letter})")
            elif col_name in columns_to_widen_two:
                worksheet.column_dimensions[column_letter].width = second_width
                logger.debug(f"Установлена ширина {second_width} для столбца {col_name} ({column_letter})")
            elif col_name in columns_to_widen_three:
                worksheet.column_dimensions[column_letter].width = third_width
                logger.debug(f"Установлена ширина {third_width} для столбца {col_name} ({column_letter})")
        
        # Сохраняем изменения
        workbook.save(output_file)
        logger.info(f"Excel файл успешно создан: {output_file}")
    
    except Exception as e:
        logger.error(f"Ошибка при записи Excel файла {output_file}: {str(e)}")
        raise  # Перебрасываем исключение для отладки