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
from config.config import REDIS_HOST, REDIS_PORT
from monitor.node_continuous_info import node_continuous_info

define('port', default=8999, help='run on the given port', type=int)
r = redis.Redis(REDIS_HOST, REDIS_PORT)


class NodeContinuousWebService:
    def start(self):
        tornado.options.parse_command_line()

        node_continuous = tornado.web.Application(handlers=[(r"/api/manage/node_continuous_info?(.*)", NodeContinuousInfoHandle)])
        node_continuous_server = tornado.httpserver.HTTPServer(node_continuous)
        node_continuous_server.listen(options.port, address='0.0.0.0')

        tornado.ioloop.IOLoop.instance().start()


class NodeContinuousInfoHandle(tornado.web.RequestHandler):

    def post(self, api_type):
        self.get(api_type)

    def get(self, api_type):

        # 获取参数中传过来的主机名字
        data = self.get_argument("params")
        request_parameter = ast.literal_eval(data)
        node_name = request_parameter['node_name']
        # 根据主机名字到redis中取值
        continuous_info = r.lindex(node_name, 0)
        continuous_dict = ast.literal_eval(continuous_info)

        return_data = {}
        return_data["data"] = continuous_dict
        return_data["status"] = 100
        return_data["message"] = ""
        self.write(json.dumps(return_data))

    def put(self, api_type):
        self.post(api_type)


if __name__ == "__main__":
    test = NodeContinuousWebService()
    test.start()
