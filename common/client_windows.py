import logging
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QDialog, QLabel, QLineEdit

from common.client_ui import Ui_MainClientWindow

logger = logging.getLogger('client')


class StartWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Log in')
        self.setGeometry(700, 430, 285, 85)
        self.label = QLabel('Введите имя пользователя:', self)
        self.label.setGeometry(70, 2, 200, 20)
        self.client_name = QLineEdit(self)
        self.client_name.setGeometry(60, 30, 167, 28)


        self.show()



class ClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)
        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)

        self.show()

    # def add_contact_window(self):
    #     global select_dialog
    #     select_dialog = AddContactDialog(self.transport, self.database)
    #     select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
    #     select_dialog.show()


if __name__ == '__main__':
    # client_app = QApplication(sys.argv)
    # main_window = ClientMainWindow()
    # main_window.setWindowTitle(f'Чат')
    # client_app.exec_()
    app = QApplication([])
    dial = StartWindow()
    app.exec_()
