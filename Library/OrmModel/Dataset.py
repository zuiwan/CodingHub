#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import  fields, post_load

from Library.OrmModel import BaseModel,BaseSchema
from Library.extensions import orm




class DataSchema(BaseSchema):
    name = fields.Str()
    description = fields.Str()
    permission = fields.Int()
    version = fields.Float()
    tags = fields.Str()
    family_id = fields.Str()
    owner_id = fields.Str()
    bg_url_id = fields.Str()
    is_recommended = fields.Boolean()
    @post_load
    def make_data(self, data):
        return Data(**data)


class Data(BaseModel):
    schema = DataSchema(strict=True)
    default_permission = 0
    name = orm.Column(orm.String(128))
    owner_id = orm.Column(orm.String(32), default='')
    description = orm.Column(orm.String(64), default='')
    permission = orm.Column(orm.Integer, default=default_permission)
    version = orm.Column(orm.Float(32), default=0)
    family_id = orm.Column(orm.String(64), default='')
    tags = orm.Column(orm.String(64), default='')
    bg_url_id = orm.Column(orm.String(32), default='')
    is_recommended = orm.Column(orm.Boolean, default=False)

    def __init__(self,
                 name,
                 owner_id,
                 description=None,
                 permission=default_permission,
                 version=None,
                 family_id=None,
                 tags=None,
                 bg_url_id=None,
                 is_recommended=None):
        self.name = name
        self.description = description
        self.permission = permission
        self.version = float(version)
        self.family_id = family_id
        self.owner_id = owner_id
        self.tags = tags
        self.bg_url_id = bg_url_id
        self.is_recommended = is_recommended