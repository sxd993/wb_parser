import asyncio
from tqdm import tqdm
from utils.api import get_all_products, get_supplier_info
from utils.excel_creator import save_to_excel
from loghandler import logger
from collections import defaultdict

async def main(query, output_file="wildberries_products.xlsx", products_per_brand=100, max_pages=5, max_products=500):
    """Основная функция парсера."""
    try:
        # Получение всех товаров
        logger.info("Получение всех товаров...")
        products = await get_all_products(query, max_pages=max_pages)
        
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
    
        # Получение уникальных ID продавцов
        supplier_ids = sorted(set(product['supplierId'] for product in sorted_products if product['supplierId']))
        logger.info(f"Найдено {len(supplier_ids)} уникальных продавцов")
        
        # Получение информации о продавцах
        supplier_data = []
        for supplier_id in tqdm(supplier_ids, desc="Получение данных о продавцах"):
            supplier_info = await get_supplier_info(supplier_id)
            supplier_data.append(supplier_info)
    
        # Сохранение результатов в Excel
        save_to_excel(sorted_products, supplier_data, output_file)
    
    except Exception as e:
        logger.error(f"Ошибка в основной функции: {str(e)}")
        raise

if __name__ == "__main__":
    query = "латунный кран"
    asyncio.run(main(query))