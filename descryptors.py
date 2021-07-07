import logging
import sys

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


class Port:
    def __set__(self, instance, value: int):
        if not 1024 <= value < 65536:
            raise ValueError('Номер порта должен быть в пределах от 1024 до 65535')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name