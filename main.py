import time
import random
from utils.api import get_all_products
from utils.file_utils import save_to_json
from utils.excel_creator import save_to_excel
from loghandler import logger
from collections import defaultdict

def main(query, output_file="wildberries_products.json", products_per_brand=100, max_pages=5, max_products=500):
    """Основная функция парсера."""
    try:
        # Получение всех товаров
        logger.info("Получение всех товаров...")
        products = get_all_products(query, max_pages=max_pages)
        
        # Ограничение общего количества товаров
        products = products[:max_products]
        logger.info(f"Ограничено до {len(products)} товаров для обработки")
    
        # Извлечение уникальных брендов для логирования
        brands = sorted(set(product['brand'] for product in products))
        logger.info("Найденные бренды:")
        for i, brand in enumerate(brands, 1):
            logger.debug(f"{i}. {brand}")
        logger.info(f"Всего брендов: {len(brands)}")
    
        # Группировка по брендам и ограничение до products_per_brand товаров на бренд
        grouped = defaultdict(list)
        for product in products:
            brand = product['brand']
            if len(grouped[brand]) < products_per_brand:
                grouped[brand].append(product)
    
        # Сортировка по бренду
        sorted_products = []
        for brand in sorted(grouped.keys()):  # Сортировка брендов по алфавиту
            sorted_products.extend(grouped[brand])
    
        # Сохранение результатов в JSON
        save_to_json(sorted_products, output_file)
        logger.info(f"Данные сохранены в {output_file}")
    
        # Сохранение результатов в Excel
        excel_output_file = output_file.replace('.json', '.xlsx')
        save_to_excel(sorted_products, excel_output_file)
    
    except Exception as e:
        logger.error(f"Ошибка в основной функции: {str(e)}")
        raise

if __name__ == "__main__":
    query = "латунный кран"
    main(query)