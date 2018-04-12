#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       cloud
   Description:
   Author:          huangzhen
   date:            2018/3/13
-------------------------------------------------
   Change Activity:
                   2018/3/13:
-------------------------------------------------
"""
__author__ = 'huangzhen'

import uuid
from marshmallow import Schema, fields, post_load
from Library.extensions import orm
import datetime
from Library.Utils.time_util import datetime_to_timestamp
import json

import traceback


class BaseSchema(Schema):
    __abstract__ = True
    id = fields.Str()
    t_created = fields.DateTime()
    t_modified = fields.DateTime()
    is_deleted = fields.Boolean()


class BaseModel(orm.Model):
    """
    Base for all model classes
    """
    __abstract__ = True

    id = orm.Column(orm.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    t_created = orm.Column(orm.DateTime, default=lambda: datetime.datetime.utcnow())
    t_modified = orm.Column(orm.DateTime, default=lambda: datetime.datetime.utcnow(),
                            onupdate=lambda: datetime.datetime.utcnow())
    is_deleted = orm.Column(orm.Integer, default=False)

    def to_dict(self):
        return self.schema.dump(self).data

    def delete(self):
        self.is_deleted = 1
        orm.session.commit()
        return True

    @classmethod
    def from_dict(cls, dct):
        return cls.schema.load(dct).data

    def commit(self):
        orm.session.commit()


class ERAProjectSchema(BaseSchema):
    uid = fields.Str()
    name = fields.Str()
    doc = fields.Str()
    default_frw = fields.Str()
    tags = fields.Str()
    perm = fields.Int()
    state = fields.Str()

    @post_load
    def make_project(self, data):
        return ERAProject(**data)


class ERAProject(BaseModel):
    schema = ERAProjectSchema(strict=True)

    name = orm.Column(orm.String(64), index=True)
    uid = orm.Column(orm.String(32), index=True)
    doc = orm.Column(orm.String(256), default='')
    default_frw = orm.Column(orm.String(32), default='')  # 深度学习框架
    tags = orm.Column(orm.String(128), default='')
    perm = orm.Column(orm.Integer, default=0)
    state = orm.Column(orm.String(16), default='')

    def __init__(self, name, uid, doc=None, default_frw=None, tags=None, permission=None, state=None):
        self.name = name
        self.uid = uid
        self.doc = doc
        self.default_frw = default_frw
        self.tags = tags
        self.permission = permission
        self.state = state


class JobSchema(BaseSchema):
    # {'t_ended': [u'Field may not be null.'], 'is_deleted': [u'Field may not be null.'],
    #  't_modified': [u'Field may not be null.'], 't_started': [u'Field may not be null.'],
    #  'state': [u'Field may not be null.'], 't_created': [u'Field may not be null.'],
    #  'accepted_value': [u'Field may not be null.'], 'id': [u'Field may not be null.']}
    uid = fields.Str()
    gid = fields.Str()
    doc = fields.Str()
    duration = fields.Int()
    project_id = fields.Str()
    code_id = fields.Str()
    data_ids = fields.Str()
    entry_cmd = fields.Str()
    start_cmd = fields.Str()
    b_tensorboard = fields.Boolean()
    b_jupyter = fields.Boolean()
    t_started = fields.DateTime(allow_none=True)
    t_ended = fields.DateTime(allow_none=True)
    perm = fields.Int()
    state = fields.Str(allow_none=True)
    accepted_value = fields.Int(allow_none=True)
    env = fields.Dict(allow_none=True)

    # 临时
    is_deleted = fields.Boolean()

    @post_load
    def make_job(self, data):
        return Job(**data)


class Job(BaseModel):
    schema = JobSchema(strict=True)

    # gid = orm.Column(orm.String(32), index=True)
    # uid = orm.Column(orm.String(32), index=True)
    # project_id = orm.Column(orm.String(32), index=True)
    # code_id = orm.Column(orm.String(32), index=True)
    # data_ids = orm.Column(orm.String(256), index=True)
    # entry_cmd = orm.Column(orm.String(256), index=True)
    # start_cmd = orm.Column(orm.String(256), index=True)
    # doc = orm.Column(orm.String(256), default='')
    # default_frw = orm.Column(orm.String(32), default='')  # 深度学习框架
    # perm = orm.Column(orm.Integer, default=0)
    # state = orm.Column(orm.String(16), default='')
    # accepted_value = orm.Column(orm.Integer, default=0)
    # b_tensorboard = orm.Column(orm.Integer, default=False)
    # b_jupyter = orm.Column(orm.Integer, default=False)
    # t_started = orm.Column(orm.DateTime)
    # t_ended = orm.Column(orm.DateTime)
    # env = orm.Column(orm.String(128))

    def __init__(self, env, uid, gid, doc, duration, project_id, code_id, data_ids, entry_cmd, start_cmd,
                 b_tensorboard, b_jupyter, t_started=None, t_ended=None, perm=None, state=None, accepted_value=None,
                 is_deleted=False, t_created=None, t_modified=None, id=None):
        self.env = env
        self.uid = uid
        self.gid = gid
        self.duration = duration
        self.project_id = project_id
        self.code_id = code_id
        self.data_ids = data_ids
        self.entry_cmd = entry_cmd
        self.start_cmd = start_cmd
        self.b_tensorboard = b_tensorboard
        self.b_jupyter = b_jupyter
        self.t_started = t_started
        self.t_ended = t_ended
        self.doc = doc
        self.perm = perm
        self.state = state
        self.accepted_value = accepted_value

        # 临时
        if is_deleted:
            self.is_deleted = is_deleted
        else:
            self.is_deleted = False
        if t_created:
            self.t_created = t_created
        else:
            self.t_created = datetime.datetime.utcnow()

        if t_modified:
            self.t_modified = t_modified
        else:

            self.t_modified = datetime.datetime.utcnow()
        if id:
            self.id = id

    @property
    def app_name(self):
        return '-'.join((self.id, str(int(datetime_to_timestamp(self.t_created)))))

    @property
    def with_gpu(self):
        print("debug: env_dict %s" % self.env_dict)
        return self.env_dict.get("with_gpu")

    @property
    def machine_type(self):
        if self.with_gpu:
            return "gpu"
        else:
            return "cpu"

    @property
    def env_dict(self):
        if isinstance(self.env, dict):
            return self.env
        else:
            return json.loads(self.env)

    @property
    def instance_type(self):
        return self.machine_type

    @property
    def environment(self):
        return self.env_dict["dl_fr_name"]

    @property
    def data_id_list(self):
        return list(eval(str(self.data_ids))) if self.data_ids else []

    @property
    def owner_id(self):
        return self.uid


class JobReqSchema(BaseSchema):
    job_id = fields.Str()
    duration = fields.Integer()
    tw_start = fields.DateTime()
    tw_end = fields.DateTime()
    resources = fields.Dict()
    value = fields.Integer()


####################### RESOURCE DEFINE ######################
# 与ERA组件同步
CPU_FLAG = 0x0000
GPU_FLAG = 0x1000
MEM_FLAG = 0x2000
FRW_FLAG = 0x3000
GPU_TYPE_DEFAULT = 0x0000
CPU_TYPE_DEFAULT = 0x0000
MEM_TYPE_DEFAULT = 0x0000

CPU_TYPE_MAP = {
    "i7": 0x0100,
    "i5": 0x0200,
}
GPU_TYPE_MAP = {
    "titan": 0x0100
}
MEM_TYPE_MAP = {
    "ddr3": 0x0100
}

# // 框架类型（即名称）由后三个字节表示
FRW_CAFFE = 0x0000
FRW_CAFFE2_PY2 = 0x0001
FRW_CAFFE_PY2 = 0x0002
FRW_CHAINER = 0x0003
# // 省略若干
FRW_TENSORFLOW = 0x0fff
FRW_TYPE_DEFAULT = FRW_TENSORFLOW
FRW_MAP = {
    "tensorflow": FRW_TENSORFLOW
}


####################### RESOURCE DEFINE ######################

class JobReq(BaseModel):
    schema = JobReqSchema(strict=True)

    DEFAULT_RESOURCES = {
        "cputype": "i5",
        "cpunum": 5,
        "gputype": "titan",
        "gpunum": 1,
        "memtype": "ddr3",
        "memnum": 7,
        "framework": "tensorflow"
    }

    # 保存到redis即可
    def __init__(self, job_id, duration, tw_start, tw_end, value, resources):
        # type: (object, object, object, object, object, object) -> object
        self.job_id = job_id
        self.duration = duration
        self.tw_start = tw_start
        self.tw_end = tw_end
        self.value = value
        self.resources = resources or self.DEFAULT_RESOURCES

    def to_dict(self):
        data = self.schema.dump(self).data
        try:
            data["resources"] = {
                "cpu": CPU_FLAG | CPU_TYPE_MAP[data["resources"]["cputype"]] | data["resources"]["cpunum"],
                "gpu": GPU_FLAG | GPU_TYPE_MAP[data["resources"]["gputype"]] | data["resources"]["gpunum"],
                "mem": MEM_FLAG | MEM_TYPE_MAP[data["resources"]["memtype"]] | data["resources"]["memnum"],
                "frw": FRW_FLAG | FRW_MAP[data["resources"]["framework"]]
            }
        except Exception:
            print('exception', traceback.format_exc())
        # del data["is_deleted"]
        return data


class JobResp:
    def __init__(self, accepted, arrival_time, accepted_price):
        self.accepted = accepted
        self.arrival_time = arrival_time
        self.accepted_price = accepted_price


class ModuleSchema(BaseSchema):
    module_type = fields.Str()
    entity_id = fields.Str(allow_none=True)
    version = fields.Int()

    uid = fields.Str()
    codehash = fields.Str(allow_none=True)
    state = fields.Str()
    size = fields.Int()

    @post_load
    def make_module(self, data):
        return Module(**data)


class Module(BaseModel):
    schema = ModuleSchema(strict=True)
    entity_id = orm.Column(orm.String(32), index=True)
    module_type = orm.Column(orm.String(32))
    version = orm.Column(orm.INT, nullable=False, default=0)
    uid = orm.Column(orm.String(32), index=True)
    codehash = orm.Column(orm.String(256))
    state = orm.Column(orm.String(16))
    size = orm.Column(orm.INT, default=0, doc="MB")

    def __init__(self,
                 uid,
                 version=None,
                 module_type="code",
                 entity_id=None,
                 codehash=None,
                 state='pending',
                 size=None,
                 id=None,
                 is_deleted=False,
                 t_created=None,
                 t_modified=None):
        """

        :rtype: object
        """
        self.module_type = module_type
        self.version = version
        self.uid = uid
        self.codehash = codehash
        self.entity_id = entity_id
        self.state = state
        self.size = size
        if id is not None:
            self.id = id
        # 临时
        if is_deleted is not None:
            self.is_deleted = is_deleted
        else:
            self.is_deleted = False
        if t_created is not None:
            self.t_created = t_created
        else:
            self.t_created = datetime.datetime.utcnow()

        if t_modified is not None:
            self.t_modified = t_modified
        else:

            self.t_modified = datetime.datetime.utcnow()

    @property
    def owner_id(self):
        return self.uid
