#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       ShoppingCart
   Description:
   Author:          huangzhen
   date:            2018/3/4
-------------------------------------------------
   Change Activity:
                   2018/3/4:
-------------------------------------------------
"""
import typing

__author__ = 'huangzhen'

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load
from Library.extensions import orm, mongo
from Library.OrmModel import BaseModel, BaseSchema
import json

'''
客户id、姓名、联系方式、地址、购物车
'''


class Item(object):
    def __init__(self, product_id, count, address, unit_price):
        self.product_id = product_id
        self.count = count
        self.address = address
        self.unit_price = unit_price

    @property
    def to_dict(self):
        if not hasattr(self, "_dict") or self._dict is None:
            self._dict = {
                "product_id": self.product_id,
                "count": self.count,
                "address": self.address,
                "unit_price": self.unit_price
            }
        return self._dict


class ShoppingCart(object):
    '''
    客户id、产品名称、数量、规格、（图片）、（显示总价）
    products为JSON数组（后续可考虑存储到MongoDB）
      {
        product_id: {
            'product_id': 商品id
            'count':  数量,
            'address': 收货地址,
            'unit_price': 单价},
          }
      }

    '''

    def __init__(self,
                 owner_id,
                 products=None):
        self.db = mongo.db.shopping_carts
        self.owner_id = owner_id
        if isinstance(products, typing.Iterable) and not isinstance(products, dict):
            # list or tuple, not dict
            self.products = {product.product_id: product.to_dict for product in products}
        else:
            # None or dict
            self.products = products or {}

    def __str__(self):
        return json.dumps(self.as_dict)

    def save(self):
        doc = self.db.find_one_and_update(
            filter={"owner_id": self.owner_id},
            update={"$set":
                        {"products.{}".format(product_id): self.as_dict["products"][product_id]
                         for product_id in self.product_ids
                         } if self.products
                        else self.as_dict},
            # projection={'seq': True, '_id': False},
            upsert=True,
            return_document=True)
        return doc

    def add_one(self, item):
        if isinstance(item, Item):
            item = item.to_dict
        self.products.update(item)

    def add_many(self, items):
        [self.add_one(item) for item in items]

    @property
    def product_ids(self):
        # return set
        if not hasattr(self, "_product_ids") or self._product_ids is None:
            self._product_ids = self.as_dict["products"].keys()
        return self._product_ids

    @property
    def as_dict(self):
        if not hasattr(self, "_dict"):
            products = json.loads(self.products) \
                if isinstance(self.products, str) \
                else self.products
            total_price = 0.0
            for product in products:
                total_price += product["unit_price"] * product["count"]
            self._dict = {
                "owner_id": self.owner_id,
                "total_price": total_price,
                "products": self.products
            }

        return self._dict

    @property
    def total_price(self):
        return self.as_dict["total_price"]

    def remove_many_from_shopping_cart(self, product_ids):
        doc = self.db.find_one_and_update(filter={"owner_id": self.owner_id},
                                          update={"$unset": {"product.{}".format(product_id): 1 for product_id in
                                                             product_ids}},
                                          return_document=True)
        return doc

    def clear_shopping_carts(self):
        self.db.delete_one({"owner_id": self.owner_id})

    def find_shopping_carts(self):
        return self.db.find_one_or_404({'owner_id': self.owner_id})

    def update_item(self, product_id, data):
        doc = self.db.find_one_and_update(filter={"owner_id": self.owner_id},
                                          update={"$set": {"product.{}".format(product_id): data}},
                                          return_document=True)
        return doc
