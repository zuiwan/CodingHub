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


from net_util import *
from time_util import *
from log_util import *


from Library.log_util import LogCenter
logger = LogCenter.instance().get_logger('NetUtilLog')
# MAC ADDRESS
import traceback
from functools import wraps
from urllib2 import urlopen, HTTPError
import json

from flask import make_response
from shortuuid import uuid


def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
def getCountryCode(ipAddress):
    try:
        response = urlopen("http://freegeoip.net/json/"+ipAddress).read().decode('utf-8')
    except HTTPError:
        return None
    responseJson = json.loads(response)
    return responseJson.get("country_code")
def dotip2int(dotip):
    # import socket,struct
    # return socket.ntohl(struct.unpack("I",socket.inet_aton(str(ip)))[0])
    return (lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])]))(dotip)

def int2dotip(ip):
    return (lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)]))(ip)


def add_cross_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = "REFERER_URL,Accept,Origin,User-Agent"
    # response.headers['Access-Control-Allow-Credentials']  = 'true'
    return response


# 跨域装饰器
def allow_cross_domain(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            rst = make_response(method(*args, **kwargs))
            return add_cross_headers(rst)
        except Exception,e:
            logger.error(repr(traceback.format_exc()))
            return jsonify({'code': ED.err_sys})

    return _decorator



def getHostnameOfUrl(url):
    # (?xi)\A
    # [a - z][a - z0 - 9 +\-.] *: //  # Scheme
    # ([a - z0 - 9\-._
    # ~ %!$ & '()*+,;=]+@)?           # User
    # ([a - z0 - 9\-._
    # ~ %]+                           # Named or IPv4 host
    # | \[[a - z0 - 9\-._
    # ~ %!$ & '()*+,;=:]+\])          # IPv6+ host
    reobj = re.compile(r"(?xi)\A[a-z][a-z0-9+\-.]*://([a-z0-9\-._~%!$&'()*+,;=]+@)?([a-z0-9\-._~%]+|[a−z0−9\-.])")
    return reobj.search(url).group(2)


# 获取IP
def getClientRemoteIP(request):
    if request.headers.get('x-forwarded-for') == None:
        return request.environ.get('REMOTE_ADDR')
    else:
        ipStr = request.headers.get('X-Forwarded-For')
        ips = ipStr.split(', ')
        ret = ips[0]
        for ip in ips:
            bis = ip.split('.')
            count = 0
            for bi in bis:
                count = count * 1000 + int(bi)
            if 10000000000 <= count and count <= 10255255255:
                continue
            if 172016000000 <= count and count <= 172131255255:
                continue
            if 192168000000 <= count and count <= 192168255255:
                continue
            ret = ip
            break
        return ret
# 获取本地IP地址
def getLocalIP(outside=True):
    import socket, fcntl, struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if outside == True:
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', "eth1"[:15]))
        return socket.inet_ntoa(inet[20:24])
    else:
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', "eth0"[:15]))
        return socket.inet_ntoa(inet[20:24])

def package_json_request_data(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            if request.method == "POST":
                request.data = json.loads(request.data)
            else:
                temp_raw_data = request.args.items()
                temp_raw_map = {}
                for temp_item in temp_raw_data:
                    temp_raw_map[temp_item[0]] = temp_item[1]
                request.data = temp_raw_map
            request.data['ip'] = getClientRemoteIP(request)
            ret = method(*args, **kwargs)
            return ret
        except Exception, e:
            logger.error(repr(traceback.format_exc()))
            return "%s package_json_request_data error" % str(request)

    return _decorator
