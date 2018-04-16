#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       manager
   Description:
   Author:          huangzhen
   date:            2018/3/14
-------------------------------------------------
   Change Activity:
                   2018/3/14:
-------------------------------------------------
"""
import json
import traceback

from Library.extensions import (
    orm as db,
    GetRedisConnection
)
rdb = GetRedisConnection()
from Library.Utils.log_util import LogCenter
from Library.singleton import Singleton, ThreadSafeSingleton
from models import Config_Model
from constants import (
    DOCKER_IMAGE_CONFIG,
    PLAN_PRICE_CONFIG,
    BILL_CONFIG,
    PACKAGE_PRICE_CONFIG,
    PLAN_CONFIG
)


@Singleton
class Config_Center(object):
    NAMESPACES = ("flask_app", "redis", "file", "mysql")

    def __init__(self):
        self.db = db
        self.rdb = rdb
        self.logger = LogCenter.instance().get_logger('conf', 'config-center')

    def _Get_Global_Config(self, namespace, method=None, *args, **kwargs):
        '''
        Handle all exceptions and return None while get config from global variable, db, file...
        :param namespace:  全局配置名称空间
        :param item: 配置名（名称空间内唯一）
        :param method: 取配置时调用方法的方法名（属于名称空间所绑定的某对象）
        :param args: 取配置时调用方法传参的参数元组
        :param kwargs: 其他参数
        :return: 未取到返回None
        '''
        res = None
        if namespace == "flask_app":
            res = flask_app.config.get(*args)
        elif namespace == "redis":
            method = method or 'get'  # default get
            # args must transmit in order as redis.Client method parameter
            try:
                try:
                    res = self.rdb.__getattr__(method)(*args)
                except AttributeError:
                    res = self.rdb.__getattribute__(method)(*args)
            except Exception as e:
                self.logger.error(repr(e))
                res = None
        elif namespace == "file":
            pass
        elif namespace == "environment":
            pass

        return res

    def _Set_Global_Config(self, namespace, method=None, *args, **kwargs):
        res = None
        if namespace == "redis":
            method = method or 'set'
            try:
                try:
                    res = self.rdb.__getattr__(method)(*args)
                except AttributeError:
                    res = self.rdb.__getattribute__(method)(*args)
            except Exception as e:
                self.logger.error(repr(e))
                res = None
        return res


@ThreadSafeSingleton
class Configurator(object):
    '''
    可作为消息发布者，向订阅配置的对象发布配置更新的消息
    '''
    TOPICS = (DOCKER_IMAGE_CONFIG.KEY, PLAN_PRICE_CONFIG.KEY, PLAN_CONFIG.KEY, BILL_CONFIG.KEY,
              PACKAGE_PRICE_CONFIG.KEY)

    def __init__(self):
        self.logger = LogCenter.instance().get_logger("conf", "configurator")
        self.cc = Config_Center.instance()
        # config改动后通知相关对象
        self.observers = {topic: [] for topic in self.TOPICS}
        # config各项
        self._DOCKER_IMAGE_CONFIG = DOCKER_IMAGE_CONFIG.as_dict
        self._PALN_CONFIG = PLAN_CONFIG.as_dict
        self._BILL_CONFIG = BILL_CONFIG.as_dict
        self._PLAN_PRICE_CONFIG = PLAN_PRICE_CONFIG.as_dict
        self._PACKAGE_PRICE_CONFIG = PACKAGE_PRICE_CONFIG.as_dict

    def add_observer(self, observer, topic):
        try:
            if observer not in self.observers[topic]:
                self.observers[topic].append(observer)
        except (KeyError, TypeError):
            return False

    def notify(self, data, topic):
        # 观察者需实现 notify 方法
        [o.notify(data) for o in self.observers[topic]]

    ######################################################################################################
    #                                       DOCKER_IMAGES part                                           #
    ######################################################################################################
    def get_docker_image_config(self):
        return self._DOCKER_IMAGE_CONFIG

    def set_docker_image_config(self, new_value):
        try:
            self._DOCKER_IMAGE_CONFIG = dict(new_value)
        except ValueError as e:
            self.logger.warning(str(e))
        else:
            # 通知更新全局对象的值
            self.notify(self._DOCKER_IMAGE_CONFIG, DOCKER_IMAGE_CONFIG.KEY)

    def Read_Docker_Image_Config(self):
        return DOCKER_IMAGE_CONFIG.adapter(
            self.cc._Get_Global_Config(DOCKER_IMAGE_CONFIG.NAMESPACE,
                                       Config_Model.TYPE_GET_FUNC_MAP[DOCKER_IMAGE_CONFIG.TYPE],
                                       DOCKER_IMAGE_CONFIG.KEY))

    def Update_Docker_Image_Config(self, env, key, tag):
        '''
        :param key: cpu/gpu
        :param env: environments name
        :param tag: image tag
        :return:
        '''
        r = self.cc._Set_Global_Config(DOCKER_IMAGE_CONFIG.NAMESPACE, "hset", DOCKER_IMAGE_CONFIG.KEY,
                                       key + DOCKER_IMAGE_CONFIG.DOCKER_ENV_SPLITTER + env,
                                       tag)
        if r is None:
            return False
        self.DOCKER_IMAGE_CONFIG = self.Read_Docker_Image_Config()
        return True

    def Remove_Docker_Image(self, env, keys):
        '''
        :param env:
        :param keys:
        :return:
        '''
        if isinstance(keys, basestring):
            keys = [keys]
        fields = [key + DOCKER_IMAGE_CONFIG.DOCKER_ENV_SPLITTER + env for key in keys if key]
        if not fields:
            return False
        r = self.cc._Set_Global_Config(DOCKER_IMAGE_CONFIG.NAMESPACE, "hdel", DOCKER_IMAGE_CONFIG.KEY, *fields)
        if r is None or int(r) != len(fields):
            # r的值为修改的field数, 不等于keys的长度时，说明有某（些）field删除失败
            self.DOCKER_IMAGE_CONFIG = self.Read_Docker_Image_Config()
            self.logger.warning("删除redis配置项可能（部分）失败，删除键： {}".format(fields))
            return False
        # 调用setter
        self.DOCKER_IMAGE_CONFIG = self.Read_Docker_Image_Config()
        return True

    ######################################################################################################
    #                                 PLAN_PRICE_CONFIG part                                             #
    ######################################################################################################
    def Update_Plan_Price_Config(self, plan_id, month, price):
        '''
        修改套餐价格配置
        :param plan_id: should be string, not int
        :param month: int, string accepted
        :param price: int, float accepted, string which is float-convertible also accepted
        :return:
        '''
        if isinstance(price, basestring):
            price = int(price)
        if isinstance(month, basestring):
            month = int(month)
        assert isinstance(month, int) and (isinstance(price, int) or isinstance(price, float))
        month = str(month)
        old = self.cc._Get_Global_Config(PLAN_PRICE_CONFIG.NAMESPACE, "get", PLAN_PRICE_CONFIG.KEY)
        if isinstance(old, str):
            updated = json.loads(old)
            updated[plan_id].update({month: price})
            updated = json.dumps(updated)
        else:
            return False
        r = self.cc._Set_Global_Config(PLAN_PRICE_CONFIG.NAMESPACE, "set", PLAN_PRICE_CONFIG.KEY, updated)
        if r is None:
            return False
        self.PLAN_PRICE_CONFIG = self.Read_Plan_Price_Config()
        return True

    def Read_Plan_Price_Config(self):
        return PLAN_PRICE_CONFIG.adapter(self.cc._Get_Global_Config(
            PLAN_PRICE_CONFIG.NAMESPACE,
            Config_Model.TYPE_GET_FUNC_MAP[PLAN_PRICE_CONFIG.TYPE],
            PLAN_PRICE_CONFIG.KEY
        ))

    def Remove_Plan_Price_Config(self, plan_id, keys=None):
        temp = self._PLAN_PRICE_CONFIG.copy()
        if plan_id not in temp:
            return False
        if keys is None or len(keys) == 0:
            # remove whole plan_id
            temp.pop(plan_id)
        else:
            [temp[plan_id].pop(key) for key in keys]
        removed = json.dumps(temp)
        r = self.cc._Set_Global_Config(PLAN_PRICE_CONFIG.NAMESPACE, "set", PLAN_PRICE_CONFIG.KEY, removed)
        if r is None:
            return False
        self.PLAN_PRICE_CONFIG = self.Read_Plan_Price_Config()
        return True

    def get_plan_price(self):
        return self._PLAN_PRICE_CONFIG

    def set_plan_price(self, new_value):
        try:
            self._PLAN_PRICE_CONFIG = dict(new_value)
        except ValueError as e:
            self.logger.warning(str(e))
        else:
            # 通知更新全局对象的值
            self.notify(self._PLAN_PRICE_CONFIG, PLAN_PRICE_CONFIG.KEY)

    ######################################################################################################
    #                                       PLAN_CONFIG part                                             #
    ######################################################################################################
    def Update_Plan_Config(self, plan_id, config):
        if not isinstance(config, dict):
            raise TypeError("plan config must be dict type")

        res = self.cc._Get_Global_Config(PLAN_CONFIG.NAMESPACE, "hget", PLAN_CONFIG.KEY, plan_id)
        if isinstance(res, basestring):
            try:
                updated = json.loads(res)
                updated.update(config)
                updated = json.dumps(updated)
            except TypeError:
                self.logger.warning(traceback.format_exc())
                return False
        elif res is None:
            # new plan_id
            updated = json.dumps(config)
        else:
            self.logger.warning("unexpected redis response: {}".format(res))
            return False
        r = self.cc._Set_Global_Config(PLAN_CONFIG.NAMESPACE, "hset", PLAN_CONFIG.KEY, plan_id, updated)
        if r is None:
            return False
        self.PLAN_CONFIG = self.Read_Plan_Config()
        return True

    def Read_Plan_Config(self):
        return PLAN_CONFIG.adapter(
            self.cc._Get_Global_Config(PLAN_CONFIG.NAMESPACE, Config_Model.TYPE_GET_FUNC_MAP[PLAN_CONFIG.TYPE],
                                       PLAN_CONFIG.KEY))

    def Remove_Plan_Config(self, plan_id, keys=None):
        if keys is None:
            # remove whole plan_id
            r = self.cc._Set_Global_Config(PLAN_CONFIG.NAMESPACE, "hdel", PLAN_CONFIG.KEY, plan_id)
            if r is None:
                return False
            self.PLAN_CONFIG = self.Read_Plan_Config()
            return True
        if isinstance(keys, basestring):
            keys = [keys]
        temp = self._PLAN_CONFIG.copy()
        [temp.pop(key) for key in keys]
        removed = json.dumps(temp)
        r = self.cc._Set_Global_Config(PLAN_CONFIG.NAMESPACE, "hset", PLAN_CONFIG.KEY, plan_id, removed)
        if r is None:
            return False
        self.PLAN_CONFIG = self.Read_Plan_Config()
        return True

    def get_plan_config(self):
        return self._PALN_CONFIG

    def set_plan_config(self, new_value):
        try:
            self._PLAN_CONFIG = dict(new_value)
        except ValueError as e:
            self.logger.warning(str(e))
        else:
            self.notify(self._PLAN_CONFIG, PLAN_CONFIG.KEY)

    ######################################################################################################
    #                                       PACKAGE_PRICE_CONFIG part                                    #
    ######################################################################################################
    def Update_Package_Price_Config(self, instance_type, hours, price_yuan):
        '''
        更新用量包的价格配置
        :param instance_type: 机型，目前支持 cpu/gpu
        :param hours: 小时数, int/string
        :param price_yuan: 价格，单位元, int, float accepted, string which is float-convertible also accepted
        :return:
        '''
        if isinstance(price_yuan, basestring):
            price_yuan = int(price_yuan)
        hours = str(hours)
        res = self.cc._Get_Global_Config(PACKAGE_PRICE_CONFIG.NAMESPACE, "get", PACKAGE_PRICE_CONFIG.KEY)
        if isinstance(res, basestring):
            try:
                config = json.loads(res)
                it_config = config.get(instance_type)
                if not it_config:
                    config[instance_type] = {hours: price_yuan}
                else:
                    it_config.update({hours: price_yuan})
                config.update({instance_type: it_config})
                updated = json.dumps(config)
            except TypeError:
                self.logger.warning(traceback.format_exc())
                return False
        elif res is None:
            # new instance type
            updated = json.dumps({instance_type: {hours: price_yuan}})
        else:
            self.logger.warning("unexpected redis response: {}".format(res))
            return False
        r = self.cc._Set_Global_Config(PACKAGE_PRICE_CONFIG.NAMESPACE, "set", PACKAGE_PRICE_CONFIG.KEY, updated)
        if r is None:
            return False
        self.PACKAGE_PRICE_CONFIG = self.Read_Package_Price_Config()
        return True

    def Remove_Package_Price_Config(self, instance_type, hours):
        '''

        :param instance_type:
        :param hours: should be string
        :return:
        '''
        hours = str(hours)
        res = self.cc._Get_Global_Config(PACKAGE_PRICE_CONFIG.NAMESPACE, "get", PACKAGE_PRICE_CONFIG.KEY)
        if isinstance(res, basestring):
            try:
                config = json.loads(res)
                it_config = config.get(instance_type)
                if not it_config:
                    if instance_type in config:
                        config.pop(instance_type)
                    else:
                        return False
                else:
                    if hours in it_config:
                        it_config.pop(hours)
                    else:
                        # non existed
                        return False
                    config.update({instance_type: it_config})
                updated = json.dumps(config)
            except TypeError:
                self.logger.warning(traceback.format_exc())
                return False
        elif res is None:
            self.logger.warning("package price config not found in redis")
            return False
        else:
            self.logger.warning("unexpected redis response: {}".format(res))
            return False
        r = self.cc._Set_Global_Config(PACKAGE_PRICE_CONFIG.NAMESPACE, "set", PACKAGE_PRICE_CONFIG.KEY, updated)
        if r is None:
            return False
        self.PACKAGE_PRICE_CONFIG = self.Read_Package_Price_Config()
        return True

    def Read_Package_Price_Config(self):
        return PACKAGE_PRICE_CONFIG.adapter(
            self.cc._Get_Global_Config(PACKAGE_PRICE_CONFIG.NAMESPACE,
                                       Config_Model.TYPE_GET_FUNC_MAP[PACKAGE_PRICE_CONFIG.TYPE],
                                       PACKAGE_PRICE_CONFIG.KEY))

    def get_package_price_config(self):
        return self._PACKAGE_PRICE_CONFIG

    def set_package_price_config(self, new_value):
        try:
            self._PACKAGE_PRICE_CONFIG = dict(new_value)
        except ValueError as e:
            self.logger.warning(str(e))
        else:
            self.notify(self._PACKAGE_PRICE_CONFIG, PACKAGE_PRICE_CONFIG.KEY)

    ######################################################################################################
    #                                       BILL_CONFIG part                                    #
    ######################################################################################################
    def get_bill_config(self):
        return self._BILL_CONFIG

    def set_bill_config(self, new_value):
        try:
            self._BILL_CONFIG = dict(new_value)
        except ValueError as e:
            self.logger.warning(str(e))
        else:
            self.notify(self._BILL_CONFIG, BILL_CONFIG.KEY)

    def Read_Bill_Config(self):
        return BILL_CONFIG.adapter(
            self.cc._Get_Global_Config(BILL_CONFIG.NAMESPACE,
                                       Config_Model.TYPE_GET_FUNC_MAP[BILL_CONFIG.TYPE],
                                       BILL_CONFIG.KEY))

    def Remove_Bill_Config(self, plan_id, instance_types):
        if isinstance(instance_types, basestring):
            instance_types = [instance_types]
        temp = self._BILL_CONFIG.copy()
        [temp.pop(instance_type) for instance_type in instance_types]
        removed = json.dumps(temp)
        r = self.cc._Set_Global_Config(BILL_CONFIG.NAMESPACE, "hset", BILL_CONFIG.KEY, plan_id, removed)
        if r is None:
            return False
        self.BILL_CONFIG = self.Read_Bill_Config()
        return True

    def Update_Bill_Config(self, plan_id, k, v):
        '''
        更新账单价格配置
        :param plan_id:
        :param k: cpu/gpu, must be string
        :param v: 1元/小时 表示为：{price: 100, price_scale: 1, time_scale: 3600}
           price: int, float accepted, string which is float-convertible also accepted
           price_scale: int, float accepted, string which is float-convertible also accepted
           time_scale: int, float accepted, string which is float-convertible also accepted
        :return:
        '''
        assert isinstance(k, basestring)
        if not (isinstance(v, dict) and "price" in v):
            raise TypeError("bill config must be dict type, and has 'price' key")
        # default scale
        v["price"] = int(v["price"])
        if "price_scale" not in v:
            v["price_scale"] = 1
        else:
            v["price_scale"] = int(v["price_scale"])
        if "time_scale" not in v:
            v["time_scale"] = 3600
        else:
            v["time_scale"] = int(v["time_scale"])
        res = self.cc._Get_Global_Config(BILL_CONFIG.NAMESPACE, "hget", BILL_CONFIG.KEY, plan_id)
        if isinstance(res, basestring):
            try:
                updated = json.loads(res)
                updated.update({k: v})
                updated = json.dumps(updated)
            except TypeError:
                self.logger.warning(traceback.format_exc())
                return False
        elif res is None:
            # new plan_id
            updated = json.dumps({k: v})
        else:
            self.logger.warning("unexpected redis response: {}".format(res))
            return False
        r = self.cc._Set_Global_Config(BILL_CONFIG.NAMESPACE, "hset", BILL_CONFIG.KEY, plan_id, updated)
        if r is None:
            return False
        self.BILL_CONFIG = self.Read_Bill_Config()
        return True

    ################### property #################
    DOCKER_IMAGE_CONFIG = property(get_docker_image_config, set_docker_image_config)
    BILL_CONFIG = property(get_bill_config, set_bill_config)
    PACKAGE_PRICE_CONFIG = property(get_package_price_config, set_package_price_config)
    PLAN_CONFIG = property(get_plan_config, set_plan_config)
    PLAN_PRICE_CONFIG = property(get_plan_price, set_plan_price)
