import time

import telethon.errors.rpcerrorlist
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from opentele.api import API, CreateNewSession, UseCurrentSession
import asyncio
import socks
import os
day_limit = 1
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
        data[i] = data[i].strip().split(':')
        data[i] = (socks.HTTP, data[i][0], data[i][1], data[i][2], data[i][3])
    return data
def get_targets():
    with open('targets.txt', 'r') as file:
        data = file.readlines()
        for i in range(len(data)):
            data[i] = data[i].split()
            if data[i][0].startswith('https://'):
                data[i][0] = data[i][0][8:]
            if data[i][0].startswith('t.me/'):
                data[i][0] = data[i][0][5:]
            data[i][1] = int(data[i][1])

    return data


targets = get_targets()
proxies = get_proxies()
sess = get_sessions()
def raspred_proxies():

    accs = list()
    counter = 0
    for i in range(len(sess)):
        accs.append([proxies[counter],sess[i], []])
        counter += 1
        if counter == len(proxies) - 1:
            counter = 0
    return accs


sessions = raspred_proxies()
for i in range(len(targets)):
    targets[i] = [targets[i][0], targets[i][1], sessions]
async def main():
    while targets:
        for i in range(len(targets)):
            if targets[i][1] <= 0:
                targets.remove(targets[i])
                continue
            if not targets[i][2]:
                print(f'Нет доступных аккаунтов для подписки на {targets[i][2]}')
                targets.remove(targets[i])
                continue
            session = targets[i][2].pop()
            if len(session[2]) >= 10:
                for q in session[2]:
                    if time.time() - q >= 24 * 60 * 60:
                        session[2].remove(q)
                if len(session[2]) >= 10:
                    continue
            tdataFolder = fr"sessions/{session[1]}/tdata"
            tdesk = TDesktop(tdataFolder)
            api = API.TelegramIOS.Generate()
            client = await tdesk.ToTelethon("newSession.session" , UseCurrentSession , api, proxy=session[0])
            await client.connect()
            channel = await client.get_entity(targets[i][0])
            await client(JoinChannelRequest(channel))
            targets[i][1] -= 1
            await client.disconnect()


asyncio.run(main())