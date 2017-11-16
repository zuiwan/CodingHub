#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from functools import wraps
from flask import request

import re

def Is_Email_Validate(email):
    if email and len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
        else:
            return False
    else:
        return False

def Is_Username_Validate(username):
    '''
    * username最少4个字符，最多20字符，只支持符号和英文，区分大小写，不支持中文等其他语言
    * Nickname 最多20字符，非必填，字符内容不做限制
    :param username:
    :return:
    '''
    #  中文  [u4e00-u9fa5]
    # ^/w+$
    if username and re.match(r"[\w-]{4,20}", username):
        return True

def Is_Password_Validate(password):
    '''
    密码内容必须包含字母和数字，可包含符号，最少8个字符，最多20字符
    :param password:
    :return:
    '''
    if password \
            and re.search(r"[a-zA-Z]", password) \
            and re.search(r"[0-9]",password) \
            and re.match(r"[\w|`~!@#$%^&*()_+-=<>\?\,\.\/\\\|]{8,20}",password):
        # 以字母开头，长度在8~20之间，只能包含字母、数字和下划线
        return True



