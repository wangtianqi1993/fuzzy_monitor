# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wtq'

import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from monitor.node_realtime_info import node_realtime_info


define('port', default=8999, help='run on the given port', type=int)


class NodeRealTimeWebService:
    def start(self):
        tornado.options.parse_command_line()
        node_realtime = tornado.web.Application(handlers=[(r"/api/manage/node_realtime_info?(.*)", NodeRealTimeInfoHandle)])
        node_realtime_server = tornado.httpserver.HTTPServer(node_realtime)
        node_realtime_server.listen(options.port, address='0.0.0.0')

        tornado.ioloop.IOLoop.instance().start()


class NodeRealTimeInfoHandle(tornado.web.RequestHandler):

    def post(self, api_type):

        node_info = node_realtime_info()

        self.write(json.dumps(node_info))

    def get(self, api_type):
        self.post(api_type)

    def put(self, api_type):
        self.post(api_type)


if __name__ == "__main__":
    test = NodeRealTimeWebService()
    test.start()
