#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from functools import wraps
from flask import make_response
unknown_err = 100
no_err= 200



# 消息:	描述:
# 500 Internal Server Error	请求未完成。服务器遇到不可预知的情况。
# 501 Not Implemented	请求未完成。服务器不支持所请求的功能。
# 502 Bad Gateway	请求未完成。服务器从上游服务器收到一个无效的响应。
# 503 Service Unavailable	请求未完成。服务器临时过载或当机。
# 504 Gateway Timeout	网关超时。
# 505 HTTP Version Not Supported	服务器不支持请求中指明的HTTP协议版本。

err_sys = 503

err_user_not_login = 506
err_user_login_expired = 507
err_access_expired = 508
err_code_invalid = 509
err_user_id_not_exist = 510
err_user_id_existed = 511
err_no_auth = 512
err_password_format = 513
err_password = 514
err_user_register_error = 515
err_non_unique = 516
err_not_found = 517
err_no_req_data = 518
err_req_data = 519
err_user_limit = 520
err_duplicate = 521
err_user_permission = 522
err_user_abnormal = 523
err_timeout = 524

Message = {}
Message[unknown_err] = {'en': 'unknown error','cn': u'未知错误'}
Message[no_err] = {'en':'no error','cn': u'成功'}
Message[err_sys] = {'en':'system error', 'cn': u'系统错误'}
Message[err_user_id_existed] = {'en':'user id existed', 'cn': u'用户已存在'}
Message[err_password] = {'en':'password error', 'cn': u'密码错误'}
Message[err_no_auth] = {'en':'no auth','cn': u'未认证'}
Message[err_code_invalid] = {'en':'invalid code invalid', 'cn': u'验证码错误'}
Message[err_non_unique] = {'en':'err_non_unique', 'cn': u'非唯一异常'}
Message[err_not_found] = {'en':'Not found', 'cn': u'未找到'}
Message[err_no_req_data] = {'en':'No request data', 'cn': u'请求数据空'}
Message[err_req_data] = {'en':'incorrect request data', 'cn': u'请求数据出错'}
Message[err_user_limit] = {'en':'user limited', 'cn': u'用户受限'}
Message[err_duplicate] = {'en':'duplicate not allowed', 'cn': u'已存在'}
Message[err_user_permission] = {'en': 'err_user_permission', 'cn': u'用户权限错误'}
Message[err_user_abnormal] = {'en': 'err_user_abnormal', 'cn': u'用户行为异常'}
Message[err_timeout] = {'en': 'err_timeout', 'cn': u'超时'}

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




def Respond_Err(err_code, err_msg=None):
    return {'code':err_code, 'data': '%s' % err_msg if err_msg else Message.get(err_code).get('cn') or Message.get(err_code).get('en')}


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