#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       Product
   Description:
   Author:          huangzhen
   date:            2018/3/4
-------------------------------------------------
   Change Activity:
                   2018/3/4:
-------------------------------------------------
"""
__author__ = 'huangzhen'

'''
2、产品（图片）信息管理（增删改查，分类统计图片）
 产品属性：图片、名称、规格、价格、单位、购买次数、好评度、商品介绍、备注
'''

from marshmallow import Schema, fields, post_load

from Library.OrmModel import BaseModel, BaseSchema
from Library.extensions import orm


class ProductSchema(BaseSchema):
    name = fields.Str()  # 名称
    spec = fields.Str()  # 规格
    img_url = fields.Str()  # 图片
    price = fields.Int()  # 价格，单位分
    boughts = fields.Int()  # 购买次数
    credit = fields.Float()  # 好评度，0.0~1.0
    intro = fields.Str()  # 商品介绍
    remark = fields.Str()  # 备注

    @post_load
    def make_product(self, data):
        return Product(**data)


class Product(BaseModel):
    schema = ProductSchema(strict=True)

    name = orm.Column(orm.String(128), index=True)
    spec = orm.Column(orm.String(256))
    img_url = orm.Column(orm.String(128))
    price = orm.Column(orm.Float(32), default=9.9)
    boughts = orm.Column(orm.Integer, default=0)
    credit = orm.Column(orm.Float(32), default=0.0)
    intro = orm.Column(orm.String(256))
    remark = orm.Column(orm.String(64))

    def __init__(self,
                 name,
                 spec,
                 img_url,
                 price,
                 boughts,
                 credit,
                 intro,
                 remark
                 ):
        self.name = name
        self.spec = spec
        self.img_url = img_url
        self.price = price
        self.boughts = boughts
        self.credit = credit
        self.intro = intro
        self.remark = remark
