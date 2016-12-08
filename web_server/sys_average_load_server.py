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
from config.config import SYSTEM_MACHINE_NAME, REDIS_SYSTEM_KEY
from api.get_system_average_info import get_sys_average_load
from util.redis_queue import RedisQueue
from monitor.node_continuous_info import node_continuous_info

define('port', default=8999, help='run on the given port', type=int)
r = redis.Redis(REDIS_HOST, REDIS_PORT)
redis_sys = RedisQueue(REDIS_SYSTEM_KEY)


class SysAverageLoadWebService:
    def start(self):
        tornado.options.parse_command_line()

        node_continuous = tornado.web.Application(
            handlers=[(r"/api/manage/(.*)", SysAverageLoadInfoHandle)])
        node_continuous_server = tornado.httpserver.HTTPServer(node_continuous)
        node_continuous_server.listen(options.port, address='0.0.0.0')

        tornado.ioloop.IOLoop.instance().start()


class SysAverageLoadInfoHandle(tornado.web.RequestHandler):
    def post(self, api_name):
        self.get(api_name)

    def get(self, api_name):
        print api_name
        return_data = get_sys_average_load()
        self.write(json.dumps(return_data))

    def put(self, api_name):
        self.post(api_name)


if __name__ == "__main__":
    test = SysAverageLoadWebService()
    test.start()

