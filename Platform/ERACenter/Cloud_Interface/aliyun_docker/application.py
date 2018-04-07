# -*- coding: utf-8 -*-

'''
https://help.aliyun.com/document_detail/26063.html

sudo pip install aliyun-python-sdk-core
sudo pip install aliyun-python-sdk-cs
'''

from aliyunsdkcore.client import AcsClient
import requests
import json

import constants


class Application_Center(object):
    client = AcsClient(constants.ACCESSKEY_ID,
                       constants.ACCESSKEY_SECRET,
                       constants.REGION_ID)

    def __init__(self, cluster):
        self.cluster = cluster
        self.verify = 'Platform/ERACenter/Cloud_Interface/aliyun_docker/pem/%s/ca.pem' % self.cluster['cluster_id']
        self.cert = ('Platform/ERACenter/Cloud_Interface/aliyun_docker/pem/%s/cert.pem' % self.cluster['cluster_id'], 'pem/%s/key.pem' % self.cluster['cluster_id'])

    # 查看应用实例列表
    def app_list(self):
        url = self.cluster['master_url'] + "/projects/"
        resp = requests.get(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 创建应用实例
    def app_create(self, name, template, **kw):
        data = {
            "name": name,
            "template": template,
        }
        data.update(kw)
        headers = {'Content-type': 'application/json'}
        url = self.cluster['master_url'] + "/projects/"
        resp = requests.post(url, verify=self.verify, cert=self.cert,
                             data=json.dumps(data), headers=headers)
        return resp.status_code == 201, resp.content

    # 删除应用实例
    def app_delete(self, name, **kw):
        url = self.cluster['master_url'] + "/projects/%s?force=true" % (name)
        resp = requests.delete(url, verify=self.verify, cert=self.cert, params=kw)
        return resp.status_code == 200, resp.content

    # 查看应用实例
    def app_info(self, name):
        url = self.cluster['master_url'] + "/projects/%s" % (name)
        resp = requests.get(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 启动应用实例
    def app_start(self, name):
        url = self.cluster['master_url'] + "/projects/%s/start" % (name)
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 停止应用实例
    def app_stop(self, name, timeout=10):
        url = self.cluster['master_url'] + "/projects/%s/stop?t=%s" % (name, timeout)
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 终止应用实例
    def app_kill(self, name, signal="KILL"):
        url = self.cluster['master_url'] + "/projects/%s/kill?signal=%s" % (name, signal)
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 重新部署应用实例
    def app_redeploy(self, name):
        url = self.cluster['master_url'] + "/projects/%s/redeploy" % name
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 更新应用配置
    def app_update(self, name, **kw):
        data = {
            "name": name,
            "description": "This is a test application",
            "template": "web:\r\n  image: nginx",
            "version": "1.0",
            "environment": {
                "USER": "abc",
                "PWD": "password"
            }
        }
        headers = {'Content-type': 'application/json'}
        url = self.cluster['master_url'] + "/projects/%s/update" % (name)
        resp = requests.post(url, verify=self.verify, cert=self.cert,
                             data=json.dumps(data), headers=headers)
        return resp.status_code == 202, resp.content

    # 查看服务实例列表
    def service_list(self):
        url = self.cluster['master_url'] + "/services/"
        resp = requests.get(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 查看服务实例
    def service_info(self, service_id):
        url = self.cluster['master_url'] + "/services/%s" % (service_id)
        resp = requests.get(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 启动服务实例
    def service_start(self, service_id):
        url = self.cluster['master_url'] + "/services/%s/start" % (service_id)
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 停止服务实例
    def service_stop(self, service_id, timeout):
        url = self.cluster['master_url'] + "/services/%s/stop?t=%s" % (service_id, timeout)
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 终止服务实例()
    def service_kill(self, service_id, signal):
        url = self.cluster['master_url'] + "/services/%s/kill?signal=%s" % (service_id, signal)
        resp = requests.post(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 伸缩服务实例
    def service_scala(self, service_id, num):
        data = {
            "type": "scale_to",
            "value": num
        }
        headers = {'Content-type': 'application/json'}
        url = self.cluster['master_url'] + "/services/%s/scale" % (service_id)
        resp = requests.post(url, verify=self.verify, cert=self.cert,
                             data=json.dumps(data), headers=headers)
        return resp.status_code == 200, resp.content

    # 创建数据卷
    def volume_create(self, name, driver, driverOpts):
        '''
        https://help.aliyun.com/document_detail/50117.html
        :param name:
        :param driver:
        :param driverOpts:
        :return:
        '''
        data = {
            "name": name,
            "driver": driver,
            "driverOpts": driverOpts
        }
        headers = {'Content-type': 'application/json'}
        url = self.cluster['master_url'] + "/volumes/create"
        resp = requests.post(url, verify=self.verify, cert=self.cert,
                             data=json.dumps(data), headers=headers)
        return resp.status_code == 201, resp.content

    # 查看数据卷
    def volume_info(self, name):
        url = self.cluster['master_url'] + "/volumes/%s" % (name)
        resp = requests.get(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 查看数据卷列表
    def volume_list(self):
        url = self.cluster['master_url'] + "/volumes"
        resp = requests.get(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 200, resp.content

    # 删除数据卷
    def volume_delete(self, name):
        url = self.cluster['master_url'] + "/volumes/%s" % (name)
        resp = requests.delete(url, verify=self.verify, cert=self.cert)
        return resp.status_code == 204, resp.content

    def get_application_status(self, name):
        result, info = self.app_info(name)
        if result:
            info = json.loads(info)
            return info['current_state']
        else:
            return None

    def get_application_info(self, name):
        ret_info = dict(current_state='', created='', updated='')
        result, info = self.app_info(name)
        if result:
            try:
                info = json.loads(info)
            except:
                info = ret_info
            return info['current_state'], info['created'], info['updated']
        else:
            return ret_info


from abc import ABCMeta, abstractmethod


class AbstractApplication(object):
    '''
    单个应用
    '''
    # for python3: class AbstractApplication(metaclass=ABCMeta)
    __metaclass__ = ABCMeta

    # class AbstractApplication(metaclass=ABCMeta):
    @abstractmethod
    def Init_Task(self):
        pass

    @abstractmethod
    def Init_Aliyun(self):
        pass

    @abstractmethod
    def Init_Instance(self):
        pass

    @abstractmethod
    def Create_App(self):
        pass

    @abstractmethod
    def Polling_State(self):
        pass

    @abstractmethod
    def Do_Before_Remove(self):
        pass

    @abstractmethod
    def Run(self):
        pass
