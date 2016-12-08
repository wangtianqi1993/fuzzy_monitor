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
from config.config import FASTDFSPORT
from util.redis_queue import RedisQueue

redis_queue = RedisQueue("storage2")
# 可以再建其他节点名字的消息队列,不同机器上该脚本的redis队列key为相应机器上的IP，连接的redis的ip是相同的


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
    # 运行node_continuous_info.sh 脚本一次会花费12s的时间
    p = subprocess.Popen("source ../util/node_continuous_info.sh %s" % (net_name), shell=True, executable="/bin/bash", stdout=subprocess.PIPE)
    p.wait()
    sys_out = p.communicate()

    sys_stus = str(sys_out[0]).split("\n")
    # get cpu rate
    cpu_rate = float(sys_stus[1])/float(sys_stus[0])
    node_realtime_info["cpu_use_rate"] = cpu_rate

    # get mem used
    mem_used = sys_stus[2]
    node_realtime_info["mem_used"] = float(mem_used)

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
    disk_use_rate = float(disk_all_space - disk_free_space) / float(disk_all_space)

    node_realtime_info["disk_free_space"] = disk_free_space
    node_realtime_info["disk_all_space"] = disk_all_space
    node_realtime_info["disk_use_rate"] = disk_use_rate

    # get network rate
    network_response_rate = sys_stus[5]
    network_request_rate = sys_stus[6]
    node_realtime_info["net_download_rate"] = float(network_response_rate)
    node_realtime_info["net_upload_rate"] = float(network_request_rate)

    # get disk rate
    disk_read_rate = sys_stus[7]
    disk_write_rate = sys_stus[8]
    node_realtime_info["disk_read_rate"] = float(disk_read_rate)
    node_realtime_info["disk_write_rate"] = float(disk_write_rate)

    # for key in node_realtime_info:
    #     print key, node_realtime_info[key]
    return node_realtime_info


def write_info_to_redis():
    """
    此脚本要实时运行，在每台机器上采取相应数据
    :return:
    """
    i = 1
    node_continuous_data = {}
    node_continuous_data["cpu_use_rate"] = {}
    node_continuous_data["mem_use_rate"] = {}
    node_continuous_data["disk_read_rate"] = {}
    node_continuous_data["disk_write_rate"] = {}
    node_continuous_data["net_upload_rate"] = {}
    node_continuous_data["net_download_rate"] = {}
    node_continuous_data["disk_use_rate"] = {}
    node_continuous_data["client_link_times"] = {}

    host_name = os.popen("cat /etc/hostname").read().split("\n")[0]
    ip = os.popen("ifconfig | perl -nle 's/dr:(\S+)/print $1/e'").read().split("\n")[0]

    node_continuous_data["host_name"] = host_name
    node_continuous_data["ip"] = ip

    while True:

        # 根据范围与指定的时间间隔采集数据
        if len(node_continuous_data["cpu_use_rate"]) < MONITOR_PEROID:

            # 采集一次系统的信息
            node_real_info = node_continuous_info(NET_NAME)

            links_command = "netstat -nat|grep -i " + FASTDFSPORT + "|wc -l"
            client_link_nums = os.popen(links_command).read().split("\n")[0]

            time_stamp = time.time()

            node_continuous_data["cpu_use_rate"][time_stamp] = node_real_info["cpu_use_rate"]
            node_continuous_data["mem_use_rate"][time_stamp] = node_real_info["mem_used"]
            node_continuous_data["disk_read_rate"][time_stamp] = node_real_info["disk_read_rate"]
            node_continuous_data["disk_write_rate"][time_stamp] = node_real_info["disk_write_rate"]
            node_continuous_data["net_upload_rate"][time_stamp] = node_real_info["net_upload_rate"]
            node_continuous_data["net_download_rate"][time_stamp] = node_real_info["net_download_rate"]
            node_continuous_data["disk_use_rate"][time_stamp] = node_real_info["disk_use_rate"]
            node_continuous_data["client_link_times"][time_stamp] = client_link_nums
            time.sleep(MONITOR_INTERVAL)

        else:
            # 到达监控的连续个数后，删除时间最早的数据
            node_real_info = node_continuous_info(NET_NAME)
            links_command = "netstat -nat|grep -i " + FASTDFSPORT + "|wc -l"
            client_link_nums = os.popen(links_command).read().split("\n")[0]
            time_stamp = time.time()

            min_cpu_time = min(node_continuous_data["cpu_use_rate"].items(), key=lambda x: x[0])[0]
            node_continuous_data["cpu_use_rate"].pop(min_cpu_time)
            node_continuous_data["mem_use_rate"].pop(min_cpu_time)
            node_continuous_data["disk_read_rate"].pop(min_cpu_time)
            node_continuous_data["disk_write_rate"].pop(min_cpu_time)
            node_continuous_data["net_upload_rate"].pop(min_cpu_time)
            node_continuous_data["net_download_rate"].pop(min_cpu_time)
            node_continuous_data["disk_use_rate"].pop(min_cpu_time)
            node_continuous_data["client_link_times"].pop(min_cpu_time)

            # 插入新的数据
            node_continuous_data["cpu_use_rate"][time_stamp] = node_real_info["cpu_use_rate"]
            node_continuous_data["mem_use_rate"][time_stamp] = node_real_info["mem_used"]
            node_continuous_data["disk_read_rate"][time_stamp] = node_real_info["disk_read_rate"]
            node_continuous_data["disk_write_rate"][time_stamp] = node_real_info["disk_write_rate"]
            node_continuous_data["net_upload_rate"][time_stamp] = node_real_info["net_upload_rate"]
            node_continuous_data["net_download_rate"][time_stamp] = node_real_info["net_download_rate"]
            node_continuous_data["disk_use_rate"][time_stamp] = node_real_info["disk_use_rate"]
            node_continuous_data["client_link_times"][time_stamp] = client_link_nums
            time.sleep(MONITOR_INTERVAL)

        if len(node_continuous_data["cpu_use_rate"]) == MONITOR_PEROID:
            if redis_queue.qsize() == 1:
                # 更新之前删除之前的元素
                redis_queue.get()
                redis_queue.put(json.dumps(node_continuous_data))
            else:
                redis_queue.put(json.dumps(node_continuous_data))

if __name__ == "__main__":
    # node_continuous_info('eth0')
    write_info_to_redis()


