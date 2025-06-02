import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Настройка и запуск Selenium драйвера."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Запуск в фоновом режиме
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def close_driver(driver):
    """Закрытие Selenium драйвера."""
    driver.quit()

def parse_product_page(driver, url):
    """Парсинг страницы товара с помощью Selenium."""
    try:
        driver.get(url)
        time.sleep(2)  # Ожидание загрузки страницы

        # Извлечение бренда
        try:
            brand = driver.find_element(By.CSS_SELECTOR, '.brand-and-name .brand').text
        except:
            brand = 'Не найдено'

        # Извлечение цены
        try:
            price = driver.find_element(By.CSS_SELECTOR, '.price-block__final-price').text
        except:
            price = 'Не найдено'

        # Извлечение описания
        try:
            description = driver.find_element(By.CSS_SELECTOR, '.product-description').text
        except:
            description = 'Не найдено'

        # Извлечение характеристик
        characteristics = {}
        try:
            specs = driver.find_elements(By.CSS_SELECTOR, '.product-params__row')
            for spec in specs:
                key = spec.find_element(By.CSS_SELECTOR, '.product-params__label').text
                value = spec.find_element(By.CSS_SELECTOR, '.product-params__value').text
                characteristics[key] = value
        except:
            characteristics = {'Характеристики': 'Не найдены'}

        return {
            'brand': brand,
            'price': price,
            'description': description,
            'specifications': characteristics
        }
    except Exception as e:
        print(f"Ошибка при парсинге страницы {url}: {e}")
        return None