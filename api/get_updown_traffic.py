# !/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'wtq'

import os
import time
import logging
from config.config import FASTDFS_PEROID
from util.transtime import transtime
from util.logger import MonitorDetectorLogger

log = MonitorDetectorLogger()


def get_updown_rate():
    """
    计算一定时间内的fastdfs上传与下载流量速度(B/S)
    :return:
    """
    try:
        client_sys_info = {}
        fdfs_mon = os.popen("/usr/bin/fdfs_monitor /etc/fdfs/client.conf").read()
        fdfs_mon_tmp = fdfs_mon.split("Group")
    except Exception, e:
        log.info("error in execute node_realtime_info")
        fdfs_mon_tmp = "a"

    upload_byte_first = 0.0
    upload_byte_second = 0.0
    download_byte_first = 0.0
    download_byte_second = 0.0
    upload_rate_dict = {}
    download_rate_dict = {}

    # for中的每个元素都是一个Group信息
    for j in range(1, len(fdfs_mon_tmp)):

        storage_split = fdfs_mon_tmp[j].split("Storage")
        group_info = storage_split[0]
        group_info = group_info.split("\n")
        group_name = group_info[1].split(" ")[-1]

        # for中的每一个元素为一个Storage信息
        for i in range(1, len(storage_split)):
            node_dict = {}
            node_name = "Storage" + str(i)
            storage_info = storage_split[i].split("\n")
            upload_byte_first += float(storage_info[40].split(" ")[-1])
            download_byte_first += float(storage_info[46].split(" ")[-1])

    time.sleep(FASTDFS_PEROID)

    fdfs_mon = os.popen("/usr/bin/fdfs_monitor /etc/fdfs/client.conf").read()
    fdfs_mon_tmp = fdfs_mon.split("Group")
    for j in range(1, len(fdfs_mon_tmp)):

        storage_split = fdfs_mon_tmp[j].split("Storage")
        group_info = storage_split[0]
        group_info = group_info.split("\n")
        group_name = group_info[1].split(" ")[-1]

        # for中的每一个元素为一个Storage信息
        for i in range(1, len(storage_split)):
            node_dict = {}

            node_name = "Storage" + str(i)
            storage_info = storage_split[i].split("\n")

            upload_byte_second += float(storage_info[40].split(" ")[-1])
            download_byte_second += float(storage_info[46].split(" ")[-1])

    upload_byte_rate = (upload_byte_second - upload_byte_first) / FASTDFS_PEROID
    download_byte_rate = (download_byte_second - upload_byte_first) / FASTDFS_PEROID
    current_time = time.time()

    upload_rate_dict[current_time] = upload_byte_rate
    download_rate_dict[current_time] = download_byte_rate



