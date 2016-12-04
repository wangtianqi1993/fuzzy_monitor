# /usr/bin/env python
# -*-coding: utf-8 -*-
__author__ = 'wtq'

import os
import time
import json
import subprocess
from config.config import MONITOR_INTERVAL
from config.config import MONITOR_PEROID
from config.config import NET_NAME
from util.redis_queue import RedisQueue

redis_queue = RedisQueue("stroage1")
# 可以再建其他节点名字的消息队列


def node_continuous_info(net_name):
    """
    user、system使用率相加,综合衡量cpu使用率
    MEM使用量(MB)
    MEM總量(MB)
    指定网卡每秒的平均接收流量 (B/S)
    指定网卡每秒的平均发送流量 (B/S)
    :return:
    """
    node_realtime_info = {}
    p = subprocess.Popen("source ../util/node_continuous_info.sh %s" % (net_name), shell=True, executable="/bin/bash", stdout=subprocess.PIPE)
    p.wait()
    sys_out = p.communicate()

    sys_stus = str(sys_out[0]).split("\n")
    # get cpu rate
    cpu_rate = float(sys_stus[1])/float(sys_stus[0])
    node_realtime_info["cpu_use_rate"] = cpu_rate

    # get mem used
    mem_used = sys_stus[2]
    node_realtime_info["mem_used"] = mem_used

    # get the all disk space and free space
    disk_all_space_raw = sys_stus[3].split("G ")
    disk_free_space = 0
    disk_free_space_raw = sys_stus[4].split("% ")
    disk_use_rate = []
    for j in range(len(disk_free_space_raw)-1):
        disk_use_rate.append(float(disk_free_space_raw[j])/100)
    disk_use_rate.append(float(disk_free_space_raw[-1].split("%")[0])/100)
    disk_all_space = 0
    for j in range(len(disk_all_space_raw)-1):
        disk_all_space += float(disk_all_space_raw[j])
        disk_free_space += float(disk_all_space_raw[j])*disk_use_rate[j]

    disk_free_space += float(disk_all_space_raw[-1].split("G")[0])*disk_use_rate[-1]
    disk_all_space += float(disk_all_space_raw[-1].split("G")[0])

    node_realtime_info["disk_free_space"] = disk_free_space
    node_realtime_info["disk_all_space"] = disk_all_space

    # get network rate
    network_response_rate = sys_stus[5]
    network_request_rate = sys_stus[6]
    node_realtime_info["net_download_rate"] = network_response_rate
    node_realtime_info["net_upload_rate"] = network_request_rate

    # get disk rate
    disk_read_rate = sys_stus[7]
    disk_write_rate = sys_stus[8]
    node_realtime_info["disk_read_rate"] = disk_read_rate
    node_realtime_info["disk_write_rate"] = disk_write_rate

    # for key in node_realtime_info:
    #     print key, node_realtime_info[key]
    return node_realtime_info


def write_info_to_redis():
    """
    :return:
    """
    i = 1
    node_continuous_data = {}
    node_continuous_data["cpu_use_rate"] = {}
    node_continuous_data["mem_use"] = {}
    node_continuous_data["disk_read_rate"] = {}
    node_continuous_data["disk_write_rate"] = {}
    node_continuous_data["net_upload_rate"] = {}
    node_continuous_data["net_download_rate"] = {}

    host_name = os.popen("cat /etc/hostname").read().split("\n")[0]
    ip = os.popen("ifconfig | perl -nle 's/dr:(\S+)/print $1/e'").read().split("\n")[0]

    node_continuous_data["host_name"] = host_name
    node_continuous_data["ip"] = ip

    # 存储采集时间段内的最早时间
    earlyest_time = 9480855070

    while True:

        # 根据范围与指定的时间间隔采集数据
        if len(node_continuous_data["cpu_use_rate"]) < MONITOR_PEROID:

            # 采集一次系统的信息
            node_real_info = node_continuous_info(NET_NAME)
            time_stamp = time.time()
            if earlyest_time > time_stamp:
                earlyest_time = time_stamp

            node_continuous_data["cpu_use_rate"][time_stamp] = node_real_info["cpu_use_rate"]
            node_continuous_data["mem_use"][time_stamp] = node_real_info["mem_used"]
            node_continuous_data["disk_read_rate"][time_stamp] = node_real_info["disk_read_rate"]
            node_continuous_data["disk_write_rate"][time_stamp] = node_real_info["disk_write_rate"]
            node_continuous_data["net_upload_rate"][time_stamp] = node_real_info["net_upload_rate"]
            node_continuous_data["net_download_rate"][time_stamp] = node_real_info["net_download_rate"]
            time.sleep(MONITOR_INTERVAL)

        else:
            # 到达监控的连续个数后，删除时间最早的数据
            node_real_info = node_continuous_info(NET_NAME)
            time_stamp = time.time()

            for i in node_continuous_data["cpu_use_rate"]:
                node_continuous_data["cpu_use_rate"].pop(i)
                break

            for i in node_continuous_data["mem_use"]:
                node_continuous_data["mem_use"].pop(i)
                break

            for i in node_continuous_data["disk_read_rate"]:
                node_continuous_data["disk_read_rate"].pop(i)
                break

            for i in node_continuous_data["disk_write_rate"]:
                node_continuous_data["disk_write_rate"].pop(i)
                break

            for i in node_continuous_data["net_upload_rate"]:
                node_continuous_data["net_upload_rate"].pop(i)
                break

            for i in node_continuous_data["net_download_rate"]:
                node_continuous_data["net_download_rate"].pop(i)
                break

            # 插入新的数据
            node_continuous_data["cpu_use_rate"][time_stamp] = node_real_info["cpu_use_rate"]
            node_continuous_data["mem_use"][time_stamp] = node_real_info["mem_use"]
            node_continuous_data["disk_read_rate"][time_stamp] = node_real_info["disk_read_rate"]
            node_continuous_data["disk_write_rate"][time_stamp] = node_real_info["disk_write_rate"]
            node_continuous_data["net_upload_rate"][time_stamp] = node_real_info["net_upload_rate"]
            node_continuous_data["net_download_rate"][time_stamp] = node_real_info["net_download_rate"]
            time.sleep(MONITOR_INTERVAL)

        if len(node_continuous_data["cpu_use_rate"]) == MONITOR_PEROID:
            if redis_queue.qsize() == 1:
                redis_queue.get()
                redis_queue.put(json.dumps(node_continuous_data))




if __name__ == "__main__":
    #node_continuous_info('eth0')
    write_info_to_redis()
    # print redis_queue.qsize()
    # print time.time()

