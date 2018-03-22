#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       service
   Description:
   Author:          huangzhen
   date:            2018/3/13
-------------------------------------------------
   Change Activity:
                   2018/3/13:
-------------------------------------------------
"""
__author__ = 'huangzhen'

import docker
import os

class Service:
    # 创建实例
    def __init__(self):
        self.client = docker.from_env()
        # self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        # self.client = docker.DockerClient(base_url='tcp://127.0.0.1:1234')
        self.service = ''

    # 服务列表
    def list(self):
        # print self.client.services.list()
        return self.client.services.list()

    # 获取服务
    def get(self, id):
        self.service = self.client.services.get(id)
        # print self.service
        return self.service

    # 创建服务
    def create(self, image, name, source, target, task_id=None, port=None, constraints=None, command=None, workdir=None,
               run_mode='cli'):

        if run_mode == 'jupyter':
            command = 'echo \"jupyter notebook --NotebookApp.token= --NotebookApp.base_url={}\" > jupyter.sh && bash jupyter.sh'.format(task_id)

        if os.path.isfile(source+"/russell_requirements.txt"):
            pre_command = "pip install -r russell_requirements.txt"
            command = 'sh -c \'{}&&{}\''.format(pre_command, command)
        else:
            command = 'sh -c \'{}\''.format(command)

        if run_mode == 'cli':
            self.service = self.client.services. \
                create(image,
                       name=name,
                       mounts=['{}:{}'.format(source, target)],
                       constraints=constraints,
                       command=command,
                       workdir=workdir,
                       )
            # print self.service.id
            return self.service.id


        elif run_mode == 'jupyter':
            self.service = self.client.services. \
                create(image,
                       name=name,
                       endpoint_spec={
                           'Ports': [
                               {
                                   'Protocol': 'tcp',
                                   'PublishedPort': port,
                                   'TargetPort': 8888
                               },
                           ]
                       },
                       mounts=['{}:{}'.format(source, target)],
                       constraints=constraints,
                       command=command,
                       workdir=workdir,
                       )
            # print self.service.id
            return self.service.id

        else:
            return None

    # 获取服务状态
    def get_stats(self, id):
        service = self.client.services.get(id)
        tasks = service.tasks()
        # print tasks[0]['Status']['State']
        return tasks[0]['Status']['State']

    # 获取服务日志
    def get_logs(self, id):
        service = self.client.services.get(id)
        # print service.logs(stdout=True, timestamps=True, follow=True)
        return service.logs(stdout=True, timestamps=True)

    # 关闭服务
    def stop(self, id):
        service = self.client.services.get(id)
        return service.remove()
