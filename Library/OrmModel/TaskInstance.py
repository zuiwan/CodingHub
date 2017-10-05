#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load

from Library.OrmModel import BaseModel,BaseSchema
from Library.extensions import orm


class TaskInstanceSchema(BaseSchema):

    log_id = fields.Str()
    container = fields.Str()
    module_id = fields.Str()
    owner_id = fields.Str()
    instanceType = fields.Str()
    state = fields.Str()
    label = fields.Str()
    style = fields.Str()
    mode = fields.Str()
    connections = fields.Str(allow_none=True)
    version = fields.Float(allow_none=True)
    instanceTypeInherited = fields.Boolean()
    outputs = fields.Str(allow_none=True)
    params = fields.Str(allow_none=True)
    type = fields.Int(allow_none=True)    # 0: module_node
    inputs = fields.Str(allow_none=True)


    @post_load
    def make_task_instance(self, data):
        return TaskInstance(**data)


class TaskInstance(BaseModel):
    schema = TaskInstanceSchema(strict=True)
    default_instanceTypeInherited = 0
    default_type = 0
    default_style = "{'top': '284px', 'left': '132px'}"
    default_inputs = "[{'name': 'input', 'type': 'dir'}]"
    owner_id = orm.Column(orm.String(32))
    log_id = orm.Column(orm.String(32))
    container = orm.Column(orm.String(64))
    module_id = orm.Column(orm.String(32))
    instanceType = orm.Column(orm.String(64))
    state = orm.Column(orm.String(32))
    label = orm.Column(orm.String(128))
    style = orm.Column(orm.String(64))
    mode = orm.Column(orm.String(32))
    connections = orm.Column(orm.String(64))
    version = orm.Column(orm.Float(32),nullable=True)
    instanceTypeInherited = orm.Column(orm.Boolean)
    outputs = orm.Column(orm.String(64),nullable=True)
    params = orm.Column(orm.String(64),nullable=True)
    type = orm.Column(orm.Integer)    # 0: module_node
    inputs = orm.Column(orm.String(64),nullable=True)





    def __init__(self,
                container,
                log_id,
                owner_id,
                instanceType,
                state,
                label,
                mode,
                module_id,
                style=default_style,
                connections=None,
                version=None,
                instanceTypeInherited=default_instanceTypeInherited,
                params=None,
                type=default_type,
                outputs=None,
                inputs=default_inputs):
        self.log_id = log_id
        self.container = container
        self.instanceType = instanceType
        self.state = state
        self.label = label
        self.style = style
        self.mode = mode
        self.module_id = module_id
        self.connections = connections
        self.version = version
        self.instanceTypeInherited = instanceTypeInherited
        self.params = params
        self.type = type
        self.outputs = outputs
        self.inputs = inputs
        self.owner_id = owner_id

