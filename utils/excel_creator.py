import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from loghandler import logger


def save_to_excel(data, supplier_data, output_file):
    """Сохранение данных в Excel файл с отдельными столбцами для всех полей и данными о продавцах."""
    try:
        # Преобразуем данные о товарах в список словарей с плоской структурой
        flat_data = []
        for product in data:
            flat_product = {
                "Артикул": product["article"],
                "Название": product["name"],
                "Бренд": product["brand"],
                "URL": product["url"],
                "Обычная цена": product["price"]["basic"],
                "Цена по ВБ Карте": product["price"]["product"],
                "Цена без ВБ Карты": product["price"]["total"],
                "Отзывы": product["feedbacks"],
                "Рейтинг": product["rating"],
                "Поставщик(продавец)": product["supplier"],
                "ID продавца": product["supplierId"],
                "Рейтинг продавца": product["supplierRating"],
            }
            flat_data.append(flat_product)

        # Создаем DataFrame для товаров
        df = pd.DataFrame(flat_data)

        # Создаем DataFrame для продавцов
        flat_supplier_data = [
            {
                "ID продавца": supplier["supplierId"],
                "Название продавца": supplier["supplierName"],
                "Полное юридическое название": supplier["supplierFullName"],
                "ИНН": supplier["inn"],
                "ОГРН": supplier["ogrn"],  # Добавляем ОГРН
                "ОГРНИП": supplier["ogrnip"],
                "Юридический адрес": supplier[
                    "legalAddress"
                ],  # Добавляем юридический адрес
                "Торговая марка": supplier["trademark"],
                "КПП": supplier["kpp"],  # Добавляем КПП
                "Номер регистрации": supplier[
                    "taxpayerCode"
                ],  # Добавляем номер регистрации
                "УНП": supplier["unp"],  # Добавляем УНП
                "БИН": supplier["bin"],  # Добавляем БИН
                "УНН": supplier["unn"],  # Добавляем УНН
                "Ссылка на продавца": supplier["supplierUrl"],
            }
            for supplier in supplier_data
        ]
        supplier_df = pd.DataFrame(flat_supplier_data)

        # Сохраняем в Excel с несколькими листами
        with pd.ExcelWriter(output_file, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name="Товары", index=False)
            supplier_df.to_excel(writer, sheet_name="Продавцы", index=False)

        # Открываем Excel-файл для настройки ширины столбцов
        workbook = load_workbook(output_file)

        # Настройка ширины столбцов для листа Товары
        worksheet = workbook["Товары"]
        columns_to_widen_one = [
            "Артикул",
            "Бренд",
            "Обычная цена",
            "Цена по ВБ Карте",
            "Цена без ВБ Карты",
        ]
        columns_to_widen_two = ["Поставщик(продавец)"]
        columns_to_widen_three = ["Название", "URL"]
        default_width = 8.43  # Стандартная ширина столбца в openpyxl
        first_width = float(default_width * 1.3)  # Увеличиваем ширину в 1.3 раза
        second_width = float(default_width * 3)  # Увеличиваем ширину в 3 раза
        third_width = float(default_width * 6)  # Увеличиваем ширину в 6 раз

        logger.debug(
            f"1st_width: {first_width}, 2nd_width: {second_width}, 3rd_width: {third_width}"
        )

        for col_idx, col_name in enumerate(df.columns, start=1):
            column_letter = get_column_letter(col_idx)
            if col_name in columns_to_widen_one:
                worksheet.column_dimensions[column_letter].width = first_width
                logger.debug(
                    f"Установлена ширина {first_width} для столбца {col_name} ({column_letter})"
                )
            elif col_name in columns_to_widen_two:
                worksheet.column_dimensions[column_letter].width = second_width
                logger.debug(
                    f"Установлена ширина {second_width} для столбца {col_name} ({column_letter})"
                )
            elif col_name in columns_to_widen_three:
                worksheet.column_dimensions[column_letter].width = third_width
                logger.debug(
                    f"Установлена ширина {third_width} для столбца {col_name} ({column_letter})"
                )

        # Настройка ширины столбцов для листа Продавец
        supplier_worksheet = workbook["Продавцы"]
        supplier_columns_to_widen_one = [
            "ID продавца",
            "ИНН",
            "ОГРН",
            "ОГРНИП",
            "КПП",
            "Номер регистрации",
            "УНП",
            "БИН",
            "УНН",
        ]
        supplier_columns_to_widen_two = ["Название продавца", "Торговая марка"]
        supplier_columns_to_widen_three = [
            "Полное юридическое название",
            "Юридический адрес",
            "Ссылка на продавца",
        ]
        for col_idx, col_name in enumerate(supplier_df.columns, start=1):
            column_letter = get_column_letter(col_idx)
            if col_name in supplier_columns_to_widen_one:
                supplier_worksheet.column_dimensions[column_letter].width = first_width
                logger.debug(
                    f"Установлена ширина {first_width} для столбца {col_name} ({column_letter}) в листе Suppliers"
                )
            elif col_name in supplier_columns_to_widen_two:
                supplier_worksheet.column_dimensions[column_letter].width = second_width
                logger.debug(
                    f"Установлена ширина {second_width} для столбца {col_name} ({column_letter}) в листе Suppliers"
                )
            elif col_name in supplier_columns_to_widen_three:
                supplier_worksheet.column_dimensions[column_letter].width = third_width
                logger.debug(
                    f"Установлена ширина {third_width} для столбца {col_name} ({column_letter}) в листе Suppliers"
                )

        # Сохраняем изменения
        workbook.save(output_file)
        logger.info(f"Excel файл успешно создан: {output_file}")

    except Exception as e:
        logger.error(f"Ошибка при записи Excel файла {output_file}: {str(e)}")
        raise
