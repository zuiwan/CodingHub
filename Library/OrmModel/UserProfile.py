#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load
from Library.extensions import orm
from Library.OrmModel import BaseModel,BaseSchema

class UserProfileSchema(BaseSchema):
    owner_id = fields.Str()
    nickname = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    organization = fields.Str(allow_none=True)
    bio = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    bg_url_id = fields.Str(allow_none=True)
    avatar_url_id = fields.Str(allow_none=True)

    @post_load
    def make_user_info(self, data):
        return UserProfile(**data)


class UserProfile(BaseModel):
    schema = UserProfileSchema(strict=True)
    owner_id = orm.Column(orm.String(32))
    nickname = orm.Column(orm.String(32))
    email = orm.Column(orm.String(64))
    organization = orm.Column(orm.String(32))
    bio = orm.Column(orm.String(64))
    phone = orm.Column(orm.String(64))
    city = orm.Column(orm.String(32))
    bg_url_id = orm.Column(orm.String(32))
    avatar_url_id = orm.Column(orm.String(32))
    def __init__(self,
                 owner_id,
                 username=None,
                 nickname=None,
                 email=None,
                 organization=None,
                 bio=None,
                 phone=None,
                 city=None,
                 bg_url_id=None,
                 avatar_url_id=None):
        self.owner_id = owner_id
        self.nickname = nickname
        self.email = email
        self.organization = organization
        self.bio = bio
        self.phone = phone
        self.city = city
        self.username = username
        self.bg_url_id = bg_url_id
        self.avatar_url_id = avatar_url_id
