#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     utils
   Description :
   Author :       huangzhen
   date：          2018/1/2
-------------------------------------------------
   Change Activity:
                   2018/1/2:
-------------------------------------------------
"""
__author__ = 'huangzhen'
import requests
from Platform.ERACenter.Core.model import Job
from sqlalchemy import and_
from Library.Utils.log_util import LogCenter
import json
from Library.extensions import rdb
import traceback

experiment_controler_logger = LogCenter.instance().get_logger('era', 'utils')
from Library import ErrorDefine as ED
from constants import (
    INFLUXDB_INTERFACE,

)
from Library.Utils import file_util
from Platform.ERACenter.Cloud_Interface.aliyun_docker.constants import CLUSTER_ID_MAP
from Application.app import flask_app
import time


def Celery_Log_Line(log_str, level="INFO"):
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    line = "[{}] [{}] | {}\n".format(current_time, level, log_str)
    return line


def Write_Job_Log(job_id, log_str, level='INFO'):
    log_path = ''.join((flask_app.config['UPLOAD_LOG_FOLDER'], job_id, "/worker.log"))
    line = Celery_Log_Line(log_str, level)
    file_util.write_file(line, log_path)
    pass


def Get_User(**find_by):
    pass


def Get_Code_Module(**find_by):
    pass


def Get_Job(**find_by):
    '''
    临时：使用redis
    :param find_by:
    :return:
    '''
    _id = find_by.get("id")
    # job = Job.query.filter(and_(Job.id == _id)).one()
    try:
        job = json.loads(rdb.get(str(_id)))
    except Exception as e:
        print("error", str(e))
        experiment_controler_logger.error(traceback.format_exc())
        return None
    print("debug", job)
    return Job.from_dict(job)


G_InfluxDB_Session = requests.session()


class Influxdb_Controler(object):
    '''
    使用requests库，完成Influxdb应用数据库查询接口的封装
    '''

    class IC_Exception(Exception):
        def __init__(self, msg):
            self.msg = msg

    influxdb_api_uri_cache = {}
    measurements_dict = {"docker_container_cpu": ("usage_percent",),
                         "docker_container_mem": ("usage", "usage_percent"),
                         "docker_container_net": ("rx_bytes", "rx_bytes_increment", "rx_rate",
                                                  "tx_bytes", "tx_bytes_increment", "tx_rate"),
                         }

    @staticmethod
    def get_influxdb_api_uri(cluster_id, ip_type="LIP", from_cache=False):
        '''
        获取访问INFLUXDB应用所在节点的ip地址和端口
        :param cluster_id:
        :param ip_type:  "LIP": 局域网IP; "EIP": 弹性公网IP
        :param from_cache: True 从类属性中获取； False: 读redis并更新类属性
        （注：一般由aliyun_docker部分代码以非cache方式调用该函数，其他部分以cache方式调用）
        :return:
            "<ip:port>"
        '''
        if ip_type not in ("LIP", "EIP"):
            return None
        try:
            if from_cache is True and Influxdb_Controler.influxdb_api_uri_cache:
                result = Influxdb_Controler.influxdb_api_uri_cache
            else:
                result = json.loads(rdb.get(INFLUXDB_INTERFACE))
                Influxdb_Controler.influxdb_api_uri_cache.update(result)
            return result[cluster_id][ip_type]
        except Exception as e:
            experiment_controler_logger.warning(str(e))
            return None

    @staticmethod
    def sql_select_string(sql, where=None, limit=None, order=None, group=None):
        if where is not None and len(where) > 0:
            if isinstance(where, list) or isinstance(where, tuple):
                where = " AND ".join(where)
            sql += " WHERE %s" % where
        if group is not None and len(group) > 0:
            if isinstance(group, list) or isinstance(where, tuple):
                group_sql = ""
                for group_item in group:
                    group_sql += "%s, " % group_item
                sql += " GROUP BY %s" % group_sql.rstrip(', ')
            else:
                sql += " GROUP BY %s" % group
        if limit is not None and len(str(limit)) > 0:
            sql += " LIMIT %s" % str(limit)
        return sql

    @staticmethod
    def sql_select(measurements, keys=None, agg_func=None, where=None, limit=None, order=None, group=None):
        if keys is None:
            select_keys = '*'
        else:
            select_keys = ""
            for key in keys:
                select_keys = "%s%s, " % (select_keys,
                                          agg_func + "(" + key + ")" + " AS " + key + "_%s" % agg_func if agg_func else key)
        sql = "SELECT %s FROM %s" % (select_keys.rstrip(', '), ','.join(measurements))
        return Influxdb_Controler.sql_select_string(sql, where, limit, order, group)

    def __init__(self, exp_id=None, cached_exp=None):
        '''
        :param cluster_id:
        '''
        if cached_exp is not None:
            exp = cached_exp
        else:
            exp = Get_Job(id=exp_id)
        if not exp:
            raise self.IC_Exception("Experiment param error or not found")
        self.aliyun_project_id = exp.app_name
        cluster_id = CLUSTER_ID_MAP[exp.instance_type_trimmed]
        self.db_endpoint = self.get_influxdb_api_uri(cluster_id, ip_type="EIP", from_cache=True)
        if not self.db_endpoint:
            raise self.IC_Exception("Get influxdb api uri failed")

    @staticmethod
    def parse_influxdb_response(response):
        try:
            code, results = response.status_code, response.json()["results"]
        except (AttributeError, KeyError) as e:
            experiment_controler_logger.error("error influxdb response: {}".format(response.content))
            raise e
        if code != 200:
            experiment_controler_logger.warning(traceback.format_exc())
            raise requests.HTTPError("Error HTTP Status Code")
        return results

    def gen_query_string(self, measurements, keys, t_s, t_e, interval, agg_func):
        '''
        根据入参生成查询语句字符串
        :param measurements: list or tuple
        :param keys: list or tuple
        :param t_s: 开始时间， '2015-08-18T00:00:00Z' 或者 None
        :param t_e: 结束时间，格式同上
        :param interval: 用于group by的时间，"1d" "1h" "1m" "1s" None
        :param agg_func: 聚合函数，"mean"等
        :return:
        '''
        # todo: check keys if legal
        # for key in keys:
        #     pass

        where_condition = ("aliyun_project_id = '%s'" % self.aliyun_project_id,
                           "time >= {}".format("'" + t_s + "'" if t_s else "now() - 1d"),
                           "time < {}".format("'" + t_e + "'" if t_e else "now()"))

        sql = Influxdb_Controler.sql_select(measurements=measurements,
                                            keys=keys,
                                            agg_func=agg_func or "mean",
                                            where=where_condition,
                                            limit=None,
                                            order=None,
                                            group=("time(%s)" % (interval or "1h"),))
        return sql

    def _execute(self, query_string, db="telegraf"):
        try:
            results = self.parse_influxdb_response(
                G_InfluxDB_Session.get(url="http://" + self.db_endpoint + "/query",
                                       params={"q": query_string,
                                               "db": db}))
        except requests.RequestException:
            experiment_controler_logger.warning(traceback.format_exc())
            code, results = ED.err_sys, None
        except Exception as e:
            experiment_controler_logger.warning("{}, influxdb query string: {}".format(str(e), query_string))
            code, results = ED.err_sys, None
        else:
            code = ED.no_err
        return code, results

    def Query(self, measurements, keys, t_s=None, t_e=None, interval=None, agg_func=None):
        sql = self.gen_query_string(measurements, keys, t_s, t_e, interval, agg_func)
        return self._execute(sql)
