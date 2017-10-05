#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load

from Library.OrmModel import BaseModel,BaseSchema
from Library.Utils import *
from User import UserSchema
from Library.extensions import orm


class TaskSchema(BaseSchema):

    name = fields.Str()
    description = fields.Str()
    permission = fields.Int()
    state = fields.Str()
    log_id = fields.Str()
    # module_id = fields.Nested(ModuleSchema, only=["id"])
    # owner_id = fields.Nested(UserSchema, only=["id"])
    module_id = fields.Str()
    project_id = fields.Str()
    owner_id = fields.Str()
    # created = fields.DateTime(allow_none=True)
    # started = fields.DateTime(allow_none=True)

    started = fields.DateTime(allow_none=True)
    ended = fields.DateTime(allow_none=True)
    duration = fields.Int(allow_none=True)
    version = fields.Float(allow_none=True)
    canvas = fields.Str(allow_none=True)
    family_id = fields.Str(allow_none=True)
    predecessor = fields.Str(allow_none=True)
    instance_type = fields.Str(allow_none=True)
    data_id = fields.Str(allow_none=True)
    task_instance_ids = fields.Str(allow_none=True)

    @post_load
    def make_experiment(self, data):
        return Task(**data)


class Task(BaseModel):
    schema = TaskSchema(strict=True)
    default_permission = 0
    default_state = "waiting"


    name = orm.Column(orm.String(128), index=True)
    description = orm.Column(orm.String(64))
    module_id = orm.Column(orm.String(32))
    project_id = orm.Column(orm.String(32))
    owner_id = orm.Column(orm.String(32))
    permission = orm.Column(orm.Integer)
    log_id = orm.Column(orm.String(32), unique=True)
    state = orm.Column(orm.String(32))

    data_id = orm.Column(orm.String(32),nullable=True)
    family_id = orm.Column(orm.String(64),nullable=True)
    version = orm.Column(orm.Float(32),nullable=True)
    predecessor = orm.Column(orm.String(64),nullable=True)
    instance_type = orm.Column(orm.String(64),nullable=True)
    started = orm.Column(orm.DateTime,nullable=True)
    ended = orm.Column(orm.DateTime,nullable=True)
    duration = orm.Column(orm.Integer,nullable=True)
    canvas = orm.Column(orm.String(64),nullable=True)
    task_instance_ids = orm.Column(orm.String(256),nullable=True)


    def __init__(self,
                 name,
                 description,
                 module_id,
                 project_id,
                 log_id,
                 owner_id,
                 state=default_state,
                 permission=default_permission,
                 version=None,
                 family_id=None,
                 data_id=None,
                 instance_type=None,
                 started=None,
                 ended=None,
                 duration=None,
                 canvas=None,
                 task_instance_ids=None,
                 predecessor=None
                 ):
        self.name = name
        self.description = description
        if started:
            self.started = self.localize_date(started)
        if ended:
            self.ended = self.localize_date(ended)
        self.state = state
        self.duration = duration
        self.log_id = log_id
        self.module_id = module_id
        self.project_id = project_id
        self.data_id = data_id
        self.version = version
        self.family_id = family_id
        self.owner_id = owner_id
        self.permission = permission
        self.task_instance_ids = task_instance_ids
        self.predecessor = predecessor
        self.instance_type = instance_type
        self.canvas = canvas
        # if canvas:
        #     nodes = canvas.get('nodes', {})
        #     self.task_instances = {}
        #     for key in nodes:
        #         self.task_instances[nodes[key].get("taskInstanceId")] = nodes[key].get("type")


    @property
    def created_pretty(self):
        return pretty_date(self.date_created)

    @property
    def duration_rounded(self):
        return int(self.duration or 0)

    @property
    def instance_type_trimmed(self):
        if self.instance_type:
            return self.instance_type.split('_')[0]
        return self.instance_type

    @property
    def is_finished(self):
        return self.state in ["shutdown", "failed", "success"]

    @property
    def has_started(self):
        return self.state not in ["waiting"]


