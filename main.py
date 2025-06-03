import time
import random
from utils.api import get_all_products
from utils.file_utils import save_to_json
from collections import defaultdict

def main(query, output_file="wildberries_products.json", products_per_brand=100, max_pages=2, max_products=2):
    """Основная функция парсера."""
    # Получение всех товаров
    print("Получение всех товаров...")
    products = get_all_products(query, max_pages=max_pages)
    
    # Ограничение общего количества товаров
    products = products[:max_products]
    print(f"\nОграничено до {len(products)} товаров для обработки")

    # Извлечение уникальных брендов для логирования
    brands = sorted(set(product['brand'] for product in products))
    print("\nНайденные бренды:")
    for i, brand in enumerate(brands, 1):
        print(f"{i}. {brand}")
    print(f"\nВсего брендов: {len(brands)}\n")

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

    # Сохранение результатов
    save_to_json(sorted_products, output_file)
    print(f"\nДанные сохранены в {output_file}")

if __name__ == "__main__":
    query = "латунный кран"
    main(query)