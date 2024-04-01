import random
import time

import api
import utils
from more_buy import get_station_code
from price import get_price_public


def get_train_name():
    # 获取所有车次并去重
    from_station_codes = list(station_info.values())
    index = 0
    length = len(from_station_codes)
    train_set = set()
    while index < length:
        print(index)
        try:
            data = api.get_station_train(from_station_codes[index]).json().get("data")
            train_set.update(data)
            index += 1  # 只有在没有异常的情况下才会更新索引
        except Exception as e:
            print(f"异常: {e}")
            time.sleep(random.random() * 10)
    # 保存结果
    train_list = list(train_set)
    train_list.sort()
    with open('../resource/train_name.txt', 'w') as file:
        for item in train_list:
            file.write(str(item) + '\n')
    print("车次获取完成")


def get_train_time():
    # 1.加载车次名称
    with open('../resource/train_name.txt', 'r') as file:
        lines = file.readlines()
    train_list = [line.strip() for line in lines]

    # 2.遍历车次，获取时刻表，存入数据库
    index = 0
    length = len(train_list)
    print(length)
    while index < length:
        print(index)
        try:
            # 获取车次编号
            response = api.get_train_no(train_list[index], date).json().get("data")
            if len(response) == 0:
                index += 1
                continue
            train_no = response[0].get("train_no")
            # 获取时刻表
            pass_station_list = api.get_train_time(train_no, train_date).json().get("data").get("data")

            for station in pass_station_list:
                sql = """insert into train_time(train_name,train_no,station_name,station_no,arrive_time,start_time,running_time,arrive_day_diff) values (?,?,?,?,?,?,?,?)"""
                params = [
                    train_list[index],
                    train_no,
                    station.get("station_name"),
                    station_info.get(station.get("station_name")),
                    station.get("arrive_time"),
                    station.get("start_time"),
                    station.get("running_time"),
                    station.get("arrive_day_diff")
                ]
                utils.sql_execute(sql, params)
            index += 1  # 只有在没有异常的情况下才会更新索引
            time.sleep(random.random() * 3)
        except Exception as e:
            print(f"异常: {e}")
            time.sleep(random.random() * 100)


def get_train_price():
    # 查询通车的任意两站点构成的所有元组
    values = utils.sql_select_all("""SELECT DISTINCT
                                            a.station_no AS from_station_code,
                                            b.station_no AS to_station_code 
                                        FROM
                                            train_time AS a
                                            INNER JOIN train_time AS b ON a.train_no = b.train_no 
                                            AND a.id < b.id 
                                        WHERE
                                            from_station_code IS NOT NULL 
                                            AND to_station_code IS NOT NULL;""")

    # 开始查询票价
    index = 0
    length = len(values)
    retry = 0
    print(length)
    while index < length:
        if retry == 0:
            print(index)
        else:
            print(f"{index}:第{retry}次重试")

        try:
            from_station_code = values[index][0]
            to_station_code = values[index][1]

            # 调用API
            data = api.get_ticket_price(from_station_code, to_station_code, train_date).json().get("data")
            # 跳过没有直达的两站点
            if len(data) == 0:
                retry += 1
                # 重试3次后依然失败
                if retry > 3:
                    print(f"{reversed_dict.get(from_station_code)}-{reversed_dict.get(to_station_code)} 没有直达车次")
                    index += 1
                    retry = 0
                time.sleep(random.random() * 5)
                continue
            retry = 0  # 成功后，重置retry

            # 遍历两点之间的每个车次
            for temp_dict in data:
                train = temp_dict.get("queryLeftNewDTO")
                # 忽略同城站点，只保留精确搜索结果
                if train.get("from_station_telecode") != from_station_code or train.get("to_station_telecode") != to_station_code:
                    continue
                # 跳过停运车次
                price = [x for x in get_price_public(train.get("infoAll_list")) if x != 0]
                if len(price) == 0:
                    continue

                sql = "insert into train_price values (?,?,?,?,?,?,?)"
                params = [
                    train.get("train_no"),
                    train.get("station_train_code"),
                    train.get("from_station_telecode"),
                    train.get("from_station_name"),
                    train.get("to_station_telecode"),
                    train.get("to_station_name"),
                    min(price)
                ]
                utils.sql_execute(sql, params)
            index += 1  # 只有在没有异常的情况下才会更新索引
            time.sleep(random.random() * 2)
        except Exception as e:
            print(f"异常: {e}")
            time.sleep(random.random() * 50)


def data_process():
    # 数据获取完毕后，进行加工处理
    utils.sql_execute("""CREATE TABLE train_data_processed AS SELECT
                                t1.*,
                                t2.price 
                                FROM
                                    (
                                    SELECT
                                        a.train_name,
                                        a.train_no,
                                        a.station_name AS from_station_name,
                                        a.station_no AS from_station_code,
                                        a.start_time,
                                        b.station_name AS to_station_name,
                                        b.station_no AS to_station_code,
                                        b.arrive_time,
                                        ( b.arrive_day_diff - a.arrive_day_diff ) AS arrive_day_diff 
                                    FROM
                                        train_time AS a
                                        INNER JOIN train_time AS b ON a.train_no = b.train_no 
                                        AND a.id < b.id 
                                    WHERE
                                        from_station_code IS NOT NULL 
                                        AND to_station_code IS NOT NULL 
                                    ) AS t1
                                    INNER JOIN train_price AS t2 ON t1.train_name = t2.train_name 
                                    AND t1.from_station_name = t2.from_station_name 
                                    AND t1.to_station_name = t2.to_station_name;""")


if __name__ == '__main__':
    # 初始化
    date = "20240305"
    train_date = "2024-03-05"
    station_info, reversed_dict = get_station_code()

    get_train_price()
