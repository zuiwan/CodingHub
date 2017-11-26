# -*- coding: utf-8 -*-

import docker


class Container:
    # 创建实例
    def __init__(self):
        self.client = docker.from_env()
        # self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        # self.client = docker.DockerClient(base_url='tcp://127.0.0.1:1234')
        self.container = ''

    # 容器列表
    def list(self):
        print self.client.containers.list()

    # 运行容器
    def run(self, image):
        # self.container = self.client.containers.run("alpine", ["echo", "hello", "world"], detach=True)
        self.container = self.client.containers.run(image, detach=True)
        print self.container.id

    # 停止容器
    def stop(self):
        print self.container.stop()

    # 获取容器id
    def get_id(self):
        print self.container.id

    # 获取容器镜像
    def get_image(self):
        print self.container.attrs['Config']['Image']

    # 获取容器运行日志
    def get_log(self):
        for line in self.container.logs(stream=True):
            print line.strip()
