import re
import time

import api
from price import get_price_yp
from utils import send_email


def get_station_code():
    response = api.get_station_telecode()
    # 使用正则表达式提取''内的字符串
    matches = re.findall(r"'(.*?)'", response)
    # 用@分割字符串，然后再用|分割
    segments = [segment.split('|') for segment in matches[0].split('@')]
    # 创建一个字典用于存储
    station_info = {}
    for segment in segments:
        if len(segment) >= 3:  # 确保分段中包含足够的元素
            station_info[segment[1]] = segment[2]
    reversed_dict = {value: key for key, value in station_info.items()}
    return station_info, reversed_dict


def search_init(from_station_code, to_station_code, train_code, train_date):
    response = api.get_remain_ticket(from_station_code, to_station_code, train_date)
    if response.status_code == 200:
        data = response.json()['data']['result']
        for result in data:
            train = result.split("|")
            if train[3] == train_code:
                train_no = train[2]
                from_station_no = train[16]
                to_station_no = train[17]
                return train_no, from_station_no, to_station_no


def get_station(train_no, from_station_telecode, to_station_telecode, start, end, train_date):
    response = api.get_passing_station(train_no, from_station_telecode, to_station_telecode, train_date)
    if response.status_code == 200:
        data = response.json()['data']['data']
        stations = [d['station_name'] for d in data]
        from_station = stations[:start]
        to_station = stations[end - 1:]
        return from_station, to_station


def search(from_station_code, to_station_code, train_code, reversed_dict, seat, train_date):
    response = api.get_remain_ticket(from_station_code, to_station_code, train_date)
    if response.status_code == 200:
        data = response.json()['data']['result']
        for result in data:
            train = result.split("|")
            ticket, price = getTicketAndPrice(train, seat)
            if train[3] == train_code and ticket not in ('', '无', '*'):
                return {
                    'train_date': train_date,
                    'train_code': train_code,
                    'from_station': reversed_dict[from_station_code],
                    'to_station': reversed_dict[to_station_code],
                    'ticket': ticket,
                    'price': price
                }


def getTicketAndPrice(train, seat):
    if seat == "硬座":
        return train[29], get_price_yp(train[39])[8]
    elif seat == "二等座":
        return train[30], get_price_yp(train[39])[2]
    elif seat == "硬卧":
        return train[28], get_price_yp(train[39])[6]
    elif seat == "无座":
        return train[26], get_price_yp(train[39])[9]


def query(from_station, to_station, train_code, station_code, reversed_dict, seat, train_date, result):
    for f in from_station:
        for t in to_station:
            res = search(station_code[f], station_code[t], train_code, reversed_dict, seat, train_date)
            if res:
                result.append(res)
            # print(f, t, res)
            time.sleep(1)


def run(train_date_list, train_code_list, from_station, to_station, seat):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"{now} | 开始查询")

    result = []
    station_code, reversed_dict = get_station_code()
    for train_date in train_date_list:
        for train_code in train_code_list:
            # 查询上车站、下车站的序号，用于下面的截取
            train_no, from_station_no, to_station_no = search_init(station_code[from_station], station_code[to_station], train_code, train_date)
            # 获取途径站，截取两头
            from_station_list, to_station_list = get_station(train_no, station_code[from_station], station_code[to_station], int(from_station_no), int(to_station_no), train_date)
            # 遍历查询多买方案
            query(from_station_list, to_station_list, train_code, station_code, reversed_dict, seat, train_date, result)

    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if len(result) > 0:
        sorted_result = sorted(result, key=lambda x: x['price'])
        send_email('火车票信息', sorted_result)
        print(f"{now} | 邮件发送成功")
    else:
        print(f"{now} | 均没有票")


if __name__ == '__main__':
    train_date_list = ['2024-04-02', '2024-04-03']
    from_station = '北京'
    to_station = '上海'
    seat = '硬座'
    train_code_list = ['T109', '1461']
    # 启动
    run(train_date_list, train_code_list, from_station, to_station, seat)
