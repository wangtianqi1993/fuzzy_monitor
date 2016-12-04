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


class NodeRealTimeInfoWebService:
    def start(self):
        tornado.options.parse_command_line()
        # app = tornado.web.Application(handlers=[(r"/detector/(.*)", AdDetectorHandler)])
        app = tornado.web.Application(handlers=[(r"/api/testsamplesystem/node_realtime_info?(.*)", NodeRealTimeInfoFunctionHandle)])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port, address='0.0.0.0')
        tornado.ioloop.IOLoop.instance().start()


class NodeRealTimeInfoFunctionHandle(tornado.web.RequestHandler):

    def post(self, api_type):

        node_info = node_realtime_info()

        self.write(json.dumps(node_info))

    def get(self, api_type):
        self.post(api_type)

    def put(self, api_type):
        self.post(api_type)


if __name__ == "__main__":
    test = NodeRealTimeInfoWebService()
    test.start()
