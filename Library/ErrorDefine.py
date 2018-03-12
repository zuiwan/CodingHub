#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       ErrorDefine
   Description:
   Author:          huangzhen
   date:            2018/3/4
-------------------------------------------------
   Change Activity:
                   2018/3/4:
-------------------------------------------------
"""
__author__ = 'huangzhen'

from functools import wraps
from flask import make_response

unknown_err = 100
no_err = 200

# 消息:	描述:
# 500 Internal Server Error	请求未完成。服务器遇到不可预知的情况。
# 501 Not Implemented	请求未完成。服务器不支持所请求的功能。
# 502 Bad Gateway	请求未完成。服务器从上游服务器收到一个无效的响应。
# 503 Service Unavailable	请求未完成。服务器临时过载或当机。
# 504 Gateway Timeout	网关超时。
# 505 HTTP Version Not Supported	服务器不支持请求中指明的HTTP协议版本。

err_sys = 503
err_not_found = 404
err_bad_request = 400


err_user_not_login = 510
err_user_login_expired = 511
err_access_expired = 512
err_user_id_not_exist = 513
err_user_id_existed = 514
err_user_register_error = 515

err_req_data = 520


Message = {}
Message[unknown_err] = {'en': 'unknown error', 'cn': u'未知错误'}
Message[no_err] = {'en': 'no error', 'cn': u'成功'}
Message[err_sys] = {'en': 'system error', 'cn': u'系统错误'}
Message[err_user_id_existed] = {'en': 'user id existed', 'cn': u'用户已存在'}
Message[err_req_data] = {'en': 'incorrect request data', 'cn': u'请求数据出错'}
Message[err_not_found] = {"en": "Not found", "cn": "未找到"}
#
# * 1.当输入的用户名不符合格式要求时，提示“用户名格式出错，只支持字母和符号”。
# * 2.用户名输入超出时不显示超出内容，提示“用户名限制20个字符”
# * 3.当用户名后台查重发现已存在时，提示“该名称已被使用”
# * 4.当输入的邮箱不符合格式要求时，提示“邮箱格式出错”
# * 5.当输入的邮箱查重发现已存在时，提示“该邮箱已注册”
# * 6.当密码不符合格式要求时，提示“密码格式出错，必须包含字母和数字”
# * 7.当密码数量不符合要求时，提示“密码最少8个字符，最多20个字符”
# * 8.当邀请码验证不正确时，提示“邀请码出错”
# * 9.当输入的邮箱验证码不正确时，提示“邮箱验证码出错”


KEYS = ('code', 'data')

def Respond_Err(err_code, err_msg=None):
    return {'code': err_code, 'data': '%s' % err_msg if err_msg
            else Message.get(err_code).get('cn') or Message.get(err_code).get('en') if Message.get(err_code) else u'未知'}


def auth_error_handler(auth):
    '''
    auth = HTTPBasicAuth()
    :param auth:
    :return:
    '''

    def decorate(f):
        @wraps(f)
        def wrapper(*args):
            res = f(*args)
            res = make_response(res)
            # if res.status_code == 200:
            #     # if user didn't set status code, use 401
            #     res.status_code = 401
            if 'WWW-Authenticate' not in res.headers.keys():
                res.headers['WWW-Authenticate'] = auth.authenticate_header()
            return res

        auth.auth_error_callback = wrapper
        return wrapper

    return decorate
