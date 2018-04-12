#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import izip

from pytz import timezone
from enum import Enum

PST_TIMEZONE = timezone("America/Los_Angeles")

CPU_INSTANCE_TYPE = "cpu"
GPU_INSTANCE_TYPE = "gpu"

# numerical value
SQL_LIMIT_HIGH = 18446744073709551615L

# text
k_email_subject_verify_code = 'Russellcloud验证码: {code}'
k_email_body_verify_code = '''您的验证码为 {code} ，感谢您使用 Russellcloud 的 服务。<br> [Russellcloud]'''
k_email_subject_forget_password = "您的验证码为：{code}"
k_email_body_forget_password = "您的验证码为：{code}"

routing_dict = {GPU_INSTANCE_TYPE: 'task.user.compute.gpu', CPU_INSTANCE_TYPE: 'task.user.compute.cpu'}
queue_dict = {GPU_INSTANCE_TYPE: 'gpu', CPU_INSTANCE_TYPE: 'cpu'}

k_log_output_1 = "Task submitted successfully, queued for processing"
k_log_output_2 = "Task start to be executed..."
k_log_output_6 = "data_volume create successfully, data_id: {}, mount dir: {}"
k_log_output_9 = "Waiting for Task to complete ~"
k_log_output_10 = "Export output dir to create new dataset : ************"

# SERVER_CONFIG_MAP = dict(
#     master=dict(
#         jupyter_url_g="http://gpu.russellcloud.com/notebook/",
#         jupyter_url_c="http://cpu.russellcloud.com/notebook/",
#         tensorboard_url_c="http://cpu.russellcloud.com/tensorboard/",
#         tensorboard_url_g="http://gpu.russellcloud.com/tensorboard/",
#         nfs_host_g="387794b016-gep85.cn-shanghai.nas.aliyuncs.com",
#         nfs_host_c="387794b016-tnq38.cn-shanghai.nas.aliyuncs.com",
#         disk_id="387794b016",
#     ),
#     test=dict(
#         jupyter_url_g="http://gpu.russellcloud.com/notebook/",
#         jupyter_url_c="http://cpu.russellcloud.com/notebook/",
#         tensorboard_url_c="http://cpu.russellcloud.com/tensorboard/",
#         tensorboard_url_g="http://gpu.russellcloud.com/tensorboard/",
#         nfs_host_g="369e84a816-qtg85.cn-shanghai.nas.aliyuncs.com",
#         nfs_host_c="369e84a816-qka26.cn-shanghai.nas.aliyuncs.com",
#         disk_id="369e84a816",
#     )
# )
SERVER_CONFIG_MAP = dict(
    master=dict(
        jupyter_url_g="http://gpu.russellcloud.com/notebook/",
        jupyter_url_c="http://cpu.russellcloud.com/notebook/",
        tensorboard_url_c="http://cpu.russellcloud.com/tensorboard/",
        tensorboard_url_g="http://gpu.russellcloud.com/tensorboard/",
        r_nfs_host_g="387794b016-gep85.cn-shanghai.nas.aliyuncs.com",
        r_nfs_host_c="387794b016-tnq38.cn-shanghai.nas.aliyuncs.com",
        rw_nfs_host_g="3d9934935b-yyr73.cn-shanghai.nas.aliyuncs.com",
        rw_nfs_host_c="3d9934935b-jxm82.cn-shanghai.nas.aliyuncs.com",
        r_disk_id="387794b016",
        rw_disk_id="3d9934935b",
    ),
    test=dict(
        jupyter_url_g="http://gpu.russellcloud.com/notebook/",
        jupyter_url_c="http://cpu.russellcloud.com/notebook/",
        tensorboard_url_c="http://cpu.russellcloud.com/tensorboard/",
        tensorboard_url_g="http://gpu.russellcloud.com/tensorboard/",
        r_nfs_host_g="369e84a816-qtg85.cn-shanghai.nas.aliyuncs.com",
        r_nfs_host_c="369e84a816-qka26.cn-shanghai.nas.aliyuncs.com",
        rw_nfs_host_g="318334978e-eap26.cn-shanghai.nas.aliyuncs.com",
        rw_nfs_host_c="318334978e-phh35.cn-shanghai.nas.aliyuncs.com",
        r_disk_id="369e84a816",
        rw_disk_id="318334978e",
    )
)
CPU_CLUSTER_EXPECT_SIZE = "cpu_cluster_expect_size"
GPU_CLUSTER_EXPECT_SIZE = "gpu_cluster_expect_size"
MACHINE_LIST = "machine_list"
USER_ARREARS_DATE_HSET = 'arrears_latest_date'
USER_ARREARS_COUNT_HSET = 'arrears_count'
TASK_ARREARS_LOG = 'task_arrears_log'
TASK_LOG_SIZE_HSET = 'task_log_size'
TASK_LOG_UPDATE_HSET = 'task_log_update'

# INFLUXDB_INTERFACE
# for aliyun.label to make influxdb watch the machine
# saved on redis, which should be a dict(string or hash) like this:
# {CLUSTER_ID: {LIP: "192.168.1.1:8086", EIP: "106.15.199.156:8086" [, PORT: 8086]}
INFLUXDB_INTERFACE = "influxdb_interface"

DEFAULT_AVATAR = 'default_avatar.png'

RUSSELL_HOST = "http://dl.russellcloud.com"
RUSSELL_WEB_HOST = "http://russellcloud.com"

RUSSELL_CPU_HOST = "http://cpu.russellcloud.com"
RUSSELL_GPU_HOST = "http://gpu.russellcloud.com"

RUSSELL_FS_HOST = "fs.russellcloud.com"

# nas挂载目录
WORKSPACE_DIR = "/root/workspace"

## state

TASK_STATE = Enum("TASK_STATE", "waiting starting running timeout failed finished stopped")
TASK_STATE_CN_TUPLE = ("等待中", "启动中", "运行中", "已超时", "已失败", "已结束", "已关闭")
TASK_SYSTEM_STOP = ('arrears', 'forgot', 'manual')

CPU_CLUSTER_ID = 'c4e9436b8530e4d739970e94943b18d9f'
GPU_CLUSTER_ID = 'c13208a667ad14e048ec10b3818a60470'
CLUSTER_TYPE = {
    GPU_CLUSTER_ID: 'gpu',
    CPU_CLUSTER_ID: 'cpu'
}
CLUSTER_ID_MAP = dict(izip(CLUSTER_TYPE.itervalues(), CLUSTER_TYPE.iterkeys()))
SCALE_TRIGGER_URL = {
    'cpu': 'https://cs.console.aliyun.com/hook/trigger?triggerUrl=YzRlOTQzNmI4NTMwZTRkNzM5OTcwZTk0OTQzYjE4ZDlmfHxub2RlX3NjYWxpbmd8MWEzMzRodDVvODA5bHw=&secret=765741667472533370526f536e54376c0319602d53a4c1e25e45fa26a471bf40',
    'gpu': 'https://cs.console.aliyun.com/hook/trigger?triggerUrl=YzEzMjA4YTY2N2FkMTRlMDQ4ZWMxMGIzODE4YTYwNDcwfHxub2RlX3NjYWxpbmd8MWE0N2hoM2pvZ2FhMnw=&secret=6966436a564c4366444961644645584b61ffe24752ccbfd7ce880a59a84328b3'
}
ACCESSKEY_ID = 'LTAIpdP2r7mjUMhW'
ACCESSKEY_SECRET = 'gQqrOPmvG9NLZjRMM9cWgNBGW1TPRl'
REGION_ID = 'cn-shanghai'
SSH_PASSWORD = "RussellCloud2017"
