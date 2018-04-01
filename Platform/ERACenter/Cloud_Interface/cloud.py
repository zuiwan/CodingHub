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
import time
from Platform.ERACenter.Cloud_Interface import redisClient

CHANNEL = "era_accepted_queue"
Accepted_Queue = redisClient.r.pubsub()  # bind listen instance
Accepted_Queue.subscribe(CHANNEL)

import json
from aliyun_docker.utils import Get_Job, Write_Job_Log

from aliyun_docker.application_impl import Application


def Get_Current_Allocation():
    while True:
        data = json.loads(Accepted_Queue.parse_response())  # waiting for the publisher
        '''
        type Allocation struct {
            JobId     ID             `json:"job_id"`
            Resources *Resource_List `json:"resources"`
            TStart    time.Time      `json:"t_start"`
            TEnd      time.Time      `json:"t_end"`
        }
        '''
        print(time.time(), data)
        jobSpec = Get_Job(id=data["job_id"])
        Do_Job(jobSpec)


def Do_Job(job):
    try:
        aliyun_app = Application(job_id=job.id,
                                 time_limit=None)
    except Exception as e:
        Write_Job_Log(job.id, str(e), "ERROR")
        return False
    try:
        ok = aliyun_app.Run()
    except Exception as e:
        Write_Job_Log(job.id, str(e), "ERROR")
        return False
    else:
        return ok
