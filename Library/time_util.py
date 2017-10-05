#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import request, make_response, jsonify
from functools import wraps
import Library.log_util as ED
import datetime
import time
import json
import re
import pytz
import uuid
import traceback
import os
from urllib2 import urlopen
from urllib2 import HTTPError
from Library.log_util import LogCenter
logger = LogCenter.instance().get_logger('TimeUtilLog')


##########################################
# 时间相关 Start
##########################################
def convert_int_2_string_single(int_time, onlydate=False, only_m_d=False):
    key_time = time.localtime(int_time)
    if onlydate == True:
        return time.strftime('%Y-%m-%d', key_time)
    elif only_m_d == True:
        return time.strftime('%m-%d', key_time)
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S', key_time)


# 将int类型时间转成字符串
def convert_int_2_string(datas, keys, onlydate=False, only_m_d=False):
    if type(datas) == dict:
        datas = [datas]
    if type(datas) != list:
        return datas
    if type(keys) == str or type(keys) == unicode:
        keys = [keys]
    if type(keys) != list:
        return datas
    for data in datas:
        for key in keys:
            if data.has_key(key) and type(data[key]) == int:
                key_time = time.localtime(data[key])
                if onlydate == True:
                    data[key] = time.strftime('%Y-%m-%d', key_time)
                elif only_m_d == True:
                    data[key] = time.strftime('%m-%d', key_time)
                else:
                    data[key] = time.strftime('%Y-%m-%d %H:%M:%S', key_time)
    return datas


# 讲 string 时间转化为int
def convert_string_2_int(timestring):
    # if type(timestring) == str or type(timestring) == unicode:
    #     return 0
    return time.mktime(time.strptime(timestring, '%Y-%m-%d %H:%M:%S'))


# 将Datetime类型转成字符串
def convert_datetime_2_string(datas, keys, onlydate=False, only_m_d=False):
    if type(datas) == dict:
        datas = [datas]
    if type(datas) != list:
        return datas
    if type(keys) == str or type(keys) == unicode:
        keys = [keys]
    if type(keys) != list:
        return datas
    for data in datas:
        for key in keys:
            if data.has_key(key) and type(data[key]) == datetime.datetime:
                if onlydate == True:
                    data[key] = data[key].strftime('%Y-%m-%d')
                elif only_m_d == True:
                    data[key] = data[key].strftime('%m-%d')
                else:
                    data[key] = data[key].strftime('%Y-%m-%d %H:%M:%S')
    return datas


def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.000Z'):
    local_tz = pytz.timezone('Asia/Chongqing')
    local_format = "%Y-%m-%d %H:%M"
    utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return int(time.mktime(time.strptime(time_str, local_format)))


def get_now_time_int():
    return int(time.time())


def get_now_time_str_ms():
    return ("%.3f" % (time.time())).decode('utf-8')


# api调用耗时
def check_api_cost_time(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            start = time.time()
            ret = method(*args, **kwargs)
            end = time.time()
            print method.__name__ + " api cost time %f s" % (end - start)
            # logger.debug(method.__name__ + " api cost time %f s" % (end - start))
            return ret
        except Exception, e:
            logger.error(repr(traceback.format_exc()))
            # return package_ret_data_from_server({'code': 99999})
            return {'code': 99999}

    return _decorator
