import requests
from fake_useragent import UserAgent

from src.config import Cookie

# 随机UserAgent池
ua = UserAgent()


# 代理IP池
def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


# 代理IP池
def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


# 车站名和电报码
def get_station_telecode():
    url = f"https://www.12306.cn/index/script/core/common/station_name_new.js"
    headers = {
        'Referer': 'https://www.12306.cn/index/index.html',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.get(url, headers=headers, proxies={"http": f"http://{proxy}"}).text
    delete_proxy(proxy)
    return response


# 查询余票（含票价）
def get_remain_ticket(from_station_code, to_station_code, train_date):
    url = f"https://kyfw.12306.cn/otn/leftTicket/queryE"
    params = {
        'leftTicketDTO.train_date': train_date,
        'leftTicketDTO.from_station': from_station_code,
        'leftTicketDTO.to_station': to_station_code,
        'purpose_codes': 'ADULT'
    }
    headers = {
        'Cookie': Cookie,
        'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.get(url, params=params, headers=headers, proxies={"http": f"http://{proxy}"})
    delete_proxy(proxy)
    return response


# 查询票价
def get_ticket_price(from_station_code, to_station_code, train_date):
    url = f"https://kyfw.12306.cn/otn/leftTicketPrice/queryAllPublicPrice"
    params = {
        'leftTicketDTO.train_date': train_date,
        'leftTicketDTO.from_station': from_station_code,
        'leftTicketDTO.to_station': to_station_code,
        'purpose_codes': 'ADULT'
    }
    headers = {
        'Referer': 'https://kyfw.12306.cn/otn/leftTicketPrice/initPublicPrice',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.get(url, params=params, headers=headers, proxies={"http": f"http://{proxy}"})
    delete_proxy(proxy)
    return response


# 经过该车站的车次（全部）
def get_station_train(train_station_code):
    url = f"https://kyfw.12306.cn/otn/zwdch/queryCC"
    data = {
        "train_station_code": train_station_code
    }
    headers = {
        'Referer': 'https://kyfw.12306.cn/otn/zwdch/init',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.post(url, data=data, headers=headers, proxies={"http": f"http://{proxy}"})
    delete_proxy(proxy)
    return response


# 搜索车次编号（最多返回200条）
def get_train_no(keyword, date):
    url = f"https://search.12306.cn/search/v1/train/search"
    params = {
        'keyword': keyword,
        'date': date
    }
    headers = {
        'Referer': 'https://kyfw.12306.cn/',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.get(url, params=params, headers=headers, proxies={"http": f"http://{proxy}"})
    delete_proxy(proxy)
    return response


# 时刻表
def get_train_time(train_no, train_date):
    url = f"https://kyfw.12306.cn/otn/queryTrainInfo/query"
    params = {
        'leftTicketDTO.train_no': train_no,
        'leftTicketDTO.train_date': train_date,
        'rand_code': '',
    }
    headers = {
        'Referer': 'https://kyfw.12306.cn/otn/queryTrainInfo/init',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.get(url, params=params, headers=headers, proxies={"http": f"http://{proxy}"})
    delete_proxy(proxy)
    return response


# 查询途径站
def get_passing_station(train_no, from_station_telecode, to_station_telecode, train_date):
    url = f"https://kyfw.12306.cn/otn/czxx/queryByTrainNo"
    params = {
        'train_no': train_no,
        'from_station_telecode': from_station_telecode,
        'to_station_telecode': to_station_telecode,
        'depart_date': train_date
    }
    headers = {
        'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
        'User-Agent': ua.random
    }
    proxy = get_proxy().get("proxy")
    response = requests.get(url, params=params, headers=headers, proxies={"http": f"http://{proxy}"})
    delete_proxy(proxy)
    return response
