#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load
from Library.extensions import orm
from Library.OrmModel import BaseModel, BaseSchema
from .User import User

'''
客户id、姓名、联系方式、地址、购物车
'''


class UserProfileSchema(BaseSchema):
    owner_id = fields.Str()
    nickname = fields.Str()
    org = fields.Str()
    bio = fields.Str()
    phone = fields.Str()
    city = fields.Str()
    addresses = fields.Str()  # 详细地址,多个
    shopping_cart_id = fields.Str()

    @post_load
    def make_user_profile(self, data):
        return UserProfile(**data)


class UserProfile(BaseModel):
    schema = UserProfileSchema(strict=True)

    owner_id = orm.Column(orm.String(32), default="", index=True)
    nickname = orm.Column(orm.String(32), default="")
    org = orm.Column(orm.String(32), default="")
    bio = orm.Column(orm.String(64), default="")
    phone = orm.Column(orm.String(64), default="")
    city = orm.Column(orm.String(32), default="")
    addresses = orm.Column(orm.String(512), default="")
    # avatar_url = orm.Column(orm.String(32))
    shopping_cart_id = orm.Column(orm.String(64), default="")

    def __init__(self,
                 owner_id,
                 nickname=None,
                 org=None,
                 bio=None,
                 phone=None,
                 city=None,
                 addresses=None,
                 shopping_cart_id=None):
        self.owner_id = owner_id
        self.nickname = nickname
        self.org = org
        self.bio = bio
        self.phone = phone
        self.city = city
        self.addresses = addresses
        self.shopping_cart_id = shopping_cart_id

    @property
    def address_list(self):
        return list(eval(str(self.addresses))) if self.addresses else []

    @property
    def name(self):
        if not hasattr(self, "_name") or self._name is None:
            try:
                self._name = orm.Query(User.name).filter_by(id=self.owner_id).one()[0]
            except Exception as e:
                self._name = None
        return self._name

    def to_dict(self):
        # return self.schema.dump(self).data
        try:
            # python3
            res = super().to_dict()
        except TypeError:
            res = super(UserProfile, self).to_dict()
        res.update({"name": self.name,
                    "address_list": self.address_list})
        return res