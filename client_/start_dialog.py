from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp
from PyQt5.QtCore import QEvent


class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Log in')
        self.setGeometry(700, 430, 187, 150)

        self.label = QLabel('Введите имя пользователя:', self)
        self.label.setGeometry(20, 2, 200, 20)

        self.client_name = QLineEdit(self)
        self.client_name.setGeometry(10, 25, 167, 25)

        self.label_pas = QLabel('Введите пароль:', self)
        self.label_pas.setGeometry(45, 57, 200, 20)

        self.client_pas = QLineEdit(self)
        self.client_pas.setEchoMode(QLineEdit.Password)
        self.client_pas.setGeometry(10, 77, 167, 25)

        self.btn_ok = QPushButton('Войти', self)
        self.btn_ok.setGeometry(9, 115, 60, 25)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.setGeometry(118, 115, 60, 25)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.show()

    def click(self):
        if self.client_name.text() and self.client_pas.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
