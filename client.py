import logging
import logs.config_client_log
import argparse
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

from client_.database import ClientDatabase
from common.variables import *
# from common.errors import ServerError
from common.decos import log
from client_.transport import ClientTransport
from client_.main_window import ClientMainWindow
from client_.start_dialog import UserNameDialog

logger = logging.getLogger('client_')


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name


if __name__ == '__main__':
    server_address, server_port, client_name = arg_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()

        if start_dialog.ok_pressed and start_dialog.client_name.text() and start_dialog.client_pas.text():
            client_name = start_dialog.client_name.text()
            client_password = start_dialog.client_pas.text()
        else:
            exit(0)

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    database = ClientDatabase(client_name)

    try:
        transport = ClientTransport(server_port, server_address, database, client_name, client_password)
        del start_dialog
    except Exception as err:
        print(str(err))
        message = QMessageBox()
        message.information(start_dialog, 'NOT OK', str(err))
        del start_dialog
        exit(1)
    transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()
