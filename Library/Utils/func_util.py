#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       func_util
   Description:
   Author:          huangzhen
   date:            2018/3/4
-------------------------------------------------
   Change Activity:
                   2018/3/4:
-------------------------------------------------
"""
__author__ = 'huangzhen'

import inspect
import os
import sys
import types
from functools import wraps


def My_Itertools_Chain(*iters):
    for iterator, parser in iters:
        try:
            for i in iterator:
                if parser and hasattr(parser, '__call__'):
                    try:
                        ret = parser(i)
                    except:
                        continue
                    yield ret
                else:
                    yield i
        except StopIteration as e:
            continue


def get_current_function_name():
    return inspect.stack()[1][3]


def get_current_function_file():
    return inspect.stack()[0][1]


def get_current_function_line():
    return inspect.stack()[0][2]


def is_new_style(cls):
    return hasattr(cls, '__class__') \
           and \
           ('__dict__' in dir(cls) or hasattr(cls, '__slots__'))


def is_new_style_2(cls):
    return str(cls).startswith('<class ')


def Is_Cls(obj):
    return type(obj) is types.InstanceType or is_new_style(obj)


def class_attrs_mapper(*attrs):
    def wrapper(method):
        @wraps(method)
        def _decorator(*args, **kwargs):
            try:
                ret = method(*args, **kwargs)
                return ret
            except Exception as e:
                pass

        return _decorator

    return wrapper


class Lazy_Attrs_Mapper(object):
    def __init__(self, *attrs):
        self.attrs = attrs

    def get(self, instance):
        # assert Is_Cls(instance), isinstance(attrs, tuple) or isinstance(attrs, list)
        vals = []
        for attr in self.attrs:
            vals.append(instance.__getattribute__(attr))
        return vals
