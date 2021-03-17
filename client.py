import sys
import json
import socket
import time
import argparse
import logging
import threading
import logs.config_client_log
from common.variables import *
from common.utils import *
import dis


logger = logging.getLogger('client')


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if ('accept' or 'listen') in methods:
            raise TypeError('Использование accept или listen в классе клиента')
        if not ('SOCK_STREAM' or 'AF_INET') in attrs:
            raise TypeError('Некорректная инициализация сокета')


class Client(metaclass=ClientVerifier):

    @log
    def create_exit_message(self, account_name):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @log
    def message_from_server(self, sock, my_username):
        print(f'Вы вошли под именем: {my_username}\n')
        while True:
            try:
                message = get_message(sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except ERROR:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break

    @log
    def create_message(self, sock, account_name='Guest'):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(sock, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {to}')
        except:
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    def print_help(self):
        print('Поддерживаемые команды:')
        print('m - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('h - вывести подсказки по командам')
        print('q - выход из программы')

    @log
    def user_interactive(self, sock, username):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'm':
                self.create_message(sock, username)
            elif command == 'h':
                self.print_help()
            elif command == 'q':
                send_message(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @log
    def create_presence(self, account_name):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @log
    def process_response_ans(self, message):
        logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ERROR(f'400 : {message[ERROR]}')
        raise ERROR(RESPONSE)

    @log
    def arg_parser(self):
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

    def main(self):
        print('Консольный месседжер. Клиентский модуль.')

        server_address, server_port, client_name = self.arg_parser()

        if not client_name:
            client_name = input('Введите имя пользователя: ')

        logger.info(
            f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((server_address, server_port))
            send_message(transport, self.create_presence(client_name))
            answer = self.process_response_ans(get_message(transport))
            logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            logger.error('Не удалось декодировать полученную Json строку.')
            exit(1)
        except ERROR as error:
            logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            exit(1)
        except ERROR as missing_error:
            logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            exit(1)
        except (ConnectionRefusedError, ConnectionError):
            logger.critical(
                f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
            exit(1)
        else:
            receiver = threading.Thread(target=self.message_from_server, args=(transport, client_name))
            receiver.daemon = True
            receiver.start()

            user_interface = threading.Thread(target=self.user_interactive, args=(transport, client_name))
            user_interface.daemon = True
            user_interface.start()
            logger.debug('Запущены процессы')

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    client = Client()
    client.main()
