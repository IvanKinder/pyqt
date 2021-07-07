from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp
from PyQt5.QtCore import QEvent


class UserNameDialog(QDialog):
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
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
