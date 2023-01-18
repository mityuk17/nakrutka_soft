from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, CreateNewSession, UseCurrentSession
import asyncio
import os
def get_sessions():
    if not os.path.exists('sessions'):
        return False
    with os.scandir('sessions') as files:
        subdir = [file.name for file in files if file.is_dir() and os.path.exists(f'sessions/{file.name}/tdata')]
    print('Собрано сессий:', len(subdir))
    return subdir
def get_proxies():
    with open('proxies.txt', 'r') as file:
        data = file.readlines()
    for i in range(len(data)):
        data[i] = data[i].strip().replace('::', ':').split(':')
        data[i] = {'http': f'http://{data[i][2]}:{data[i][3]}@{data[i][0]}:{data[i][1]}/'}
    return data
def get_targets():
    with open('targets.txt', 'r') as file:
        data = file.readlines()
        for i in range(len(data)):
            data[i] = data[i].strip()
    return data
sessions = get_sessions()
print(sessions)
targets = get_targets()
proxies = get_proxies()
def raspred_proxies():
    accs = list()
    counter = 0
    for i in range(len(sessions)):
        accs.append([proxies[counter],sessions[i]])
        counter += 1
        if counter == len(proxies) - 1:
            counter = 0
    return accs
