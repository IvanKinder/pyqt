import sys

from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QMessageBox, qApp, QLabel, QTableView
from PyQt5.uic import loadUi


class ClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('common/client.ui', self)


def main():
    app = QApplication(sys.argv)
    ex = ClientMainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
