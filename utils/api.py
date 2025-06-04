import aiohttp
import asyncio
import json
from urllib.parse import quote
import random
from tqdm import tqdm
from loghandler import logger

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
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

async def fetch_url(session, url):
    """Асинхронное выполнение GET-запроса."""
    try:
        async with session.get(url, headers=get_headers(), timeout=5) as response:
            logger.debug(f"Запрос к {url}, статус: {response.status}, Content-Type: {response.headers.get('Content-Type')}")
            if response.status != 200:
                logger.error(f"HTTP ошибка при запросе {url}: {response.status}")
                return None
            # Читаем текст ответа
            text = await response.text()
            if not text:
                logger.warning(f"Пустой ответ от {url}")
                return None
            # Принудительно декодируем как JSON, игнорируя Content-Type
            try:
                data = json.loads(text)
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка декодирования JSON от {url}: {str(e)}. Текст ответа: {text[:500]}...")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Неизвестная ошибка при запросе {url}: {str(e)}")
        return None

async def get_all_products(query, max_pages=50):
    """Асинхронное получение всех товаров по запросу через API с пагинацией."""
    encoded_query = quote(query)
    base_url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-1255987&hide_dtype=13&lang=ru&query={encoded_query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
    all_products = []
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        tasks = []
        for page in range(1, min(max_pages + 1, 101)):
            url = f"{base_url}&page={page}"
            tasks.append(fetch_url(session, url))
        
        for page, result in enumerate(tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Парсинг страниц")):
            data = await result
            if not data:
                logger.info(f"Нет данных на странице {page + 1}. Продолжаем...")
                continue
            products = data.get("data", {}).get("products", [])
            if not products:
                logger.info(f"Нет продуктов на странице {page + 1}. Завершение пагинации.")
                break
            logger.debug(f"Получено {len(products)} товаров на странице {page + 1}")
            for p in products:
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
                if not price["product"]:
                    logger.warning(f"price.product отсутствует для товара {p.get('id', 'unknown')}")
                all_products.append(
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
            logger.info(f"Обработана страница {page + 1}, собрано товаров: {len(all_products)}")
            await asyncio.sleep(0.1)  # Задержка для избежания блокировки
    return all_products

# Кэш для данных продавцов
sellers_cache = {}

async def get_supplier_info(supplier_id):
    """Асинхронное получение информации о продавце по ID через новый API."""
    if supplier_id in sellers_cache:
        logger.debug(f"Используется кэш для продавца {supplier_id}")
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
            logger.info(f"Успешно получены данные о продавце {supplier_id}: {supplier_data['supplierFullName']}")
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
        return supplier_data