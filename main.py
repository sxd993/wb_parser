import time
from utils.api import get_brands, get_products_by_brand
from utils.scraper import parse_product_page, setup_driver, close_driver
from utils.file_utils import save_to_json

def main(query, output_file="wildberries_products.json", products_per_brand=100):
    """Основная функция парсера."""
    # Настройка Selenium
    driver = setup_driver()
    
    # Получение и логирование списка брендов
    print("Получение списка брендов...")
    brands = get_brands(query)
    if not brands:
        print("Бренды не найдены.")
        close_driver(driver)
        return

    # Вывод списка брендов для логирования
    print("\nНайденные бренды:")
    for i, brand in enumerate(brands, 1):
        print(f"{i}. {brand}")
    print(f"\nВсего брендов: {len(brands)}\n")

    # Парсинг товаров по брендам
    all_products = []
    for brand in brands:
        print(f"\nОбработка бренда: {brand}")
        # Получение товаров бренда
        products = get_products_by_brand(query, brand, limit=products_per_brand)
        for product in products:
            print(f"Парсинг товара: {product['name']}")
            # Парсинг страницы товара
            product_data = parse_product_page(driver, product['url'])
            if product_data:
                product_data['product_name'] = product['name']
                product_data['product_url'] = product['url']
                all_products.append(product_data)
            time.sleep(1)  # Задержка для избежания блокировки

    # Сохранение результатов
    save_to_json(all_products, output_file)
    print(f"\nДанные сохранены в {output_file}")

    # Закрытие браузера
    close_driver(driver)

if __name__ == "__main__":
    query = "латунный кран"
    main(query)