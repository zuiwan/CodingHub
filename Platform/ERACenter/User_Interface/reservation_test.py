#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       test
   Description:
   Author:          huangzhen
   date:            2018/4/1
-------------------------------------------------
   Change Activity:
                   2018/4/1:
-------------------------------------------------
"""
__author__ = 'huangzhen'
import time
from datetime import (
    datetime,
    timedelta
)
import traceback
import sys
import json

sys.path.append(".")
sys.path.append("..")
from Platform.ERACenter.Core.model import JobReq, Job
from Platform.ERACenter.User_Interface.user import Reservation_Center
from Platform.ERACenter.Core.model import Module
from Library.extensions import rdb
from Library.Utils import time_util


def reserve_loooop():
    minutes = 1
    VALUE = 1798
    while True:
        rc = Reservation_Center()
        try:
            now = datetime.utcnow()
            res = {
                "cputype": "i5",
                "cpunum": 5,
                "gputype": "titan",
                "gpunum": 1,
                "memtype": "ddr3",
                "memnum": 7,
                "framework": "tensorflow"
            }
            jobReq = JobReq(job_id="1", duration=100,
                            tw_start=now, tw_end=now + timedelta(minutes=minutes),
                            value=VALUE, resources=res)
            # print("debug, model, jobReq.id: %s" % jobReq.id)
            minutes += 1
            resp = rc.makeReservation(jobReq)
            # print("debug", resp)
            # "0001-01-01T00:00:00Z"
            if resp["accepted"] is True:
                print("Arrival time: %s" % time_util.string_toDatetime(resp["arrival_time"]))
                time.sleep(10)
            else:
                # global VALUE
                print("rejected, your bidding price is: %d" % VALUE)
                VALUE += 100
                continue
        except Exception as e:
            print(traceback.format_exc())
            continue


def Create_Job(id, env, uid, gid, doc, duration, project_id, code_id, data_ids, entry_cmd, start_cmd,
               b_tensorboard, b_jupyter, perm):
    job = Job(env=env, uid=uid, gid=gid, doc=doc, duration=duration, project_id=project_id, code_id=code_id,
              data_ids=data_ids,
              entry_cmd=entry_cmd,
              start_cmd=start_cmd,
              b_tensorboard=b_tensorboard, b_jupyter=b_jupyter, perm=perm)
    job.id = id
    print("create job, id: %s" % job.id)
    rdb.set(id, json.dumps(job.to_dict()))
    return job


def createJob():
    # env format
    '''
    type Environment struct {
        DlFrName    string `json:"dl_fr"`
        Os      string       `json:"os"` // 操作系统
        WithGpu bool         `json:"with_gpu"`
    }
    '''
    for jobid in range(10):
        env = {
            "dl_fr_name": "tensorflow-1.5:py2",
            "os": "ubuntu16",
            "with_gpu": False
        }
        # uid, code_id均指向Rus测试环境数据
        Create_Job(id=str(jobid), env=env, duration=10000, uid="e2500321e4f2411890cd6bbd1ce7b45c", gid="1",
                   doc="test{}".format(jobid),
                   project_id="1", code_id="5e2cd0464abb4e96aa7405e39f703654",
                   data_ids=["1,"],
                   entry_cmd="python main.py",
                   start_cmd="", b_tensorboard=False, b_jupyter=True, perm=0)


if __name__ == "__main__":
    createJob()
    reserve_loooop()
