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
from Library.extensions import (
    rdb as redisClient,
)
from aliyun_docker.utils import Get_Job, Write_Job_Log
from aliyun_docker.application_impl import Application
from celery import Celery

Accepted_Queue = redisClient.pubsub()


def make_celery_app():
    app = Celery('Platform.ERACenter.Cloud_Interface.cloud', broker='redis://localhost:6379')
    return app


celery_app = make_celery_app()


def initSubscribe():
    CHANNEL = "era_accepted_queue"
    # Accepted_Queue =   # bind listen instance
    Accepted_Queue.subscribe(CHANNEL)


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
            '''
            type Allocation struct {
                JobId     ID             `json:"job_id"`
                Resources *Resource_List `json:"resources"`
                TStart    time.Time      `json:"t_start"`
                TEnd      time.Time      `json:"t_end"`
            }
            '''
            # task = Do_Job.apply_async(args=[data["job_id"], ])
            task = Do_Job.delay(data["job_id"])
            print("Apply job, apply id: %s, state: %s\n++++++++++++++++++++++++++++++++++" %
                  (task.id, getattr(task, "state", "FAILURE")))
        else:
            print("unexpected resp type: {}".format(resp))
        time.sleep(10)

import traceback
@celery_app.task
def Do_Job(job_id):
    # 对于未到调度时间的作业，在此处休眠
    print("+++++++++++++++++++++++++++")
    try:
        aliyun_app = Application(job_id=job_id,
                                 time_limit=172800)
    except Exception as e:
        Write_Job_Log(job_id, traceback.format_exc(), "DEBUG")
        Write_Job_Log(job_id, str(e), "ERROR")
        return False
    try:
        ok = aliyun_app.Run()
    except Exception as e:
        Write_Job_Log(job_id, str(e), "ERROR")
        return False
    else:
        return ok


if __name__ == "__main__":
    initSubscribe()
    Get_Current_Allocation()
