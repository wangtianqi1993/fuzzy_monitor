# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wtq'

import ast
import json
import redis
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from config.config import MONITOR_PEROID
from config.config import REDIS_HOST, REDIS_PORT
from config.config import SYSTEM_MACHINE_NAME
from util.redis_queue import RedisQueue
from monitor.node_continuous_info import node_continuous_info

define('port', default=8999, help='run on the given port', type=int)
r = redis.Redis(REDIS_HOST, REDIS_PORT)
redis_sys = RedisQueue("system")


class SysAverageLoadWebService:
    def start(self):
        tornado.options.parse_command_line()

        node_continuous = tornado.web.Application(
            handlers=[(r"/api/manage/system_load_monitor?(.*)", SysAverageLoadInfoHandle)])
        node_continuous_server = tornado.httpserver.HTTPServer(node_continuous)
        node_continuous_server.listen(options.port, address='0.0.0.0')

        tornado.ioloop.IOLoop.instance().start()


class SysAverageLoadInfoHandle(tornado.web.RequestHandler):
    def post(self, api_type):
        self.get(api_type)

    def get(self, api_type):

        machine_names = SYSTEM_MACHINE_NAME
        time_stamp = []

        cpu_average = [0]*MONITOR_PEROID
        mem_average = [0]*MONITOR_PEROID
        disk_average = [0]*MONITOR_PEROID
        is_calculate = 0
        machine_nums = len(SYSTEM_MACHINE_NAME)

        # 根据主机名字到redis中取值
        for node_name in machine_names:
            continuous_info = r.lindex(node_name, 0)
            continuous_dict = ast.literal_eval(continuous_info)

            # 获取时间
            if not is_calculate:
                for key in sorted(continuous_dict["cpu_use_rate"].keys()):
                    time_stamp.append(key)
                is_calculate = 1

            # 不同机器的相应统计值相累加
            index = 0
            for key in sorted(continuous_dict["cpu_use_rate"].keys()):
                cpu_average[index] += float(continuous_dict["cpu_use_rate"][key]) / machine_nums
                mem_average[index] += float(continuous_dict["mem_use_rate"][key]) / machine_nums
                disk_average[index] += float(continuous_dict["disk_use_rate"][key]) / machine_nums
                index += 1

        sys_average_load = {}
        sys_average_load["cpu_use_rate"] = {}
        sys_average_load["mem_use_rate"] = {}
        sys_average_load["disk_use_rate"] = {}

        for index in range(len(time_stamp)):
            sys_average_load["cpu_use_rate"][time_stamp[index]] = cpu_average[index]
            sys_average_load["mem_use_rate"][time_stamp[index]] = mem_average[index]
            sys_average_load["disk_use_rate"][time_stamp[index]] = disk_average[index]

        # 系统信息存入到redis中
        if redis_sys.qsize() == 1:
            redis_sys.get()
            redis_sys.put(json.dumps(sys_average_load))
        else:
            redis_sys.put(json.dumps(sys_average_load))

        return_data = {}
        return_data["data"] = sys_average_load
        return_data["status"] = 100
        return_data["message"] = ""
        self.write(json.dumps(return_data))

    def put(self, api_type):
        self.post(api_type)


if __name__ == "__main__":
    test = SysAverageLoadWebService()
    test.start()

