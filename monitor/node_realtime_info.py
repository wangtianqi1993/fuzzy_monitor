# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'wtq'

import os
import time
import logging
from util.transtime import transtime
from util.logger import MonitorDetectorLogger

log = MonitorDetectorLogger()


def node_realtime_info():
    """
    :return:
    """
    try:
        client_sys_info = {}
        fdfs_mon = os.popen("/usr/bin/fdfs_monitor /etc/fdfs/client.conf").read()
        fdfs_mon_tmp = fdfs_mon.split("Group")
    except Exception, e:
        log.info("error in execute node_realtime_info")
        fdfs_mon_tmp = "a"
    # for中的每个元素都是一个Group信息
    for j in range(1, len(fdfs_mon_tmp)):

        storage_split = fdfs_mon_tmp[j].split("Storage")
        group_info = storage_split[0]
        group_info = group_info.split("\n")
        group_name = group_info[1].split(" ")[-1]

        client_sys_info["data"] = []

        # for中的每一个元素为一个Storage信息
        for i in range(1, len(storage_split)):
            node_dict = {}

            node_name = "Storage" + str(i)
            storage_info = storage_split[i].split("\n")
            storage_ip = storage_info[1].split(" ")[-1]
            status = storage_info[2].split(" ")[-1]

            node_dict["status"] = status
            node_dict["node_name"] = node_name
            node_dict["node_ip"] = storage_ip

            join_time = storage_info[5].split("= ")[1]
            node_dict["join_time"] = join_time

            current_time_stump = time.time()
            join_time_stump = transtime(join_time)
            duraing_time_minute = (current_time_stump - join_time_stump) / 60
            node_dict["online_time"] = duraing_time_minute
            free_storage = storage_info[8].split(" ")[-2]
            total_storage = storage_info[7].split(" ")[-2]
            print free_storage
            node_dict["disk_free_space"] = free_storage
            node_dict["disk_all_space"] = total_storage

            client_sys_info["data"].append(node_dict)

    client_sys_info["status"] = 100
    client_sys_info["message"] = ""

    return client_sys_info
    # except Exception, e:
    #     print 'get fastdfs info error', e

if __name__ == "__main__":
    node_realtime_info()

