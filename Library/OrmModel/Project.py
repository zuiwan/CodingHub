#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load

from Library.OrmModel import BaseModel, BaseSchema
from Library.extensions import orm

class ProjectSchema(BaseSchema):

    name = fields.Str()
    description = fields.Str()
    default_env = fields.Str()
    family_id = fields.Str()
    latest_version = fields.Float()
    owner_id = fields.Str()
    tags = fields.Str()
    permission = fields.Int()
    fork_from_id = fields.Str()
    status = fields.Str()
    bg_url_id = fields.Str()
    is_recommended = fields.Boolean()
    @post_load
    def make_project(self, data):
        return Project(**data)


class Project(BaseModel):
    schema = ProjectSchema(strict=True)
    '''
    permission:integer
    0 public default
    1 private
    '''
    default_permission = 0

    name = orm.Column(orm.String(64), index=True)
    owner_id = orm.Column(orm.String(32))
    description = orm.Column(orm.String(64), default='')
    default_env = orm.Column(orm.String(64), default='')
    family_id = orm.Column(orm.String(64), default='')
    latest_version = orm.Column(orm.Float(32), default=0)
    tags = orm.Column(orm.String(64), default='')
    permission = orm.Column(orm.Integer, default=default_permission)
    fork_from_id = orm.Column(orm.String(32), default='')
    status = orm.Column(orm.String(8), default='')
    bg_url_id = orm.Column(orm.String(32), default='')
    is_recommended = orm.Column(orm.Boolean, default=False)

    def __init__(self,
                 name,
                 owner_id,
                 description=None,
                 default_env=None,
                 family_id=None,
                 latest_version=None,
                 tags=None,
                 permission=default_permission,
                 fork_from_id=None,
                 status=None,
                 bg_url_id=None,
                 is_recommended=None):
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.default_env = default_env
        self.family_id = family_id
        self.latest_version = latest_version
        self.tags = tags
        self.permission = permission
        self.fork_from_id = fork_from_id
        self.status = status
        self.bg_url_id = bg_url_id
        self.is_recommended = is_recommended
