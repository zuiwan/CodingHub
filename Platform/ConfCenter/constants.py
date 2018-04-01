#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       aliyun_docker
   Description:
   Author:          huangzhen
   date:            2018/3/10
-------------------------------------------------
   Change Activity:
                   2018/3/10:
-------------------------------------------------
"""

__author__ = 'huangzhen'
# 主要使用redis持久化存储各项配置信息
# 项目启动时从redis中加载到内存

from models import (
    Docker_Image_Config,
    Bill_Config,
    Package_Price_Config,
    Plan_Price_Config,
    Plan_Config
)

# 确保线程安全的全局性
DOCKER_IMAGE_CONFIG = Docker_Image_Config.instance()
BILL_CONFIG = Bill_Config.instance()
PACKAGE_PRICE_CONFIG = Package_Price_Config.instance()
PLAN_PRICE_CONFIG = Plan_Price_Config.instance()
PLAN_CONFIG = Plan_Config.instance()

# DOCKER_PRE = "registry.cn-shanghai.aliyuncs.com/russellcloud/"
DOCKER_PRE = "registry-vpc.cn-shanghai.aliyuncs.com/russellcloud/"

NOT_SUPPORT_JUPYTER_LIST = ['caffe']
SUPPORT_TENSORBOARD_LIST = ['tensorflow-1.4', 'tensorflow-1.4:py2']

