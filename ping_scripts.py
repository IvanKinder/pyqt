import ipaddress
import os
from subprocess import Popen, PIPE


url_list = ['yandex.ru', '2.2.2.2', '192.168.0.1', '192.168.0.100']


def host_ping(ping_list: list, timeout=500, requests=1):
    result = {'Доступные': [], 'Недоступные': []}
    for url in ping_list:
        try:
            url = ipaddress.ip_address(url)
        except ValueError:
            pass
        proc = Popen(f'ping {url} -w {timeout} -n {requests}', shell=False, stdout=PIPE)
        proc.wait()
        if proc.returncode == 0:
            result['Доступные'].append(str(url))
            print(f'{url} - доступен')
        else:
            result['Недоступные'].append(str(url))
            print(f'{url} - недоступен')
    print()


def host_range_ping(url: str, n: int):
    urls = []
    url = ipaddress.ip_address(url)
    for i in range(n):
        urls.append(str(url + i))
    host_ping(urls)


if __name__ == '__main__':
    host_ping(url_list)
    host_range_ping('192.168.0.1', 5)
