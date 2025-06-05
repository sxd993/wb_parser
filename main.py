import asyncio
from tqdm import tqdm
from utils.api import get_all_products, get_supplier_info
from utils.excel_creator import save_to_excel

async def main(query, output_file="wildberries_products.xlsx", max_products=1000, progress_handler=None):
    """Основная функция парсера."""
    try:
        # Получение всех товаров с прогресс-баром
        products = await get_all_products(query, max_products=max_products, progress_handler=progress_handler)
    
        # Сортировка по бренду
        sorted_products = sorted(products, key=lambda x: x['brand'])
    
        # Получение уникальных ID продавцов
        supplier_ids = sorted(set(product['supplierId'] for product in sorted_products if product['supplierId']))
        
        # Установка общего количества для прогресс-бара продавцов
        if progress_handler:
            progress_handler.set_total(len(supplier_ids))
        
        # Получение информации о продавцах асинхронно
        supplier_data = await asyncio.gather(
            *(get_supplier_info(supplier_id, progress_handler) for supplier_id in supplier_ids),
            return_exceptions=True
        )
        # Фильтрация результатов, если были ошибки
        supplier_data = [data for data in supplier_data if not isinstance(data, Exception)]
    
        # Сохранение результатов в Excel
        save_to_excel(sorted_products, supplier_data, output_file)
    
    except Exception as e:
        raise Exception(f"Ошибка в основной функции: {str(e)}")

if __name__ == "__main__": 
    query = "латунный кран"
    asyncio.run(main(query, max_products=100))