#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask
import datetime
import time
import re
import pytz
import uuid
import traceback
from functools import wraps
import json
from shortuuid import uuid
import requests

from Library import ErrorDefine as ED
from .log_util import LogCenter

logger = LogCenter.instance().get_logger("utils", 'NetUtilLog')


def getMacAddress():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def getCountryCode(ipAddress):
    try:
        response = requests.get("http://freegeoip.net/json/" + ipAddress)
        responseJson = response.json()
    except requests.exceptions.HTTPError:
        return None
    except Exception:
        return None
    return responseJson.get("country_code")


def dotIp2Int(dotip):
    # import socket,struct
    # return socket.ntohl(struct.unpack("I",socket.inet_aton(str(ip)))[0])
    return (lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])]))(dotip)


def int2DotIp(ip):
    return (lambda x: '.'.join([str(x / (256 ** i) % 256) for i in range(3, -1, -1)]))(ip)


def addCrossHeaders(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = "REFERER_URL,Accept,Origin,User-Agent"
    # response.headers['Access-Control-Allow-Credentials']  = 'true'
    return response


# 跨域装饰器
def allowCrossomain(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            rst = flask.make_response(method(*args, **kwargs))
            return addCrossHeaders(rst)
        except Exception:
            logger.error(repr(traceback.format_exc()))
            return flask.jsonify({'code': ED.err_sys})

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


def getSourceName(request):
    source = None
    spec_host = ['qiuye']
    host_name = request.host
    host_name = host_name.replace('www.', '')
    host_list = host_name.split('.')
    if len(host_list) > 0 and host_list[0] in spec_host:
        source = host_list[0]
    else:
        ret_data = request.data
        if ret_data != None and type(ret_data) == dict and ret_data.has_key('source'):
            source = ret_data['source']
    return source

def require_field_in_data(*fields):
    '''
    Attention, In Order like this !!!
        @package_json_request_data
        @require_field_in_data("field1", "field2")
    :param method:
    :return:
    '''
    def decorator(method):
        @wraps(method)
        def _decorator(*args, **kwargs):
            try:
                for field in fields:
                    if field not in flask.request.data:
                        return ED.Respond_Err(ED.err_req_data, "{} required !!!".format(field))
                ret = method(*args, **kwargs)
                return ret
            except Exception as e:
                logger.error(repr(traceback.format_exc()))
                return "%s package_json_request_data error" % str(fields)
        return _decorator
    return decorator

def package_json_request_data(method):
    request = flask.request
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            if request.method in ("POST", "PUT"):
                request.data = json.loads(request.data, encoding="utf-8")
            else:
                temp_raw_data = request.args.items()
                temp_raw_map = {}
                for temp_item in temp_raw_data:
                    temp_raw_map[temp_item[0]] = temp_item[1]
                request.data = temp_raw_map
            request.data['ip'] = getClientRemoteIP(request)
            request.data['host'] = request.host
            source = getSourceName(request)
            if source != None and source != '':
                request.data["source"] = source
            ret = method(*args, **kwargs)
            return ret
        except Exception as e:
            logger.error(repr(traceback.format_exc()))
            return "fields %s required, package_json_request_data error" % str(request)

    return _decorator


def add_cross_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = "*"
    response.headers['Access-Control-Expose-Headers'] = "*"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# 跨域装饰器
def allow_cross_domain(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            response = method(*args, **kwargs)
            if not isinstance(response, flask.make_response("")):
                response = flask.make_response(response)
            return add_cross_headers(response)
        except Exception:
            logger.error(repr(traceback.format_exc()))
            return flask.jsonify({'code': ED.err_sys})

    return _decorator
