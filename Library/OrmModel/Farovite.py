#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load

from Library.OrmModel import BaseModel, BaseSchema
from Library.extensions import orm

class FavoriteSchema(BaseSchema):

    name = fields.Str()
    description = fields.Str()
    owner_id = fields.Str()
    tags = fields.Str()
    permission = fields.Int()
    origin=fields.Str()
    is_recommended = fields.Boolean()
    @post_load
    def make_project(self, data):
        return Favorite(**data)


class Favorite(BaseModel):
    schema = FavoriteSchema(strict=True)
    '''
    permission:integer
    0 public default
    1 private
    '''
    default_permission = 0

    name = orm.Column(orm.String(64), index=True)
    owner_id = orm.Column(orm.String(32))
    description = orm.Column(orm.String(64), default='')
    tags = orm.Column(orm.String(64), default='')
    permission = orm.Column(orm.Integer, default=default_permission)
    is_recommended = orm.Column(orm.Boolean, default=False)

    def __init__(self,
                 owner_id,
                 name=None,
                 description=None,
                 tags=None,
                 permission=default_permission,
                 is_recommended=None):
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.tags = tags
        self.permission = permission
        self.is_recommended = is_recommended
