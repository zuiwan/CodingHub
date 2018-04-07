# -*- coding: utf-8 -*-

'''
https://help.aliyun.com/document_detail/26047.html

sudo pip install aliyun-python-sdk-core
sudo pip install aliyun-python-sdk-cs
sudo pip install aliyun-python-sdk-ecs

changelog:
2017-12-29: upgrade aliyun-python-sdk-cs from 2.1.2 to 2.2.1
'''
import httplib
import requests
import json
from functools import wraps
from pprint import (
    pformat,
    pprint
)
from aliyunsdkcore.client import (
    AcsClient,
    ServerException
)
from aliyunsdkcs.request.v20151215 import (
    CreateClusterRequest,
    DescribeClustersRequest,
    DeleteClusterRequest,
    ScaleClusterRequest,
    DescribeClusterDetailRequest,
    DescribeClusterCertsRequest,
    DescribeClusterScaledNodeRequest,
    DeleteClusterNodeRequest
)
from aliyunsdkecs.request.v20140526 import (
    DescribeInstancesRequest,
    StopInstanceRequest,
    DeleteInstanceRequest
)

import constants
import setting
from application import AbstractApplication


def cluster_http_exception_decorator(se_handler=None):
    '''
    Cluster类的HTTP请求异常处理补丁
    '''

    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                res = f(*args, **kwargs)
            except ServerException as se:
                res = se_handler(se) if se_handler and hasattr(se_handler, '__call__') else None
            except Exception as e:
                raise e
            return res

        return wrapper

    return decorate


def server_exception_handler():
    raise Exception()


class Cluster_Center(object):
    '''
    多个集群
    注意：各个请求接口均返回dict或者list等python对象而非字符串，不需要json.loads
    '''

    client = AcsClient(constants.ACCESSKEY_ID,
                       constants.ACCESSKEY_SECRET,
                       constants.REGION_ID)

    error_handler = cluster_http_exception_decorator(server_exception_handler)

    # def __new__(cls, *args, **kwargs):
    #     cls.error_handler = server_exception_handler(kwargs.get("http_err_handler"))
    #     return super(Cluster_Center, cls).__new__(cls)

    def __init__(self, cpu_or_gpu=None, *args, **kwargs):
        self._cluster_info = {}
        self.is_gpu = cpu_or_gpu == "gpu"

    def __setitem__(self, cluster_id, detail):
        self._cluster_info[cluster_id] = detail

    def __getitem__(self, item):
        return self._cluster_info[item]

    def __len__(self):
        return len(self._cluster_info.keys())

    def __repr__(self):
        return pformat(self._cluster_info)

    def __iter__(self):
        if not self._cluster_info:
            self.list(localize=True)
        for cluster_id, detail in self._cluster_info.items():
            yield self[cluster_id]

    @error_handler
    def list(self, name=None, localize=False):
        '''
        查看所有集群实例
        :param name: 可选，返回指定集群的详情
               localize: 为True则保存查询结果到内存中的实例对象
        :return:
            [
                {
                    "agent_version": "string",
                    "cluster_id": "string",
                    "created": "datetime",
                    "external_loadbalancer_id": "string",
                    "master_url": "string",
                    "name": "string",
                    "network_mode": "string",
                    "region_id": "string",
                    "security_group_id": "string",
                    "size": "numbers",
                    "state": "string",
                    "updated": "datetime",
                    "vpc_id": "string",
                    "vswitch_id": "string"
                }
            ]
        '''
        req = DescribeClustersRequest.DescribeClustersRequest()
        req.set_accept_format('json')
        if name is not None and isinstance(name, basestring):
            req.set_Name(name)

        resp = self.client.do_action_with_exception(req)
        if localize is True:
            for cluster_instance in resp:
                self[cluster_instance["cluster_id"]] = cluster_instance
        return resp

    # 创建集群实例
    @error_handler
    def create(self, password, instance_type, name, size, network_mode, data_disk_category, data_disk_size,
               ecs_image_id):
        req = CreateClusterRequest.CreateClusterRequest()
        # request_body = '''
        # {
        #     "password": "<ECS SSH 密码，需要符合ECS密码规范>",
        #     "instance_type": "<ECS 实例类型>",
        #     "name": "<集群名称>",
        #     "size": <集群包含的节点数量，公测期间最大是10>,
        #     "network_mode": "<网络类型,可以选择classic or vpc>",
        #     "data_disk_category": "<磁盘类型，需要根据具体的实例类型确定>",
        #     "data_disk_size": <磁盘大小，需要根据具体的示例类型确定>,
        #     "ecs_image_id": "<镜像ID，具体参考文档中关于镜像的说明>"
        # }'''

        request_body = '''{
            "password": {},
            "instance_type": {},
            "name": {},
            "size": {},
            "network_mode": {},
            "data_disk_category": {},
            "data_disk_size": {},
            "ecs_image_id": {}
        }'''.format(password, instance_type, name, size, network_mode, data_disk_category, data_disk_size, ecs_image_id)

        req.set_content(request_body)
        req.add_header('X-Acs-Region-Id', '<Region-Id>')
        res = self.client.do_action_with_exception(req)
        return res

    @error_handler
    def delete(self, cluster_id):
        '''
        # 删除集群实例
        :param cluster_id: 集群ID，必须
        :return:
                HTTP/1.1 202 Accepted
                <公共响应头>
        '''
        req = DeleteClusterRequest.DeleteClusterRequest()
        req.set_ClusterId(cluster_id)
        res = self.client.do_action_with_exception(req)
        return res

    @error_handler
    def info(self, id):
        '''
        查看集群实例
        :param id: 集群ID，必须
        :return:{
                    "agent_version": "string",
                    "cluster_id": "string",
                    "created": "datetime",
                    "external_loadbalancer_id": "string",
                    "master_url": "string",
                    "name": "string",
                    "network_mode": "string",
                    "region_id": "string",
                    "security_group_id": "string",
                    "size": "numbers",
                    "state": "string",
                    "updated": "datetime",
                    "vpc_id": "string",
                    "vswitch_id": "string"
                }
        '''
        req = DescribeClusterDetailRequest.DescribeClusterDetailRequest()
        req.set_accept_format('json')
        req.set_ClusterId(id)
        res = self.client.do_action_with_exception(req)
        return res

    # 获取集群证书
    @error_handler
    def cert(self, id):
        req = DescribeClusterCertsRequest.DescribeClusterCertsRequest()
        req.set_ClusterId(id)
        res = self.client.do_action_with_exception(req)
        return res

    # 集群扩容
    @error_handler
    def scala(self, cluster_id,
              instance_type=None,
              size=None,
              data_disk_category="cloud",
              data_disk_size=None,
              ecs_image_id="ubuntu_14_0405_64_40G_base_20170222.vhd",
              password=None, io_optimized="optimized"):
        '''

        :param cluster_id:
        :param instance_type: https://help.aliyun.com/document_detail/25378.html?spm=5176.doc26058.2.4.MyVfSv
        :param size:  must great than current size
        :param data_disk_category: "cloud" (<=2000GB * 4) or "ephemeral_ssd" (<=800GB * 4)
        :param data_disk_size:  GB
        :param ecs_image_id: "ubuntu_14_0405_64_40G_base_20170222.vhd" or "centos_7_2_64_40G_base_20170222.vhd"
        :param password:
        :param io_optimized: "optimized" or None
        :return:
            HTTP/1.1 202 Accepted
            <公共响应头>
        '''
        req = ScaleClusterRequest.ScaleClusterRequest()
        req.set_ClusterId(cluster_id)

        body = {
            "password": password or constants.SSH_PASSWORD,
            "instance_type": instance_type,
            "size": size,
            "data_disk_category": data_disk_category,
            "data_disk_size": data_disk_size,
            "ecs_image_id": ecs_image_id,
            "io_optimized": io_optimized
        }
        req.set_content(json.dumps(body))
        res_body = self.client.do_action_with_exception(req)
        return res_body

    # 获取扩容节点信息
    @error_handler
    def scala_nodes(self, cluster_id):
        req = DescribeClusterScaledNodeRequest.DescribeClusterScaledNodeRequest()
        req.set_ClusterId(cluster_id)
        res_body = self.client.do_action_with_exception(req)
        return res_body

    # 删除节点
    @error_handler
    def delete_node(self, cluster_id, ip, releaseInstance=False):
        req = DeleteClusterNodeRequest.DeleteClusterNodeRequest()
        if releaseInstance:
            req.add_query_param("releaseInstance", "true")
        req.set_ClusterId(cluster_id)
        req.set_Ip(ip)
        res_body = self.client.do_action(req)
        return res_body

    # 触发器扩容
    @error_handler
    def triggle_scale_out(self, cluster_id, size=-1, cluster_type="cpu"):  # size=-1表示扩容一台机器
        current_size = self.info(cluster_id)['size']
        step = 1 if size == -1 else size - current_size
        params = '&type=scale_out&step={}'.format(step)
        resp = requests.get(
            constants.SCALE_TRIGGER_URL[cluster_type] + params)
        return resp.content

    # 触发器缩容
    @error_handler
    def triggle_scale_in(self, cluster_id, size=-1, cluster_type="cpu"):  # size=-1表示缩容一台机器
        current_size = self.info(cluster_id)['size']
        step = 1 if size == -1 else current_size - size
        for _ in range(step):
            params = '&type=scale_in'
            resp = requests.get(
                constants.SCALE_TRIGGER_URL[cluster_type] + params)
            if resp.status_code != 200:
                return False
        return True

    @error_handler
    def describe_instances(self, instance_ids=None, page_size=20):
        """
        https://help.aliyun.com/document_detail/25506.html?spm=a2c4g.11186623.6.854.hG0tyK
        根据实例id获取具体
        :param instance_ids:一个python数组或json处理后字符串
        :param page_size:返回的实例数量，默认是单集群的最大机器数20
        :return:
        """
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        if instance_ids:
            request.set_InstanceIds(instance_ids if type(instance_ids) == str else json.dumps(instance_ids))
        request.set_PageSize(page_size)
        return self.client.do_action_with_exception(request)['Instances']['Instance']

    @error_handler
    def stop_instance(self, instance_id, force=False):
        request = StopInstanceRequest.StopInstanceRequest()
        request.set_InstanceId(instance_id)
        if force:
            request.set_ForceStop("true")
        return self.client.do_action(request)

    @error_handler
    def delete_instance(self, instance_id, force=False):
        request = DeleteInstanceRequest.DeleteInstanceRequest()
        request.set_InstanceId(instance_id)
        if force:
            request.set_Force("true")
        return self.client.do_action(request)


class Cluster(Cluster_Center):
    '''
    单个集群
    '''

    def __init__(self, cluster_id=None, cpu_or_gpu="cpu"):
        super(Cluster, self).__init__(cpu_or_gpu=cpu_or_gpu)
        if cluster_id is None or not isinstance(cluster_id, basestring):
            cluster_id = constants.CLUSTER_ID_MAP.get(cpu_or_gpu)
        self.cluster_id = cluster_id
        self.cluster_info = self.info(cluster_id)

    def __len__(self):
        return self.cluster_info['size']

    @property
    def cluster(self):
        return self.cluster_info
