# !/usr/bin/env python
# -*-coding:utf-8 -*-
__author__ = 'wtq'

import ast
import json
import redis
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from config.config import REDIS_HOST, REDIS_PORT
from config.config import DISK_ALL_SPACE, MEM_ALL_SPACE, CPU_KERNEL_NUMS
from monitor.node_continuous_info import node_continuous_info

define('port', default=8998, help='run on the given port', type=int)
r = redis.Redis(REDIS_HOST, REDIS_PORT)


class SysRealTimeWebService:
    def start(self):
        tornado.options.parse_command_line()

        node_continuous = tornado.web.Application(handlers=[(r"/api/manage/system_realtime_info?(.*)", SysRealTimeInfoHandle)])
        node_continuous_server = tornado.httpserver.HTTPServer(node_continuous)
        node_continuous_server.listen(options.port, address='0.0.0.0')

        tornado.ioloop.IOLoop.instance().start()


class SysRealTimeInfoHandle(tornado.web.RequestHandler):

    def post(self, api_type):
        self.get(api_type)

    def get(self, api_type):

        # 根据主机名字到redis中取值
        system_info = r.lindex("system", 0)
        system_realtime_info = {}
        system_realtime_info["disk_all_space"] = DISK_ALL_SPACE
        system_realtime_info["cpu_kernal_nums"] = CPU_KERNEL_NUMS
        system_realtime_info["mem_all_space"] = MEM_ALL_SPACE

        system_dict = ast.literal_eval(system_info)
        for key in sorted(system_dict["disk_use_rate"].keys(), reverse=True):
            system_realtime_info["disk_use_rate"] = system_dict["disk_use_rate"][key]
            system_realtime_info["mem_use_rate"] = system_dict["mem_use_rate"][key]
            system_realtime_info["cpu_use_rate"] = system_dict["cpu_use_rate"][key]
            break

        return_data = {}
        return_data["data"] = system_realtime_info
        return_data["status"] = 100
        return_data["message"] = ""
        self.write(json.dumps(return_data))

    def put(self, api_type):
        self.post(api_type)


if __name__ == "__main__":
    test = SysRealTimeWebService()
    test.start()
