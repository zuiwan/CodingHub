#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       celery_config
   Description:
   Author:          huangzhen
   date:            2018/4/6
-------------------------------------------------
   Change Activity:
                   2018/4/6:
-------------------------------------------------
"""
__author__ = 'huangzhen'

from kombu import Queue

# from datetime import timedelta
# from celery.schedules import crontab

celery_queues = (
    Queue('eracompute', exchange='eracompute', routing_key='task.eracompute'),
    Queue('eagerjob', exchange='eagerjob', routing_key='task.eagerjob'),
)

timezone = 'Asia/Shanghai'
# CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_ALWAYS_EAGER = True

# task_acks_late = True
# worker_prefetch_multiplier = 1
#
# beat_schedule = {
#     # 'perhalfhour': {
#     #     'task': 'App.aliyun_api.is_healthy',
#     #     'schedule': 30 * 60,
#     #     'args': ('1min',),
#     #     'options': {'queue': 'sys'}
#     # },
#     'perday': {
#         'task': 'App.aliyun_api.check_plan',
#         'schedule': crontab(hour=0, minute=0),
#         'args': ('PLAN CHECK',),
#         'options': {'queue': 'sys'}
#     },
#     # 'perhour': {
#     #     'task': 'App.aliyun_api.healthy_check',
#     #     'schedule': timedelta(hours=1),
#     #     'args': ('HEALTHY CHECK',),
#     #     'options': {'queue': 'sys'}
#     # },
#     'permin': {
#         'task': 'App.aliyun_api.notify',
#         'schedule': timedelta(minutes=1),
#         'args': ('SEND NOTIFY',),
#         'options': {'queue': 'sys'}
#     },
#     'per5min': {
#         'task': 'App.aliyun_api.cluster_stat',
#         'schedule': timedelta(minutes=5),
#         'args': ('CLUSTER STAT',),
#         'options': {'queue': 'sys'}
#     },
#     'scale_in_check_permin': {
#         'task': 'App.aliyun_api.auto_scale_in_check',
#         'schedule': timedelta(minutes=1),
#         'options': {'queue': 'sys'}
#     },
#     'arrears': {
#         'task': 'App.aliyun_api.arrears_notify',
#         'schedule': crontab(hour=0, minute=0),
#         'args': ('SEND ARREARS NOTIFY',),
#         'options': {'queue': 'sys'}
#     },
#     'nfs_clear_perday': {
#         'task': 'App.aliyun_api.clear_task',
#         # 'schedule': timedelta(minutes=1),
#         'schedule': crontab(hour=16, minute=0),
#         'options': {'queue': 'sys'}
#     },
#     # 'perhour': {
#     #     'task': 'App.aliyun_api.recycle_experiments',
#     #     'schedule': 1 * 3600,
#     #     'args': ('EXPERIMENTS STATE CHECK',),
#     #     'options': {'queue': 'sys'}
#     # }
# }
# CELERYBEAT_SCHEDULE = {
#     'perminute': {
#         'task': 'App.aliyun_api.check_plan',
#         'schedule': timedelta(seconds=5),
#         'args': (1, 2)
#     }
# }
# CELERY_ROUTES = {
#     'App.celery_api.forkProject': {
#         'queue': 'file',
#         'routing_key': 'task.user.file.#'
#     },
# }
