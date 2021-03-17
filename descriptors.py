class PortVerifier:

    def __set__(self, instance, value: int):
        if not 1024 <= value < 65536:
            raise ValueError('Номер порта должен быть неотрицательным')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
