import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5 import QtGui
from utils.api import get_total_products
from main import main
import qasync
from tqdm import tqdm

class TqdmToProgressBar(QObject):
    """Класс для перенаправления обновлений tqdm в QProgressBar."""
    progress_updated = pyqtSignal(int)
    total_updated = pyqtSignal(int)

    def __init__(self, progress_bar):
        super().__init__()
        self.progress_bar = progress_bar
        self.progress_updated.connect(self.progress_bar.setValue)
        self.total_updated.connect(self.progress_bar.setMaximum)

    def update(self, n=1):
        self.progress_updated.emit(self.progress_bar.value() + n)

    def set_total(self, total):
        self.total_updated.emit(total)

class ParserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Парсер Wildberries")
        self.setGeometry(100, 100, 450, 550)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel("Парсер Wildberries")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Поле для поискового запроса
        self.query_label = QLabel("Поисковый запрос:")
        self.query_label.setStyleSheet("font-size: 14px; color: #555;")
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Введите запрос, например, 'смартфон'")
        self.query_input.setStyleSheet("font-size: 14px; padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        query_layout = QHBoxLayout()
        query_layout.addStretch()
        query_layout.addWidget(self.query_input, 1)
        query_layout.addStretch()
        main_layout.addWidget(self.query_label)
        main_layout.addLayout(query_layout)

        # Кнопка для подгрузки общего количества товаров
        self.load_total_button = QPushButton("Подгрузить количество товаров")
        self.load_total_button.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                padding: 8px; 
                background-color: #6B7280; 
                color: white; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
            }
        """)
        self.load_total_button.clicked.connect(self.load_total_products)
        load_total_layout = QHBoxLayout()
        load_total_layout.addStretch()
        load_total_layout.addWidget(self.load_total_button, 1)
        load_total_layout.addStretch()
        main_layout.addLayout(load_total_layout)

        # Поле для общего количества товаров
        self.total_label = QLabel("Всего товаров доступно: Не загружено")
        self.total_label.setStyleSheet("font-size: 14px; color: #555;")
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        main_layout.addLayout(total_layout)

        # Поле для количества товаров для парсинга
        self.max_products_label = QLabel("Количество товаров для парсинга:")
        self.max_products_label.setStyleSheet("font-size: 14px; color: #555;")
        self.max_products_input = QLineEdit("1000")
        self.max_products_input.setValidator(QtGui.QIntValidator(1, 1000000))
        self.max_products_input.setStyleSheet("font-size: 14px; padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        max_products_layout = QHBoxLayout()
        max_products_layout.addStretch()
        max_products_layout.addWidget(self.max_products_input, 1)
        max_products_layout.addStretch()
        main_layout.addWidget(self.max_products_label)
        main_layout.addLayout(max_products_layout)

        # Поле для имени выходного файла
        self.output_file_label = QLabel("Имя выходного файла:")
        self.output_file_label.setStyleSheet("font-size: 14px; color: #555;")
        self.output_file_input = QLineEdit("wildberries_products.xlsx")
        self.output_file_input.setStyleSheet("font-size: 14px; padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        output_file_layout = QHBoxLayout()
        output_file_layout.addStretch()
        output_file_layout.addWidget(self.output_file_input, 1)
        output_file_layout.addStretch()
        main_layout.addWidget(self.output_file_label)
        main_layout.addLayout(output_file_layout)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("font-size: 12px; padding: 5px;")
        self.progress_bar.setTextVisible(True)
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addStretch()
        main_layout.addLayout(progress_layout)

        # Кнопка для запуска парсинга
        self.parse_button = QPushButton("Начать парсинг")
        self.parse_button.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                padding: 10px; 
                background-color: #4A90E2; 
                color: white; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:disabled {
                background-color: #A0C4FF;
            }
        """)
        parse_button_layout = QHBoxLayout()
        parse_button_layout.addStretch()
        parse_button_layout.addWidget(self.parse_button, 1)
        parse_button_layout.addStretch()
        self.parse_button.clicked.connect(self.start_parsing)
        main_layout.addLayout(parse_button_layout)

        # Поле для статуса
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setStyleSheet("font-size: 12px; border: 1px solid #ccc; border-radius: 5px; padding: 5px; background-color: white;")
        self.status_output.setFixedHeight(100)
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        status_layout.addWidget(self.status_output, 1)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)

    @qasync.asyncSlot()
    async def load_total_products(self):
        query = self.query_input.text().strip()
        if not query:
            self.status_output.append("Ошибка: Введите поисковый запрос")
            return
        self.load_total_button.setEnabled(False)
        self.status_output.append("Загрузка общего количества товаров...")
        try:
            total = await get_total_products(query)
            if total > 0:
                self.total_label.setText(f"Всего товаров доступно: {total}")
                self.status_output.append(f"Получено значение total: {total}")
            else:
                self.total_label.setText("Всего товаров доступно: Не удалось загрузить")
                self.status_output.append("Не удалось получить количество товаров")
        except Exception as e:
            self.status_output.append(f"Ошибка загрузки total: {str(e)}")
            self.total_label.setText("Всего товаров доступно: Ошибка")
        finally:
            self.load_total_button.setEnabled(True)

    async def run_parsing(self, query, max_products, output_file, progress_handler):
        try:
            await main(query, output_file, max_products, progress_handler)
            self.status_output.append(f"Парсинг завершен. Файл сохранен: {output_file}")
        except Exception as e:
            self.status_output.append(f"Ошибка при парсинге: {str(e)}")
        finally:
            self.parse_button.setEnabled(True)
            self.load_total_button.setEnabled(True)
            self.progress_bar.setValue(0)

    @qasync.asyncSlot()
    async def start_parsing(self):
        query = self.query_input.text().strip()
        if not query:
            self.status_output.append("Ошибка: Введите поисковый запрос")
            return
        try:
            max_products = int(self.max_products_input.text())
        except ValueError:
            self.status_output.append("Ошибка: Введите корректное число для количества товаров")
            return
        output_file = self.output_file_input.text().strip()
        if not output_file:
            self.status_output.append("Ошибка: Введите имя выходного файла")
            return
        self.parse_button.setEnabled(False)
        self.load_total_button.setEnabled(False)
        self.status_output.append("Парсинг начат...")
        progress_handler = TqdmToProgressBar(self.progress_bar)
        await self.run_parsing(query, max_products, output_file, progress_handler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = ParserApp()
    window.show()
    with loop:
        loop.run_forever()