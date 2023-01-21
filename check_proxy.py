import requests
import socks
proxy = {"proxy_type":'http','addr':'193.203.105.83', 'port':'24588','username': 'YOh61zxq05','password': 'uafCtOrg2L'}
#proxies = {'http':"http://YOh61zxq05:uafCtOrg2L@193.203.105.83:24588"}
print(requests.get('http://kwork.ru', proxies=proxy))