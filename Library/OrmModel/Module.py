#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load


from Library.OrmModel import BaseModel,BaseSchema
from Library.extensions import orm

from User import UserSchema


class ModuleSchema(BaseSchema):

    name = fields.Str()
    description = fields.Str()
    command = fields.Str()
    mode = fields.Str(allow_none=True)
    module_type = fields.Str()
    default_env = fields.Str()
    family_id = fields.Str(allow_none=True)
    project_id = fields.Str()
    version = fields.Float(allow_none=True)
    outputs = fields.Str()
    inputs = fields.Str()
    owner_id = fields.Str()
    code = fields.Str()
    tags = fields.Str(allow_none=True)
    codehash = fields.Str()
    permission = fields.Int()

    @post_load
    def make_module(self, data):
        return Module(**data)


class Module(BaseModel):
    schema = ModuleSchema(strict=True)
    default_outputs = "[{'name': 'output', 'type': 'dir'}]"
    default_inputs = "[{'name': 'input', 'type': 'dir'}]"
    default_code = "[{'name': 'code', 'type': 'dir'}]"
    default_permission = 0

    name = orm.Column(orm.String(128), index=True)
    description = orm.Column(orm.String(64))
    command = orm.Column(orm.String(256))
    mode = orm.Column(orm.String(32))
    module_type = orm.Column(orm.String(32))
    default_env = orm.Column(orm.String(64))
    family_id = orm.Column(orm.String(64),nullable=True)
    project_id = orm.Column(orm.String(64))
    version = orm.Column(orm.Float(32), nullable=True)
    outputs = orm.Column(orm.String(256))
    inputs = orm.Column(orm.String(256))
    owner_id = orm.Column(orm.String(32))
    code = orm.Column(orm.String(256))
    tags = orm.Column(orm.String(64), nullable=True)
    codehash = orm.Column(orm.String(256))
    permission = orm.Column(orm.Integer)


    def __init__(self,
                 name,
                 description,
                 command,
                 owner_id,
                 project_id,
                 codehash,
                 family_id=None,
                 tags=None,
                 version=None,
                 mode="cli",
                 module_type="code",
                 default_env=None,
                 outputs=default_outputs,
                 inputs=default_inputs,
                 code=default_code,
                 permission=default_permission,
                 ):
        self.name = name
        self.description = description
        self.command = command
        self.mode = mode
        self.module_type = module_type
        self.default_env = default_env
        self.family_id = family_id
        self.version = version
        self.outputs = outputs
        self.inputs = inputs
        self.owner_id = owner_id
        self.code = code
        self.tags = tags
        self.codehash = codehash
        self.permission = permission
        self.project_id = project_id