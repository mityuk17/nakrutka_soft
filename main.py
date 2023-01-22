import time
import json
import telethon

import aiohttp
from python_socks.async_.asyncio import Proxy
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
import telethon.errors.rpcerrorlist
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from opentele.api import API, CreateNewSession, UseCurrentSession
import asyncio
import socks
import os
import threading
import random
day_limit = int(input('Введите суточный лимит на подписки с одного аккаунта:'))
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
        data[i] = {"proxy_type":'http','addr':data[i][0], 'port':int(data[i][1]),'username': data[i][2],'password': data[i][3]}
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
        accs.append([proxies[counter],sess[i]])
        counter += 1
        if counter >= len(proxies) - 1:
            counter = 0
    return accs


sessions = raspred_proxies()
for i in range(len(targets)):
    random_sessions = sessions.copy()
    random.shuffle(random_sessions)
    targets[i] = [targets[i][0], targets[i][1], random_sessions]
num_threads = min(len(targets),int(input('Введите количество потоков:')))

def raspred_targets_by_threads():
    threads_data = list()
    for i in range(num_threads):
        threads_data.append([])
    while targets:
        for i in range(len(threads_data)):
            if not(targets):
                break
            threads_data[i].append(targets.pop())
    return threads_data
def get_threads():
    threads = []
    threads_data = raspred_targets_by_threads()
    for i in range(num_threads):
        threads.append(threading.Thread(target=start_main, args=[threads_data[i]]))
    for i in threads:
        i.start()
def start_main(targets):
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(targets))
    #asyncio.run(main(targets))
async def main(targets):
    while targets:
        for i in range(len(targets)):
            if not targets:
                break
            try:
                if targets[i][1] <= 0:
                    targets.remove(targets[i])
                    continue
            except IndexError:
                continue
            if not targets[i][2]:
                print(f'Нет доступных аккаунтов для подписки на {targets[i][0]}')
                targets.remove(targets[i])
                continue
            #await asyncio.sleep(10)
            session = targets[i][2].pop()

            tdataFolder = fr"sessions/{session[1]}/tdata"
            if not os.path.exists(tdataFolder):
                continue
            tdesk = TDesktop(tdataFolder)
            api = API.TelegramDesktop.Generate(session[1])
            print(f'Попытка подключиться к {session[1]}')
            try:
                server = 'proxy.mtproto.co'  # Прокси с сайта mtproto.co
                port = 443  # Можете  оставить эти (Если будут акетуальные)
                secret = 'dd11112222333344445555666677778888'  # Пароль от прокси


                connection = telethon.connection.ConnectionTcpMTProxyRandomizedIntermediate
                proxy = (socks.HTTP, session[0]['addr'],session[0]['port'], session[0]['username'], session[0]['password'])
                print(proxy)
                client = await tdesk.ToTelethon(f"session_files/{session[1]}.session" , UseCurrentSession, api, connection=connection, proxy=(server,port,secret))
            except Exception as e:
                print(e)
                print(f'Некорректная tdata {session[1]}')
                continue
            if client.is_connected():
                targets[i][2] = [session] + targets[i][2]
                print(f'Сессия {session[1]} уже активна.')
                continue
            with open("sessions_limits.json", 'r', encoding='utf8') as file:
                data = json.load(file)
            if data.get(session[1]):
                limits = data.get(session[1])
            else:
                limits = []
                with open('sessions_limits.json', 'w', encoding='utf8') as file:
                    data[session[1]] = limits
                    json.dump(data, file)
            if len(limits) >= day_limit:
                for q in limits:
                    if time.time() - q >= 24 * 60 * 60:
                        limits.remove(q)
                        with open('sessions_limits.json', 'w', encoding='utf8') as file:
                            data[session[1]] = limits
                            json.dump(data, file)
                if len(limits) >= day_limit:
                    print(f'Для сессии {session[1]} исчерпан суточный лимит подписок')
                    targets[i][2] = [session] + targets[i][2]
                    continue
            try:
                await client.connect()
                print( await client.GetCurrentSession())
            except OSError:
                print(f'Не удалось подключиться к сессии {session[1]}')
                continue
            if not(await client.get_me()):
                os.replace(fr'sessions/{session[1]}', fr'banned_sessions/{session[1]}')
            print(f'Подключена сессия {session[1]} для подписки на {targets[i][0]}')
            # try:
            #     channel = await client.get_entity(targets[ i ][ 0 ])
            # except TypeError:
            #     print(f'Некорректное значение {targets[i][0]}')
            #     continue
            # except ValueError:
            #     print(f'Не найден канал по ссылке {targets[i][0]}')
            #     continue
            # flag = False
            # for chat in (await client(telethon.functions.messages.GetAllChatsRequest(except_ids=[]))).chats:
            #     if channel.title == chat.title:
            #         flag = True
            # if flag:
            #     try:
            #         print(f'{session[ 1 ]} уже подписан на {targets[ i ][ 0 ]}')
            #         await client.disconnect()
            #         continue
            #     except OSError:
            #         print(f'Ошибка при отключении от сессии {session[1]}')
            #         continue
            print(f'Попытка сессии {session[1]} подписаться на {targets[i][0]}')
            try:
                #
                await client(JoinChannelRequest(targets[i][0]))
            except ValueError:
                try:
                    await client(telethon.tl.functions.messages.ImportChatInviteRequest(targets[i][0][1:]))
                except Exception as e:
                    print(e)
                    continue
            except telethon.errors.rpcerrorlist.ChannelsTooMuchError:
                print(f'Превышен лимит на количество каналов для сессии {session[1]}')
                continue
            except telethon.errors.rpcerrorlist.SessionRevokedError:
                print(f'Проблемы с авторизацией для сессии {session[1]}')
                continue
            except telethon.errors.rpcerrorlist.ChannelInvalidError:
                print(f'Некорректный объект типа \"Канал\"')
                continue
            except telethon.errors.rpcerrorlist.ChannelPrivateError:
                print(f'Канал имеет тип \"Приватный\", невозможно к нему присоединиться')
                continue
            except telethon.errors.rpcerrorlist.UserDeactivatedBanError:
                print(f'Сессия {session[1]} забанена')
                if os.path.exists(fr'sessions/{session[1]}'):
                    os.replace(fr'sessions/{session[ 1 ]}' , fr'banned_sessions/{session[ 1 ]}')
                continue
            with open('sessions_limits.json', 'r', encoding='utf8') as file:
                data = json.load(file)
                data[session[1]].append(time.time())
            with open('sessions_limits.json', 'w', encoding='utf8') as file:
                json.dump(data,file)
            print(f'Сессия{session[1]} подписалась на {targets[i][0]}')
            targets[i][1] -= 1
            await client.disconnect()

get_threads()