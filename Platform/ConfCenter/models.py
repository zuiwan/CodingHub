#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       models
   Description:     将配置抽象为数据模型对象
   Author:          huangzhen
   date:            2018/3/14
-------------------------------------------------
   Change Activity:
                   2018/3/14:
-------------------------------------------------
@ThreadSafeSingle
class ConfigA_Model(Config_Model):
    DEFAULT_CONFIG = 默认配置
    NAMESPACE = 名称空间，即配置存储位置， redis，file，mysql等
    KEY = 对应名称空间下一级的键，例如redis的key，file的path等

    def adapter(self, d):
        将从配置源读入的原始配置数据d转化为形如DEFAULT_CONFIG的配置
    def __init__(self):
        super(ConfigA_Model.get_cls(), self).__init__()
        调用refresh。
    def notify(self):
        对于已实例化且订阅了配置变更消息的配置对象，配置变更发布者将通知实例更新配置信息
    def refresh(self):
        从配置源读取配置并由adapter转换为DEFAULT_CONFIG的结构，读取失败则使用默认配置

## 特别说明，不要使用数字类型作为哈希表的任何键（包括嵌套哈希表），应当转换为字符串类型。
"""
import ctypes
import mmap
import os
import struct
import json
import sys
import traceback

from App.common.singleton import ThreadSafeSingleton
from App.extension import rdb

__author__ = 'huangzhen'


class Config_Model(object):
    DEFAULT_CONFIG = None
    KEY = None
    NAMESPACE = None
    TYPE = "hash"
    TYPE_GET_FUNC_MAP = {
        "hash": "hgetall",
        "string": "get"
    }
    # fixed offset, to show counter of config change times
    VERSION_OFFSET = struct.calcsize('i')
    LENGTH_OFFSET = struct.calcsize('i')
    HEADER_OFFSET = VERSION_OFFSET + LENGTH_OFFSET
    PAGESIZE = mmap.PAGESIZE

    def __init__(self):
        '''
        1. 刷新子类对象的默认配置信息：CONFIG；
        2. 通过模拟更新调用，冷启动共享内存；
        3. 打开子类配置所属的共享内存"句柄"
        '''
        self.identifier = '/tmp/configurations_{}'.format(self.__class__.__name__)  # MUST BE FIRST
        self.refresh()
        # config_version to improve cache usage
        self._version = 0
        # string length of bytes
        self._offset = 0
        # first write to solve cold-boot issue
        self.notify(self.CONFIG, init=True)
        # Open the file for reading, keeping open
        fd = os.open(self.identifier, os.O_RDONLY)
        # Memory map the file
        self._buf = mmap.mmap(fd, self.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ)

    def adapter(self, d):
        if not d:
            raise ValueError(r"None type or blank string not allowed")
        if isinstance(d, basestring):
            return json.loads(d)
        elif isinstance(d, dict):
            m = {}
            for k, v in d.items():
                try:
                    m[k] = json.loads(v, encoding="utf-8") if isinstance(v, basestring) and v else v
                except ValueError:
                    m[k] = v
            return m
        else:
            raise TypeError(r"unexpected config source data type: {}".format(type(d)))

    def __getitem__(self, item):
        '''
        Read operation
        :param item:
        :return:
        '''
        try:
            return self.as_dict[str(item)]
        except (KeyError, TypeError, ValueError):
            raise AttributeError(r"'%s' object has no attribute '%s'" % (self.__class__.__name__, item))

    def get(self, item):
        '''
        Read operation. Helper for __getitem__.
        :param item:
        :return:
        '''
        return self[item]

    def string(self):
        return json.dumps(self.as_dict)

    def __len__(self):
        return len(self.string())

    @property
    def as_dict(self):
        '''
        进程安全级别的只读。
        大多数时候，所有进程内的内存中CONFIG是保持同步的，因此可以直接返回CONFIG这个字典。
        为了确保另外一小部分时候的同步性，读共享内存，比对其头部的version，version一致则是同步的；
        version不一致，则更新本对象的CONFIG和version。
        虽然都要读共享内存，但是version避免了读json字符串再转为json对象的开销。
        :return:
        '''
        try:
            version, = struct.unpack('i', self._buf[:self.VERSION_OFFSET])
            if version != self._version:
                # cache missed
                length, = struct.unpack('i', self._buf[self.VERSION_OFFSET:self.HEADER_OFFSET])
                try:
                    # most cases this way
                    raw, = struct.unpack('{}s'.format(length),
                                         self._buf[self.HEADER_OFFSET:self.HEADER_OFFSET + length + 1])
                except struct.error:
                    # this can fix the less exceptions, but I do not know why right now
                    raw, = struct.unpack('{}s'.format(length),
                                         self._buf[self.HEADER_OFFSET:self.HEADER_OFFSET + length])
                self.CONFIG = json.loads(raw, encoding="utf-8")
                self._version = version
                self._offset = length
        except Exception as e:
            # maybe some bugs caused by os file stuff
            print("'%s' read failed, error: %s" % (self.__class__.__name__, str(e)),
                  "DEBUG traceback: {}".format(traceback.format_exc()))
            self.refresh()
        return self.CONFIG

    def notify(self, data, init=False):
        '''
        全局更新
        :param data: should be a configuration dict
        :param init: for cold start
        :return: None
        '''
        self.CONFIG = data
        # open file descriptor for writing
        fd = os.open(self.identifier, os.O_CREAT | os.O_RDWR)
        # Assert return value equals to mmap.PAGESIZE
        if init is True:
            size = self.PAGESIZE
            os.write(fd, '\x00' * size)
        else:
            size = os.path.getsize(self.identifier)
        # Create the mmap instance with the following params:
        # fd: File descriptor which backs the mapping or -1 for anonymous mapping
        # length: Must in multiples of PAGESIZE (usually 4 KB)
        # flags: MAP_SHARED means other processes can share this mmap
        # prot: PROT_WRITE means this process can write to this mmap
        buf = mmap.mmap(fd, size, mmap.MAP_SHARED, mmap.PROT_WRITE)
        # 头部版本标识（4字节）
        v = ctypes.c_int.from_buffer(buf)
        # if first init, i.value default as 0
        v.value += 1
        self._version = v.value
        buf.flush()  # 及时同步版本号，降低写冲突风险
        # 头部长度标识（4字节）
        l = ctypes.c_int.from_buffer(buf, self.VERSION_OFFSET)
        string = json.dumps(data, encoding="utf-8")
        l.value = len(string)
        self._offset = l.value
        # Now ceate a string first creating a c_char array for shared memory
        s_type = ctypes.c_char * self._offset
        # Now create the ctypes instance with offset
        s = s_type.from_buffer(buf, self.HEADER_OFFSET)
        s.raw = string
        buf.flush()
        buf.close()

    def refresh(self):
        try:
            method = self.TYPE_GET_FUNC_MAP[self.TYPE]
            try:
                config = self.adapter(rdb.__getattr__(method)(self.KEY))
            except AttributeError:
                config = self.adapter(rdb.__getattribute__(method)(self.KEY))
        except:
            config = None
        self.CONFIG = config or self.DEFAULT_CONFIG
        return self


@ThreadSafeSingleton
class Bill_Config(Config_Model):
    '''
    消费账单的价格
    '''
    NAMESPACE = "redis"
    KEY = "bill_config"
    TYPE = "hash"
    # 价格单位为0.01元，则price_scale=0.01，相较于标准价格单位分的方法比例
    # time_scale，相较于标准时间单位秒的放大比例
    DEFAULT_CONFIG = {
        "0": {
            "cpu": {
                "price": 100,
                "time_scale": 3600,
                "price_scale": 1
            }, "gpu": {
                "price": 800,
                "time_scale": 3600,
                "price_scale": 1
            }
        },
        "1": {
            "cpu": {
                "price": 100,
                "time_scale": 3600,
                "price_scale": 1

            }, "gpu": {
                "price": 800,
                "time_scale": 3600,
                "price_scale": 1
            }
        }
    }

    def __init__(self):
        super(Bill_Config.get_cls(), self).__init__()


@ThreadSafeSingleton
class Plan_Price_Config(Config_Model):
    '''
    套餐的价格
    '''
    NAMESPACE = "redis"
    KEY = "usage_plan_price_config"
    TYPE = "string"
    # 第一层键为plan_id（套餐等级），第二层键为时间，单位月，其对应的值为价格，人民币元。
    DEFAULT_CONFIG = {
        "1": {"1": 50, "3": 120, "6": 210}
    }

    def __init__(self):
        super(Plan_Price_Config.get_cls(), self).__init__()


@ThreadSafeSingleton
class Package_Price_Config(Config_Model):
    '''
    用量包的价格
    '''
    NAMESPACE = "redis"
    KEY = "usage_package_price_config"
    TYPE = "string"
    # key为时间，单位小时， value为人民币，单位元。
    DEFAULT_CONFIG = {"gpu": {"10": 80, "100": 500, "50": 300},
                      "cpu": {"10": 7, "100": 59, "50": 33}}

    def __init__(self):
        super(Package_Price_Config.get_cls(), self).__init__()


@ThreadSafeSingleton
class Plan_Config(Config_Model):
    '''
    套餐的具体信息
    '''
    DEFAULT_CONFIG = {
        '0': {
            'regular_cpu_balance': 10 * 3600,
            'regular_gpu_balance': 0,
            'concurrency': 2,
            'task_longest_limit': 21600,
            'disk_usage_limit': 10 * (1 << 10),  # MB
            'private_project_num': 0,
            'public_project_num': sys.maxint,
            'private_dataset_num': 0,
            'public_dataset_num': sys.maxint,
            'priority': 0,
            'name': 'free trial',
            'price': 0,
            "cpu_price_per_hour": 1,
            "gpu_price_per_hour": 8
        },
        "1": {
            'regular_cpu_balance': 20 * 3600,
            'regular_gpu_balance': 10 * 3600,
            'concurrency': 5,
            'task_longest_limit': 172800,
            'disk_usage_limit': 100 * (1 << 10),
            'private_project_num': 10,
            'public_project_num': sys.maxint,
            'private_dataset_num': 10,
            'public_dataset_num': sys.maxint,
            'priority': 1,
            'name': 'vip',
            'price': 50,
            "cpu_price_per_hour": 1,
            "gpu_price_per_hour": 8
        }}
    KEY = "plan_config"
    NAMESPACE = "redis"
    TYPE = "hash"
    PAGESIZE = 2 * mmap.PAGESIZE

    def __init__(self):
        super(Plan_Config.get_cls(), self).__init__()


@ThreadSafeSingleton
class Docker_Image_Config(Config_Model):
    '''
    官方支持的镜像列表
    '''
    DEFAULT_CONFIG = {
        "cpu": {
            "caffe": "caffe:1.0-py3.6",
            "caffe:py2": "caffe:1.0-py2.6",
            "chainer": "chainer:1.23.0-py3.6",
            "chainer-1.23": "chainer:1.23.0-py3.6",
            "chainer-1.23:py2": "chainer:1.23.0-py2.6",
            "chainer-2.0": "chainer:2.0.0-py3.6",
            "chainer-2.0:py2": "chainer:2.0.0-py2.6",
            "chainer:py2": "chainer:1.23.0-py2.6",
            "keras": "tensorflow:1.1.0-py3_aws.7",
            "keras:py2": "tensorflow:1.1.0-py2_aws.7",
            "kur": "kur:0.6.0-py3.6",
            "mxnet:py2": "mxnet:0.10.0-py2.6",
            "mxnet-1.0:py2": "mxnet:1.0.0-py2",
            "pytorch": "pytorch:0.2.0-py3.15",
            "pytorch-0.1": "pytorch:0.1-py3.8",
            "pytorch-0.1:py2": "pytorch:0.1-py2.8",
            "pytorch-0.2": "pytorch:0.2.0-py3.15",
            "pytorch-0.2:py2": "pytorch:0.2.0-py2.15",
            "pytorch-0.3": "pytorch:0.3.0-py3.17",
            "pytorch-0.3:py2": "pytorch:0.3.0-py2.17",
            "pytorch:py2": "pytorch:0.2.0-py2.15",
            "tensorflow": "tensorflow:1.1.0-py3_aws.7",
            "tensorflow-0.12": "tensorflow:0.12.1-py3.6",
            "tensorflow-0.12:py2": "tensorflow:0.12.1-py2.6",
            "tensorflow-1.0": "tensorflow:1.0.1-py3_aws.7",
            "tensorflow-1.0:py2": "tensorflow:1.0.1-py2_aws.7",
            "tensorflow-1.1": "tensorflow:1.1.0-py3_aws.7",
            "tensorflow-1.1:py2": "tensorflow:1.1.0-py2_aws.7",
            "tensorflow-1.2": "tensorflow:1.2.1-py3_aws.7",
            "tensorflow-1.2:py2": "tensorflow:1.2.1-py2_aws.7",
            "tensorflow-1.3": "tensorflow:1.3.1-py3_aws.13",
            "tensorflow-1.3:py2": "tensorflow:1.3.1-py2_aws.13",
            "tensorflow-1.4": "tensorflow:1.4.0-py3_aws.14",
            "tensorflow-1.4:py2": "tensorflow:1.4.0-py2_aws.14",
            "tensorflow:py2": "tensorflow:1.1.0-py2_aws.7",
            "theano": "theano:0.9.0-py3.6",
            "theano-0.8": "theano:0.8.2-py3.6",
            "theano-0.8:py2": "theano:0.8.2-py2.6",
            "theano-0.9": "theano:0.9.0-py3.6",
            "theano-0.9:py2": "theano:0.9.0-py2.6",
            "theano:py2": "theano:0.9.0-py2.6",
            "torch": "torch:7-py3.6",
            "torch:py2": "torch:7-py2.6",
            "paddle:py2": "paddle:latest",
            "caffe2:py2": "caffe:2.0-py2.7"
        },
        "gpu": {
            "caffe": "caffe:1.0-gpu-py3.6",
            "caffe:py2": "caffe:1.0-gpu-py2.6",
            "chainer": "chainer:1.23.0-gpu-py3.9",
            "chainer-1.23": "chainer:1.23.0-gpu-py3.9",
            "chainer-1.23:py2": "chainer:1.23.0-gpu-py2.9",
            "chainer-2.0": "chainer:2.0.0-gpu-py3.9",
            "chainer-2.0:py2": "chainer:2.0.0-gpu-py2.9",
            "chainer:py2": "chainer:1.23.0-gpu-py2.9",
            "keras": "tensorflow:1.1.0-gpu-py3_aws.7",
            "keras:py2": "tensorflow:1.1.0-gpu-py2_aws.7",
            "kur": "kur:0.6.0-gpu-py3.6",
            "mxnet:py2": "mxnet:0.10.0-gpu-py2.6",
            "mxnet-1.0:py2": "mxnet:1.0.0-gpu-py2",
            "pytorch": "pytorch:0.2.0-gpu-py3.15",
            "pytorch-0.1": "pytorch:0.1-gpu-py3.8",
            "pytorch-0.1:py2": "pytorch:0.1-gpu-py2.8",
            "pytorch-0.2": "pytorch:0.2.0-gpu-py3.15",
            "pytorch-0.2:py2": "pytorch:0.2.0-gpu-py2.15",
            "pytorch-0.3": "pytorch:0.3.0-gpu.cuda8cudnn6-py3.17",
            "pytorch-0.3:py2": "pytorch:0.3.0-gpu.cuda8cudnn6-py2.17",
            "pytorch:py2": "pytorch:0.2.0-gpu-py2.15",
            "tensorflow": "tensorflow:1.1.0-gpu-py3_aws.7",
            "tensorflow-0.12": "tensorflow:0.12.1-gpu-py3.6",
            "tensorflow-0.12:py2": "tensorflow:0.12.1-gpu-py2.6",
            "tensorflow-1.0": "tensorflow:1.0.1-gpu-py3.7",
            "tensorflow-1.0:py2": "tensorflow:1.0.1-gpu-py2.7",
            "tensorflow-1.1": "tensorflow:1.1.0-gpu-py3_aws.7",
            "tensorflow-1.1:py2": "tensorflow:1.1.0-gpu-py2_aws.7",
            "tensorflow-1.2": "tensorflow:1.2.1-gpu-py3_aws.7",
            "tensorflow-1.2:py2": "tensorflow:1.2.1-gpu-py2_aws.7",
            "tensorflow-1.3": "tensorflow:1.3.1-gpu-py3_aws.13",
            "tensorflow-1.3:py2": "tensorflow:1.3.1-gpu-py2_aws.13",
            "tensorflow-1.4": "tensorflow:1.4.0-gpu-py3_aws.14",
            "tensorflow-1.4:py2": "tensorflow:1.4.0-gpu-py2_aws.14",
            "tensorflow:py2": "tensorflow:1.1.0-gpu-py2_aws.7",
            "theano": "theano:0.9.0-gpu-py3.6",
            "theano-0.8": "theano:0.8.2-gpu-py3.6",
            "theano-0.8:py2": "theano:0.8.2-gpu-py2.6",
            "theano-0.9": "theano:0.9.0-gpu-py3.6",
            "theano-0.9:py2": "theano:0.9.0-gpu-py2.6",
            "theano:py2": "theano:0.9.0-gpu-py2.6",
            "torch": "torch:7-gpu-py3.6",
            "torch:py2": "torch:7-gpu-py2.6",
            "paddle:py2": "paddle:latest-gpu",
            "caffe2:py2": "caffe:2.0-gpu-py2.7"
        }
    }
    NAMESPACE = "redis"
    KEY = "docker_images"
    TYPE = "hash"
    PAGESIZE = 2 * mmap.PAGESIZE  # 比较大，默认的4096字节不够用
    DOCKER_ENV_SPLITTER = '$'

    def __init__(self):
        super(Docker_Image_Config.get_cls(), self).__init__()

    def adapter(self, d):
        '''
        :param d:
        :return:
        '''
        if not d:
            raise ValueError(r"None type or blank string not allowed")
        m = {}
        for k, v in d.items():
            l = k.split(self.DOCKER_ENV_SPLITTER)
            if l[0] not in m:
                m[l[0]] = {}
            m[l[0]][l[1]] = v
        return m
