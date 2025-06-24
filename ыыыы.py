#
# def send_password_by_email(email_to, password):
#     # Настройки SMTP (пример для Gmail)
#     smtp_server = "smtp.gmail.com"
#     smtp_port = 587
#     smtp_username = "your_email@gmail.com"  # Замените на ваш email
#     smtp_password = "your_app_password"    # Пароль приложения (не основной пароль!)
#
#     # Создаем сообщение
#     msg = MIMEMultipart()
#     msg['From'] = smtp_username
#     msg['To'] = email_to
#     msg['Subject'] = "Ваш новый пароль"
#
#     body = f"Ваш новый пароль: {password}\n\nНе сообщайте его никому!"
#     msg.attach(MIMEText(body, 'plain'))
#
#     try:
#         # Подключаемся к серверу и отправляем
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(smtp_username, smtp_password)
#             server.send_message(msg)
#         print("Пароль успешно отправлен на email!")
#         return True
#     except Exception as e:
#         print(f"Ошибка при отправке email: {e}")
#         return False

import datetime
print(datetime.date.today())

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser,
                             QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import QFile, QTextStream, QIODevice
import os


def view_document(self, file_path):
    """
    Просмотр содержимого документа в режиме только для чтения

    Args:
        file_path: Путь к файлу документа
    """
    # Проверка существования файла
    if not os.path.exists(file_path):
        QMessageBox.warning(self, "Ошибка", "Файл не найден")
        return

    # Создаем диалоговое окно для просмотра
    view_dialog = QDialog(self)
    view_dialog.setWindowTitle(f"Просмотр документа - {os.path.basename(file_path)}")
    view_dialog.resize(800, 600)

    layout = QVBoxLayout()

    # Текстовое поле для отображения содержимого
    text_browser = QTextBrowser()
    text_browser.setReadOnly(True)

    try:
        # Чтение файла
        file = QFile(file_path)
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            stream = QTextStream(file)
            text_browser.setPlainText(stream.readAll())
            file.close()
        else:
            raise IOError("Не удалось открыть файл")
    except Exception as e:
        text_browser.setPlainText(f"Ошибка при чтении файла:\n{str(e)}")

    # Кнопка закрытия
    close_btn = QPushButton("Закрыть")
    close_btn.clicked.connect(view_dialog.close)

    layout.addWidget(text_browser)
    layout.addWidget(close_btn)
    view_dialog.setLayout(layout)

    view_dialog.exec_()