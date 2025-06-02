import time
import random
from utils.api import get_all_products
from utils.scraper import parse_product_page, setup_driver, close_driver
from utils.file_utils import save_to_json
from collections import defaultdict

# Список User-Agent для ротации
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
]

def main(query, output_file="wildberries_products.json", products_per_brand=100, max_pages=2, max_products=500):
    """Основная функция парсера."""
    # Настройка Selenium
    driver = setup_driver()
    
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

    # Парсинг страниц товаров
    all_products = []
    failed_urls = []
    for product in products:
        # Ротация User-Agent для Selenium
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(USER_AGENTS)})
        print(f"Парсинг товара: {product['name']} (бренд: {product['brand']})")
        product_data = parse_product_page(driver, product['url'])
        if product_data:
            product_data['product_name'] = product['name']
            product_data['product_url'] = product['url']
            product_data['brand'] = product['brand']  # Используем бренд из API
            all_products.append(product_data)
        else:
            failed_urls.append(product['url'])
        time.sleep(random.uniform(1, 2))  # Случайная задержка для избежания блокировки

    # Логирование проблемных страниц
    if failed_urls:
        print(f"\nНе удалось спарсить {len(failed_urls)} страниц:")
        for url in failed_urls:
            print(url)

    # Группировка по брендам и ограничение до 100 товаров на бренд
    grouped = defaultdict(list)
    for product in all_products:
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

    # Закрытие браузера
    close_driver(driver)

if __name__ == "__main__":
    query = "латунный кран"
    main(query)