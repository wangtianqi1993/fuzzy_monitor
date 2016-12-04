# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from decimal import *
import subprocess


def kvm_monitor():
    # 得到启动的虚拟机的名字	
    try:
        kvm_list = os.popen("virsh list|grep running").read()
    except Exception, e:
        kvm_list = ""
    kvm_name = []
    line_names = kvm_list.split('\n')
    for line_th in range(0, len(line_names) - 1):
        line_name = line_names[line_th]
        name = line_name.split(" ")
        kvm_name.append(name[6])
    # 得到不同虚拟机的信息
    kvm_info = {}
    current_time = time.time()
    kvm_info["current_time"] = time.time()

    for k_name in kvm_name:
        kvm_info[k_name] = {}
        try:
            cpu_time = os.popen("virsh dominfo " + k_name + "|grep CPU").read().split(":")[-1]
        except Exception, e:
            cpu_time = 0
        cpu_time = cpu_time.split(" ")[-1].split("s")[0]
        print cpu_time
        kvm_info[k_name]["cpu_time"] = float(cpu_time)
        try:
            rx_bytes = os.popen("virsh domifstat " + k_name + " vnet0|grep rx_bytes").read().split(" ")[2]
        except Exception, e:
            rx_bytes = 0
        print rx_bytes
        kvm_info[k_name]["rx_bytes"] = float(rx_bytes)
        try:
            rx_packets = os.popen("virsh domifstat " + k_name + " vnet0|grep rx_packets").read().split(" ")[2]
        except Exception, e:
            rx_packets = 0
        try:
            tx_bytes = os.popen("virsh domifstat " + k_name + " vnet0|grep tx_bytes").read().split(" ")[2]
        except Exception, e:
            tx_bytes = 0
        try:
            tx_packets = os.popen("virsh domifstat " + k_name + " vnet0|grep tx_packets").read().split(" ")[2]
        except Exception, e:
            tx_packets = 0
        print rx_packets
        print tx_bytes
        print tx_packets
        kvm_info[k_name]["rx_packets"] = float(rx_packets)
        kvm_info[k_name]["tx_bytes"] = float(tx_bytes)
        kvm_info[k_name]["tx_packets"] = float(tx_packets)
        # 获得虚拟机的内存使用情况
        try:
            mem = os.popen("virsh dominfo " + k_name + "|grep memory").read().split(" ")
        except Exception, e:
            max_mem = 0
            used_mem = 0

        max_mem = mem[6]
        used_mem = mem[12]
        kvm_info[k_name]["max_mem"] = float(max_mem)
        kvm_info[k_name]["used_mem"] = float(used_mem)
        try:
            cpu_times = os.popen("virsh domstats " + k_name + "|grep cpu").read().split("\n")
        except Exception, e:
            cpu_all_time = 2
            cpu_user_time = 1
            cpu_sys_time = 1
        cpu_all_time = cpu_times[0].split("=")[1]
        cpu_user_time = cpu_times[1].split("=")[1]
        cpu_sys_time = cpu_times[2].split("=")[1]
        print cpu_all_time
        print cpu_user_time
        print cpu_sys_time
        cpu_user_rate = Decimal(cpu_user_time) / Decimal(cpu_all_time)
        cpu_sys_rate = Decimal(cpu_sys_time) / Decimal(cpu_all_time)
        print cpu_user_rate
        print cpu_sys_rate
        kvm_info[k_name]["cpu_user_rate"] = cpu_user_rate
        kvm_info[k_name]["cpu_sys_rate"] = cpu_sys_rate


if __name__ == "__main__":
    kvm_monitor()
