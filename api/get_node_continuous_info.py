# !usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wtq'

import ast
import json
import redis
from config.config import REDIS_HOST, REDIS_PORT

r = redis.Redis(REDIS_HOST, REDIS_PORT)


def get_node_continuous_info(node_name):
    """
    根据node_name 返回一段时间内的连续信息
    :param node_name:
    :return:
    """
    continuous_info = r.lindex(node_name, 0)
    continuous_dict = ast.literal_eval(continuous_info)

    return_data = {}
    return_data["data"] = continuous_dict
    return_data["status"] = 100
    return_data["message"] = ""
    print return_data
    return return_data

if __name__ == "__main__":
    get_node_continuous_info("storage1")
