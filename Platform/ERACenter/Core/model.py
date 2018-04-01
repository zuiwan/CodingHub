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


class ProjectSchema(BaseSchema):
    uid = fields.Str()
    name = fields.Str()
    doc = fields.Str()
    default_frw = fields.Str()
    tags = fields.Str()
    perm = fields.Int()
    state = fields.Str()

    @post_load
    def make_project(self, data):
        return Project(**data)


class Project(BaseModel):
    schema = ProjectSchema(strict=True)

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
    t_started = fields.DateTime()
    t_ended = fields.DateTime()
    perm = fields.Int()
    state = fields.Str()
    accepted_value = fields.Int()

    @post_load
    def make_job(self, data):
        return Job(**data)


class Job(BaseModel):
    scheme = JobSchema(strict=True)
    gid = orm.Column(orm.String(32), index=True)
    uid = orm.Column(orm.String(32), index=True)
    project_id = orm.Column(orm.String(32), index=True)
    code_id = orm.Column(orm.String(32), index=True)
    data_ids = orm.Column(orm.String(256), index=True)
    entry_cmd = orm.Column(orm.String(256), index=True)
    start_cmd = orm.Column(orm.String(256), index=True)
    doc = orm.Column(orm.String(256), default='')
    default_frw = orm.Column(orm.String(32), default='')  # 深度学习框架
    perm = orm.Column(orm.Integer, default=0)
    state = orm.Column(orm.String(16), default='')
    accepted_value = orm.Column(orm.Integer(11), default=0)
    b_tensorboard = orm.Column(orm.Integer, default=False)
    b_jupyter = orm.Column(orm.Integer, default=False)
    t_started = orm.Column(orm.DateTime)
    t_ended = orm.Column(orm.DateTime)
    env = orm.Column(orm.String(128))

    def __init__(self, uid, gid, doc, duration, project_id, code_id, data_ids, entry_cmd, start_cmd,
                 b_tensorboard, b_jupyter, t_started, t_ended, perm, state, accepted_value):
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

    @property
    def app_name(self):
        return '-'.join((self.id, str(int(datetime_to_timestamp(self.t_created)))))

    @property
    def with_gpu(self):
        return self.env_dict.get("with_gpu")

    @property
    def machine_type(self):
        if self.with_gpu:
            return "gpu"
        else:
            return "cpu"

    @property
    def env_dict(self):
        return json.loads(self.env)


class JobReqSchema(BaseSchema):
    job_id = fields.Str()
    duration = fields.Integer()
    tw_start = fields.DateTime()
    tw_end = fields.DateTime()
    resources = fields.Dict()


class JobReq(BaseModel):
    schema = JobReqSchema(strict=True)

    # 保存到redis即可
    def __init__(self, job_id, duration, tw_start, tw_end, value, resources):
        self.job_id = job_id
        self.duration = duration
        self.tw_start = tw_start
        self.tw_end = tw_end
        self.value = value
        self.resources = resources


class JobResp:
    def __init__(self, accepted, arrival_time, accepted_price):
        self.accepted = accepted
        self.arrival_time = arrival_time
        self.accepted_price = accepted_price
