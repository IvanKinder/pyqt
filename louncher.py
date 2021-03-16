from subprocess import Popen, CREATE_NEW_CONSOLE


processes = []


while True:
    action = input('Выберите действие: q - выход , s - запустить сервер и клиенты, x - закрыть все окна: ')

    if action == 'q':
        break
    if action == 's':
        processes.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))
        processes.append(Popen('python client.py -n user1', creationflags=CREATE_NEW_CONSOLE))
        processes.append(Popen('python client.py -n user2', creationflags=CREATE_NEW_CONSOLE))
    if action == 'x':
        for proc in processes:
            proc.kill()
        processes = []
