# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wtq'

import ast
import json
import redis
from config.config import MONITOR_PEROID
from config.config import REDIS_HOST, REDIS_PORT
from config.config import SYSTEM_MACHINE_NAME, REDIS_SYSTEM_KEY
from util.redis_queue import RedisQueue
from monitor.node_continuous_info import node_continuous_info

r = redis.Redis(REDIS_HOST, REDIS_PORT)
redis_sys = RedisQueue(REDIS_SYSTEM_KEY)


def get_sys_average_load():
    machine_names = SYSTEM_MACHINE_NAME
    time_stamp = []

    client_link_times = [0] * MONITOR_PEROID
    is_calculate = 0

    # 根据主机名字到redis中取值
    for node_name in machine_names:

        continuous_info = r.lindex(node_name, 0)
        continuous_dict = ast.literal_eval(continuous_info)
        print node_name, continuous_dict

        # 获取时间
        if not is_calculate:
            for key in sorted(continuous_dict["cpu_use_rate"].keys()):
                time_stamp.append(key)
            is_calculate = 1

        # 不同机器的相应统计值相累加
        index = 0
        for key in sorted(continuous_dict["cpu_use_rate"].keys()):
            client_link_times[index] += float(continuous_dict["client_link_times"][key])
            index += 1

    sys_average_load = {}
    sys_average_load["client_link_counts"] = {}

    for index in range(len(time_stamp)):
        sys_average_load["client_link_counts"][time_stamp[index]] = client_link_times[index]

    return_data = {}
    return_data["data"] = sys_average_load
    return_data["status"] = 100
    return_data["message"] = ""
    print return_data

    return return_data

if __name__ == "__main__":
    get_sys_average_load()
