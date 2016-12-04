# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wtq'

import os
import time


def fdfs_monitor():
    """

    :return:
    """
    try:
        fdfs_info = {}
        fdfs_info["current_time"] = time.time()
        print fdfs_info["current_time"]
        fdfs_mon = os.popen("/usr/bin/node_realtime_info /etc/fdfs/client.conf").read()
        fdfs_mon_tmp = fdfs_mon.split("Group")
        # for中的每个元素都是一个Group信息
        for j in range(1, len(fdfs_mon_tmp)):

            storage_split = fdfs_mon_tmp[j].split("Storage")
            group_info = storage_split[0]
            group_info = group_info.split("\n")
            group_name = group_info[1].split(" ")[-1]

            # 存储每个group的具体信息由group_name作为key
            fdfs_info[group_name] = {}
            disk_total_space = group_info[2].split(" ")[-2]
            disk_free_space = group_info[3].split(" ")[-2]
            trunk_free_space = group_info[4].split(" ")[-2]

            # 以下三个值单位MB
            fdfs_info[group_name]["disk_total_space"] = float(disk_total_space)
            fdfs_info[group_name]["disk_free_space"] = float(disk_free_space)
            fdfs_info[group_name]["trunk_free_space"] = float(trunk_free_space)
            fdfs_info[group_name]["storage_info"] = []
            # for中的每一个元素为一个Storage信息
            for i in range(1, len(storage_split)):
                storage_info = storage_split[i].split("\n")
                storage_ip = storage_info[1].split(" ")[-1]

                # 存储每个storage的具体信息由storage_ip作为key
                #fdfs_info[group_name][storage_ip] = {}
                storage_temp = {}

                total_storage = storage_info[7].split(" ")[-2]
                free_storage = storage_info[8].split(" ")[-2]
                total_upload_count = storage_info[20].split(" ")[-1]
                success_upload_count = storage_info[21].split(" ")[-1]
                total_delete_count = storage_info[30].split(" ")[-1]
                success_delete_count = storage_info[31].split(" ")[-1]
                total_download_count = storage_info[32].split(" ")[-1]
                success_download_count = storage_info[33].split(" ")[-1]
                total_create_link_count = storage_info[36].split(" ")[-1]
                success_create_link_count = storage_info[37].split(" ")[-1]
                total_upload_bytes = storage_info[40].split(" ")[-1]
                success_upload_bytes = storage_info[41].split(" ")[-1]
                total_download_bytes = storage_info[46].split(" ")[-1]
                success_download_bytes = storage_info[47].split(" ")[-1]

                storage_temp["storage_ip"] = storage_ip

                storage_temp["total_storage"] = float(total_storage)
                storage_temp["free_storage"] = float(free_storage)
                storage_temp["total_upload_count"] = float(total_upload_count)
                storage_temp["success_upload_count"] = float(success_upload_count)
                storage_temp["total_delete_count"] = float(total_delete_count)
                storage_temp["success_delete_count"] = float(success_delete_count)
                storage_temp["total_download_count"] = float(total_download_count)
                storage_temp["success_download_count"] = float(success_download_count)
                storage_temp["total_create_link_count"] = float(total_create_link_count)
                storage_temp["success_create_link_count"] = float(success_create_link_count)
                storage_temp["total_upload_bytes"] = float(total_upload_bytes)
                storage_temp["success_upload_bytes"] = float(success_upload_bytes)
                storage_temp["total_download_bytes"] = float(total_download_bytes)
                storage_temp["success_download_bytes"] = float(success_download_bytes)
                fdfs_info[group_name]["storage_info"].append(storage_temp)

            for key in fdfs_info[group_name]:
                print key, fdfs_info[group_name][key]

            for key in fdfs_info[group_name]['storage_info'][0]:
                print key, fdfs_info[group_name]['storage_info'][0][key]

    except Exception, e:
        print 'get fastdfs info error', e

if __name__ == "__main__":
    fdfs_monitor()
