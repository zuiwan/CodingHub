#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       Contacts
   Description:
   Author:          huangzhen
   date:            2018/3/13
-------------------------------------------------
   Change Activity:
                   2018/3/13:
-------------------------------------------------
"""
__author__ = 'huangzhen'

from marshmallow import Schema, fields, post_load
from Library.extensions import orm
from Library.OrmModel import BaseModel, BaseSchema
from Library.Utils.net_util import get_ip_info


class ContactsSchema(BaseSchema):
    namespace = fields.Str()
    nickname = fields.Str()
    name = fields.Str()
    org = fields.Str()
    bio = fields.Str()
    phone = fields.Str()
    city = fields.Str()
    addresses = fields.Str()  # 详细地址,多个
    profile_id = fields.Str()
    source_ip = fields.Str()

    @post_load
    def make_contacts(self, data):
        return Contacts(**data)


class Contacts(BaseModel):
    schema = ContactsSchema(strict=True)
    namespace = orm.Column(orm.String(32), default="public")
    nickname = orm.Column(orm.String(32), default="")
    name = orm.Column(orm.String(32), default="")
    org = orm.Column(orm.String(32), default="")
    phone = orm.Column(orm.String(32), default="")
    city = orm.Column(orm.String(32), default="")
    addresses = orm.Column(orm.String(512), default="")
    profile_id = orm.Column(orm.String(32), default="")
    source_ip = orm.Column(orm.String(32), default="")

    def __init__(self,
                 owner_id,
                 name,
                 namespace,
                 nickname=None,
                 org=None,
                 phone=None,
                 city=None,
                 addresses=None,
                 source_ip=None):
        self.owner_id = owner_id
        self.name = name
        self.nickname = nickname
        self.org = org
        self.phone = phone
        self.city = city
        self.addresses = addresses
        self.namespace = namespace
        self.source_ip = source_ip

    @property
    def address_list(self):
        if self.addresses:
            if ',' in self.addresses:
                return list(eval(str(self.addresses)))
            else:
                return [self.addresses]
        return []

    @property
    def source_position(self):
        return get_ip_info(self.source_ip)
