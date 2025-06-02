import requests
from urllib.parse import quote
import time

# Настройка заголовков для API запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

def get_all_products(query, max_pages=50):
    """Получение всех товаров по запросу через API с пагинацией."""
    encoded_query = quote(query)
    url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1255987&hide_dtype=13&lang=ru&query={encoded_query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
    all_products = []
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
            all_products.extend([
                {
                    'id': p['id'],
                    'name': p['name'],
                    'brand': p.get('brand', 'Неизвестный бренд'),
                    'url': f"https://www.wildberries.ru/catalog/{p['id']}/detail.aspx"
                } for p in products
            ])
            print(f"Обработана страница {page}, собрано товаров: {len(all_products)}")
            page += 1
            time.sleep(1)  # Задержка для избежания блокировки
        except Exception as e:
            print(f"Ошибка при получении товаров на странице {page}: {e}")
            break

    return all_products