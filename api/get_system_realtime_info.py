# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wtq'

import ast
import json
import redis
from config.config import REDIS_HOST, REDIS_PORT, REDIS_SYSTEM_KEY
from config.config import DISK_ALL_SPACE, MEM_ALL_SPACE, CPU_KERNEL_NUMS
from config.config import SYSTEM_MACHINE_NAME

r = redis.Redis(REDIS_HOST, REDIS_PORT)


def get_system_realtime_info():
    # 根据主机名字到redis中取值
    system_info = r.lindex(REDIS_SYSTEM_KEY, 0)
    system_realtime_info = {}
    system_realtime_info["disk_all_space"] = DISK_ALL_SPACE
    system_realtime_info["cpu_kernal_nums"] = CPU_KERNEL_NUMS
    system_realtime_info["mem_all_space"] = MEM_ALL_SPACE
    system_realtime_info["disk_use_rate"] = 0
    system_realtime_info["mem_use_rate"] = 0
    system_realtime_info["cpu_use_rate"] = 0

    machine_nums = len(SYSTEM_MACHINE_NAME)
    machine_names = SYSTEM_MACHINE_NAME

    for node_name in machine_names:
        continuous_info = r.lindex(node_name, 0)
        continuous_dict = ast.literal_eval(continuous_info)

        for key in sorted(continuous_dict["cpu_use_rate"].keys(), reverse=True):
            system_realtime_info["cpu_use_rate"] += float(continuous_dict["cpu_use_rate"][key]) / machine_nums
            system_realtime_info["mem_use_rate"] += float(continuous_dict["mem_use_rate"][key]) / machine_nums
            system_realtime_info["disk_use_rate"] += float(continuous_dict["disk_use_rate"][key]) / machine_nums
            break

    return_data = {}
    return_data["data"] = system_realtime_info
    return_data["status"] = 100
    return_data["message"] = ""
    print return_data

    return return_data

if __name__ == "__main__":
    get_system_realtime_info()
