#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       cloud
   Description:
   Author:          huangzhen
   date:            2018/3/13
-------------------------------------------------
   Change Activity:
                   2018/3/13:
-------------------------------------------------
"""
__author__ = 'huangzhen'
import sys

sys.path.append(".")
import time
import json
import traceback
from Library.extensions import (
    rdb as redisClient,
)
from Library.Utils import time_util
from aliyun_docker.utils import Write_Job_Log
from aliyun_docker.application_impl import Application
from celery import Celery


def make_celery_app():
    app = Celery('Platform.ERACenter.Cloud_Interface.cloud', broker='redis://localhost:6380')
    return app


celery_app = make_celery_app()

CHANNEL = "era_accepted_queue"
LOOP_INTERVAL = 3
normalization_coefficient = (9 - 0) / (4294967295 - 0)  # uint32值到[0,9]的归一化系数
Accepted_Queue = redisClient.pubsub()


def initSubscribe():
    Accepted_Queue.subscribe(CHANNEL)


def getCurrentAllocation():
    # 支持更多的celery调用参数：持续优化
    for item in Accepted_Queue.listen():
        resp = item["data"]  # get channel message
        if resp == 1L:
            continue  # blank message
        else:
            try:
                data = json.loads(redisClient.get(str(resp)))  # transfer data type
            except Exception as e:
                print("get allocation detail failed, reason: {}".format(str(e)))
                continue
            Do_Job.delay(args=[data["job_id"]],
                         eta=time_util.string_toDatetime(data["arrival_time"]),
                         priority=0 + normalization_coefficient * (data["accepted_value"] - 0))
            time.sleep(LOOP_INTERVAL)


def Get_Current_Allocation():
    for item in Accepted_Queue.listen():
        resp = item["data"]  # default 1L
        if resp == 1L:
            continue
        elif isinstance(resp, basestring):
            try:
                data = json.loads(resp)  # waiting for the publisher
                assert "job_id" in data
            except Exception as e:
                print("error", str(e), "resp is: {}".format(resp))
                continue
            task = Do_Job.delay(data["job_id"])
            print("Apply job, apply id: %s, state: %s\n++++++++++++++++++++++++++++++++++" %
                  (task.id, getattr(task, "state")))
        else:
            print("unexpected resp type: {}".format(resp))
        time.sleep(LOOP_INTERVAL)


@celery_app.task
def Do_Job(job_id):
    try:
        aliyun_app = Application(job_id=job_id)
    except Exception as e:
        Write_Job_Log(job_id, traceback.format_exc(), "DEBUG")
        Write_Job_Log(job_id, "Init aliyun application failed, reason: %s" % str(e), "ERROR")
        return False
    try:
        ok = aliyun_app.Run()
    except Exception as e:
        Write_Job_Log(job_id, "Run aliyun application failed, reason: %s" % str(e), "ERROR")
        Write_Job_Log(job_id, traceback.format_exc(), "DEBUG")
        return False
    else:
        return ok


if __name__ == "__main__":
    initSubscribe()
    Get_Current_Allocation()
