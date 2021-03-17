from socket import socket, AF_INET, SOCK_STREAM
import sys
import argparse
import json
import logging
import select
import time
import logs.config_server_log
from common.variables import *
from common.utils import *
from decos import log
from descriptors import PortVerifier
from metaclasses import ServerVerifier

logger = logging.getLogger('server')


class Server(metaclass=ServerVerifier):

    listen_port = PortVerifier()

    def __init__(self):
        self.listen_port = self.arg_parser()[1]

    def main(self):
        listen_address = self.arg_parser()[0]
        logger.info(
            f'Запущен сервер, порт для подключений: {self.listen_port} , адрес с которого принимаются подключения: {listen_address}. Если адрес не указан, принимаются соединения с любых адресов.')
        transport = socket(AF_INET, SOCK_STREAM)
        transport.bind((listen_address, self.listen_port))
        transport.settimeout(0.5)

        clients = []
        messages = []

        names = dict()

        transport.listen(MAX_CONNECTIONS)
        while True:
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), messages, client_with_message, clients,
                                               names)
                    except:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            for i in messages:
                try:
                    self.process_message(i, names, send_data_lst)
                except:
                    logger.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()

    @log
    def process_message(self, message, names, listen_socks):
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            send_message(names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    @log
    def process_client_message(self, message, messages_list, client, clients, names):
        logger.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            clients.remove(names[ACCOUNT_NAME])
            names[ACCOUNT_NAME].close()
            del names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return

    @staticmethod
    @log
    def arg_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p

        if not 1023 < listen_port < 65536:
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {listen_port}. Допустимы адреса с 1024 до 65535.')
            exit(1)

        return listen_address, listen_port


if __name__ == '__main__':
    server = Server()
    server.main()
