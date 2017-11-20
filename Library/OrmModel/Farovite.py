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
    catalog=fields.Str()
    origin=fields.Str()
    url=fields.Str()
    project_id=fields.Int()
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
    default_catalog="myCatalog"

    name = orm.Column(orm.String(64), index=True)
    owner_id = orm.Column(orm.String(32))
    description = orm.Column(orm.String(64), default='')
    tags = orm.Column(orm.String(64), default='')
    permission = orm.Column(orm.Integer, default=default_permission)
    is_recommended = orm.Column(orm.Boolean, default=False)
    origin=orm.Column(orm.String(64))
    catalog=orm.Column(orm.String(64),default=default_catalog)
    url=orm.Column(orm.String(64))
    project_id=orm.Column(orm.Integer)

    def __init__(self,
                 owner_id,
                 url,
                 project_id,
                 origin=None,
                 catalog=default_catalog,
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
        self.catalog=catalog
        self.url=url
        self.project_id=project_id
        self.origin=origin
