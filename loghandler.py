import logging
import os
from logging.handlers import RotatingFileHandler

class MessageCountFilter(logging.Filter):
    """Фильтр для подсчета сообщений и очистки файла при превышении лимита."""
    def __init__(self, max_messages, log_file):
        super().__init__()
        self.max_messages = max_messages
        self.log_file = log_file
        self.message_count = 0

    def filter(self, record):
        self.message_count += 1
        if self.message_count > self.max_messages:
            # Очищаем файл
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.truncate(0)
            self.message_count = 1  # Сбрасываем счетчик после очистки
        return True

def setup_logging():
    """Настройка логирования с ротацией файлов и очисткой по количеству сообщений."""
    # Создаем папку logs, если она не существует
    os.makedirs("logs", exist_ok=True)

    # Создаем логгер
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень для логгера

    # Очищаем существующие обработчики, чтобы избежать дублирования
    logger.handlers = []

    # Форматтер для логов
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Обработчик для info.log (INFO и DEBUG)
    info_handler = RotatingFileHandler(
        'logs/info.log', maxBytes=15*1024, backupCount=5, encoding='utf-8'
    )
    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(formatter)
    # Фильтр для записи только INFO и DEBUG
    info_handler.addFilter(lambda record: record.levelno in [logging.INFO, logging.DEBUG])
    # Добавляем фильтр для подсчета сообщений
    info_handler.addFilter(MessageCountFilter(max_messages=200, log_file='logs/info.log'))

    # Обработчик для error.log (ERROR)
    error_handler = RotatingFileHandler(
        'logs/error.log', maxBytes=15*1024, backupCount=5, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    # Добавляем фильтр для подсчета сообщений
    error_handler.addFilter(MessageCountFilter(max_messages=100, log_file='logs/error.log'))

    # Обработчик для вывода в консоль (только определенные INFO сообщения)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    # Фильтр для вывода только сообщений о сохранении JSON и Excel
    console_handler.addFilter(lambda record: record.levelno == logging.INFO and 
                            ("Данные сохранены" in record.getMessage() or 
                             "Excel файл успешно создан" in record.getMessage()))

    # Добавляем обработчики к логгеру
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger

# Создаем логгер для использования в других модулях
logger = setup_logging()