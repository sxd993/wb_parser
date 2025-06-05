import aiohttp
import asyncio
import json
from urllib.parse import quote
import random

# Список User-Agent для ротации
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

def get_headers():
    """Возвращает заголовки с случайным User-Agent."""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Origin": "https://www.wildberries.ru",
        "Referer": "https://www.wildberries.ru/",
    }

async def fetch_url(session, url):
    """Асинхронное выполнение GET-запроса."""
    try:
        async with session.get(url, headers=get_headers(), timeout=10) as response:
            if response.status != 200:
                print(f"Status code: {response.status}")
                return None
            text = await response.text()
            if not text:
                print("Empty response")
                return None
            try:
                data = json.loads(text)
                return data
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e} - Raw response: {text[:500]}")
                return None
    except aiohttp.ClientError as e:
        print(f"ClientError: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при запросе {url}: {e}")
        raise

async def get_total_products(query):
    """Получение общего количества доступных товаров по запросу."""
    encoded_query = quote(query)
    url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1255987&hide_dtype=13&lang=ru&query={encoded_query}&resultset=filters&spp=30&suppressSpellcheck=false&uclusters=2"
    async with aiohttp.ClientSession() as session:
        data = await fetch_url(session, url)
        if data and isinstance(data, dict) and "data" in data and isinstance(data["data"], dict) and "total" in data["data"]:
            return data["data"]["total"]
        elif data:
            print(f"Unexpected data structure: {data}")
        else:
            print("No data returned from API")
        return 0

async def get_brand_ids(query):
    """Получение всех brand ID из каталога товаров по запросу."""
    encoded_query = quote(query)
    brand_ids = set()
    page = 1

    async with aiohttp.ClientSession() as session:
        while True:
            url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1255987&hide_dtype=13&lang=ru&query={encoded_query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false&page={page}"
            data = await fetch_url(session, url)
            if not data or "data" not in data or "products" not in data["data"]:
                break
            products = data["data"]["products"]
            if not products:
                break
            for product in products:
                brand_id = product.get("brandId")
                if brand_id:
                    brand_ids.add(brand_id)
            page += 1
            await asyncio.sleep(0.05)  # Уменьшенная задержка
    return list(brand_ids)

async def get_products_by_brand(query, brand_id, max_products_per_brand, progress_handler=None):
    """Получение товаров для конкретного brand ID."""
    encoded_query = quote(query)
    base_url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1581689&fbrand={brand_id}&hide_dtype=13&lang=ru&page=1&q1={encoded_query}&query={encoded_query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false&uclusters=2&uiv=0&uv=AQIAAQIDAAoACcgxQ948xkLCQ1W8GUVxwoK6aDz-v2PEtbzJOeG4C7iXOzZBfcNyPkREqcHqQVfEw0Lgu2NAbMpZxOa4G8OiwbzIE0HSHSu-M85MM-wVG-JDWqxUlIRcLIQtY16L-tSC1FVL54RlNFQsFoR8BBCjoAQHs35LzkPZFBOjwVxKrCh7-GREVGTMYtRcVGXzuVSzi8_cXCLHzEUjblQGY4eEnPQhbBB8GuOs3EEDFnPXLCjr0jPLhF4r_suY851kE7xrvGgTFFvJlDRjcJRZJE0Mchxsk2Ux0qwHDA7sFBQZM4VEQ7vBxIBD35Ph9DCr56xITGQj2zOtzIgjQbNqk_28cTPWYxVS1VNqsxVTFV"
    products = []
    page = 1

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=50)  # Увеличен лимит соединений
    ) as session:
        while len(products) < max_products_per_brand:
            url = base_url.replace("page=1", f"page={page}")
            data = await fetch_url(session, url)
            if not data:
                break
            product_data = data.get("data", {}).get("products", [])
            if not product_data:
                break
            for p in product_data:
                if len(products) >= max_products_per_brand:
                    break
                price = {
                    "basic": None,
                    "product": None,
                    "total": None,
                }
                if p.get("price"):
                    price_data = p.get("price", {})
                    price = {
                        "product": (
                            price_data.get("product", 0) / 100
                            if price_data.get("product")
                            else None
                        ),
                    }
                elif p.get("sizes"):
                    for size in p.get("sizes", []):
                        if size.get("price"):
                            price_data = size["price"]
                            price = {
                                "basic": (
                                    price_data.get("basic", 0) / 100
                                    if price_data.get("basic")
                                    else None
                                ),
                                "product": (
                                    price_data.get("product", 0) / 100
                                    if price_data.get("product")
                                    else None
                                ),
                                "total": (
                                    price_data.get("total", 0) / 100
                                    if price_data.get("total")
                                    else None
                                ),
                            }
                            break
                products.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "brand": p.get("brand", "Неизвестный бренд"),
                        "url": f"https://www.wildberries.ru/catalog/{p['id']}/detail.aspx",
                        "price": price,
                        "article": p.get("id"),
                        "feedbacks": p.get("feedbacks", 0),
                        "rating": p.get("reviewRating", 0),
                        "supplier": p.get("supplier", "Неизвестный продавец"),
                        "supplierId": p.get("supplierId", 0),
                        "supplierRating": p.get("supplierRating", 0),
                    }
                )
                if progress_handler:
                    progress_handler.update(1)
            page += 1
            await asyncio.sleep(0.05)  # Уменьшенная задержка
    return products

async def get_all_products(query, max_products, progress_handler=None):
    """Асинхронное получение всех товаров по запросу через API для всех brand ID."""
    brand_ids = await get_brand_ids(query)
    if not brand_ids:
        return []

    all_products = []
    if progress_handler:
        progress_handler.set_total(max_products)

    # Распараллеливаем запросы для всех brand_id
    async def fetch_products_for_brand(brand_id):
        return await get_products_by_brand(
            query,
            brand_id,
            max_products - len(all_products),
            progress_handler
        )

    # Выполняем запросы параллельно
    tasks = [fetch_products_for_brand(brand_id) for brand_id in brand_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if not isinstance(result, Exception):
            all_products.extend(result)
        if len(all_products) >= max_products:
            break

    return all_products[:max_products]

# Кэш для данных продавцов
sellers_cache = {}

async def get_supplier_info(supplier_id, progress_handler=None):
    """Асинхронное получение информации о продавце по ID через новый API."""
    if supplier_id in sellers_cache:
        if progress_handler:
            progress_handler.update(1)
        return sellers_cache[supplier_id]

    url = f"https://static-basket-01.wb.ru/vol0/data/supplier-by-id/{supplier_id}.json"
    async with aiohttp.ClientSession() as session:
        data = await fetch_url(session, url)
        if data:
            supplier_data = {
                "supplierId": data.get("supplierId", supplier_id),
                "supplierName": data.get("supplierName", "Неизвестно"),
                "supplierFullName": data.get("supplierFullName", "Неизвестно"),
                "inn": data.get("inn", "Неизвестно"),
                "ogrn": data.get("ogrn", "Неизвестно"),
                "ogrnip": data.get("ogrnip", "Неизвестно"),
                "legalAddress": data.get("legalAddress", "Неизвестно"),
                "trademark": data.get("trademark", "Неизвестно"),
                "kpp": data.get("kpp", "Неизвестно"),
                "taxpayerCode": data.get("taxpayerCode", "Неизвестно"),
                "unp": data.get("unp", "Неизвестно"),
                "bin": data.get("bin", "Неизвестно"),
                "unn": data.get("unn", "Неизвестно"),
                "supplierUrl": f"https://www.wildberries.ru/seller/{supplier_id}",
            }
            sellers_cache[supplier_id] = supplier_data
        else:
            supplier_data = {
                "supplierId": supplier_id,
                "supplierName": "Неизвестно",
                "supplierFullName": "Неизвестно",
                "inn": "Неизвестно",
                "ogrn": "Неизвестно",
                "ogrnip": "Неизвестно",
                "legalAddress": "Неизвестно",
                "trademark": "Неизвестно",
                "kpp": "Неизвестно",
                "taxpayerCode": "Неизвестно",
                "unp": "Неизвестно",
                "bin": "Неизвестно",
                "unn": "Неизвестно",
                "supplierUrl": f"https://www.wildberries.ru/seller/{supplier_id}",
            }
            sellers_cache[supplier_id] = supplier_data
        if progress_handler:
            progress_handler.update(1)
        return supplier_data