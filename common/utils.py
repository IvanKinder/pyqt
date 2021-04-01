from common.variables import *
# from errors import IncorrectDataRecivedError, NonDictInputError
import json
import sys
sys.path.append('../')
from decos import log


# Утилита приёма и декодирования сообщения
# принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
@log
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            # raise IncorrectDataRecivedError
            raise ERROR
    else:
        # raise IncorrectDataRecivedError
        raise ERROR


# Утилита кодирования и отправки сообщения
# принимает словарь и отправляет его
@log
def send_message_util(sock, message):
    if not isinstance(message, dict):
        # raise NonDictInputError
        raise ERROR
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
