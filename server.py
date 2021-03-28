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
from server_database import ServerStorage

logger = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    listen_port = PortVerifier()

    def __init__(self, database):
        self.listen_port = self.arg_parser()[1]
        self.database = database

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
                        for key, value in names.items():
                            if value == client_with_message:
                                self.database.user_logout(key)
                                names[key] = None
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            for i in messages:
                try:
                    self.process_message(i, names, send_data_lst)
                except:
                    for key, value in names.items():
                        if value == i[DESTINATION]:
                            self.database.user_logout(key)
                    logger.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()

    @log
    def process_message(self, message, names, listen_socks):
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            send_message(names[message[DESTINATION]], message)
            self.database.process_message(message[SENDER], message[DESTINATION])
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    @log
    def process_client_message(self, message, messages_list, client, clients, names):
        logger.debug(f'Разбор сообщения от клиента : {message}')
        print(message)
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            client_to_db = (message['user']['account_name'], client.getsockname()[0], client.getsockname()[1],)
            if message[USER][ACCOUNT_NAME] not in names.keys() or names[message[USER][ACCOUNT_NAME]] is None:
                self.database.user_login(client_to_db[0], client_to_db[1], client_to_db[2])
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
        elif ACTION in message and message[ACTION] == MESSAGE_HISTORY:
            hist = self.database.message_history()
            for h in hist:
                if message[ACCOUNT_NAME] in h:
                    print(h)
                    text = f'Отправленных сообщений: {h[2]}; полученных сообщений: {h[3]}'
                    out = {
                        ACTION: GET_CONTACTS,
                        MESSAGE_TEXT: text,
                        RESPONSE: RESPONSE_201
                    }
                    send_message(client, out)
            return
        elif ACTION in message and message[ACTION] == GET_CONTACTS and ACCOUNT_NAME in message:
            contacts_list = self.database.get_contacts(message[ACCOUNT_NAME])
            out = {
                ACTION: GET_CONTACTS,
                MESSAGE_TEXT: f'\n{contacts_list}',
                RESPONSE: RESPONSE_202
            }
            send_message(client, out)
            return
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message:
            tmp_list = []
            for u in self.database.users_list():
                tmp_list.append(u[0])
            if message[CONTACT] in self.database.get_contacts(message[ACCOUNT_NAME]):
                msg_text = 'Контакт уже в списке'
            elif message[CONTACT] not in tmp_list:
                msg_text = 'Такого пользователя не существует'
            else:
                msg_text = 'Контакт добавлен'
                self.database.add_contact(message[ACCOUNT_NAME], message[CONTACT])
            out = {
                ACTION: ADD_CONTACT,
                RESPONSE: RESPONSE_200,
                MESSAGE_TEXT: msg_text
            }
            send_message(client, out)
            return
        elif ACTION in message and message[ACTION] == DEL_CONTACT and ACCOUNT_NAME in message:
            if message[CONTACT] in self.database.get_contacts(message[ACCOUNT_NAME]):
                msg_text = 'Контакт удален'
                self.database.remove_contact(message[ACCOUNT_NAME], message[CONTACT])
            else:
                msg_text = 'Нет такого контакта'
            out = {
                ACTION: DEL_CONTACT,
                RESPONSE: RESPONSE_201,
                MESSAGE_TEXT: msg_text
            }
            send_message(client, out)
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
        try:
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
        except:
            pass

try:
    database = ServerStorage()
    server = Server(database)
    server.main()
except:
    pass
