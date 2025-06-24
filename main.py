import sys

from PyQt5.QtCore import QFile, QIODevice, QTextStream
from PyQt5.QtWidgets import QApplication, QLineEdit, QMessageBox, QFileDialog, QTableWidgetItem, QDialog, QVBoxLayout, \
    QTextBrowser, QPushButton
from sqlalchemy import or_, extract, update
from gui.windows import AutorizationWindow, AdminWindow, ManagerWindow, ViewerWindow, DocumentForm, DocumentViewer
from session import session
import bcrypt
from orm import UsersORM, DocumentsORM
import random
import string
import datetime
import os



class Control():
    def __init__(self, w):
        self.AutorizationWin = w
        self.AdmWin = AdminWindow()
        self.ManagerWin = ManagerWindow()
        self.ViewerWin = ViewerWindow()
        self.DocsWin = DocumentForm()
        self.DocsViewer = DocumentViewer()
        self.AutorizationWin.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.AutorizationWin.pushButton.clicked.connect(self.login)
        self.AdmWin.pushButton_10.clicked.connect(self.add_user)
        self.AdmWin.pushButton_8.clicked.connect(self.delete_user)
        self.AdmWin.pushButton_2.clicked.connect(self.show_add_docs)
        self.DocsWin.browse_button.clicked.connect(self.browse_file)
        self.DocsWin.add_button.clicked.connect(self.add_document)
        self.AdmWin.pushButton_5.clicked.connect(self.delete_document)
        self.AdmWin.pushButton.clicked.connect(self.search_documents)
        self.AdmWin.pushButton_6.clicked.connect(self.issue_to_manager)
        self.AdmWin.pushButton_7.clicked.connect(self.return_document)
        self.AdmWin.tableWidget_2.cellDoubleClicked.connect(self.admin_open_file)
        self.ManagerWin.pushButton.clicked.connect(self.search_documents)
        self.ManagerWin.tableWidget.cellDoubleClicked.connect(self.manager_open_file)
        self.ViewerWin.tableWidget.cellDoubleClicked.connect(self.viewer_open_file)
        self.ManagerWin.pushButton_3.clicked.connect(self.issue_to_viewer)
        self.ManagerWin.pushButton_4.clicked.connect(self.return_from_viewer)


    def login(self):
        email = self.AutorizationWin.lineEdit.text()  # Поле для email
        password = self.AutorizationWin.lineEdit_2.text()  # Поле для пароля
        user = session.query(UsersORM).filter_by(email=email).first()
        if user and self.check_password(user.hash_password, password):
            self.current_user_id = user.id
            self.current_user_role = user.role_id
            print(user.id)
            if user.role_id == 1:  #роль 1 = админ
                self.AdmWin.show()
                self.show_users()
                self.show_documents()

            elif user.role_id == 2:  # Менеджер
                self.ManagerWin.show()
                self.show_documents_manager()
            elif user.role_id == 3:
                self.ViewerWin.show()
                self.show_documents_viwer()
            self.AutorizationWin.close()
        else:
            self.AutorizationWin.label_error.setText("Неверный email или пароль")

    def add_user(self):
        try:
            password = self.generate_password()
            new_user = UsersORM(name=self.AdmWin.lineEdit_2.text(),
                            surname=self.AdmWin.lineEdit_3.text(),
                            patronymic=self.AdmWin.lineEdit_4.text(),
                            email=self.AdmWin.lineEdit_5.text(),
                            role_id=int((self.AdmWin.comboBox.currentText())[0]),
                            hash_password=self.hash_password(password))

            session.add(new_user)
            session.commit()
            self.show_users()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(None, "Ошибка", f"Не удалось добавить пользователя: {e}")

    def find_user_in_table(self):
        selected_row = self.AdmWin.tableWidget.currentRow()
        user_id = int(self.AdmWin.tableWidget.item(selected_row, 0).text())
        return user_id

    def delete_user(self):
        user_id = self.find_user_in_table()
        confirm = QMessageBox.question(
            None,
            "Подтверждение",
            f"Вы уверены, что хотите удалить пользователя с ID {user_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            user = session.get(UsersORM, user_id)
            session.delete(user)
            session.commit()
            self.show_users()

    def show_users(self):
        users = (session.query(UsersORM.id, UsersORM.name, UsersORM.surname, UsersORM.patronymic, UsersORM.email, UsersORM.role_id).all())
        self.AdmWin.tableWidget.setRowCount(len(users))
        row = 0
        for user in users:
            col = 0
            for item in user:
                self.cellinfo = QTableWidgetItem(str(item))
                self.AdmWin.tableWidget.setItem(row, col, self.cellinfo)
                col += 1
            row += 1
        self.AdmWin.tableWidget.resizeColumnsToContents()

    def generate_password(self):
        letters = (random.choices(string.ascii_letters, k=random.randint(7, 8)))
        digits = (random.choices(string.digits, k=random.randint(2, 3)))
        # Объединяем буквы и цифры, перемешиваем
        password = list(letters + digits)
        random.shuffle(password)
        password = str(''.join(password))
        msgBox = QMessageBox()
        msgBox.setWindowTitle("registration succeed!")
        msgBox.setText(f"сгенерирован пароль: {password}")
        msgBox.exec_()
        return password


    def check_password(self, hash_password: str, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hash_password.encode('utf-8'))

    def hash_password(self, password: str) -> str:
        """Хэширует пароль с солью (salt) и возвращает строку в формате bcrypt."""
        salt = bcrypt.gensalt()  # Генерация соли
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')  # Преобразуем bytes в строку

    def show_add_docs(self):
        self.DocsWin.show()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None, 'Выберите файл документа', '',
            'Все файлы (*);;Документы (*.docx *.xlsx *.pdf *.txt)'
        )
        if file_path:
            self.DocsWin.file_input.setText(file_path)

    def add_document(self):
        # Получаем данные из формы
        title = self.DocsWin.title_input.text().strip()
        category = self.DocsWin.category_input.currentText().strip()
        security_level = self.DocsWin.security_input.value()
        file_path = self.DocsWin.file_input.text().strip()
        print(title, category, security_level, file_path, self.current_user_id)
        # Валидация данных
        if not title:
            QMessageBox.warning(None, 'Ошибка', 'Введите название документа')
            return
        if not file_path:
            QMessageBox.warning(None, 'Ошибка', 'Выберите файл документа')
            return
        try:
            new_document = DocumentsORM(title=title,
                                        category=category,
                                        security_level=security_level,
                                        file_path=file_path,
                                        cration_date= datetime.datetime.now(),
                                        creator_id=self.current_user_id)
            session.add(new_document)
            session.commit()
            QMessageBox.information(None, 'Успех', 'Документ успешно добавлен')
        except Exception as db_error:
            session.rollback()
            QMessageBox.critical(self.DocsWin, 'Ошибка БД', f'Ошибка при сохранении: {str(db_error)}')
        self.show_documents()
        self.DocsWin.hide()

    def find_document_in_admin_table(self):
        selected_row = self.AdmWin.tableWidget_2.currentRow()
        document_id = int(self.AdmWin.tableWidget_2.item(selected_row, 0).text())
        return document_id

    def find_document_in_manager_table(self):
        selected_row = self.ManagerWin.tableWidget.currentRow()
        document_id = int(self.ManagerWin.tableWidget.item(selected_row, 0).text())
        return document_id

    def find_document_in_viewer_table(self):
        selected_row = self.ViewerWin.tableWidget.currentRow()
        document_id = int(self.ViewerWin.tableWidget.item(selected_row, 0).text())
        print(document_id)
        return document_id

    def delete_document(self):
        document_id = self.find_document_in_admin_table()
        confirm = QMessageBox.question(
            None,
            "Подтверждение",
            f"Вы уверены, что хотите удалить документ с ID {document_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            document = session.get(DocumentsORM, document_id)
            session.delete(document)
            session.commit()
            self.show_documents()

    def show_documents(self):
        documents = (session.query(DocumentsORM.id, DocumentsORM.title, DocumentsORM.category, DocumentsORM.cration_date, DocumentsORM.security_level, DocumentsORM.file_path).all())
        self.AdmWin.tableWidget_2.setRowCount(len(documents))
        row = 0
        for document in documents:
            col = 0
            for item in document:
                cellinfo = QTableWidgetItem(str(item))
                self.AdmWin.tableWidget_2.setItem(row, col, cellinfo)
                col += 1
            row += 1
        self.AdmWin.tableWidget_2.resizeColumnsToContents()

    def show_documents_manager(self):
        documents = (session.query(DocumentsORM.id, DocumentsORM.title, DocumentsORM.category, DocumentsORM.cration_date, DocumentsORM.security_level, DocumentsORM.file_path).filter(DocumentsORM.security_level <= 2).all())
        self.ManagerWin.tableWidget.setRowCount(len(documents))
        row = 0
        for document in documents:
            col = 0
            for item in document:
                cellinfo = QTableWidgetItem(str(item))
                self.ManagerWin.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1
        self.ManagerWin.tableWidget.resizeColumnsToContents()

    def show_documents_viwer(self):
        documents = (session.query(DocumentsORM.id, DocumentsORM.title, DocumentsORM.category, DocumentsORM.cration_date, DocumentsORM.security_level).filter(DocumentsORM.security_level == 1).all())
        self.ViewerWin.tableWidget.setRowCount(len(documents))
        print(documents)
        row = 0
        for document in documents:
            col = 0
            for item in document:
                cellinfo = QTableWidgetItem(str(item))
                self.ViewerWin.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1
        self.ViewerWin.tableWidget.resizeColumnsToContents()

    def search_documents(self):
        if self.current_user_role == 1:
            search_term = self.AdmWin.lineEdit.text()
            self.AdmWin.tableWidget_2.setRowCount(0)
        elif self.current_user_role == 2:
            search_term = self.ManagerWin.lineEdit.text()
            self.ManagerWin.tableWidget.setRowCount(0)
        else:
            search_term = self.ViewerWin.lineEdit.text()
            self.ViewerWin.tableWidget.setRowCount(0)
        try:
            query = session.query(DocumentsORM)

            # Проверяем, является ли поисковый запрос годом (4 цифры)
            year_search = None
            if search_term.isdigit() and len(search_term) == 4:
                try:
                    year_search = int(search_term)
                    if 1900 <= year_search <= datetime.datetime.now().year:
                        # Фильтр по году из даты создания
                        query = query.filter(
                            extract('year', DocumentsORM.cration_date) == year_search
                        )
                except ValueError:
                    pass

            if not year_search:
                # Поиск по названию или категории (регистронезависимый)
                search_pattern = f"%{search_term}%"
                query = query.filter(
                    or_(
                        DocumentsORM.title.ilike(search_pattern),
                        DocumentsORM.category.ilike(search_pattern)
                    )
                )

            if self.current_user_role == 1:
                documents = query.order_by(DocumentsORM.cration_date.desc()).all()
                if not documents:
                    QMessageBox.information(None, "Результаты", "Документы не найдены")
                    return
                self.AdmWin.tableWidget_2.setRowCount(len(documents))
                for row, doc in enumerate(documents):
                    self.AdmWin.tableWidget_2.setItem(row, 0, QTableWidgetItem(str(doc.id)))
                    self.AdmWin.tableWidget_2.setItem(row, 1, QTableWidgetItem(doc.title))
                    self.AdmWin.tableWidget_2.setItem(row, 2, QTableWidgetItem(doc.category))
                    self.AdmWin.tableWidget_2.setItem(row, 3, QTableWidgetItem(doc.cration_date.strftime("%d.%m.%Y")))
                    self.AdmWin.tableWidget_2.setItem(row, 4, QTableWidgetItem(str(doc.security_level)))
                    self.AdmWin.tableWidget_2.setItem(row, 5, QTableWidgetItem(doc.file_path))
                    # Настраиваем отображение таблицы
                self.AdmWin.tableWidget_2.resizeColumnsToContents()

            if self.current_user_role == 2:
                documents = query.order_by(DocumentsORM.cration_date.desc()).filter(DocumentsORM.security_level <= 2).all()
                if not documents:
                    QMessageBox.information(None, "Результаты", "Документы не найдены")
                    return
                self.ManagerWin.tableWidget.setRowCount(len(documents))
                for row, doc in enumerate(documents):
                    self.ManagerWin.tableWidget.setItem(row, 0, QTableWidgetItem(str(doc.id)))
                    self.ManagerWin.tableWidget.setItem(row, 1, QTableWidgetItem(doc.title))
                    self.ManagerWin.tableWidget.setItem(row, 2, QTableWidgetItem(doc.category))
                    self.ManagerWin.tableWidget.setItem(row, 3, QTableWidgetItem(doc.cration_date.strftime("%d.%m.%Y")))
                    self.ManagerWin.tableWidget.setItem(row, 4, QTableWidgetItem(str(doc.security_level)))
                    self.ManagerWin.tableWidget.setItem(row, 5, QTableWidgetItem(doc.file_path))
                # Оптимизация отображения
                self.ManagerWin.tableWidget_2.resizeColumnsToContents()
            else:
                documents = query.order_by(DocumentsORM.cration_date.desc()).filter(DocumentsORM.security_level == 1).all()
                if not documents:
                    QMessageBox.information(None, "Результаты", "Документы не найдены")
                self.ViewerWin.tableWidget.setRowCount(len(documents)-1)
                for row, doc in enumerate(documents):
                    self.ViewerWin.tableWidget.setItem(row, 0, QTableWidgetItem(str(doc.id)))
                    self.ViewerWin.tableWidget.setItem(row, 1, QTableWidgetItem(doc.title))
                    self.ViewerWin.tableWidget.setItem(row, 2, QTableWidgetItem(doc.category))
                    self.ViewerWin.tableWidget.setItem(row, 3, QTableWidgetItem(doc.cration_date.strftime("%d.%m.%Y")))
                    self.ViewerWin.tableWidget.setItem(row, 4, QTableWidgetItem(str(doc.security_level)))
                if not documents:
                    QMessageBox.information(None, "Результаты", "Документы не найдены")
                    return


        except Exception as e:
            print(f"Ошибка при поиске документов: {str(e)}")
            return []

    def issue_to_manager(self):
        try:
            # Получаем текущий документ
            document_id = self.find_document_in_admin_table()
            document = session.get(DocumentsORM, document_id)
            if not document:
                QMessageBox.warning(None, "Ошибка", "Документ не найден")
                return False
            # Проверяем текущий уровень защиты
            if document.security_level == 3:
                # Обновляем уровень защиты
                session.execute(
                    update(DocumentsORM)
                    .where(DocumentsORM.id == document_id)
                    .values(security_level=2)
                )
                session.commit()
                QMessageBox.information(None, "Успех",
                                        "Документ выдан менеджеру (уровень защиты изменен с 3 на 2)")
                self.show_documents()
                return True
            else:
                QMessageBox.information(None, "Информация",
                                        f"Документ уже имеет уровень защиты {document.security_level} - изменения не требуются")
                return False
        except Exception as e:
            session.rollback()
            QMessageBox.critical(None, "Ошибка",
                                 f"Не удалось выдать документ менеджеру:\n{str(e)}")
            return False

    def return_document(self):
        document_id = self.find_document_in_admin_table()
        try:
            # Получаем документ
            document = session.get(DocumentsORM, document_id)
            if not document:
                QMessageBox.warning(None, "Ошибка", "Документ не найден")
                return False
            # Проверяем текущий уровень защиты
            if document.security_level in (1, 2):
                old_level = document.security_level
                # Обновляем уровень защиты на 3
                stmt = (
                    update(DocumentsORM)
                    .where(DocumentsORM.id == document_id)
                    .values(security_level=3)
                )
                session.execute(stmt)
                session.commit()
                QMessageBox.information(None,"Успех","Документ возвращен (уровень защиты изменен)")
                self.show_documents()
                return True
            else:
                QMessageBox.information(None, "Информация","Документ уже имеет уровень защиты 3 - изменения не требуются")
                return False
        except Exception as e:
            session.rollback()
            QMessageBox.critical(None,"Ошибка", f"Не удалось вернуть документ:\n{str(e)}")
            return False

    def issue_to_viewer(self):
        """
        Менеджер выдает документ вьюверу (устанавливает уровень защиты 1)
        """
        try:
            # Получаем ID выбранного документа
            document_id = self.find_document_in_manager_table()
            if not document_id:
                QMessageBox.warning(None, "Ошибка", "Документ не выбран")
                return False
            # Получаем документ из БД
            document = session.get(DocumentsORM, document_id)
            if not document:
                QMessageBox.warning(None, "Ошибка", "Документ не найден в базе данных")
                return False
            # Проверяем текущий уровень защиты
            if document.security_level == 2:
                # Обновляем уровень защиты на 1
                stmt = (
                    update(DocumentsORM)
                    .where(DocumentsORM.id == document_id)
                    .values(security_level=1)
                )
                session.execute(stmt)
                session.commit()

                QMessageBox.information(None, "Успех","Документ выдан вьюверу (уровень защиты изменен с 2 на 1)")
                self.show_documents_manager()  # Обновляем таблицу документов
                return True

            elif document.security_level == 1:
                QMessageBox.information(None, "Информация", "Документ уже выдан вьюверу (уровень защиты 1)")
                return False
            else:
                QMessageBox.warning(None,"Ошибка","Нельзя выдать документ с уровнем защиты 3 вьюверу")
                return False
        except Exception as e:
            session.rollback()
            QMessageBox.critical(None,"Ошибка",f"Не удалось выдать документ вьюверу:\n{str(e)}")
            return False

    def return_from_viewer(self):
        """
        Менеджер забирает документ у вьювера (устанавливает уровень защиты 2)
        """
        try:
            # Получаем ID выбранного документа
            document_id = self.find_document_in_manager_table()
            if not document_id:
                QMessageBox.warning(None, "Ошибка", "Документ не выбран")
                return False
            # Получаем документ из БД
            document = session.get(DocumentsORM, document_id)
            if not document:
                QMessageBox.warning(None, "Ошибка", "Документ не найден в базе данных")
                return False
            # Проверяем текущий уровень защиты
            if document.security_level == 1:
                # Обновляем уровень защиты на 2
                stmt = (
                    update(DocumentsORM)
                    .where(DocumentsORM.id == document_id)
                    .values(security_level=2)
                )
                session.execute(stmt)
                session.commit()

                QMessageBox.information(
                    None, "Успех", "Документ возвращен (уровень защиты изменен с 1 на 2)")
                self.show_documents_manager()  # Обновляем таблицу документов
                return True

            elif document.security_level == 2:
                QMessageBox.information(None,"Информация","Документ уже имеет уровень защиты 2")
                return False
            else:
                return False

        except Exception as e:
            session.rollback()
            QMessageBox.critical(None,"Ошибка",f"Не удалось вернуть документ:\n{str(e)}")
            return False

    def admin_open_file(self):
        file = session.get(DocumentsORM,self.find_document_in_admin_table())
        file_path = file.file_path
        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def manager_open_file(self):
        file = session.get(DocumentsORM, self.find_document_in_manager_table())
        file_path = file.file_path
        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def viewer_open_file(self):
        document_id = self.find_document_in_viewer_table()
        if self.DocsViewer.load_document(document_id):
            self.DocsViewer.show()
        else:
            QMessageBox.warning(None, "Ошибка", "Не удалось загрузить документ")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AutorizationWindow()
    w.show()
    c = Control(w)
    sys.exit(app.exec_())