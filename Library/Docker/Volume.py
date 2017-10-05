# -*- coding: utf-8 -*-

import docker


class Volume:
    # 创建实例
    def __init__(self):
        self.client = docker.from_env()
        # self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        # self.client = docker.DockerClient(base_url='tcp://127.0.0.1:1234')
        self.volume = ''

    # 创建数据卷
    def create(self, name, driver):
        self.volume = self.client.volumes.create(name=name,
                                                 driver=driver,
                                                 driver_opts={},
                                                 labels={})
        print self.volume
