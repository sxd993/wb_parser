import requests
from urllib.parse import quote
import time

# Настройка заголовков для API запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

def get_brands(query, max_pages=50):
    """Получение списка брендов для заданного запроса через API с пагинацией."""
    encoded_query = quote(query)
    url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1255987&hide_dtype=13&lang=ru&query={encoded_query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
    brands = set()
    page = 1

    while page <= max_pages:
        try:
            response = requests.get(f"{url}&page={page}", headers=headers)
            response.raise_for_status()
            data = response.json()
            products = data.get('data', {}).get('products', [])
            if not products:
                print(f"Нет продуктов на странице {page}. Завершение пагинации.")
                break
            for item in products:
                brand = item.get('brand', '')
                if brand:
                    brands.add(brand)
            print(f"Обработана страница {page}, найдено брендов: {len(brands)}")
            page += 1
            time.sleep(1)  # Задержка для избежания блокировки
        except Exception as e:
            print(f"Ошибка при получении брендов на странице {page}: {e}")
            break

    return list(brands)

def get_products_by_brand(query, brand, limit=100):
    """Получение товаров по бренду через API."""
    encoded_query = quote(query)
    encoded_brand = quote(brand)
    url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1255987&hide_dtype=13&lang=ru&query={encoded_query}&brand={encoded_brand}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
    products = []
    page = 1
    while len(products) < limit:
        try:
            response = requests.get(f"{url}&page={page}", headers=headers)
            response.raise_for_status()
            data = response.json()
            if not data['data']['products']:
                break
            for product in data['data']['products']:
                if len(products) >= limit:
                    break
                products.append({
                    'id': product['id'],
                    'name': product['name'],
                    'url': f"https://www.wildberries.ru/catalog/{product['id']}/detail.aspx"
                })
            page += 1
            time.sleep(1)  # Задержка для избежания блокировки
        except Exception as e:
            print(f"Ошибка при получении товаров для бренда {brand}: {e}")
            break
    return products