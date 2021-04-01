import logging
import sys
from socket import socket, AF_INET, SOCK_STREAM

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from server_database import ServerStorage
from common.variables import *
import time
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QDialog, QLabel, QLineEdit, QPushButton, QMessageBox
from common.client_ui import Ui_MainClientWindow
from common.utils import send_message_util

logger = logging.getLogger('client')


class StartWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Log in')
        self.setGeometry(700, 430, 285, 95)

        self.label = QLabel('Введите имя пользователя:', self)
        self.label.setGeometry(70, 2, 200, 20)

        self.client_name = QLineEdit(self)
        self.client_name.setGeometry(60, 30, 167, 28)

        self.btn_ok = QPushButton('Войти', self)
        self.btn_ok.setGeometry(59, 65, 60, 25)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.setGeometry(168, 65, 60, 25)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.show()

    def click(self):
        if self.client_name.text():
            qApp.exit()


class ClientMainWindow(QMainWindow):
    def __init__(self, sock, client_name, database):
        super().__init__()
        self.sock = sock
        self.client_name = client_name
        self.database = database

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)
        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.btn_send.clicked.connect(self.send_message_from_ui)

        self.show()

    def add_contact_window(self):
        global select_dialog
        select_dialog = self.possible_contacts_update()
        select_dialog.show()

    def send_message_from_ui(self):
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()

        # def create_message(self, sock, account_name='Guest'):
        to = 'u'
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.client_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message_text
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message_util(sock, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {to}')
        except:
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    @pyqtSlot(str)
    def get_message_ui(self, sender):
        if sender == self.current_chat:
            self.history_list_update()
        else:
            if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}, открыть чат с ним?', QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    # self.current_chat = sender
                    # self.set_active_user()
                print('===============')

    def possible_contacts_update(self):
        contacts_list = set(self.database.get_contacts())
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        # self.ui.list_contacts.setModel(self.contacts_model)
        # users_list = set(self.database.get_users())
        # users_list.remove(self.transport.username)
        # self.selector.addItems(users_list - contacts_list)


if __name__ == '__main__':
    server_address = '127.0.0.1'
    server_port = 7777
    database = ServerStorage()
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_address, server_port))
    start_app = QApplication([])
    start_window = StartWindow()
    start_app.exec_()
    client_name = start_window.client_name.text()
    del start_app
    client_app = QApplication(sys.argv)
    main_window = ClientMainWindow(sock, client_name, database)
    main_window.setWindowTitle(f'Чат - {client_name}')
    client_app.exec_()
