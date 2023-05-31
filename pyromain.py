import time
import json
import telethon
from pyrogram import Client
import telethon.errors.rpcerrorlist
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from opentele.api import API , CreateNewSession , UseCurrentSession
from TGConvertor.manager.manager import SessionManager
from pathlib import Path
import asyncio
import socks
import os
import threading
import random
check = False
threads = list
lock = threading.Lock()
day_limit = int(input('Введите суточный лимит на подписки с одного аккаунта:'))


def get_sessions():
    if not os.path.exists('sessions'):
        return False
    with os.scandir('sessions') as files:
        subdir = [ file.name for file in files if file.is_dir() and os.path.exists(f'sessions/{file.name}/tdata') ]
    print('Собрано сессий:' , len(subdir))
    return subdir


def get_proxies():
    with open('proxies.txt' , 'r') as file:
        data = file.readlines()
    for i in range(len(data)):
        data[ i ] = data[ i ].strip().split(':')
        data[ i ] = {"proxy_type": 'socks5' , 'addr': data[ i ][ 0 ] , 'port': int(data[ i ][ 1 ]) ,
                     'username': data[ i ][ 2 ] , 'password': data[ i ][ 3 ]}
    return data


def get_targets():
    with open('targets.txt' , 'r') as file:
        data = file.readlines()
        for i in range(len(data)):
            data[ i ] = data[ i ].split()
            if data[ i ][ 0 ].startswith('https://'):
                data[ i ][ 0 ] = data[ i ][ 0 ][ 8: ]
            if data[ i ][ 0 ].startswith('t.me/'):
                data[ i ][ 0 ] = data[ i ][ 0 ][ 5: ]
            data[ i ][ 1 ] = int(data[ i ][ 1 ])

    return data


targets = get_targets()
proxies = get_proxies()
sess = get_sessions()


def raspred_proxies():
    accs = list()
    counter = 0
    for i in range(len(sess)):
        accs.append([ proxies[ counter ] , sess[ i ] ])
        counter += 1
        if counter >= len(proxies) - 1:
            counter = 0
    return accs


sessions = raspred_proxies()
for i in range(len(targets)):
    random_sessions = sessions.copy()
    random.shuffle(random_sessions)
    targets[ i ] = [ targets[ i ][ 0 ] , targets[ i ][ 1 ] , random_sessions ]
num_threads = min(len(targets) , int(input('Введите количество потоков:')))


def raspred_targets_by_threads():
    threads_data = list()
    for i in range(num_threads):
        threads_data.append([ ])
    while len(targets) > 1:
        for i in range(len(threads_data)):
            if not (targets):
                break
            if len(targets) == 1:
                threads_data[ i ].append(targets[ 0 ])
                break
            threads_data[ i ].append(targets.pop())
    return threads_data


def get_threads():
    global threads, check
    threads = [ ]
    threads_data = raspred_targets_by_threads()
    for i in range(num_threads):
        threads.append(threading.Thread(target=start_main , args=[ threads_data[ i ] ]))
    for i in threads:
        i.start()
    check = True


def start_main(targets):
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(targets))
    # asyncio.run(main(targets))


async def main(targets):
    while targets:
        for i in range(len(targets)):
            if not targets:
                break
            try:
                if targets[ i ][ 1 ] <= 0:
                    targets.remove(targets[ i ])
                    continue
            except IndexError:
                continue
            if not targets[ i ][ 2 ]:
                print(f'Нет доступных аккаунтов для подписки на {targets[ i ][ 0 ]}')
                targets.remove(targets[ i ])
                continue
            session = targets[ i ][ 2 ].pop()
            try:
                api = API.TelegramDesktop.Generate(session[ 1 ])
            except ZeroDivisionError:
                api = API.TelegramDesktop.Generate()
            print(f'Попытка подключиться к {session[ 1 ]}')
            try:
                # proxy = (socks.HTTP, session[0]['addr'],session[0]['port'], session[0]['username'], session[0]['password'])
                proxy = {
                    'scheme': 'socks5' ,
                    'hostname': session[ 0 ][ 'addr' ] ,
                    'port': session[ 0 ][ 'port' ] ,
                    'username': session[ 0 ][ 'username' ] ,
                    'password': session[ 0 ][ 'password' ]
                }
                sess = SessionManager.from_tdata_folder(Path(fr"sessions/{session[ 1 ]}/tdata"))
                sess.api = api
                client = sess.pyrogram_client(proxy=proxy)

            except Exception as e:
                print(e)
                print(f'Некорректная tdata {session[ 1 ]}')
                continue
            if client.is_connected:
                targets[ i ][ 2 ] = [ session ] + targets[ i ][ 2 ]
                print(f'Сессия {session[ 1 ]} уже активна.')
                continue
            try:
                with lock:
                    with open("sessions_limits.json" , 'r' , encoding='utf8') as file:
                        data = json.load(file)
                if data.get(session[ 1 ]):
                    limits = data.get(session[ 1 ])
                else:
                    limits = [ ]
                    data[ session[ 1 ] ] = limits
                    with lock:
                        with open('sessions_limits.json' , 'w' , encoding='utf8') as file:
                            json.dump(data , file)
            except Exception as e:
                print('Ошибка при работе с json файлом.')
                print(e)
                limits = [ ]
            if len(limits) >= day_limit:
                for q in limits:
                    if time.time() - q >= 24 * 60 * 60:
                        limits.remove(q)
                        data[ session[ 1 ] ] = limits
                        with lock:
                            with open('sessions_limits.json' , 'w' , encoding='utf8') as file:
                                json.dump(data , file)
                if len(limits) >= day_limit:
                    print(f'Для сессии {session[ 1 ]} исчерпан суточный лимит подписок')
                    targets[ i ][ 2 ] = [ session ] + targets[ i ][ 2 ]
                    continue
            try:
                await client.start()
            except ConnectionError:
                print(f'Не удалось подключиться к сессии {session[ 1 ]}')
                continue
            except TypeError:
                print(f'Не удалось подключиться к сессии {session[ 1 ]}')
                continue
            if not (await client.get_me()):
                os.replace(fr'sessions/{session[ 1 ]}' , fr'banned_sessions/{session[ 1 ]}')
            print(f'Подключена сессия {session[ 1 ]} для подписки на {targets[ i ][ 0 ]}')
            print(f'Попытка сессии {session[ 1 ]} подписаться на {targets[ i ][ 0 ]}')
            try:

                await client.join_chat(targets[ i ][ 0 ])
            except ValueError:
                print('Не найден канал {targets[i][0]}')
                continue
            except KeyError:
                print(f'Не найден канал {targets[i][0]}')
                continue
            try:
                with lock:
                    with open('sessions_limits.json' , 'r' , encoding='utf8') as file:
                        data = json.load(file)
                data[ session[ 1 ] ].append(time.time())
                with lock:
                    with open('sessions_limits.json' , 'w' , encoding='utf8') as file:
                        json.dump(data , file)
                print(f'Сессия{session[ 1 ]} подписалась на {targets[ i ][ 0 ]}')
                targets[ i ][ 1 ] -= 1
            except json.JSONDecodeError:
                print("Ошибка при записи в json-файл")
            except Exception as e:
                print('Ошибка при работе с json-файлом')
            await client.stop()
    print(f'Поток {threading.currentThread()} закончил работу')


get_threads()


def check_alive(thread):
    return thread.is_alive()


while True:
    flag = False

    if threads and check:
        for thread in threads:
            if thread.is_alive():
                flag = True
    if not(flag):
        break
print('Закончена работа программы')
