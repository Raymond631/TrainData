import itertools
from datetime import datetime, timedelta

import networkx as nx

from src import utils


# 构建图
def build_graph():
    # 创建一个有向图
    G = nx.DiGraph()
    values = utils.sql_select_all("""select from_station_name, to_station_name, min(price) from train_data_processed group by from_station_name, to_station_name""")
    index = 1
    for from_station_name, to_station_name, price in values:
        index += 1
        # 添加节点和边
        G.add_edge(from_station_name, to_station_name, weight=price)
    print(f"边数：{index}")
    return G


# 前k条最短路径
def k_shortest_paths(G, source, target, max_station_num):
    results = []
    try:
        # 加上weight="price"就是把价格作为权重，不加默认权重为1
        for path in nx.shortest_simple_paths(G, source, target):
            if len(path) > max_station_num:
                # 如果中转次数超过限制
                break
            else:
                train_list = [(u, v, G[u][v]['weight']) for u, v in zip(path[:-1], path[1:])]
                results.append({
                    "path": path,
                    "price": sum(train[2] for train in train_list),
                    "time_cost": compute_time_cost(train_list)
                })
    except Exception as e:
        print(f"异常：{e}")
    return results


def compute_time_cost(train_list):
    path_list = []
    for train in train_list:
        from_station_name = train[0]
        to_station_name = train[1]
        price = train[2]
        # 查询相邻两站之间的时间
        values = utils.sql_select_all(f"""SELECT
                                                start_time,
                                                arrive_time,
                                                arrive_day_diff 
                                            FROM
                                                train_data_processed 
                                            WHERE
                                                from_station_name = '{from_station_name}' 
                                                AND to_station_name = '{to_station_name}' 
                                                AND price = {price};""")
        path_list.append(values)

    time_cost = []
    for solution in itertools.product(*path_list):
        # 每趟车的跨天
        day_diff = sum(t[2] for t in solution)
        # 中转跨天
        for index in range(len(solution) - 1):
            if solution[index + 1][0] < solution[index][1]:
                day_diff += 1
        time_second = time_str_compute(solution[-1][0], solution[0][1], day_diff)
        time_cost.append(int(time_second))
    return seconds_to_str(min(time_cost))


def time_str_compute(time_str1, time_str2, day_diff):
    time_obj1 = datetime.strptime(time_str1, '%H:%M')
    time_obj2 = datetime.strptime(time_str2, '%H:%M')
    # 计算时间差
    time_diff = time_obj1 - time_obj2
    # 加上24小时
    new_time_obj = time_diff + timedelta(days=day_diff)
    return new_time_obj.total_seconds()


def seconds_to_str(seconds):
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    return "%02d时%02d分" % (hours, minutes)


if __name__ == '__main__':
    from_station_name = "东安东"
    to_station_name = "温岭"
    max_mid_station_num = 1  # 最多中转次数

    # 搜索遍历
    G = build_graph()
    results = k_shortest_paths(G, from_station_name, to_station_name, max_mid_station_num + 2)

    # 排序输出
    path_num = 100  # 显示前100条结果
    sorted_data = itertools.islice(sorted(results, key=lambda x: x['price']), path_num)
    for i in sorted_data:
        print(i)
