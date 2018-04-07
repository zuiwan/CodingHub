#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.append("..")
sys.path.append(".")
import json
from Library.extensions import rdb

# ######### 集群资源限制配置开始 ###########
# 参数指标大小单位配置，参考https://docs.docker.com/engine/reference/run/#specify-an-init-process

MACHINE_RESOURCE_QUEUE_REDIS_KEY_PREFIX = "machine_resource_queue_"
MACHINE_SCALING_FLAG_REDIS_KEY = "machine_scaling_flag"
DOCKER_COMPOSE_MEMORY_LIMIT_KEY = "mem_limit"
MACHINE_RESOURCE_LIMIT_REDIS_KEY = "machine_resource_limit"
DEFAULT_MACHINE_RESOURCE_LIMIT = {
    "gpu_high": {"memory": "28g", "concurrency": 1},  # 当前型号GPU机器最多运行1个任务
    "cpu_high": {"memory": "7g", "concurrency": 2}
}
machine_resource_limit = rdb.get(MACHINE_RESOURCE_LIMIT_REDIS_KEY)
if not machine_resource_limit:
    machine_resource_limit = DEFAULT_MACHINE_RESOURCE_LIMIT
else:
    machine_resource_limit = json.loads(machine_resource_limit)
