#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load

from Library.OrmModel import BaseModel, BaseSchema
from Library.extensions import orm


class FavoriteSchema(BaseSchema):
    name = fields.Str()
    description = fields.Str(allow_none=True)
    owner_id = fields.Str()
    tags = fields.Str()  # 标签
    origin = fields.Str()  # 出处，暂时不用
    source = fields.Str()  # 出处
    is_private = fields.Boolean()  # 是否私有
    is_recommended = fields.Boolean()  # 是否推荐（is_private=False）
    is_unread = fields.Boolean()  # 是否未读
    catalog = fields.Str()  # 目录
    url = fields.Str()  # url类收藏

    content_id = fields.Str()  # 爬虫爬取到的网页内容（mongodb那边的id）
    project_id = fields.Int()  # 所属项目id

    @post_load
    def make_favorite(self, data):
        return Favorite(**data)


class Favorite(BaseModel):
    schema = FavoriteSchema(strict=True)

    default_permission = 0
    default_catalog = "default"

    name = orm.Column(orm.String(64))
    owner_id = orm.Column(orm.String(32))
    description = orm.Column(orm.String(64), default='')
    tags = orm.Column(orm.String(64), default='')
    is_recommended = orm.Column(orm.Boolean, default=False)
    is_private = orm.Column(orm.Boolean, default=False)
    is_unread = orm.Column(orm.Boolean, default=False)
    origin = orm.Column(orm.String(64), default='')
    catalog = orm.Column(orm.String(64), default=default_catalog)
    url = orm.Column(orm.String(64))
    project_id = orm.Column(orm.Integer)

    def __init__(self,
                 owner_id,
                 url=None,
                 project_id=None,
                 source=None,
                 origin=None,
                 name=None,
                 catalog=None,
                 description=None,
                 tags=None,
                 is_recommended=None,
                 is_unread=None):
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.tags = tags
        self.is_recommended = is_recommended
        self.is_unread = is_unread
        self.catalog = catalog
        self.url = url
        self.project_id = project_id
        self.origin = origin
        self.source = source
