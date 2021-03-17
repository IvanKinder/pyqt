import dis


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
        if not ('SOCK_STREAM' or 'AF_INET') in methods:
            raise TypeError('Некорректная инициализация сокета')
        for value in dict(clsdict).values():
            if str(type(value)) == "<class 'socket.socket'>":
                raise TypeError('Сокет создается на уровне класса')


class ServerVerifier(type):
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
        if 'connect' in methods:
            raise TypeError('Использование connect в классе сервера')
        if not ('SOCK_STREAM' or 'AF_INET') in methods:
            raise TypeError('Некорректная инициализация сокета')
