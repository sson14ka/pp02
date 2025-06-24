from PyQt5 import uic
from PyQt5.QtCore import QFile, QIODevice, QTextStream
from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QVBoxLayout, QLineEdit, QComboBox, QSpinBox, QPushButton, \
    QDialog, QTextBrowser, QMessageBox
from session import session
from orm import UsersORM, DocumentsORM, RolesORM
import bcrypt
import os



class AutorizationWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi("gui/formautorization.ui", self)
        self.label_error = QLabel(self)
        self.label_error.setGeometry(230, 170, 300, 30)  # Позиция и размер
        self.label_error.setStyleSheet("color: red; background-color: white;")


class ViewerWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi("gui/formviser.ui", self)
        headers = ["id", "Название", "Категория", "Дата создания", "Уровень доступа"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

class ManagerWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi("gui/managermain.ui", self)
        headers = ["id", "Название", "Категория", "Дата создания", "Уровень доступа", "Путь к файлу"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

class AdminWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi("gui/adminka.ui", self)

        headers = ["id","Имя", "Фамилия","Отчество", "Почта", "Уровень доступа"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        doc_headers = ["id", "Название","Категория","Дата создания","Уровень доступа", "Путь к файлу"]
        self.tableWidget_2.setColumnCount(len(doc_headers))
        self.tableWidget_2.setHorizontalHeaderLabels(doc_headers)

    def hash_password(password: str) -> str:
        """Хэширует пароль с солью (salt) и возвращает строку в формате bcrypt."""
        salt = bcrypt.gensalt()  # Генерация соли
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')  # Преобразуем bytes в строку


class DocumentForm(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Добавление нового документа')
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        # Название документа
        self.title_label = QLabel('Название документа:')
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Категория документа
        self.category_label = QLabel('Категория:')
        self.category_input = QComboBox()
        self.category_input.addItems(['Приказы', 'Договоры', 'Отчеты', 'Презентации', 'Техническая документация'])
        self.category_input.setEditable(True)  # Разрешаем ввод своей категории
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_input)

        # Уровень доступа
        self.security_label = QLabel('Уровень доступа (1-3):')
        self.security_input = QSpinBox()
        self.security_input.setRange(1, 3)
        self.security_input.setValue(1)
        layout.addWidget(self.security_label)
        layout.addWidget(self.security_input)

        # Путь к файлу
        self.file_label = QLabel('Файл документа:')
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.browse_button = QPushButton('Выбрать файл...')


        file_layout = QVBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # Кнопка добавления
        self.add_button = QPushButton('Добавить документ')
        layout.addWidget(self.add_button)
        self.setLayout(layout)

class DocumentViewer(QDialog):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Просмотр документа")
            self.resize(800, 600)

            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            # Текстовое поле для отображения содержимого
            self.text_browser = QTextBrowser()
            self.text_browser.setReadOnly(True)
            self.layout.addWidget(self.text_browser)

    def load_document(self, document_id):
            """Загружает документ для просмотра"""
            print("loading started..")
            file = session.get(DocumentsORM, document_id)
            file_path = file.file_path
            print(file_path)
            try:
                # Проверка существования файла
                if not os.path.exists(file_path):
                    QMessageBox.warning(self, "Ошибка", "Файл не найден")
                    return False

                # Чтение файла
                file = QFile(file_path)
                if file.open(QIODevice.ReadOnly | QIODevice.Text):
                    stream = QTextStream(file)
                    self.text_browser.setPlainText(stream.readAll())
                    file.close()
                    self.setWindowTitle(f"Просмотр - {os.path.basename(file_path)}")
                    return True
                else:
                    raise IOError("Не удалось открыть файл")
            except Exception as e:
                self.text_browser.setPlainText(f"Ошибка при чтении файла:\n{str(e)}")
                return False




